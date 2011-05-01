
from types import *
from vtrace import *

import sys
import vdb
import gtk
import gtk.gdk
import pygtk
import pydoc
import struct
import getopt
import inspect
import gtk.glade
import traceback
import threading

import time
import pango
import gobject
import vtrace
import vwidget.main as vw_main
import vdb.gui.extensions

symtype_names = {
    SYM_MISC:"Unknown",
    SYM_GLOBAL:"Global",
    SYM_LOCAL:"Local",
    SYM_FUNCTION:"Function",
    SYM_SECTION:"Section",
    SYM_META:"Meta"}

def hex(num):
    return "0x%.8x" % num

class VdbWindow(Notifier):

    """
    Any VdbWindow extender should name it's class the same as
    the top level gtk.Window object in their glade thing.
    """

    def __init__(self, db, fname):
        Notifier.__init__(self)
        self.vdb = db

        #self.perminant = False

        # Override these for your own gui updating
        self.detached_inactive = []
        self.running_inactive = []
        self.ignore_list = [NOTIFY_DETACH,NOTIFY_EXIT,NOTIFY_LOAD_LIBRARY,NOTIFY_CONTINUE]


        self.glade = gtk.glade.XML(fname)
        self.glade.signal_autoconnect(self)
        self.glade.signal_connect("destroy_event",self.destroy)

        self.vdb.registerNotifier(NOTIFY_ALL, self)

        if self.vdb.config.has_section("FontPreferences"):
            for font in self.vdb.config.options("FontPreferences"):
                descr = pango.FontDescription(font)
                windows = self.vdb.config.get("FontPreferences",font).split(",")
                for window in windows:
                    widget = self.getWidget(window)
                    if not widget:
                        continue
                    widget.modify_font(descr)

    def setupWindow(self):
        """
        Every extender of VdbWindow will need to call this *after*
        the original constructor *and* their own internal setups...
        """
        t = self.vdb.getTrace()
        if t.isRunning():
            self.updateGuiStatus(NOTIFY_CONTINUE)
        else:
            self.updateGuiStatus(NOTIFY_BREAK)
        self.updateWindow(t)

    def handleDelete(self, widget, event):
        """
        For use in hiding windows that you don't want destroyed...
        """
        widget.hide()
        return True

    def acquireLock(self):
        vw_main.guilock.acquire()

    def releaseLock(self):
        vw_main.guilock.release()

    def destroy(self, *args):
        self.vdb.deregisterNotifier(NOTIFY_ALL, self)

    def getTreeviewTextColumn(self, name, index,onedit=False):
        """
        Return a default "TreeViewColumn" of name "name"
        whose TreeModel index for the renderer is "index"
        """
        cell = gtk.CellRendererText()
        if onedit:
            cell.set_property("editable", True)
            cell.connect("edited", onedit)
        col = gtk.TreeViewColumn(name,cell,text=index)
        col.set_property("resizable",True)
        col.set_property("sizing",1)
        return col

    def setTreeSelected(self, treename, column, value):
        tree = self.getWidget(treename)
        model = tree.get_model()
        path,view = tree.get_cursor()
        if path:
            iter = model.get_iter(path)
            model.set_value(iter, column, value)

    def getTreeSelected(self, treename, colnum):
        """
        Utility for getting the object in the given
        row for the named tree
        """
        obj = None
        treeview = self.getWidget(treename)
        model = treeview.get_model()
        path,view = treeview.get_cursor()
        if path:
            iter = model.get_iter(path)
            obj = model.get_value(iter, colnum)

        return obj

    def updateGuiStatus(self, event=NOTIFY_BREAK):
        if event == NOTIFY_ATTACH:
            self.activateList(self.detached_inactive, True)

        elif event == NOTIFY_DETACH:
            self.activateList(self.detached_inactive, False)

        elif event == NOTIFY_CONTINUE:
            self.activateList(self.running_inactive, False)

        elif event == NOTIFY_EXIT:
            self.activateList(self.detached_inactive, False)

        else: # Just about anything else means we've broken
            t = self.vdb.getTrace()
            if not t.shouldRunAgain():
                self.activateList(self.running_inactive, True)

    def activateList(self, widgetlist, status=True):
        for name in widgetlist:
            wid = self.getWidget(name)
            wid.set_sensitive(status)

    def setTitle(self, title):
        widget = self.getWidget(self.__class__.__name__)
        if widget:
            widget.set_title(title)

    def setSensitive(self, widgetname, sensitive):
        wid = self.getWidget(widgetname)
        wid.set_sensitive(sensitive)

    def intFromWidget(self, wName):
        text = self.textFromWidget(wName)
        t = self.vdb.getTrace()
        return t.parseExpression(text)

    def textFromWidget(self, wName):
        wid = self.glade.get_widget(wName)
        if not wid:
            raise Exception("ERROR - Can't find widget %s" % wName)
        return wid.get_text()

    def getWidget(self, name):
        return self.glade.get_widget(name)

    def doRedraw(self):
        """
        You *must* have the lock when calling this!
        """
        wid = self.getWidget(self.__class__.__name__)
        if wid:
            gobject.idle_add(wid.queue_draw)
        else:
            print "DORKED:",self.__class__.__name__

    def notify(self, event, trace):

        self.acquireLock()
        try:
            self.updateGuiStatus(event)

            if event in self.ignore_list:
                return # This *will* hit the finally

            if trace.shouldRunAgain():
                return

            self.updateWindow(trace)
        finally:
            self.releaseLock()

    def updateWindow(self, trace):
        """
        Other windows may over-ride this
        to refresh their data when they should.
        (ALL CALLERS MUST HAVE THE GTK LOCK ALREADY)
        """
        pass

    def textFromCombo(self, widgetname):
        combo = self.getWidget(widgetname)
        model = combo.get_model()
        active = combo.get_active()
        return model[active][0]

