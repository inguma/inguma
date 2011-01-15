##      main.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os, sys, time, vte, threading

# Need root for most modules, so...
if os.geteuid() != 0:
    print "You must be root to run most of the modules."
    answer = raw_input("Do you want to continue [y/N]? ")
    if answer.lower() != 'y':
        sys.exit(1)

# Perform the GTK UI dependency check here
from . import dependencyCheck
import lib.ui.config as config
dependencyCheck.gtkui_dependency_check(config)

# Now that I know that I have them, import them!
import pygtk
import gtk, gobject, pango

# This is just general info, to help people knowing their system
print "Starting Inguma, running on:"
print "  Python version:"
print "\n".join("    "+x for x in sys.version.split("\n"))
print "  GTK version:", ".".join(str(x) for x in gtk.gtk_version)
print "  PyGTK version:", ".".join(str(x) for x in gtk.pygtk_version)
print

# Threading initializer
if sys.platform == "win32":
    gobject.threads_init()
else:
    gtk.gdk.threads_init()

# splash!
from lib.ui.splash import Splash
splash = Splash()

# Import ui modules
splash.push(("Loading UI modules"))
import lib.ui.core as core
import lib.ui.propDialog as propDialog
import lib.ui.kbwin as kbwin
import lib.ui.pbar as pbar
import lib.ui.om as om
import lib.ui.graphTBar as graphTBar
import lib.ui.rceTBar as rceTBar
import lib.ui.rcecore as rcecore
import lib.ui.kbtree as kbtree
import lib.ui.nodeMenu as nodeMenu
import lib.ui.graphMenu as graphMenu
import lib.ui.addTargetDlg as addtargetdlg
import lib.ui.exploits as exploits
import lib.ui.libTerminal as libTerminal
import lib.ui.threadstv as threadstv
import lib.ui.reportWin as reportWin

MAINTITLE = "Inguma - A Free Penetration Testing and Vulnerability Research Toolkit"

ui_menu = """
<ui>
  <toolbar name="Toolbar">
    <toolitem action="Load"/>
    <toolitem action="Save"/>
    <toolitem action="Import"/>
    <toolitem action="Edit"/>
    <separator name="s1"/>
    <toolitem action="Proxy"/>
    <toolitem action="Web Server"/>
    <toolitem action="Sniffer"/>
    <separator name="s3"/>
    <toolitem action="Scapy"/>
    <separator name="s4"/>
    <toolitem action="Add Target"/>
    <toolitem action="Preferences"/>
    <toolitem action="Show Log"/>
    <toolitem action="Show KB"/>
    <separator name="s5"/>
    <toolitem action="Report"/>
    <toolitem action="Quit"/>
  </toolbar>
</ui>
"""

rce_menu = """
<ui>
  <toolbar name="RceToolbar">
    <toolitem action="New"/>
    <toolitem action="Load"/>
    <separator name="s1"/>
    <separator name="s2"/>
    <toolitem action="Show Log"/>
    <separator name="s3"/>
    <toolitem action="Debugger"/>
    <separator name="s4"/>
    <toolitem action="Quit"/>
  </toolbar>
</ui>
"""

class MainApp:
    '''Main GTK application'''

    def __init__(self):

