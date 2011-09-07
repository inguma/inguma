#       systray.py
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

import os
import gtk
import lib.ui.about as about

class Systray(gtk.StatusIcon):
    '''Systray'''

    def __init__(self, main):
        super(Systray,self).__init__()

        self.main = main

        self.set_from_file('logo' + os.sep + 'inguma_16.png')
        self.connect('popup-menu', self.on_right_click)
        self.connect('activate', self.on_left_click)
        self.set_tooltip(('Inguma 0.4'))
        
    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(event_button, event_time)

    def on_left_click(self, icon):
        if self.main.window.get_property("visible"):
            self.main.window.hide()
        else:
            self.main.window.show()
        self.set_from_file('logo' + os.sep + 'inguma_16.png') 
        return True

    def set_new_tooltip(self, text):
        if text:
            self.set_tooltip((text))
        else:
            self.set_tooltip(('Inguma 0.4'))

    def make_menu(self, event_button, event_time):
        menu = gtk.Menu()

        # show about dialog
        about_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about_item.show()
        about_item.connect('activate', self.create_about_dialog)
        menu.append(about_item)

        # add quit item
        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.show()
        quit_item.connect('activate', self.main.quit, None)
        menu.append(quit_item)

        menu.popup(None, None, gtk.status_icon_position_menu,
                   event_button, event_time, self)

    def create_about_dialog(self, widget):

        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
