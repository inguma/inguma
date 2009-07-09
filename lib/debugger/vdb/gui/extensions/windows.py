
import os
import vwidget
import vtrace.tools.win32heap as win32heap

import vdb
import vdb.gui

import vwidget

import gtk
import pango

busy_color = (0xff, 0, 0)
def_color  = (0, 0xff, 0)

class Win32HeapWindow(vdb.gui.VdbWindow):
    def __init__(self, db):
        vdb.gui.VdbWindow.__init__(self, db, os.path.join(vdb.basepath,"glade","Win32Heap.glade"))
        self.font = pango.FontDescription("Monospace 10")
        self.setupHeapTree()
        self.setupChunkList()
        self.spaceview = vwidget.SpaceView([], dwidth=40)
        hb = self.getWidget("hbox1")
        hb.pack_start(self.spaceview, expand=False)
        self.spaceview.show()
        hb.resize_children()

    def chunkListActivated(self, tree, path, column):
        model = tree.get_model()
        iter = model.get_iter(path)
        chunk = model.get_value(iter, 0)
        vdb.gui.MemoryWindow(self.vdb, "0x%.8x" % chunk.address, len_expr=str(len(chunk)))

    def heapTreeActivated(self, tree, path, column):
        model = tree.get_model()
        iter = model.get_iter(path)
        o = model.get_value(iter, 0)
        if isinstance(o, win32heap.Win32Heap):
            if tree.row_expanded(path):
                tree.collapse_row(path)
            else:
                tree.expand_row(path, False)
        elif isinstance(o, win32heap.Win32Segment):
            self.updateChunkList(o)

    def updateWindow(self, trace):
        self.updateHeapTree()

    def setupChunkList(self):
        tree = self.getWidget("Win32ChunkList")
        tree.modify_font(self.font)
        col1 = self.getTreeviewTextColumn("Chunkaddr", 1)
        col2 = self.getTreeviewTextColumn("Size", 2)
        col3 = self.getTreeviewTextColumn("Busy", 3) # FIXME make a picture?
        col4 = self.getTreeviewTextColumn("Bytes", 4)
        tree.append_column(col1)
        tree.append_column(col2)
        tree.append_column(col3)
        tree.append_column(col4)
        store =  gtk.ListStore(object,str,str,str,str)
        tree.set_model(store)

    def updateChunkList(self, seg):
        """
        Because this is already parsing chunks, we'll have this update
        the segment view as well.
        """
        tree = self.getWidget("Win32ChunkList")
        model = tree.get_model()
        model.clear()

        spaces = []
        for c in seg.getChunks():

            if c.isBusy():
                color = busy_color
                bstr = "X"
            else:
                color = def_color
                bstr = ""

            bytes = c.getDataBytes(maxsize=10)
            r = ""
            for b in bytes:
                ob = ord(b)
                if ob >= 0x20 and ob < 0x7f:
                    r += b
                else:
                    r += "."

            spaces.append((c.address, len(c), color, r))
            model.append((c, "0x%.8x" % c.address, len(c), bstr, r))

        self.spaceview.updateSpaces(spaces)

    def setupHeapTree(self):
        tree = self.getWidget("Win32HeapTree")
        tree.modify_font(self.font)
        col1 = self.getTreeviewTextColumn("Heap", 1)
        col2 = self.getTreeviewTextColumn("Segment", 2)
        tree.append_column(col1)
        tree.append_column(col2)
        store =  gtk.TreeStore(object,str,str)
        tree.set_model(store)
        self.updateHeapTree(tree)

    def updateHeapTree(self, tree=None):
        if tree == None:
            tree = self.getWidget("Win32HeapTree")
        t = self.vdb.getTrace()
        model = tree.get_model()
        model.clear()
        if not t.isAttached():
            return

        # Populate the heap list
        for h in win32heap.getHeaps(t):
            #i = model.append(None, (h,"0x%.8x" % h.address,"0x%.8x" % int(h.heap.Flags),""))
            for s in h.getSegments():
                i = model.append(None, (s, "0x%.8x" % h.address,"0x%.8x" % s.address))
                model.append(i, (None, repr(h.heap), repr(s.seg)))

def heapview(vdb, line):
    """
    Open a Win32 Heap View window.

    Usage: heapview
    """
    Win32HeapWindow(vdb)

def vdbGuiExtension(vdb, mainwin):
    vdb.registerCmdExtension(heapview)

