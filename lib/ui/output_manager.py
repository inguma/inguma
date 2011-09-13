##      output_manager.py
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

import os, sys

import gtk

class OutputManager:

    def __init__(self, iface, ing=None):

        self.ing = ing
        self.iface = iface

        if self.iface != 'gui' and self.iface != 'console':
            print "Output interface not valid, must be 'gui' or 'console'"
            sys.exit(0)

    def echo(self, data = "", window=True, newline=True):

        if window == True and self.isGui:
            window = self.SHOW_MODULE_WIN

        if self.iface == 'gui' and not window:
            #print "GTK UI: ", data
            enditer = self.omwidget.get_end_iter()
            if newline:
                self.omwidget.insert(enditer, data + '\n')
            else:
                self.omwidget.insert(enditer, data)
            #self.omwidget.set_text(data + '\n')
            self.update_helpers()
            self.alert_tab()

        elif self.iface == 'gui' and window:
            enditer = self.module_dialog.output_buffer.get_end_iter()
            if newline:
                self.module_dialog.output_buffer.insert(enditer, data + '\n')
            else:
                self.module_dialog.output_buffer.insert(enditer, data)
            self.update_helpers()
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

    def alert_tab(self):
        bottom_nb = self.ing.bottom_nb
        if bottom_nb.get_current_page() != 0:
            self.ing.log_icon.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU)

    #
    # Statusbar output methods
    #
    def insert_sb_text(self, text):
        context = self.ing.statusbar.get_context_id(text)
        self.icon = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file('logo' + os.sep + 'inguma_16.png')
        scaled_buf = pixbuf.scale_simple(16,16,gtk.gdk.INTERP_BILINEAR)
        self.icon.set_from_pixbuf(scaled_buf)

        self.ing.statusbar.pack_start(gtk.VSeparator(), False, False, 2)
        self.ing.statusbar.pack_start(gtk.Label(text), False, False, 2)
        self.ing.statusbar.pack_start(self.icon, False, False, 2)

    def insert_bokken_text(self, data_dict, version):
        '''data_dict ontains text to be added.
           Key will be the title
           Value will be... well, the value :)'''

        context = self.ing.bokken_sb.get_context_id('sb')        
        self.text = ''
        for element in data_dict.keys():
            self.text += element.capitalize() + ': ' + str(data_dict[element]) + ' | '
        self.ing.bokken_sb.push(context, self.text)
        if version:
            self.icon = gtk.Image()
            pixbuf = gtk.gdk.pixbuf_new_from_file('lib/ui/bokken/data/icon.png')
            scaled_buf = pixbuf.scale_simple(16,16,gtk.gdk.INTERP_BILINEAR)
            self.icon.set_from_pixbuf(scaled_buf)

            self.ing.bokken_sb.pack_end(gtk.Label('Bokken ' + version), False)
            self.ing.bokken_sb.pack_end(self.icon, False, False, 2)
            self.ing.bokken_sb.pack_end(gtk.VSeparator(), False)
        #self.ing.bokken_sb.show_all()

    def clear_sb_text(self):
        context = self.ing.statusbar.get_context_id('sb')        
        self.ing.statusbar.pop(context)

    def update_helpers(self):
        core = self.ing.uicore
        targets = str(len(core.get_kbfield('targets')))
        vulns = str(core.get_vulns())
        self.ing.statusbar.update_helpers([targets, vulns, '0'])