#        #################################################################################################################################
#        # Load and apply gtkrc
#        #################################################################
#        # No exception control because rc_parse doesn't throw exception on fail... sad but true ;)
#        ORIGDIR = os.getcwd()
#        os.chdir('lib/ui/data/Brave/gtk-2.0/')
#        gtk.rc_parse('gtkrc')
#        os.chdir(ORIGDIR)

        # Load Output Manager
        self.gom = om.OutputManager('gui')

        #################################################################################################################################
        # Create a new window
        #################################################################
        splash.push(("Creatin main window..."))
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_focus = True
        self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.connect("delete_event", self.quit)
        splash.push(("Loading..."))
        gtk.settings_get_default().set_long_property("gtk-button-images", True, "main") 

        # Title
        self.window.set_title(MAINTITLE)

        # Positions
        self.window.resize(800, 600)
        self.window.move(25, 25)
        # Maximize window
        self.window.maximize()

        #################################################################################################################################
        # Load core...
        #################################################################
        #Initialize KB
        splash.push(("Loading KB..."))
        self.uicore = core.UIcore()
        self.uicore.add_local_asn()
        self.uicore.set_om(self.gom)
        self.gom.set_core(self.uicore)

        #################################################################################################################################
        # Main VBox
        #################################################################
        mainvbox = gtk.VBox(False, 1)
        mainvbox.set_border_width(1)
        self.window.add(mainvbox)
        mainvbox.show()

        #################################################################################################################################
        # Tool Bars HBox
        #################################################################
        tbhbox = gtk.HBox(False, 1)
        mainvbox.pack_start(tbhbox, False, False, 1)
        tbhbox.show()

        #################################################################################################################################
        # UIManager for MAP Toolbar
        #################################################################
        # to make it nice we'll put the toolbar into the handle box,
        # so that it can be detached from the main window
        self.handlebox = gtk.HandleBox()
        tbhbox.pack_start(self.handlebox, True, True, 1)

        # Create a UIManager instance
        splash.push(("Creating menu and toolbar..."))
        uimanager = gtk.UIManager()
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)
        self._actiongroup = actiongroup = gtk.ActionGroup('UIManager')

        # Create actions
        actiongroup.add_actions([
            # xml_name, icon, real_menu_text, accelerator, tooltip, callback

            ('Load', gtk.STOCK_OPEN, ('Load'), None, (''), self.loadKB),
            ('Save', gtk.STOCK_SAVE, ('Save'), None, (''), self.saveKB),
            ('Import', gtk.STOCK_CONVERT, ('Import'), None, (''), self.importScan),
            ('Edit', gtk.STOCK_EDIT, ('Edit'), None, (''), self.loadEditor),
            ('Proxy', gtk.STOCK_CONNECT, ('Proxy'), None, (''), gtk.main_quit),
            ('Web Server', gtk.STOCK_EXECUTE, ('Web'), None, ('Web'), gtk.main_quit),

            #('Sniffer', gtk.STOCK_NETWORK, ('Sniffer'), None, (''), gtk.main_quit),
            ('Sniffer', gtk.STOCK_NETWORK, ('Sniffer'), None, (''), self.run_sniffer),
            ('Scapy', gtk.STOCK_HELP, ('Scapy'), None, (''), self.show_term),
            ('Add Target', gtk.STOCK_ADD, ('Add Target'), None, (''), self.addTarget),
            ('Preferences', gtk.STOCK_PREFERENCES, ('Preferences'), None, (''), self.showPref),
            ('Show Log', gtk.STOCK_DND, ('Show Log'), None, (''), self.show_log),
            ('Show KB', gtk.STOCK_DND, ('Show KB'), None, (''), self.show_kb),
            ('Report', gtk.STOCK_DND, ('Report'), None, (''), self.report),
            ('Quit', gtk.STOCK_QUIT, ('Quit'), None, (''), gtk.main_quit),
        ])

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(ui_menu)

        # Toolbar
        toolbar = uimanager.get_widget('/Toolbar')
        toolbar.set_style(gtk.TOOLBAR_BOTH)

        # Disabled until I get them working
        button_proxy = uimanager.get_widget('/Toolbar/Proxy')
        button_proxy.set_sensitive(False)
        button_web = uimanager.get_widget('/Toolbar/Web Server')
        button_web.set_sensitive(False)

        # Disable if not GtkSourceView2
        if not config.HAS_SOURCEVIEW:
            button_edit = uimanager.get_widget('/Toolbar/Edit')
            button_edit.set_sensitive(False)

        # Disable if not Vte
        if not config.HAS_VTE:
            button_sniffer = uimanager.get_widget('/Toolbar/Sniffer')
            button_sniffer.set_sensitive(False)
            button_scapy = uimanager.get_widget('/Toolbar/Scapy')
            button_scapy.set_sensitive(False)

        self.handlebox.add(toolbar)
        toolbar.show()
        self.handlebox.show()

        #################################################################################################################################
        # Map tab
        #################################################################
        # Will contain on top the notebook and on bottom log window
        self.vpaned = gtk.VPaned()
        # Will contain xdot widget and kb window
        self.hpaned = gtk.HPaned()

        #################################################################
        # KB Textview
        #################################################################
        self.textview = kbwin.KBwindow()
        #self.gom.set_kbwin(self.textview)

        #################################################################
        # KB TreeView
        #################################################################
        self.treeview = kbtree.KBtree()
        self.tree = self.treeview.createTree()
        self.treeview.updateTree()
        self.gom.set_kbwin(self.treeview)
        self.tree.show()

        #################################################################
        # xdot map
        #################################################################
        from . import inxdot

