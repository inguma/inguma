import gtk
import gtk.glade

class VWindow:
    """
    A class for all vdb/vivisect windows to inherit from.  Full of
    little utilities that make GUI writing slightly less painful.

    When inheriting from this class, you *must* make your classname
    the same as the top level window object in your glade project.
    """

    def __init__(self, fname, layout):
        self.glade = gtk.glade.XML(fname)
        self.glade.signal_autoconnect(self)
        self.getWidget(self.__class__.__name__).connect("delete_event", self.delete)
        self.notebook_groups = {}
        self.vwlayout = layout

    def delete(self, window, event):
        print "ENDING GEOM:",repr(self.getGeometry())
        return False

    def getGeometry(self):
        """
        Returns a tuple of (x, y, xsize, ysize) for later use in setGeometry()
        """
        win = self.getWidget(self.__class__.__name__)
        x, y = win.get_position()
        xsize, ysize = win.get_size()
        return (x, y, xsize, ysize)

    def setGeometry(self, geom):
        win = self.getWidget(self.__class__.__name__)
        win.move(geom[0], geom[1])
        win.resize(geom[2], geom[3])

    def setTitle(self, title):
        widget = self.getWidget(self.__class__.__name__)
        if widget:
            widget.set_title(title)

    def setSensitive(self, widgetname, sensitive):
        wid = self.getWidget(widgetname)
        wid.set_sensitive(sensitive)

    def textFromWidget(self, wName):
        wid = self.glade.get_widget(wName)
        if not wid:
            raise Exception("ERROR - Can't find widget %s" % wName)
        return wid.get_text()

    def getWidget(self, name):
        return self.glade.get_widget(name)

    def show(self):
        self.getWidget(self.__class__.__name__).show()

    def hide(self):
        self.getWidget(self.__class__.__name__).hide()

