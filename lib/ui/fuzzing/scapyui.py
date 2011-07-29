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

import gtk

class ScapyUI(gtk.Frame):
    def __init__(self):
        super(ScapyUI,self).__init__()

        self.label = gtk.Label()
        quote = "<b>Scapy Fuzzer</b>"
        self.label.set_markup(quote)
        self.set_label_widget(self.label)

        # VBox to add pannels and buttons
        self.vbox = gtk.VBox(False, 2)

        # HBox to add panels
        self.panels_hbox = gtk.HBox(False, 10)

        # Information label, icon and HBox
        self.info_hbox = gtk.HBox(False, 2)
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 1: Add the layers that you want to fuzz on to the right column:')
        self.desc_label.set_padding(0, 4)
        self.info_hbox.pack_start(self.info, False, False, 2)
        self.info_hbox.pack_start(self.desc_label, False, False, 2)

        # Panels
        #

        # Scapy layers pannel
        self.layers_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.layers_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Scapy layers Treeview
        self.store = gtk.ListStore(str, str)
        self.layers_tv = gtk.TreeView(self.store)
        self.layers_tv.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Layers", rendererText, text=0)
        column.set_sort_column_id(0)
        self.layers_tv.append_column(column)
        self.layers_tv.set_model(self.store)

        self.layers_sw.add_with_viewport(self.layers_tv)

        # Selected layers Treeview
        self.selected_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.selected_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.store = gtk.ListStore(str)
        self.selected_tv = gtk.TreeView(self.store)
        self.selected_tv.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Selected Layers", rendererText, text=0)
        column.set_sort_column_id(0)
        self.selected_tv.append_column(column)
        self.selected_tv.set_model(self.store)

        self.selected_sw.add_with_viewport(self.selected_tv)

        self.hseparator = gtk.HSeparator()

        #
        # Start/stop buttons and HBox

        # HBox for buttons
        self.buttons_hbox = gtk.HBox(True, 3)

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

        self.buttons_hbox.add(self.start)
        self.buttons_hbox.add(self.stop)
        self.halign = gtk.Alignment(0.97, 0, 0, 0)
        self.halign.add(self.buttons_hbox)

        # Add panels and buttons
        self.panels_hbox.pack_start(self.layers_sw, True, True, 1)
        self.panels_hbox.pack_start(self.selected_sw, True, True, 1)

        self.vbox.pack_start(self.info_hbox, False, False, 2)
        self.vbox.pack_start(self.panels_hbox, True, True, 1)
        self.vbox.pack_start(self.hseparator, False, False, 3)
        self.vbox.pack_start(self.halign, False, False, 3)

        self.add(self.vbox)
