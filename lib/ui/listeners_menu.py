#       listeners_menu.py
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
import lib.globals as glob

class ListenersMenu(Gtk.MenuBar):
    '''Listeners popup menu'''

    def __init__(self, main, tree):
        super(ListenersMenu,self).__init__()

        self.main = main
        self.tree = tree
        self.uicore = main.uicore

    def create_menu(self, host, port):
        # Listener Menu
        self.host = host
        self.port = port

        listener_menu = Gtk.Menu()

        self.targetm = Gtk.ImageMenuItem(Gtk.STOCK_CONNECT)
        label = self.targetm.get_children()[0]
        label.set_markup('<b>' + ':'.join([self.host, self.port]) + '</b>')
        listener_menu.append(self.targetm)

        # Separator
        sep = Gtk.SeparatorMenuItem()
        listener_menu.append(sep)

        # Stop listener
        self.stopmenu = Gtk.ImageMenuItem(Gtk.STOCK_STOP)
        self.stopmenu.get_children()[0].set_label('Stop listener')
        self.stopmenu.connect('activate', self._stop_listener)

        listener_menu.append(self.stopmenu)

        return listener_menu

    def _stop_listener(self, widget):
        listener_id = self.host + ':' + self.port
        glob.listeners[listener_id].exit()
        self.tree.fill_listeners_list()
        if listener_id in self.tree.connections:
            self.tree.connections.remove(listener_id)
