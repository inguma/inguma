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
        self.treeview = self.main.treeview
        self.uicore = main.uicore
        self.gom = main.gom
        self.button = button

        self.main_vbox = gtk.VBox(False, 5)
        self.main_hbox = gtk.HBox(False, 7)
        self.desc_hbox = gtk.HBox(False, 0)
        self.iface_vbox = gtk.VBox(False, 2)
        self.ports_vbox = gtk.VBox(False, 2)

        # Description icon
        self.desc_icon = gtk.Image()
        self.desc_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)

        # Description label
        self.desc_label = gtk.Label()
        self.desc_label.set_markup('<b>Select interface and port to listen on</b>')
        self.desc_label.set_padding(4, 0)
        halign = gtk.Alignment(0, 1, 0, 0)
        halign.add(self.desc_label)

        # Choose network iface combo
        store = gtk.ListStore(gtk.gdk.Pixbuf, str)
        self.iface_combo = gtk.ComboBox(store)
        rendererText = gtk.CellRendererText()
        rendererPix = gtk.CellRendererPixbuf()
        self.iface_combo.pack_start(rendererPix, False)
        self.iface_combo.pack_start(rendererText, True)
        self.iface_combo.add_attribute(rendererPix, 'pixbuf', 0)
        self.iface_combo.add_attribute(rendererText, 'text', 1)

        # fill and select interfaces
        count = 0
        active_iface = self.uicore.get_interface()
        icon = gtk.Image()
        #icon.set_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU)
        icon = icon.render_icon(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU)
        for iface in self.uicore.get_interfaces():
            store.append([icon, iface])
            if iface == active_iface:
                i = count
            count += 1
        self.iface_combo.set_active(i)

        # Port entry
        self.port_entry = gtk.Entry()
        self.port_entry.set_icon_from_stock(1, gtk.STOCK_ADD)
        self.default_color = self.port_entry.get_style().text[0]
        self.port_entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
        self.port_entry.set_text('Port to listen')
        self.port_entry.set_icon_tooltip_text(1, 'Create new listener')
        self.port_entry.connect('focus-in-event', self._clean, 'in')
        self.port_entry.connect('focus-out-event', self._clean, 'out')
        self.port_entry.connect('activate', self._go_entry)
        self.port_entry.connect('icon-press', self._go)

        # IP address label
        self.ip_label = gtk.Label()
        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        active_iface = model[active][1]
        ip_addr = self.uicore.get_iface_ip(active_iface)
        self.ip_label.set_text(ip_addr)
        self.ip_label.set_padding(4, 0)
        ip_halign = gtk.Alignment(0, 0, 0, 0)
        ip_halign.add(self.ip_label)

        self.iface_combo.connect('changed', self.get_ip)

        # Used ports label
        self.used_ports_label = gtk.Label()
        self.used_ports_label.set_markup('Ports in use:')
        ports_halign = gtk.Alignment(0, 1, 0, 0)
        ports_halign.add(self.used_ports_label)

        # Ports list
        self.ports_list = self._create_ports_list()

        # Packing elements
        self.desc_hbox.pack_start(self.desc_icon, False, False, 1)
        self.desc_hbox.pack_start(halign, False, False, 1)

        self.iface_vbox.pack_start(self.iface_combo, False, False, 2)
        self.iface_vbox.pack_start(ip_halign, True, True, 2)

        self.ports_vbox.pack_start(self.port_entry, True, True, 2)
        self.ports_vbox.pack_start(ports_halign, True, True, 2)
        self.ports_vbox.pack_start(self.ports_list, True, True, 2)

        self.main_hbox.pack_start(self.iface_vbox, False, False)
        self.main_hbox.pack_start(self.ports_vbox, False, False)

        self.main_vbox.pack_start(self.desc_hbox, False, False)
        self.main_vbox.pack_start(self.main_hbox, False, False)

        self.add_content(self.main_vbox)

        # Finish
        self.show_all()

    ##############################################################
    # Methods

    def _create_ports_list(self):
        store = gtk.ListStore(str)

        if self.uicore.listeners:
            for listener in self.uicore.listeners.keys():
                port = listener.split('_')[1]
                store.append([port])

        treeView = gtk.TreeView(store)
        treeView.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", rendererText, text=0)
        column.set_sort_column_id(0)
        treeView.append_column(column)
        treeView.set_headers_visible(False)

        return treeView

    def get_ip(self, widget):
        '''get IP address of selected iface and change ip label'''

        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        active_iface = model[active][1]
        ip_addr = self.uicore.get_iface_ip(active_iface)
        self.ip_label.set_text(ip_addr)

    def _clean(self, widget, event, data):
        if data == 'in':
            if widget.get_text() == 'Port to listen':
                self.port_entry.modify_text(gtk.STATE_NORMAL, self.default_color)
                widget.set_text('')
        elif data == 'out':
            if widget.get_text() == '':
                self.port_entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
                widget.set_text('Port to listen')

    def _go_entry(self, widget):
        port = widget.get_text()
        host = self.ip_label.get_text()
        colormap = widget.get_colormap()
        #bg_ok = colormap.alloc_color("white")
        bg_not_valid = colormap.alloc_color("red")
    
        if port and port != 'Port to listen':
            self.uicore.create_listener(host, int(port))
            self._quit(widget)
            self.treeview.update_tree()
        else:
            widget.modify_base(gtk.STATE_NORMAL, bg_not_valid)

    def _go(self, widget, icon_pos, event):
        port = widget.get_text()
        host = self.ip_label.get_text()
        colormap = widget.get_colormap()
        #bg_ok = colormap.alloc_color("white")
        bg_not_valid = colormap.alloc_color("red")
    
        if port and port != 'Port to listen':
            self.uicore.create_listener(host, int(port))
            self._quit(widget)
            self.treeview.update_tree()
        else:
            widget.modify_base(gtk.STATE_NORMAL, bg_not_valid)
