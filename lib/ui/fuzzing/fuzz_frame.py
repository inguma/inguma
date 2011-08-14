##      fuzz_frame.py
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

import lib.ui.fuzzing.krashui as krashui
import lib.ui.fuzzing.scapyui as scapyui

class FuzzFrame(gtk.VBox):
    def __init__(self):
        super(FuzzFrame,self).__init__(False, 0)

        # Description label
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 1: Fill in Target IP and Port here, and use one of the panels below to start fuzzing!')
        self.desc_label.set_padding(0, 11)

        # IP and Port fields
        self.ip_label = gtk.Label('Target IP:')
        self.ip_entry = gtk.Entry(max=15)
        self.ip_entry.set_width_chars(15)
        self.port_label = gtk.Label('Port:')
        self.port_entry = gtk.Entry(max=5)
        self.port_entry.set_width_chars(5)

        # HBox to add IP/Port stuff
        self.top_hbox = gtk.HBox(False, 5)

        self.top_hbox.pack_start(self.info, False, False, 2)
        self.top_hbox.pack_start(self.desc_label, False, False, 3)
        self.top_hbox.pack_start(self.ip_label, False, False, 1)
        self.top_hbox.pack_start(self.ip_entry, False, False, 1)
        self.top_hbox.pack_start(self.port_label, False, False, 1)
        self.top_hbox.pack_start(self.port_entry, False, False, 1)

        self.pack_start(self.top_hbox, False, False, 1)

        # HBox to add fuzzers
        self.hbox = gtk.HBox(True, 5)

        # Add krash and scapy fuzzers stuff

        self.krashui = krashui.KrashUI(self.ip_entry, self.port_entry)
        self.scapyui = scapyui.ScapyUI(self.ip_entry, self.port_entry)

        self.hbox.pack_start(self.krashui, True, True, 1)
        self.hbox.pack_start(self.scapyui, True, True, 1)

        self.pack_end(self.hbox, True, True, 1)
