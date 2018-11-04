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
from gi.repository import Gtk
import lib.ui.about as about
import lib.globals as glob

class Systray(Gtk.StatusIcon):
    '''Systray'''

    def __init__(self, main):
        super(Systray,self).__init__()

        self.main = main

        self.set_from_file(os.path.join('logo', 'inguma_32.png'))
        self.connect('popup-menu', self.on_right_click)
        self.connect('activate', self.on_left_click)
        self.set_tooltip_text('Inguma ' + glob.version)

    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(event_button, event_time)

    def on_left_click(self, icon):
        if self.main.get_property("visible"):
            self.main.hide()
        else:
            self.main.show()
        self.set_from_file(os.path.join('logo', 'inguma_32.png'))
        return True

    def set_new_tooltip(self, text):
        if text:
            self.set_tooltip((text))
        else:
            self.set_tooltip(('Inguma %s' % glob.version))

    def make_menu(self, event_button, event_time):
        menu = Gtk.Menu()

        # show about dialog
        about_item = Gtk.ImageMenuItem(Gtk.STOCK_ABOUT)
        about_item.show()
        about_item.connect('activate', self.create_about_dialog)
        menu.append(about_item)

        # add quit item
        quit_item = Gtk.ImageMenuItem(Gtk.STOCK_QUIT)
        quit_item.show()
        quit_item.connect('activate', self.main._quit, None)
        menu.append(quit_item)

        menu.popup(None, None, Gtk.status_icon_position_menu,
                   event_button, event_time, self)

    def create_about_dialog(self, widget):

        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
