##      cmenu.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
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

import pygtk
import gtk, gobject

from . import core
uicore = core.UIcore()

from . import targetDialog
from . import xfiles
from . import config

class contextMenu(gtk.Menu):

    def __init__(self):
        gtk.Menu.__init__(self)

    def createMenus(self, tv, gom):

        uicore.set_om(gom)

        categories = uicore.get_categories()
        catnum = 1
        for category in categories:

            #Create menu for category
            menulabel = str(catnum) + ') ' + category.capitalize()
            catmenu = gtk.MenuItem(menulabel)
            self.append(catmenu)

            # Create submenu with module list
            submenu = gtk.Menu()
            modules = uicore.get_modules(category)
            for element in modules:
                #print "Adding module:", element.name, "\tDescription:", element.brief_description
                subdis = gtk.MenuItem(element.name)

                # Run diferent callback for discovers...
                if category == 'discovers':
                    subdis.connect("button-release-event", self.showDialog, element.name)
                # ...and gathers
                elif category == 'gathers':
                    subdis.connect("button-release-event", self.showGather, element.name)
                else:
                    #subdis.connect("button-release-event", uicore.uiRunModule, element.name)
                    subdis.connect("button-release-event", self.showGather, element.name)

                # Add tooltips
                tooltip = gtk.Tooltips()
                tooltip.set_tip(subdis, element.brief_description, tip_private=None)

                submenu.append(subdis)
            catmenu.set_submenu(submenu)

            sep = gtk.SeparatorMenuItem()
            self.append(sep)

            catnum += 1

        self.show_all()

    def showDialog(self, widget, callback_data, module):
        tg = targetDialog.TargetDialog(module, uicore)

    def showGather(self, widget, callback_data, module):
        inputs = getattr(config, module)
        if not inputs:
            tg = xfiles.GatherDialog(module, gtk.STOCK_NEW, ["target", "port", "timeout"], uicore)
        else:
            tg = xfiles.GatherDialog(module, gtk.STOCK_NEW, inputs, uicore)
