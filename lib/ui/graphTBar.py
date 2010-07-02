#       graphTBar.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
#       Based on code from w3af by Andres Riancho (w3af.sourceforge.net)
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

import gtk

class GraphMenu(gtk.VBox):
    ''' Menu for the xdot graph widget '''
    def __init__(self, graph, core):
        gtk.VBox.__init__(self)
        self.graph = graph

        self.uicore = core
        self.toolbox = self
        b = SemiStockButton("", gtk.STOCK_ZOOM_IN, 'Zoom In')
        b.connect("clicked", self._zoom, "in")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_OUT, 'Zoom Out')
        b.connect("clicked", self._zoom, "out")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_FIT, 'Zoom Fit')
        b.connect("clicked", self._zoom, "fit")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_ZOOM_100, 'Zoom 100%')
        b.connect("clicked", self._zoom, "100")
        self.toolbox.pack_start(b, False, False)
        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Graph direction buttons
        b = SemiStockButton("", gtk.STOCK_GO_UP, 'Up')
        b.connect("clicked", self._dir, "BT")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_GO_DOWN, 'Down')
        b.connect("clicked", self._dir, "TB")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_GO_BACK, 'Left')
        b.connect("clicked", self._dir, "RL")
        self.toolbox.pack_start(b, False, False)
        b = SemiStockButton("", gtk.STOCK_GO_FORWARD, 'Right')
        b.connect("clicked", self._dir, "LR")
        self.toolbox.pack_start(b, False, False)

        # Separator
        self.sep = gtk.HSeparator()
        self.toolbox.pack_start(self.sep, False, False)

        # Cluster ToggleButton
        self.img_leave = gtk.image_new_from_stock(gtk.STOCK_LEAVE_FULLSCREEN,  gtk.ICON_SIZE_BUTTON)
        self.img_full = gtk.image_new_from_stock(gtk.STOCK_FULLSCREEN,  gtk.ICON_SIZE_BUTTON)
        self.clusterBtn = gtk.ToggleButton("")
        self.clusterBtn.set_property("image", self.img_leave)
        self.clusterBtn.connect('clicked', self._on_toggle)
        self.toolbox.pack_start(self.clusterBtn, False, False)

        # Grayed?
        self.toolbox.set_sensitive(True)
        self.show_all()

    def _zoom(self, widg, what):
        #f = getattr(self.widget, "on_zoom_"+what)
        f = getattr(self.graph, "on_zoom_"+what)
        f(None)

    def _dir(self, widg, where):
        ret = self.uicore.set_direction(where)
        if ret:
            self.graph.set_dotcode( self.uicore.get_kbfield('dotcode') )

    def _on_toggle(self, widget):
        self._zoom(widget, '100')
        if self.clusterBtn.get_active():
            self.clusterBtn.set_property("image", self.img_full)
            self.uicore.getFolded()
            self.graph.set_dotcode( self.uicore.get_kbfield('dotcode') )
        else:
            self.clusterBtn.set_property("image", self.img_leave)
            self.uicore.getDot(False)
            self.graph.set_dotcode( self.uicore.get_kbfield('dotcode') )

#    def _addTarget(self, widg):
#        addw = addtarget.TargetDialog()

class SemiStockButton(gtk.Button):
    '''Takes the image from the stock, but the label which is passed.
    
    @param text: the text that will be used for the label
    @param image: the stock widget from where extract the image
    @param tooltip: the tooltip for the button

    @author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    '''
    def __init__(self, text, image, tooltip=None):
        super(SemiStockButton,self).__init__(stock=image)
        align = self.get_children()[0]
        box = align.get_children()[0]
        (self.image, self.label) = box.get_children()
        self.label.set_text(text)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
            
    def changeInternals(self, newtext, newimage, tooltip=None):
        '''Changes the image and label of the widget.
    
        @param newtext: the text that will be used for the label
        @param newimage: the stock widget from where extract the image
        @param tooltip: the tooltip for the button
        '''
        self.label.set_text(newtext)
        self.image.set_from_stock(newimage, gtk.ICON_SIZE_BUTTON)
        if tooltip is not None:
            self.set_tooltip_text(tooltip)
