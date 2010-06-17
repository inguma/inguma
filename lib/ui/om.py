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

import pygtk
import gtk, gobject

class OutputManager:

    def __init__(self, iface):

        self.iface = iface
        if self.iface != 'gui' and self.iface != 'console':
            print "Output interface not valid, must be 'gui' or 'console'"
            sys.exit(0)

    def echo(self, data, window=True):

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

        self.module_dialog = ModuleDialog()

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

class ModuleDialog(gtk.Dialog):
    '''Window to popup module output'''

    def __init__(self):
        super(ModuleDialog,self).__init__('Module output', None, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(400, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        # Log TextView
        #################################################################
        self.output_text = gtk.TextView(buffer=None)
        self.output_text.set_wrap_mode(gtk.WRAP_NONE)
        self.output_text.set_editable(False)
        self.output_buffer = self.output_text.get_buffer()

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled_window.is_visible = True

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.output_text)

        #self.vbox.pack_start(self.output_text)
        self.vbox.pack_start(self.scrolled_window)
        self.show_all()
