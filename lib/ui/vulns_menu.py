#       vulns_menu.py
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

from gi.repository import Gtk

from webbrowser import open_new

class VulnsMenu(Gtk.MenuBar):
    '''Vulns popup menu'''

    def __init__(self, main):
        super(VulnsMenu,self).__init__()

        self.main = main

    def create_menu(self, poc, target):
        # Function Menu
        vulnmenu = Gtk.Menu()
        self.poc = poc
        self.id = target.split('-')[0]
        self.host = target.split('-')[1]

        self.targetm = Gtk.ImageMenuItem(target)
        label = self.targetm.get_children()[0]
        label.set_markup('<b>OSVDB id: ' + self.id + '</b>')
        vulnmenu.append(self.targetm)

        # Separator
        sep = Gtk.SeparatorMenuItem()
        vulnmenu.append(sep)

        # Open with browser, bokken and osvbd web
        self.browsermenu = Gtk.ImageMenuItem(Gtk.STOCK_INDENT)
        self.browsermenu.get_children()[0].set_label('Open in browser')
        self.browsermenu.connect('activate', self.open_poc)

        vulnmenu.append(self.browsermenu)

        self.bokkenmenu = Gtk.ImageMenuItem(Gtk.STOCK_INDENT)
        self.bokkenmenu.get_children()[0].set_label('Open with Bokken')
        self.bokkenmenu.connect('activate', self.open_bokken)

        vulnmenu.append(self.bokkenmenu)

        self.osvdbmenu = Gtk.ImageMenuItem(Gtk.STOCK_INDENT)
        self.osvdbmenu.get_children()[0].set_label('Open in OSVDB')
        self.osvdbmenu.connect('activate', self.open_osvdb)

        vulnmenu.append(self.osvdbmenu)

        return vulnmenu

    def open_osvdb(self, widget):
        open_new('http://osvdb.org/show/osvdb/' + self.id)

    def open_poc(self, widget):
        open_new('http://' + self.host + self.poc)

    def open_bokken(self, widget):
        self.main.toolbar.hide()
        self.main.bokken_tb.show()
        self.main.statusbar.hide()
        self.main.bokken_statusbar.show_all()
        self.main.bottom_nb.hide()
        self.main.notebook.set_current_page(2)
        self.main.bokken_tb.new_file(None, 'http://' + self.host + self.poc)
