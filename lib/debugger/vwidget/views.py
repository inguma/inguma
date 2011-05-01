
import gtk
import vwidget.util as vw_util

class VView(gtk.ScrolledWindow):

    __display_name__ = "Stuff!"

    def __init__(self, view, layout):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vwlayout = layout
        self.vwactive = True
        self.vwname = None
        self.vwview = view
        size = self.vwGetLayoutOption("size")
        if size != None:
            xstr,ystr = size.split(",")
            x = int(xstr)
            y = int(ystr)
            self.vwview.set_size_request(x,y)
        self.add(view)

    def vwGetLayoutOption(self, option, default=None):
        """
        Get a layout option that is specific to this view.
        """
        viewname = self.vwGetViewName()
        if not self.vwlayout.has_section(viewname):
            return default
        if not self.vwlayout.has_option(viewname, option):
            return default
        return self.vwlayout.get(viewname, option)

    def vwSetSensitive(self, sensitive=True):
        """
        Set this view object as "sensitive" to user input
        """
        if self.vwactive != sensitive:
            self.vwactive = sensitive
            self.treeview.set_sensitive(sensitive)

    def vwGetDisplayName(self):
        if self.vwname == None:
            return self.__class__.__display_name__
        return self.vwname

    def vwSetDisplayName(self, name):
        self.vwname = name

    def vwGetViewName(self):
        return self.__class__.__name__

class GladeView(VView):
    """
    Create a vwidget "view" by stealing the top child out of a window
    defined in a glade file.  As in my other glade wrappers, your
    class must be named the same as the top level window...
    """
    def __init__(self, gladefile, layout):
        self.vwglade = gtk.glade.XML(gladefile)
        self.vwglade.signal_autoconnect(self)
        win = self.vwglade.get_wiget(self.__class__.__name__)
        view = win.get_child()
        view.deparent()
        win.destroy()
        VView.__init__(self, view, layout)

    def vwGetWidget(self, name):
        return self.vwglade.get_widget(name)

class VTreeView(VView):

    __model_class__ = gtk.ListStore
    # Some example column definitions
    __cols__ = (
        (None, 0, object),
        ("Address",1, str),
        ("Stuff",2, str)
    )

    def __init__(self, layout):
        self.treeview = gtk.TreeView()
        self.treeview.connect("row_activated", self.vwActivated)

        VView.__init__(self, self.treeview, layout)

        ftypes = []
        for name,index,ctype in self.__class__.__cols__:
            ftypes.append(ctype)
            if name == None:
                continue
            col = self.vwMakeColumn(name,index)
            self.treeview.append_column(col)

        self.model = self.__class__.__model_class__(*ftypes)
        self.treeview.set_model(self.model)

        self.add(self.treeview)
        self.vwLoad()

    def vwLoad(self):
        # Over-ride this to cause a load from scratch
        pass

    def vwClear(self):
        # This clears the view
        self.model.clear()

    def vwRemove(self, iter):
        self.model.remove(iter)

    def vwActivated(self, tree, path, column):
        # over-ride this for activation callbacks
        pass

    def vwGetSelected(self, column):
        """
        Get the selected row's column by index
        """
        return vw_util.getTreeSelected(self.treeview, column)

    def vwMakeColumn(self, name, index, onedit=False):
        # NOTE: keep this for backward compat for a bit
        return vw_util.makeColumn(name, index, onedit)