#        self.context = cmenu.contextMenu()
#        self.context.createMenus(self.textview, self.gom)
#
#        self.xdotw = inxdot.MyDotWidget(self.context, self.uicore)

        # nodeMenu initialization stuff
        self.uiman = nodeMenu.UIManager(self.gom, self.uicore, config)
        self.uiman.set_data(None)
        accel = self.uiman.get_accel_group()
        self.window.add_accel_group(accel)

        # graphMenu initialization stuff
        self.graph_uiman = graphMenu.UIManager(self.gom, self.uicore)
        #self.graph_uiman.set_data(None)
        graph_accel = self.graph_uiman.get_accel_group()
        self.window.add_accel_group(graph_accel)

        self.xdotw = inxdot.MyDotWidget(self.uiman, self.graph_uiman, self.uicore)
        setattr(self.graph_uiman, 'xdot', self.xdotw)

        self.xdotw.set_size_request(900,450)
        self.gom.set_map(self.xdotw)
        setattr(self.uicore, 'xdot', self.xdotw)
        self.uicore.getDot(doASN=True)

        self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
        self.xdotw.zoom_image(1.0)

        #################################################################
        # Graph Menu
        #################################################################
        gmenu = graphTBar.GraphMenu(self.xdotw, self.uicore)
        #################################################################
        # HBox for Map and GraphMenu
        #################################################################
        menubox = gtk.HBox()
        menubox.pack_start(self.xdotw, True, True)
        menubox.pack_start(gmenu, False, False)
        # Show elements
        gmenu.show()
        menubox.show()

        #################################################################
        # Scrolled Window
        #################################################################
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.set_size_request(100,100)

        # Add Textview to Scrolled Window
        #self.scrolled_window.add_with_viewport(self.textview)
        self.scrolled_window.add_with_viewport(self.tree)

        #################################################################
        # Map Iface
        #################################################################
        bufferf = "Map"
        frame = gtk.Frame(bufferf)
        frame.set_border_width(5)
        frame.show()
        label = gtk.Label('Map')

        # Test XDOT MAP
        frame.add(self.hpaned)
        #self.hpaned.add1(self.xdotw)
        self.hpaned.add1(menubox)
        self.hpaned.add2(self.scrolled_window)
        self.textview.show()

        # Check visibility on config preferences
        if config.SHOW_KBTREE:
            self.scrolled_window.show()
            self.scrolled_window.is_visible = True
        else:
            self.scrolled_window.is_visible = False

        self.hpaned.show()
        self.xdotw.show()

        label = gtk.Label('Map')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        #################################################################
        # Notebook
        #################################################################
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        #notebook.append_page(frame, label)
        self.notebook.append_page(frame, b)
        self.notebook.connect("switch_page", self.onSwitch)

        #################################################################################################################################
        # Consoles Tab
        #################################################################
        label = gtk.Label('Term')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        term_box = gtk.VBox()
        term_button = gtk.Button("New Tab")
        # Disable if VTE not available
        if not config.HAS_VTE:
            term_button.set_sensitive(False)
        term_box.pack_start(term_button,False)
        self.term_notebook = libTerminal.TerminalNotebook()
        #term_button.connect("clicked", term_notebook.new_tab)
        term_button.connect("clicked", self.new_tab)
        term_box.pack_start(self.term_notebook)
        setattr(self.uiman, 'termnb', self.term_notebook)
        setattr(self.uiman, 'mainnb', self.notebook)

        self.notebook.append_page(term_box, b)
        term_box.show_all()

        #################################################################################################################################
        # RCE Iface
        #################################################################
        # xdot rce
        import xdot
        self.xdotr = xdot.DotWidget()
        self.xdotr.set_size_request(600,512)
        self.xdotr.show()

        bufferf = "RCE"
        frame = gtk.Frame(bufferf)
        frame.set_border_width(5)
        frame.set_size_request(400, 400)

        label = gtk.Label('RCE')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()
        self.notebook.append_page(frame, b)

        # RCE graph menu
        self.rmenu = rceTBar.RceMenu(self.xdotr, rcecore)
        self.dasmenu = rceTBar.DasmMenu()

        #################################################################################################################################
        # UIManager for RCE Toolbar
        #################################################################
        # to make it nice we'll put the toolbar into the handle box,
        # so that it can be detached from the main window
        self.rcehb = gtk.HandleBox()
        tbhbox.pack_start(self.rcehb, True, True, 1)

        # Create a UIManager instance
        rceuiman = gtk.UIManager()
        rceaccelgroup = rceuiman.get_accel_group()
        self.window.add_accel_group(rceaccelgroup)
        self._actiongroup = actiongroup = gtk.ActionGroup('UIManager')

        # Create actions
        actiongroup.add_actions([
            # xml_name, icon, real_menu_text, accelerator, tooltip, callback

            ('New', gtk.STOCK_NEW, ('New'), None, (''), self.newBin),
            ('Load', gtk.STOCK_OPEN, ('Load'), None, (''), self.loadBin),
            ('Show Log', gtk.STOCK_DND, ('Show Log'), None, (''), self.show_log),
            #('Debugger', gtk.STOCK_EXECUTE, ('Debugger'), None, (''), gtk.main_quit),
            ('Debugger', gtk.STOCK_EXECUTE, ('Debugger'), None, (''), self.run_debugger),
            #('Report', gtk.STOCK_DND, ('Report'), None, (''), gtk.main_quit),
            ('Quit', gtk.STOCK_QUIT, ('Quit'), None, (''), gtk.main_quit),
        ])

        # Add the actiongroup to the rceuiman
        rceuiman.insert_action_group(actiongroup, 0)
        rceuiman.add_ui_from_string(rce_menu)

        # Toolbar
        rcetoolbar = rceuiman.get_widget('/RceToolbar')
        self.rcehb.add(rcetoolbar)
        self.rcehb.hide()

        #################################################################
        # RCE HBox and VBoxes
        #################################################################
        rcepaned = gtk.HPaned()
        lrcevb = gtk.VBox(False, 1)
        rrcevb = gtk.VBox(False, 1)

        rcepaned.add1(lrcevb)
        rcepaned.add2(rrcevb)

        lrcevb.pack_start(self.rmenu, False, False, 1)
        rrcevb.pack_start(self.dasmenu, False, False, 1)

        rcepaned.show_all()

        #################################################################
        # Textview RCE
        #################################################################
        rcetv = gtk.TextView(buffer=None)
        rcetv.set_wrap_mode(gtk.WRAP_NONE)
        rcetv.set_editable(False)
        fontdesc = pango.FontDescription("MonoSpace 10")
        #fontdesc = pango.FontDescription("Purisa 10")
        rcetv.modify_font(fontdesc)
        rcetv.show()
        self.textbuffer = rcetv.get_buffer()

        # Scrolled Window
        rce_scrolled_window = gtk.ScrolledWindow()
        rce_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        rce_scrolled_window.show()
        # Add Textview to Scrolled Window
        rce_scrolled_window.add_with_viewport(rcetv)

        # Add xdotr and textview to rcehbox
        lrcevb.pack_start(self.xdotr, True, True, 2)
        rrcevb.pack_start(rce_scrolled_window, True, True, 2)

        frame.add(rcepaned)
        frame.show()
        rcepaned.show()

        #################################################################################################################################
        # Xploit Iface
        #################################################################
        bufferf = "Exploit"
        frame = gtk.Frame(bufferf)
        frame.set_border_width(5)
        frame.show()
        label = gtk.Label('Exploit')
        frame.add(label)
        label.show()
        label = gtk.Label('Exploit')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        self.exploitsInst = exploits.Exploits(config, self.term_notebook)
        exploitsGui = self.exploitsInst.get_widget()
        exploitsGui.show_all()
        self.notebook.append_page(exploitsGui, b)

        #mainvbox.pack_start(notebook, True, True, 1)
        self.vpaned.add1(self.notebook)
        self.notebook.show()


        #################################################################################################################################
        # Log Window
        #################################################################
        self.logtext = gtk.TextView(buffer=None)
        self.logtext.set_wrap_mode(gtk.WRAP_NONE)
        self.logtext.set_editable(False)
        #self.logtext.set_size_request(40,40)
        self.logbuffer = self.logtext.get_buffer()
        self.logbuffer.set_text('Loading Inguma...\n')
        self.logtext.show()

        #################################################################
        # Log Scrolled Window
        #################################################################
        self.log_scrolled_window = gtk.ScrolledWindow()
        self.log_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.log_scrolled_window.is_visible = True

        #Always on bottom on change
        self.vajd = self.log_scrolled_window.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.log_scrolled_window: self.rescroll(a,s))
        
        #self.log_scrolled_window.set_size_request(40,40)
        #self.logtext.set_size_request(20,20)

        # Add Textview to Scrolled Window
        self.log_scrolled_window.add_with_viewport(self.logtext)

        # Set logtext as output for gui
        self.gom.set_gui(self.logbuffer)

        # Add Scrolled Log Window to Bottom Notebook
        ############################################

        # Notebook for bottom panel
        self.bottom_nb = gtk.Notebook()
        self.bottom_nb.set_tab_pos(gtk.POS_LEFT)

        # Icon and label for Logs tab
        label = gtk.Label('Logs')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_JUSTIFY_FILL, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        self.bottom_nb.append_page(self.log_scrolled_window, b)

        # Icon and label for Actions tab
        label = gtk.Label('Actions')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        # Add Threads TreeView
        self.threadsInst = threadstv.ThreadsTv()
        threadsGui = self.threadsInst.get_widget()
        threadsGui.show_all()

        self.bottom_nb.append_page(threadsGui, b)

        #self.bottom_nb.set_scrollable(True)
        self.bottom_nb.set_current_page(0)

        # Check visibility on config preferences
        if config.SHOW_LOG:
            self.bottom_nb.is_visible = True
            self.bottom_nb.show()
        else:
            self.bottom_nb.is_visible = False

        self.vpaned.add2(self.bottom_nb)
        mainvbox.pack_start(self.vpaned, True, True, 1)
        self.log_scrolled_window.show()

        # Add threadtv to core
        self.uicore.set_threadtv(self.threadsInst)
        setattr(self.graph_uiman, 'threadtv', self.threadsInst)