class ResultWindow(VdbWindow):

    def __init__(self, db, data=None, title="Results",show=True):
        VdbWindow.__init__(self, db, vdb.basepath+"glade/ResultWindow.glade")

        self.detached_inactive = ["ResultList",]
        self.running_inactive = ["ResultList",]

        self.MemoryWindow = None
        self.format = (str,str)
        self.setupResultView()
        win = self.getWidget("ResultWindow")
        win.set_title(title)
        if data:
            self.setupResultData(data)
        if show:
            win.show()
        self.setupWindow()

    def setupResultView(self):
        tree = self.getWidget("ResultList")
        # Create a set of Columns to render
        addrcol = self.getTreeviewTextColumn("Address",0)
        descrcol = self.getTreeviewTextColumn("Description", 1)

        tree.append_column(addrcol)
        tree.append_column(descrcol)

        tree.set_model(gtk.ListStore(*self.format))

    def memWinDelete(self, widget, event):
        self.MemoryWindow = None
        return False

    def setupResultData(self, data):
        """
        MUST ONLY BE CALLED BY THREADS THAT OWN THE GTK LOCK ALREADY
        """
        tree = self.getWidget("ResultList")
        store = tree.get_model()
        store.clear()

        for row in data:
            store.append(row)

    def RowActivated(self, treeview, path, treeviewcol):
        model = treeview.get_model()
        iter = model.get_iter(path)
        addr = model.get_value(iter, 0)
        if not self.MemoryWindow:
            self.MemoryWindow = MemoryWindow(self.vdb, addr, "256")
            self.MemoryWindow.getWidget("MemoryWindow").connect("delete_event", self.memWinDelete)

        self.MemoryWindow.gotoAddressExpression(addr,"256")

class MemoryMapWindow(ResultWindow):
    def setupResultView(self):
        self.format = (str,str,str,str)
        tree = self.getWidget("ResultList")
        # Create a set of Columns to render
        cell = gtk.CellRendererText()

        addrcol = self.getTreeviewTextColumn("Address",0)
        sizecol = self.getTreeviewTextColumn("Size",1)
        permcol = self.getTreeviewTextColumn("Perms",2)
        filecol = self.getTreeviewTextColumn("File",3)

        tree.append_column(addrcol)
        tree.append_column(sizecol)
        tree.append_column(permcol)
        tree.append_column(filecol)

        tree.set_model(gtk.ListStore(*self.format))
        
    def updateWindow(self, trace):
        data = []
        if trace.isAttached():
            for map in trace.getMaps():
                data.append( (hex(map[0]),hex(map[1]),self.vdb.vmemProtFormat(map[2]),map[3]) )
        self.setupResultData(data)

class StackTraceWindow(ResultWindow):

    def setupResultView(self):
        self.format = (str,str,str)

        tree = self.getWidget("ResultList")

        framecol = self.getTreeviewTextColumn("Prog Counter",0)
        pccol = self.getTreeviewTextColumn("Frame Pointer",1)
        namecol = self.getTreeviewTextColumn("Best Name",2)

        tree.append_column(framecol)
        tree.append_column(pccol)
        tree.append_column(namecol)

        tree.set_model(gtk.ListStore(*self.format))

    def updateWindow(self, trace):
        data = []
        if trace.isAttached():
            for pc,frame in trace.getStackTrace():
                bestname = self.vdb.bestName(pc)
                data.append((hex(pc),hex(frame),bestname))
        self.setupResultData(data)

class FileDescriptorWindow(ResultWindow):
    """
    A window for viewing file descriptors
    """
    def setupResultView(self):
        self.format = (str,str,str)
        tree = self.getWidget("ResultList")

        fdcol = self.getTreeviewTextColumn("File Descriptor", 0)
        typecol = self.getTreeviewTextColumn("Type", 1)
        bestcol = self.getTreeviewTextColumn("Best Name", 2)

        tree.append_column(fdcol)
        tree.append_column(typecol)
        tree.append_column(bestcol)

        tree.set_model(gtk.ListStore(*self.format))

    def updateWindow(self, trace):
        data = []
        if trace.isAttached():
            for fdnum,fdtype,bestname in trace.getFds():
                fdnum = repr(fdnum)
                data.append((fdnum,fdtype,bestname))
        self.setupResultData(data)

