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

import gtk

class ListenersMenu(gtk.MenuBar):
    '''Listeners popup menu'''

    def __init__(self, main, tree):
        super(ListenersMenu,self).__init__()

        self.main = main
        self.gom = main.gom
        self.tree = tree
        self.uicore = main.uicore

    def create_menu(self, host, port):
        # Listener Menu
        self.host = host
        self.port = port

        listener_menu = gtk.Menu()

        self.targetm = gtk.ImageMenuItem(gtk.STOCK_CONNECT)
        label = self.targetm.get_children()[0]
        label.set_markup('<b>' + ' '.join([self.host, self.port]) + '</b>')
        listener_menu.append(self.targetm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        listener_menu.append(sep)

        # Stop listener
        self.stopmenu = gtk.ImageMenuItem(gtk.STOCK_STOP)
        self.stopmenu.get_children()[0].set_label('Stop listener')
        self.stopmenu.connect('activate', self._stop_listener)

        listener_menu.append(self.stopmenu)

        return listener_menu

    def _stop_listener(self, widget):
        self.uicore.listeners[self.host + '_' + self.port].exit()
        self.uicore.listeners.pop(self.host + '_' + self.port)
        self.gom.echo('Killed listener at port: ' + str(self.port), False)
        self.tree.fill_listeners_list()
        self.tree.connections.remove(self.port)
