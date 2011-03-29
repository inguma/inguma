##      om.py
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

import sys

class OutputManager:

    def __init__(self, iface):

        self.iface = iface
        if self.iface != 'gui' and self.iface != 'console':
            print "Output interface not valid, must be 'gui' or 'console'"
            sys.exit(0)

    def echo(self, data, window=True):

        if window == True and self.isGui:
            window = self.SHOW_MODULE_WIN

        if self.iface == 'gui' and not window:
            #print "GTK UI: ", data
            enditer = self.omwidget.get_end_iter()
            self.omwidget.insert(enditer, data + '\n')
            #self.omwidget.set_text(data + '\n')

        elif self.iface == 'gui' and window:
            enditer = self.module_dialog.output_buffer.get_end_iter()
            self.module_dialog.output_buffer.insert(enditer, data + '\n')
            #self.omwidget.set_text(data + '\n')

        elif self.iface == 'console':
            print data

        return False

    def update_graph(self, dotcode):

        self.map.set_dotcode(dotcode)

    def create_module_dialog(self):

        import lib.ui.ModuleDialog as ModuleDialog
        self.module_dialog = ModuleDialog.ModuleDialog()

        return False

    def set_gui(self, widget):

        self.omwidget = widget

    def set_kbwin(self, kbwin):

        self.kbwin = kbwin

    def set_map(self, map):

        self.map = map

    def set_core(self, core):

        self.uicore = core

    def set_new_nodes(self, state):

        self.newNodes = state

    def get_new_nodes(self):

        return self.newNodes
