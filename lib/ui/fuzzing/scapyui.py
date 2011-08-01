##      scapyui.py
#       
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
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

import gtk, gobject

from scapy.all import *

class ScapyUI(gtk.Frame):
    def __init__(self):
        super(ScapyUI,self).__init__()

        self.label = gtk.Label()
        quote = "<b>Scapy Fuzzer</b>"
        self.label.set_markup(quote)
        self.set_label_widget(self.label)

        # VBox to add panels and buttons
        self.vbox = gtk.VBox(False, 2)

        # HBox to add panels
        self.panels_hbox = gtk.HBox(False, 10)

        # Information label, icon and HBox
        self.info_hbox = gtk.HBox(False, 2)
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 2: Add the layers that you want to fuzz on to the right column:')
        self.desc_label.set_padding(0, 4)
        self.info_hbox.pack_start(self.info, False, False, 2)
        self.info_hbox.pack_start(self.desc_label, False, False, 2)

        # Panels
        #

        # Scapy layers panel
        self.layers_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.layers_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Scapy layers Treeview
        self.layers_store = gtk.ListStore(str)
        self.layers_tv = gtk.TreeView(self.layers_store)
        self.layers_tv.set_rules_hint(True)
        #self.layers_tv.set_hover_selection(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_resizable(True)
        self.layers_tv.append_column(column)
        self.layers_tv.set_model(self.layers_store)

        self.layers_sw.add_with_viewport(self.layers_tv)

        # Selected layers Treeview
        self.selected_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.selected_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.selected_store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        self.selected_tv = gtk.TreeView(self.selected_store)
        self.selected_tv.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Selected Layers", rendererText, text=0)
        column.set_sort_column_id(0)
        self.selected_tv.append_column(column)

        self.toggle = gtk.CellRendererToggle()
        self.toggle.set_property('activatable', True)
        self.toggle.connect( 'toggled', self.activate, self.selected_store )
        self.toggle_column = gtk.TreeViewColumn("Fuzz", self.toggle)
        self.toggle_column.add_attribute( self.toggle, "active", 1)
        self.selected_tv.append_column(self.toggle_column)

        self.selected_tv.set_model(self.selected_store)

        self.selected_sw.add_with_viewport(self.selected_tv)

        # Drag and Drop stuff
        self.layers_tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("text/plain", gtk.TARGET_SAME_APP, 80)], gtk.gdk.ACTION_COPY)
        self.layers_tv.connect("drag-data-get", self.drag_data_get_cb)
        self.selected_tv.enable_model_drag_dest([("text/plain", 0, 80)], gtk.gdk.ACTION_COPY)
        self.selected_tv.connect("drag-data-received", self.drag_data_received_cb)

        self.hseparator = gtk.HSeparator()

        #
        # Start/stop buttons and HBox

        # HBoxes for buttons
        self.buttons_hbox = gtk.HBox(False, 3)
        self.buttons_left_hbox = gtk.HBox(False, 3)
        self.buttons_right_hbox = gtk.HBox(True, 1)

        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 3: Start fuzzing!')
        self.desc_label.set_padding(0, 4)
        self.buttons_left_hbox.pack_start(self.info, False, False, 2)
        self.buttons_left_hbox.pack_start(self.desc_label, False, False, 2)

        # Start/stop buttons
        self.start = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_PLAY)
        self.start.set_size_request(60, 30)
        self.stop = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_STOP)
        self.stop.set_size_request(60, 30)

        # Remove labels from buttons... sigh
        label = self.start.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')
        label = self.stop.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')

        self.buttons_right_hbox.add(self.start)
        self.buttons_right_hbox.add(self.stop)
        self.halign = gtk.Alignment(0.97, 0, 0, 0)
        self.halign.add(self.buttons_right_hbox)

        self.buttons_hbox.pack_start(self.buttons_left_hbox)
        self.buttons_hbox.pack_start(self.halign)

        # Add panels and buttons
        self.panels_hbox.pack_start(self.layers_sw, True, True, 1)
        self.panels_hbox.pack_start(self.selected_sw, True, True, 1)

        self.vbox.pack_start(self.info_hbox, False, False, 2)
        self.vbox.pack_start(self.panels_hbox, True, True, 1)
        self.vbox.pack_start(self.hseparator, False, False, 3)
        self.vbox.pack_start(self.buttons_hbox, False, False, 3)

        self.add(self.vbox)

        self.get_layers()

    def activate(self, cell, path, model):
        model[path][1] = not model[path][1]
        return

    def drag_data_get_cb(self, treeview, context, selection, info, timestamp):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        text = model.get_value(iter, 0)
        selection.set('text/plain', 8, text)
        return

    def drag_data_received_cb(self, treeview, context, x, y, selection, info, timestamp):
        obj = eval(selection.data)

        layers = {}
        layers[selection.data] = []

        if isinstance(obj, type) and issubclass(obj, Packet):
            for f in obj.fields_desc:
                layers[selection.data].append(str(f.name))
            self.add_layer(layers)

    def add_layer(self, layers):
        for layer in layers.keys():
            parent = self.selected_store.append( None, (layer, None) )
            for element in layers[layer]:
                self.selected_store.append( parent, (element, None) )

    def get_layers(self):

        import __builtin__
        all = __builtin__.__dict__.copy()
        all.update(globals())
        objlst = sorted(conf.layers, key=lambda x:x.__name__)
        for o in objlst:
            short = "%-10s" % (o.__name__)
            #long = "%s" % (o.name)
            iter = self.layers_store.append([short])
