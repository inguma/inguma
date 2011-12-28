##      listener_dialog.py
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

import lib.ui.popup_dialog as popup_dialog

class ListenerDialog(popup_dialog.PopupDialog):
    '''Dialog for adding a new listener'''

    def __init__(self, main, coord, button):

        super(ListenerDialog, self).__init__(main, coord, button)

        # Core instance for manage the KB
        self.main = main
        self.uicore = main.uicore
        self.gom = main.gom
        self.button = button

        self.main_vbox = gtk.VBox(False, 5)
        self.hbox = gtk.HBox(False, 2)

        # Description label
        self.desc_label = gtk.Label('Select interface and port to listen on:')
        self.desc_label.set_padding(5, 0)
        halign = gtk.Alignment(0, 1, 0, 0)
        halign.add(self.desc_label)

        # Choose network iface combo
        self.iface_combo = gtk.combo_box_new_text()

        # fill and select interfaces
        count = 0
        active_iface = self.uicore.get_interface()
        for iface in self.uicore.get_interfaces():
            self.iface_combo.append_text(iface)
            if iface == active_iface:
                i = count
            count += 1
        self.iface_combo.set_active(i)

        # Port entry
        self.port_entry = gtk.Entry()
        self.port_entry.set_icon_from_stock(1, gtk.STOCK_ADD)
        self.port_entry.set_text('Port to listen')

        self.hbox.pack_start(self.iface_combo, False, False, 2)
        self.hbox.pack_start(self.port_entry, True, True, 2)

        self.main_vbox.pack_start(halign, False, False)
        self.main_vbox.pack_start(self.hbox, False, False)

        self.add_content(self.main_vbox)

        # Finish
        self.show_all()
