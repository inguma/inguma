##      right_buttons.py
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

class RightButtons(gtk.VBox):
    '''Right buttons for Treeview change'''

    def __init__(self):
        super(RightButtons,self).__init__(False, 1)

    ##################################
    # Methods

    def create_buttons(self):
        # Icons
        self.tgt_icon = gtk.Image()
        self.tgt_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.vuln_icon = gtk.Image()
        self.vuln_icon.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU)
        self.shell_icon = gtk.Image()
        self.shell_icon.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)

        # Buttons
        a = gtk.VBox(False, 1)
        tgttb = gtk.ToggleButton()
        tgttb.set_active(True)
        l = gtk.Label('Targets')
        l.set_angle(270)
        a.pack_start(self.tgt_icon, False, False, 1)
        a.pack_start(l, False, False, 1)
        tgttb.add(a)
        self.pack_start(tgttb, False, False, 0)

        a = gtk.VBox(False, 1)
        vulntb = gtk.ToggleButton()
        l = gtk.Label('Vulnerabilities')
        l.set_angle(270)
        a.pack_start(self.vuln_icon, False, False, 1)
        a.pack_start(l, False, False, 1)
        vulntb.add(a)
        vulntb.set_sensitive(False)
        self.pack_start(vulntb, False, False, 0)

        a = gtk.VBox(False, 1)
        shelltb = gtk.ToggleButton()
        l = gtk.Label('Shells')
        l.set_angle(270)
        a.pack_start(self.shell_icon, False, False, 1)
        a.pack_start(l, False, False, 1)
        shelltb.add(a)
        self.pack_start(shelltb, False, False, 0)
        shelltb.set_sensitive(False)

        self.show_all()
