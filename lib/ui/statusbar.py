#       statusbar.py
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
from gi.repository import Pango

class Statusbar(Gtk.Statusbar):
    '''Statusbar for main window'''

    def __init__(self):
        super(Statusbar,self).__init__()

    def create_statusbar(self):
        self._statusbar = Gtk.HBox()
        self._status_holder = self
        # OMG
        frame = self._status_holder.get_children()[0]
        box = frame.get_children()[0]
        frame.remove(box)
        frame.add(self._statusbar)

    # Method to add content to the status bar
    def add_text(self, data_dict, version):
        '''data_dict ontains text to be added.
           Key will be the title
           Value will be... well, the value :)'''
        self.box = Gtk.HBox(False, 1)
        self._statusbar.pack_start(self.box, True, True, 1)
        ellipsize=Pango.EllipsizeMode.NONE

        # Tragets, vulns and shell indicators
        self.targ_icon = Gtk.Image()
        self.targ_icon.set_tooltip_text("Targets discovered")
        self.targ_icon.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
        self.vuln_icon = Gtk.Image()
        self.vuln_icon.set_tooltip_text("Vulnerabilities discovered")
        self.vuln_icon.set_from_stock(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.MENU)
        self.shll_icon = Gtk.Image()
        self.shll_icon.set_tooltip_text("Shells available (not yet working)")
        self.shll_icon.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'terminal.png'))
        self.shll_icon.set_sensitive(False)

        self.targ_label = Gtk.Label(label='0')
        self.targ_label.set_ellipsize(ellipsize)
        #self.targ_label.set_alignment(1.0, 1.0)
        self.targ_label.set_padding(1, 5)
        self.vuln_label = Gtk.Label(label='0')
        self.vuln_label.set_ellipsize(ellipsize)
        #self.vuln_label.set_alignment(1.0, 1.0)
        self.vuln_label.set_padding(1, 5)
        self.shll_label = Gtk.Label(label='0')
        self.shll_label.set_ellipsize(ellipsize)
        #self.shll_label.set_alignment(1.0, 1.0)
        self.shll_label.set_padding(1, 5)

        sep = Gtk.VSeparator()

        # KB icon and label
        self.kb_icon = Gtk.Image()
        self.kb_icon.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'database.png'))
        self.kb_label = Gtk.Label(label='No KB has been saved/loaded yet')
        #self.kb_label.set_alignment(1.0, 1.0)
        self.kb_label.set_padding(1, 5)

        # builds the helpers
        self.box.pack_start(self.targ_icon, False, False, padding=1)
        self.box.pack_start(self.targ_label, False, False, padding=5)
        self.box.pack_start(self.vuln_icon, False, False, padding=1)
        self.box.pack_start(self.vuln_label, False, False, padding=5)
        self.box.pack_start(self.shll_icon, False, False, padding=1)
        self.box.pack_start(self.shll_label, False, False, padding=5)
        self.box.pack_start(sep, False, False, 5)
        self.box.pack_start(self.kb_icon, False, False, padding=1)
        self.box.pack_end(self.kb_label, True, True, padding=1)

        if version:
            _icon = Gtk.Image.new_from_file('logo' + os.sep + 'inguma_16.png')
            self.pack_start(_icon, False, False, 1)
            label = Gtk.Label()
            label.set_markup('<b>Inguma ' + version + '</b>')
            label.set_alignment(0.5, 0.6)
            self.pack_end(label, False, False, 1)

        self.show_all()

    def _set_message(self, msg):
        '''Inserts a message in the statusbar.'''
        self.kb_label.set_text('Actual KB: ' + msg)

    def update_helpers(self, values=None):
        if values:
            self.targ_label.set_text(values[0])
            self.vuln_label.set_text(values[1])
            self.shll_label.set_text(values[2])

    def remove_all(self):
        for child in self.box.get_children():
            self.box.remove(child)
        for child in self.get_children():
            if type(child) is not Gtk.Frame:
                self.remove(child)
