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

import gtk

class VulnsMenu(gtk.MenuBar):
    '''Vulns popup menu'''

    def __init__(self, uicore, main):
        super(VulnsMenu,self).__init__()

        self.uicore = uicore
        self.main = main

    def create_menu(self, target):
        # Function Menu
        vulnmenu = gtk.Menu()

        self.targetm = gtk.ImageMenuItem(target)
        self.targetm.set_image(self.target_img)
        label = self.targetm.get_children()[0]
        label.set_markup('<b>OSVDB id: ' + target + '</b>')
        vulnmenu.append(self.targetm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        vulnmenu.append(sep)

        # Open with browser, bokken and osvbd web
        self.browsermenu = gtk.ImageMenuItem(gtk.STOCK_INDENT)
        self.browsermenu.get_children()[0].set_label('Open in browser')

        vulnmenu.append(self.browsermenu)

        self.bokkenmenu = gtk.ImageMenuItem(gtk.STOCK_INDENT)
        self.bokkenmenu.get_children()[0].set_label('Open with Bokken')

        vulnmenu.append(self.bokkenmenu)

        self.osvdbmenu = gtk.ImageMenuItem(gtk.STOCK_INDENT)
        self.osvdbmenu.get_children()[0].set_label('Open in OSVDB')

        vulnmenu.append(self.osvdbmenu)

        return vulnmenu