class StructWindow(VdbWindow):
    """
    A window type for viewing Vstruct structures
    """
    def __init__(self, db):
        VdbWindow.__init__(self, db, vdb.basepath + "glade/StructWindow.glade")
        tree = self.getWidget("StructTree")
        tree.append_column(self.getTreeviewTextColumn("Field Name", 1))
        tree.append_column(self.getTreeviewTextColumn("Value", 2))
        tree.set_model(gtk.TreeStore(object,str,str))


        combo = self.getWidget("VStructModuleCombo")
        combo.connect("changed", self.ModuleComboChanged)
        combo.set_model(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        #model = combo.get_model()
        for name in vstruct.getModuleNames():
            combo.append_text(name)
            #model.append(name)
        

        scombo = self.getWidget("VStructStructureCombo")
        scombo.connect("changed", self.StructComboChanged)
        scombo.set_model(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        scombo.pack_start(cell, True)
        scombo.add_attribute(cell, 'text', 0)

    def getComboText(self, combo):
        iter = combo.get_active_iter()
        if iter == None:
            return None
        return combo.get_model().get_value(iter, 0)

    def ModuleComboChanged(self, combo):
        mname = self.getComboText(combo)
        combo = self.getWidget("VStructStructureCombo")
        model = combo.get_model()
        model.clear()
        if mname == None:
            return
        for sname in vstruct.getStructNames(mname):
            combo.append_text(sname)

    def StructComboChanged(self, combo):
        self.updateWindow(self.vdb.getTrace())

    def StructTreeDoubleClicked(self, treeview, path, treeviewcol):
        model = treeview.get_model()
        iter = model.get_iter(path)
        item = model.get_value(iter, 0)
        if item == None:
            return

        if isinstance(item, vstruct.v_ptr):
            MemoryWindow(self.vdb, addr_expr="0x%.8x" % item.value)

    def GuiUpdate(self, *args):
        self.updateWindow(self.vdb.getTrace())

    def updateWindow(self, trace):
        tree = self.getWidget("StructTree")
        model = tree.get_model()
        model.clear()

        expstr = self.getWidget("StructAddrText").get_text()
        mname = self.getComboText(self.getWidget("VStructModuleCombo"))
        sname = self.getComboText(self.getWidget("VStructStructureCombo"))

        if sname == None or mname == None:
            return

        if not expstr: # Either None *or* a "" string...
            return

        # Update the structure from process memory
        addr = trace.parseExpression(expstr)

        s = trace.getStruct("%s.%s" % (mname,sname), addr)

        p = model.append(None, (None, s.__class__.__name__, "0x%.8x" % addr))
        self.addToModel(model, p, s)
        tree.expand_row(model.get_path(p), False)

    def addToModel(self, model, parent, value):
        for name,vtype in value._fields_:
            f = getattr(value, name)
            self.putItem(model, parent, name, f)

    def putItem(self, model, parent, name, item):
        if isinstance(item, vstruct.VStruct):
            p = model.append(parent, (item,name, item.__class__.__name__))
            self.addToModel(model, p, item)

        elif isinstance(item, vstruct.v_ptr):
            model.append(parent, (item, name, "0x%.8x" % item.value))

        elif isinstance(item, vstruct.VArray):
            a = model.append(parent, (item, name, "Array"))
            for i in item:
                self.putItem(model, a, "", i)
        else:
            model.append(parent, (item, name, "0x%.8x (%d)" % (item.value, item.value)))

class MemoryWindow(VdbWindow):
    """
    The auto-connect handler class for the memory windows.
    """

    def __init__(self, db, addr_expr="esp",len_expr="256",format="Bytes"):
        VdbWindow.__init__(self, db, vdb.basepath+"glade/MemoryWindow.glade")
        self.mem = "robs mom is kewl"
        self.addr = 0

        memfmt = self.getWidget("MemoryFormat")
        active = 0

        format_names = self.vdb.getFormatNames()

        for i in range(len(format_names)):
            if format_names[i] == format:
                active = i
            memfmt.append_text(format_names[i])

        memfmt.set_active(active)

        self.getWidget("MemoryExpression").set_text(addr_expr)
        self.getWidget("MemoryLength").set_text(len_expr)

        self.testtag = self.getWidget("CharText").get_buffer().create_tag("strlen")
        self.testtag.set_property("background","red")

        try:
            self.MemoryExpression()
        except:
            pass
        self.getWidget("MemoryWindow").show()
        self.setupWindow()

    def gotoAddressExpression(self, address, length):
        self.getWidget("MemoryExpression").set_text(address)
        self.getWidget("MemoryLength").set_text(length)
        self.MemoryExpression()

    def MemoryExpression(self, *args):
        self.addr = self.intFromWidget("MemoryExpression")
        mlen = self.intFromWidget("MemoryLength")

        t = self.vdb.getTrace()

        if t.isAttached():
            self.mem = t.readMemory(self.addr, mlen)
            self.UpdateDataView()

    def updateTitle(self):
        expr = self.textFromWidget("MemoryExpression")
        format = self.textFromCombo("MemoryFormat")
        self.setTitle("MemoryWindow: %s (%s)" % (expr,format))

    def UpdateDataView(self, *args):
        addrbuf = ""
        charbuf = ""
        databuf = ""

        format = self.textFromCombo("MemoryFormat")

        addrbuf,databuf,charbuf = self.vdb.doFormat(format, self.addr, self.mem)

        abuf = self.getWidget("AddressText").get_buffer()
        dbuf = self.getWidget("DataText").get_buffer()
        cbuf = self.getWidget("CharText").get_buffer()

        abuf.set_text("")
        dbuf.set_text("")
        cbuf.set_text("")

        abuf.insert_with_tags(abuf.get_end_iter(), addrbuf)
        dbuf.insert_with_tags(dbuf.get_end_iter(), databuf)
        cbuf.insert_with_tags(cbuf.get_end_iter(), charbuf)
        self.updateTitle()

    def updateWindow(self, trace):
        self.MemoryExpression(None)

class MainWindow(VdbWindow):
    """
    Implement all the necissary handlers for the current
    vdb GUI. Requires a VDB instance as an argument
    """

    def __init__(self, db=None):
        if not db:
            db = vdb.Vdb()
            
        self.go = True

        # NOTE: This sets self.vdb from db...
        VdbWindow.__init__(self, db, vdb.basepath+"glade/vdb.glade")

        self.cli = vdb.VdbCli(db)
        self.cli.stdout = self

        self.register_views = {}
        self.stackwin = None

        self.setupSymbolView()
        self.setupMetaView()
        self.setupVtraceHelp()
        self.setupRegisterTree()
        self.setupSignalCombo()
        self.setupShortcutKeys()

        self.setupPages()
        self.setupProcessTree()

        # Keep the command history in the gui
        self.cmdindex = -1
        self.cmdhist = ["",]

        # NOTE: For GUI debugging, take this out...
        sys.excepthook = self.excepthook

        self.running_inactive = (
            "ThreadCombo",
            "ContinueButton",
            "SnapshotButton",
            "RegisterTree",
            "DetachButton",
            "SearchButton",
            "StepButton",
            "PendingSignalCombo",
            "ViewMemoryWindow",
            "ViewDisassemblyWindow",
            "RunScript",
            )

        self.detached_inactive = (
            "ThreadCombo",
            "ContinueButton",
            "SnapshotButton",
            "RegisterTree",
            "DetachButton",
            "SearchButton",
            "BreakButton",
            "StepButton",
            "ViewMemoryWindow",
            "ViewDisassemblyWindow",
            "RunScript",
            "PendingSignalCombo",
            "AutoContinueMenu",
            )

        self.auto_cont_map = {
        "AutoContAttach":NOTIFY_ATTACH,
        "AutoContSignal":NOTIFY_SIGNAL,
        "AutoContBreak":NOTIFY_BREAK,
        "AutoContCreateThread":NOTIFY_CREATE_THREAD,
        "AutoContLoadLib":NOTIFY_LOAD_LIBRARY,
        "AutoContThreadExit":NOTIFY_EXIT_THREAD,
        "AutoContUnloadLib":NOTIFY_UNLOAD_LIBRARY}

        #self.vdb.initTrace(trace) # Setup the trace group modes
        self.tooltip = gtk.Tooltips()
        self.setupModesMenu()
        self.updateModesMenu()

        self.updateGuiStatus(NOTIFY_DETACH)
        self.getWidget("MainWindow").show()
        self.setupWindow()

        t = self.vdb.getTrace()

        if t.isAttached():
            self.activateList(self.detached_inactive, True)
            if t.isRunning():
                self.activateList(self.running_inactive, False)
            else:
                self.activateList(self.running_inactive, True)
        else:
            self.activateList(self.detached_inactive, False)

        self.vdb.stdout = self
        self.vdb.stderr = self

        self.loadGuiExtensions()
        self.cmdKeyboardFocus()

    def loadGuiExtensions(self):
        vdb.gui.extensions.loadGuiExtensions(self.vdb, self)

    def registerGuiExtension(self, callback):
        """
        Register a GUI extension which will end up with it's
        name in the Extensions dropdown and callback on click.
        """
        self.vdb.vprint("%s: %s" % (name.__name__, callback))

    def destroy(self, *args):
        VdbWindow.destroy(self)
        sys.stdout = self.savedout
        
    def setupModesMenu(self):
        self.mode_items = {}
        modes_list = gtk.Menu()
        t = self.vdb.getTrace()
        for key,val in t.modes.items():
            item = gtk.CheckMenuItem(key)
            item.set_active(val)
            self.mode_items[key] = item
            self.tooltip.set_tip(item, t.modedocs[key])
            item.connect('activate', self.ModeItemToggle, key)
            item.show()
            modes_list.append(item)

        self.getWidget("ModesMenu").set_submenu(modes_list)

    def updateModesMenu(self):
        for key,val in self.vdb.modes.items():
            self.mode_items[key].set_active(val)

    def setupAutoContinue(self,trace):
        for key,val in self.auto_cont_map.items():
            if val in trace.auto_continue:
                self.getWidget(key).set_active(True)

    def autoContinueToggle(self, menuitem):
        name = menuitem.get_name()
        state = menuitem.get_active()

        t = self.vdb.getTrace()
        event = self.auto_cont_map[name]
        if state:
            t.enableAutoContinue(event)
        else:
            t.disableAutoContinue(event)

    def write(self, buf):
        self.acquireLock()
        try:
            widget = self.getWidget("MainText")
            txtbuf = widget.get_buffer()

            end = txtbuf.get_end_iter()
            txtbuf.place_cursor(end)
            txtbuf.insert_with_tags(end, buf)

            i = txtbuf.get_insert()
            widget.scroll_to_mark(i, 0)

            widget.queue_draw()
        finally:
            self.releaseLock()

    def ModeItemToggle(self, menu_item, name):
        self.vdb.setMode(name, menu_item.get_active())

    def setupPages(self):
        widget = self.getWidget("CommandFrame")
        self.appendPage(widget, "Command")

        self.stackwin = StackTraceWindow(self.vdb, show=False)
        widget = self.stackwin.getWidget("ResultFrame")
        self.appendPage(widget , "Stack Trace")

        #FIXME Perhaps these should go back to being frames?
        win = MemoryMapWindow(self.vdb,title="Memory Maps",show=False)
        widget = win.getWidget("ResultFrame")
        self.appendPage(widget, "Memory Maps")

        win = FileDescriptorWindow(self.vdb,show=False)
        widget = win.getWidget("ResultFrame")
        self.appendPage(widget, "File Descriptors")

        widget = self.getWidget("SymbolFrame")
        self.appendPage(widget, "Symbols")

        widget = self.getWidget("MetaFrame")
        self.appendPage(widget, "Metadata")

    def appendPage(self, page, name):
        notebook = self.getWidget("MainNotebook")
        label = gtk.Label(name)
        label.set_padding(8,0)
        if page.get_parent():
            container = gtk.VBox()
            page.reparent(container)
            page = container
        page.show()
        notebook.append_page(page, label)

    def SnapoutPage(self, pagenum=-1):
        """
        Snapout a page to a window... if pagenum == -1,
        do the currently selected page.
        """
        notebook = self.getWidget("MainNotebook")
        if pagenum == -1:
            pagenum = notebook.get_current_page()

        page = notebook.get_nth_page(pagenum)
        label = notebook.get_tab_label(page)
        title = label.get_text()
        pagesize = page.size_request()

        window = gtk.Window()
        window.set_title(title)
        window.connect("destroy",self.PagerDestroy)
        #window.resize(*pagesize)
        window.resize(550, 300)
        # Stuff the page reference and name into the
        # object for later retreval
        window.vdb_page = page
        window.vdb_title = title

        page.reparent(window)
        window.show()

    def PagerDestroy(self, window):
        self.appendPage(window.vdb_page, window.vdb_title)

    def setupShortcutKeys(self):
        self.shortcut_keys = {}
        if self.vdb.config.has_section("ShortcutKeys"):
            for opt in self.vdb.config.options("ShortcutKeys"):
                try:
                    val = int(opt)
                    methname = self.vdb.config.get("ShortcutKeys",opt)
                    method = getattr(self, methname)
                    self.shortcut_keys[val] = method
                except:
                    self.vdb.verror("ERROR - Config error: %s not valid shortcut key or method" % opt)

    def StructWindowButton(self, *args):
        StructWindow(self.vdb)

    def cmdKeyboardFocus(self):
        self.getWidget("CommandEntry").grab_focus()

    def useHistory(self, delta):
        i = self.cmdindex
        try:
            self.getWidget("CommandEntry").set_text(self.cmdhist[i])
            self.cmdindex += delta
        except IndexError, msg:
            self.getWidget("CommandEntry").set_text("")
            self.cmdindex = 0
        self.cmdKeyboardFocus()

    def CommandEntryKeystroke(self, widget, event):
        if event.keyval == 65362:
            self.useHistory(-1)
            return True
            #self.cmdKeyboardFocus()
        elif event.keyval == 65364:
            self.useHistory(1)
            return True
            #self.cmdKeyboardFocus()

    def CommandEntry(self, *args):
        """
        A command and <return> have been entered in the
        CommandEntry widget
        """
        cmd = self.textFromWidget("CommandEntry")
        self.cmdhist.append(cmd)
        self.cmdindex = -1
        self.getWidget("CommandEntry").set_text("")
        self.releaseLock()
        self.write("vdb> %s\n" % cmd)
        try:
            cmd = self.cli.precmd(cmd)
            self.cli.onecmd(cmd)
        finally:
            self.acquireLock()

    def MainWindowQuit(self, widget, object=None):
        vw_main.go = False

    def NewDisassemblyWindow(self, *args):
        t = self.vdb.getTrace()
        if t.isAttached():
            MemoryWindow(self.vdb, t.archGetPcName(), "256", "ASM")
        else:
            MemoryWindow(self.vdb)

    def NewMemoryWindow(self, *args):
        MemoryWindow(self.vdb)

    def MainWindowKey(self, gnomeapp, gdkevent):
        method = self.shortcut_keys.get(gdkevent.keyval, None)
        if method:
            method()

    def UpdateProcessList(self, *args):
        tree = self.getWidget("ProcessTree")
        model = tree.get_model()
        model.clear()

        t = self.vdb.getTrace()
        for p in t.ps():
            model.append(p)

    def setupProcessTree(self):
        tree = self.getWidget("ProcessTree")
        # Set the model for the process selection dialog
        tree.set_model(gtk.ListStore(int,str))

        pidcol = self.getTreeviewTextColumn("Process Id", 0)
        namecol = self.getTreeviewTextColumn("Process Name", 1)
        
        tree.append_column(pidcol)
        tree.append_column(namecol)

    def VscriptLoad(self, *args):
        s = gtk.FileChooserDialog(
                            title="Load Vscript File",
                            action=gtk.FILE_CHOOSER_ACTION_OPEN,
                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        res = s.run()
        if res == gtk.RESPONSE_OK:
            f = file(s.get_filename(), "r")
            buffer = self.getWidget("VscriptText").get_buffer()
            buffer.set_text(f.read())
            f.close()

        s.destroy()

    def VscriptSave(self, *args):
        s = gtk.FileChooserDialog(
                            title="Save Vscript File",
                            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        res = s.run()
        if res == gtk.RESPONSE_OK:
            buffer = self.getWidget("VscriptText").get_buffer()
            start,end = buffer.get_bounds()
            text = buffer.get_text(start,end)
            f = file(s.get_filename(), "w")
            f.write(text)
            f.close()

        s.destroy()

    def VscriptCancel(self, *args):
        self.getWidget("VscriptDialog").hide()

    def VscriptRun(self, *args):
        buffer = self.getWidget("VscriptText").get_buffer()
        start, end = buffer.get_bounds()
        script = buffer.get_text(start,end)
        self.releaseLock()

        try:
            self.vdb.scriptstring(script, "interactive.py")
        finally:
            self.acquireLock()

    def RunInteractiveScript(self, *args):
        dialog = self.getWidget("VscriptDialog")
        dialog.show()

    def RunScript(self, *args):
        dialog = self.getWidget("RunDialog")
        dialog.set_title("Run VDB Script")
        dialog.show()

    def ExecTrace(self, *args):
        dialog = self.getWidget("RunDialog")
        dialog.set_title("Execute New Trace")
        dialog.show()

    def RunCancel(self, *args):
        self.getWidget("RunDialog").hide()

    def RunOk(self, *args):
        dialog = self.getWidget("RunDialog")
        dialog.hide()
        title = dialog.get_title()
        self.releaseLock()
        try:
            if title == "Execute New Trace":
                #FIXME what is this now?
                t = self.vdb.newTrace()
                t.execute(self.textFromWidget("RunText"))
            elif title == "Run VDB Script":
                # a little parser duplication hackery...
                self.cli.do_script(self.textFromWidget("RunText"))
            else:
                raise Exception("ERROR - Unknown RunDialog Title: %s" % title)
        finally:
            self.acquireLock()

    def issueNotice(self, message, title="Notice"):
        ndialog = self.getWidget("NoticeDialog")
        self.getWidget("NoticeDialogText").get_buffer().set_text(message)
        ndialog.set_title(title)
        ndialog.show()

    def excepthook(self, etype, value, tb):
        msg  = "Exception Type: %s\n" % etype.__name__
        msg += "Exception Value: %s\n" % value
        msg += "Traceback Follows:\n"
        for line in traceback.format_tb(tb):
            msg += line

        self.issueNotice(msg, "Exception")

    def NoticeDialogOk(self, *args):
        self.getWidget("NoticeDialog").hide()

    def AttachButton(self, *args):
        dialog = self.glade.get_widget("AttachDialog")
        self.UpdateProcessList()
        ret = dialog.run()
        dialog.hide()
        if ret == gtk.RESPONSE_OK:
            pidstr = self.textFromWidget("AttachPidText")
            if not pidstr:
                return

            pid = int(pidstr)

            self.releaseLock()
            t = self.vdb.newTrace()
            try:
                t.attach(pid)
            finally:
                self.acquireLock()

    def ProcessTreeSelected(self, *args):
        pid = self.getTreeSelected("ProcessTree",0)
        if pid == None:
            return
        self.getWidget("AttachPidText").set_text(str(pid))

    def AttachActivated(self, *args):
        """
        For things like hitting enter in the pid input box
        """
        self.getWidget("AttachDialog").response(gtk.RESPONSE_OK)

    def setupMetaView(self):
        tree = self.getWidget("MetaTree")
        namecol = self.getTreeviewTextColumn("Name", 0)
        valcol = self.getTreeviewTextColumn("Value", 1)

        tree.append_column(namecol)
        tree.append_column(valcol)

    def setupSymbolView(self, *args):
        tree = self.getWidget("SymbolTree")
        namecol = self.getTreeviewTextColumn("Name", 1)
        valcol = self.getTreeviewTextColumn("Value", 2)
        sizecol = self.getTreeviewTextColumn("Size", 3)

        tree.append_column(namecol)
        tree.append_column(valcol)
        tree.append_column(sizecol)
        self.clearSymbolView()

    def clearSymbolView(self, *args):
        store =  gtk.TreeStore(object,str,str,str)
        tree = self.getWidget("SymbolTree")
        tree.set_model(store)
        self.sym_files_done = []
        self.symexpanded = []

    def updateSymbolView(self, trace):
        tree = self.getWidget("SymbolTree")
        store = tree.get_model()

        libs = trace.getNormalizedLibNames()

        # Catch "attach" and clean out...
        if len(libs) == 0:
            self.clearSymbolView()

        else:
            libs.sort()
            for fname in libs:
                if fname in self.sym_files_done:
                    continue
                f = store.append(None, (None, fname, None, None))
                store.append(f, (None, "Stuff", None, None))
                self.sym_files_done.append(fname)

    def expandSymbolTree(self, treeview, iter, something):
        model = treeview.get_model()
        fname = model.get_value(iter, 1)

        if fname in self.symexpanded:
            return

        t = self.vdb.getTrace()
        syms = t.getSymsForFile(fname)
        if len(syms) == 0:
            return

        glob_node = model.append(iter, (None,"Globals",None,None))
        func_node = model.append(iter, (None,"Functions",None,None))
        sec_node = model.append(iter, (None,"Sections",None, None))
        misc_node = model.append(iter, (None,"Misc.",None,None))

        for sym in syms:
            if len(str(sym)) == 0:
                continue
            tmpnode = misc_node
            if sym.stype == SYM_GLOBAL:
                tmpnode = glob_node
            elif sym.stype == SYM_FUNCTION:
                tmpnode = func_node
            elif sym.stype == SYM_SECTION:
                tmpnode = sec_node
            model.append(tmpnode, (sym, str(sym), hex(long(sym)), len(sym)))

        self.symexpanded.append(fname)

    def activateSymbolTree(self, treeview, path, treeviewcol):
        model = treeview.get_model()
        iter = model.get_iter(path)
        sym = model.get_value(iter, 0)
        if sym == None:
            return

        addr = long(sym)
        size = len(sym)
        if sym.stype == vtrace.SYM_FUNCTION:
            fmt = "ASM"
        else:
            fmt = "Bytes"

        if size == 0:
            size = 256

        MemoryWindow(self.vdb, hex(addr), str(size), fmt)
            
    def addToStore(self, store, parent, key, val):
        if type(val) == DictType:
            node = store.append(parent, [key, ""])
            for key,val in val.items():
                self.addToStore(store, node, key, val)
        elif type(val) in [ListType,TupleType]:
            node = store.append(parent, [key,""])
            for item in val:
                self.addToStore(store, node, "", item)
        elif type(val) in [IntType, LongType]:
            numstr = repr(val)
            if val > 1024:
                numstr = hex(val)
            store.append(parent, [key, numstr])
        else:
            store.append(parent, [key, repr(val)])

    def updateMetaView(self, trace):
        tree = self.getWidget("MetaTree")
        store = gtk.TreeStore(str,str)

        metadata = trace.metadata
        for key,val in metadata.items():
            self.addToStore(store, None, key, val)
        tree.set_model(store)

    def HideWindow(self, *args):
        return False


    def DetachButton(self, *args):
        """
        WARNING: functions like trace.detach()
        and self.vdb.run() REQUIRE you to release the
        lock first so that remote debugging theads can
        do their thing on the notifier calls!
        """
        self.releaseLock()
        try:
            self.vdb.getTrace().detach()
        finally:
            self.acquireLock()

    def ContinueButton(self, *args):
        self.releaseLock()
        try:
            self.vdb.getTrace().run()
        finally:
            self.acquireLock()

    def SnapshotButton(self, *args):
        filename = None
        s = gtk.FileChooserDialog(
                            title="Save Process Snapshot",
                            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        res = s.run()
        if res == gtk.RESPONSE_OK:
            filename = s.get_filename()
        s.destroy()

        if filename != None:
            trace = self.vdb.getTrace()
            snap = trace.takeSnapshot()
            snap.saveToFile(filename)

    def BreakButton(self, *args):
        self.vdb.setMode("RunForever", False)
        self.releaseLock()
        try:
            self.vdb.getTrace().sendBreak()
        except:
            self.vdb.verror("WARNING - Trace not running")
        self.acquireLock()
        self.updateSignalCombo(0)

    def StepButton(self, *args):
        self.releaseLock()
        try:
            self.vdb.getTrace().stepi()
        finally:
            self.acquireLock()

    def PendingSignalCombo(self, *args):
        signame = self.textFromCombo("PendingSignalCombo")
        signo = self.vdb.getSignal(signame)
        self.vdb.setMeta("PendingSignal",signo)

    def setupSignalCombo(self):
        self.sigcombo_lookup = {} # To lookup by signo which active slot
        combo = self.getWidget("PendingSignalCombo")
        index = 0
        for i in range(signal.NSIG):
            name = self.vdb.getSignal(i)
            if name:
                self.sigcombo_lookup[i] = index
                combo.append_text(name)
                index+=1
        combo.set_active(0)

    def updateSignalCombo(self, signal):
        combo = self.getWidget("PendingSignalCombo")
        index = self.sigcombo_lookup.get(signal, 0)
        combo.set_active(index)

    def updateThreadCombo(self, trace):
        combo = self.getWidget("ThreadCombo")
        model = combo.get_model()

        model.clear()

        if trace.isAttached():
            thrid = trace.getMeta("ThreadId")
            threads = trace.getThreads().keys()
            for i in range(len(threads)):
                model.append([str(threads[i])])
            combo.set_active(threads.index(thrid))

    def threadComboSelected(self, combo):
        which = combo.get_active_text()
        if which == None:
            return

        self.vdb.getTrace().selectThread(int(which))

        self.ResetRegisterTree()
        self.stackwin.updateWindow(self.vdb.getTrace())

    def RegisterEdited(self, renderer, row, value):
        t = self.vdb.getTrace()
        value = t.parseExpression(value)
        regname = self.getTreeSelected("RegisterTree", 0)
        t.setRegisterByName(regname, value)
        self.ResetRegisterTree()

    def setupRegisterTree(self):
        tree = self.glade.get_widget("RegisterTree")
        tree.set_model(gtk.ListStore(str,str,str,str))

        arch = self.vdb.getTrace().getMeta("Architecture")
        regview = "RegisterView:" + arch

        combo = self.getWidget("RegisterViewCombo")
        for view in self.vdb.config.options(regview):
            opt = self.vdb.config.get(regview,view)
            self.register_views[view] = opt
            combo.append_text(view)

        col0 = self.getTreeviewTextColumn("Register",0)
        col1 = self.getTreeviewTextColumn("Hex",1,onedit=self.RegisterEdited)
        col2 = self.getTreeviewTextColumn("Decimal",2)
        col3 = self.getTreeviewTextColumn("Chars",3)

        tree.append_column(col0)
        tree.append_column(col1)
        tree.append_column(col2)
        tree.append_column(col3)

        combo.set_active(0)

    def ResetRegisterTree(self):
        tree = self.getWidget("RegisterTree")
        store = tree.get_model()
        # Create a store of data
        #FIXME we don't need to create one every time!
        store.clear()

        viewname = self.textFromCombo("RegisterViewCombo")
        view = self.register_views.get(viewname).split(",")

        t = self.vdb.getTrace()

        if t.isAttached():
            regs = t.getRegisters()
            if not view:
                view = regs.keys()

            for name in view:
                val = regs.get(name,None)
                if val == None:
                    store.append([name,"<error>","<error>","<error>"])
                else:
                    #chrs = repr(struct.pack("P", val))
                    chrs = ""
                    valcpy = val
                    while valcpy:
                        cval = valcpy & 0xff
                        if cval >= 0x20 and cval < 0x7f:
                            chrs += chr(cval)
                        else:
                            chrs += "."
                        valcpy = valcpy >> 8
                    store.append([name,"0x%.8x"%val,"%d"%val,chrs])
        else:
            for name in view:
                store.append([name,"0","0","0"])

        tree.set_model(store)

    def SearchButton(self, *args):
        self.getWidget("SearchDialogRangeCombo").set_active(0)
        self.getWidget("SearchDialogTypeCombo").set_active(0)
        base = self.getWidget("SearchDialogBaseText")
        base.set_text("")
        base.set_sensitive(False)
        length = self.getWidget("SearchDialogLengthText")
        length.set_text("")
        length.set_sensitive(False)
        self.getWidget("SearchDialog").show()

    def SearchDialogOk(self, *args):

        self.getWidget("SearchDialog").hide()
        self.bannerUp("Searching...")
        results = []
        printres = []

        range = self.getWidget("SearchDialogRangeCombo").get_active()
        stype = self.getWidget("SearchDialogTypeCombo").get_active()
        input = self.getWidget("SearchDialogInputText").get_text()

        t = self.vdb.getTrace()
        if stype == 0: # It's a string
            searchbytes = eval('"%s"' % input)
        elif stype == 1: # It's an address
            saddr = t.parseExpression(input)
            searchbytes = struct.pack("L",saddr)
        elif stype == 2: # It's an RE
            raise Exception("Not Supported Yet")

        if range == 0:
            # Search all of memory
            pass
        else:
            pass
            # Search a memory range

        results = t.searchMemory(searchbytes)

        self.bannerDown()

        if len(results) == 0:
            self.vdb.vprint("No Results")
        else:
            for addr in results:
                printres.append(("0x%.8x" % addr, self.vdb.bestName(addr)))
            ResultWindow(self.vdb, printres, "Search: %s" % (repr(searchbytes)))

    def bannerUp(self, message):
        self.getWidget("BannerLabel").set_label(message)
        self.getWidget("BannerWindow").show()

    def bannerDown(self):
        self.getWidget("BannerWindow").hide()

    def SearchRangeCombo(self, *args):
        a = self.getWidget("SearchDialogRangeCombo").get_active()

        if a == 1:
            self.setSensitive("SearchDialogBaseText", True)
            self.setSensitive("SearchDialogLengthText", True)
        else:
            self.setSensitive("SearchDialogBaseText", False)
            self.setSensitive("SearchDialogLengthText", False)

    def setupVtraceHelp(self):
        self.getWidget("HelpApiText").get_buffer().set_text("use 'pydoc vtrace'")

    def HelpVtraceButton(self, *args):
        self.getWidget("HelpWindow").show()

    def updateWindow(self, trace):
        try:
            self.updateMetaView(trace)
            self.updateModesMenu()
            self.setupAutoContinue(trace)
            #FIXME this must make the GUI slow...
            self.updateSymbolView(trace)
            self.updateSignalCombo(trace.getMeta("PendingSignal"))
            self.updateThreadCombo(trace)
            self.ResetRegisterTree()
        except:
            self.vdb.verror("WARNING - Exception during notify in GUI (%s)" % traceback.format_exc())

def domain(db=None):
    w = MainWindow(db=db)
    vw_main.main()
    t = w.vdb.getTrace()
    if t.isAttached():
        t.detach()

