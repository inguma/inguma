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

import gtk

class Statusbar(gtk.Statusbar):
    '''Statusbar for main window'''

    def __init__(self, init_msg=None):
        super(Statusbar,self).__init__()

        self.sbar_context = self.get_context_id('sb')

        if not init_msg:
            init_msg = 'No KB has been saved/loaded yet'
        self._set_message(init_msg)

    def _set_message(self, msg):
        '''Inserts a message in the statusbar.'''
        self.push(self.sbar_context, '  Actual KB: ' + msg)

    def _create_helpers(self):
        self.helpers_box = gtk.HBox()

        self.targ_icon = gtk.Image()
        self.targ_icon.set_tooltip_text("Targets discovered")
        self.targ_icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.vuln_icon = gtk.Image()
        self.vuln_icon.set_tooltip_text("Vulnerabilities discovered")
        self.vuln_icon.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU)
        self.shll_icon = gtk.Image()
        self.shll_icon.set_tooltip_text("Shells available (not yet working)")
        self.shll_icon.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)
        self.shll_icon.set_sensitive(False)

        self.targ_label = gtk.Label('0')
        self.vuln_label = gtk.Label('0')
        self.shll_label = gtk.Label('0')

        # builds the helpers
        self.pack_start(self.targ_icon, False, False, padding=2)
        self.pack_start(self.targ_label, False, False, padding=2)
        self.pack_start(self.vuln_icon, False, False, padding=2)
        self.pack_start(self.vuln_label, False, False, padding=2)
        self.pack_start(self.shll_icon, False, False, padding=2)
        self.pack_start(self.shll_label, False, False, padding=2)

        self.pack_end(self.helpers_box, False, False, 1)

    def update_helpers(self, values=None):
        if values:
            self.targ_label.set_text(values[0])
            self.vuln_label.set_text(values[1])
            self.shll_label.set_text(values[2])
