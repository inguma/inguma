#       rcemenu.py
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

class RceMenu(gtk.HBox):
    ''' Menu for the xdot graph widget '''
    def __init__(self, graph, rcecore):
        gtk.HBox.__init__(self)
        self.graph = graph
        self.rcecore = rcecore

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
#        # XXX Separator XXX
#        self.sep = gtk.VSeparator()
#        self.toolbox.pack_start(self.sep, False, False)

        self.combo = gtk.combo_box_new_text()
        self.combo.set_sensitive(False)
        self.combo.connect("changed", self.load_function)
        self.toolbox.pack_end(self.combo, False, False)

        # Grayed?
        self.toolbox.set_sensitive(True)
        self.show_all()

    def set_functions(self, functions):
        for func in functions:
            self.combo.append_text(func.name)

        self.combo.set_active(0)
        self.combo.set_sensitive(True)

    def set_poc(self, poc):
        self.poc = poc
        self.theFile = poc.split('/')[-1]

    def load_function(self, widget):
        model = self.combo.get_model()
        active = self.combo.get_active()

        func = model[active][0]

        f = open('dis/navigator/dbs/' + self.theFile.split('.')[0] + '/' + func + '.dot', 'r')
        dotcode = f.read()
        f.close()

        self.graph.set_dotcode(dotcode)

    def _zoom(self, widg, what):
        #f = getattr(self.widget, "on_zoom_"+what)
        f = getattr(self.graph, "on_zoom_"+what)
        f(None)

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

class DasmMenu(gtk.HBox):
    ''' Menu for the xdot graph widget '''
    def __init__(self):
        gtk.HBox.__init__(self)

        self.dasmbox = self

        self.combo = gtk.combo_box_new_text()
        self.combo.set_sensitive(False)
        self.dasmbox.pack_end(self.combo, False, False)

    def set_options(self):
        options = ['Disassembly', "Hexdump"]
        for option in options:
            self.combo.append_text(option)

        self.combo.set_active(0)
        self.combo.set_sensitive(True)