#        #################################################################################################################################
#        # Progress Bar
#        #################################################################
#        self.progressbar = pbar.PBar()
#        self.progressbar.set_stopped()
#        mainvbox.pack_start(self.progressbar, False, False, 1)

        #################################################################################################################################
        #StatusBar
        #################################################################
        statusbar = gtk.Statusbar() 
        mainvbox.pack_end(statusbar, False, False, 1)
        context_id = statusbar.get_context_id("Inguma 0.2")
        message_id = statusbar.push(context_id, 'Inguma 0.2')
        statusbar.show()

        #################################################################################################################################
        # finish it
        #################################################################
        self.vpaned.show()
        self.window.show()
        splash.destroy()
        
        gtk.main()

#################################################################################################################################
# Functions
#################################################################

    def loadKB(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder('./data/')
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.gom.echo( 'Loading KB...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()
            self.uicore.loadKB(res)

            # Update KB textview
            self.textview.updateWin()
            self.treeview.updateTree()
            # Update Map
            self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.xdotw.zoom_image(1.0)

            # Adding text to Log window
            self.gom.echo( 'Loaded' , False)

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)
        chooser.destroy()

    def saveKB(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder('./data/')
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.uicore.saveKB(filename)
            self.gom.echo( filename + ' selected' , False)
        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected' , False)
        chooser.destroy()

    def importScan(self, widget):
        """ Parse and import nmap scan """

        # Choose nmap scan file
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name('Nmap scan')
        filter.add_pattern('*.xml')
        chooser.add_filter(filter)

        # Try to parse and import data
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.gom.echo( 'Loading Nmap Scan...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()

            import lib.ui.nmapParser as nmapParser
            try:
                self.gom.echo( 'Parsing scan results...', False)
                nmapData = nmapParser.parseNmap(res)
                self.gom.echo( 'Inserting data in KB...', False)
                nmapParser.insertData(self.uicore, nmapData)


                askASN = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Resolve ASN of IP addresses?")
                do_asn = askASN.run()

                self.gom.echo( 'Loaded\nUpdating Graph', False)

                if do_asn == gtk.RESPONSE_YES:
                    doASN=True
                else:
                    doASN=False

                t = threading.Thread(target=self.uicore.getDot, args=(doASN,))
                t.start()

                askASN.destroy()

                gobject.timeout_add(1000, self.update_graph, t)
#                self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
#                self.gom.kbwin.updateTree()

            except:
                md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Error loading file")
                md.run()
                md.destroy()

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)

        chooser.destroy()

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False


    def loadEditor(self, widget):
        """ Loads module editor """

        import lib.ui.editor as editor
        editor.main()

    def showPref(self, widget):
        # FIXME: Change propWhatever to prefWhatever.
        propDialog.propDialog(self.uicore, self.gom, self.threadsInst, config)

    def show_term(self, widget):
        self.new_tab('scapy', 'scapy')

    def run_sniffer(self, widget):
        self.new_tab('sniffer', 'tools/sniffer')

    def new_tab(self, widget, command=''):
        self.term_notebook.new_tab(command)
        self.notebook.set_current_page(1)

    def report(self, widget):

        reportWin.reportWin(self.uicore)

    def show_log(self, widget):
        ''' Show/hide log panel'''

        if self.bottom_nb.is_visible == True:
            self.bottom_nb.hide()
            self.bottom_nb.is_visible = False

        else:
            self.bottom_nb.show()
            self.bottom_nb.is_visible = True

    def show_kb(self, widget):
        ''' Show/hide KB panel'''

        if self.scrolled_window.is_visible == True:
            self.scrolled_window.hide()
            self.scrolled_window.is_visible = False

        else:
            self.scrolled_window.show()
            self.textview.updateWin()
            self.treeview.updateTree()
            self.scrolled_window.is_visible = True

    def onSwitch(self, widget, data, more):
        if more == 2:
            self.handlebox.hide()
            self.rcehb.show()
            self.bottom_nb.hide()
            self.bottom_nb.is_visible = False
        else:
            self.rcehb.hide()
            self.handlebox.show()
            self.bottom_nb.show()
            self.bottom_nb.is_visible = True

        #Detect Exploits tab selected to start loading exploits...
        if more == 3:
            if self.exploitsInst.check_exploits() == False:
                opt = self.exploitsInst.show_dialog()
                if opt == True:
                    t = threading.Thread(target=self.exploitsInst.load_exploits, args=(self.gom,))
                    t.start()
                    self.threadsInst.add_action('Load Exploits', 'local', t)
            else:
                t = threading.Thread(target=self.exploitsInst.load_exploits, args=(self.gom,))
                t.start()
                self.threadsInst.add_action('Load Exploits', 'local', t)

    def newBin(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.gom.echo( 'Loading Binary...', False)
            self.gom.echo( chooser.get_filename(), False )
            res = chooser.get_filename()
            rcecore.uploadFile(res)
            rcecore.generate_graphs(res)
            dasm, func = rcecore.get_complete_dasm(res)
            self.textbuffer.set_text(dasm)
            dotcode = rcecore.get_dot_code(func[0].name, res)
            self.xdotr.set_dotcode(dotcode)

            self.rmenu.set_functions(func)
            self.rmenu.set_poc(res)
            self.dasmenu.set_options()

            # Adding text to Log window
            self.gom.echo( 'Loaded!' , False)
            chooser.destroy()

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)
        chooser.destroy()

    def loadBin(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder('dis/navigator/dbs/')

        filter = gtk.FileFilter()
        filter.set_name("KB files")
        filter.add_pattern("*.kb")
        chooser.add_filter(filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.gom.echo( 'Loading Database...', False)
            self.gom.echo( chooser.get_filename() , False)
            res = chooser.get_filename()
            kb = res.split('.')[0]
            dasm, func = rcecore.get_complete_dasm(kb)
            self.textbuffer.set_text(dasm)
            dotcode = rcecore.get_dot_code(func[0].name, kb)
            self.xdotr.set_dotcode(dotcode)

            self.rmenu.set_poc(res)
            self.rmenu.set_functions(func)
            self.dasmenu.set_options()

            # Adding text to Log window
            self.gom.echo( 'Loaded!' , False)
            chooser.destroy()
        
        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)
        chooser.destroy()

    def addTarget(self, event):

        addtgt = addtargetdlg.addTargetDialog(self.uicore, self.gom, self.threadsInst, config)

    def rescroll(self, adj, scroll):
        adj.set_value(adj.upper-adj.page_size)
        scroll.set_vadjustment(adj)

    def quit(self, widget, event, data=None):
        '''Main quit.

        @param widget: who sent the signal.
        @param event: the event that happened
        @param data: optional data to receive.
        '''
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        self.gom.echo( 'Exit!', False)
        gtk.main_quit()
        return False

    def run_debugger(self, widget):
        '''run vdbbin GUI'''

        import threading
        t = threading.Thread( target=os.popen('lib/debugger/vdbbin -G') )
        t.start()
#        os.popen('lib/debugger/vdbbin -G')

def main():
    MainApp()
