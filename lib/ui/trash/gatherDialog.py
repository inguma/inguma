##      gatherDialog.py
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

import sys
sys.path.append('../..')
import lib.IPy as IPy

from . import core

class GatherDialog:
    '''Dialog for adding gather modules required data'''

    def __init__(self, module, core):

        TITLE = "Scpecify data for " + module

        # Core instance for manage the KB
        self.uicore = core
        # Module to be launched after insert the data
        self.module = module

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.resize(250, 75)

        # Target label
        self.tglabel = gtk.Label("Target:")
        self.tglabel.set_alignment(0.0, 0.5)
        # Target ComboBox
        self.combobox = gtk.combo_box_new_text()
        for host in self.uicore.get_kbfield('hosts'):
            self.combobox.append_text(host)
#        self.combobox.set_active(self.uicore.user_data[0])

        # Port label
        self.ptlabel = gtk.Label("Port:")
        self.ptlabel.set_alignment(0.0, 0.5)
        # Port Entry
        self.ptentry = gtk.Entry(max=5)
        self.ptentry.set_text(self.uicore.user_data['port'])

        # Timeout label
        self.tolabel = gtk.Label("Timeout:")
        self.tolabel.set_alignment(0.0, 0.5)
        self.toentry = gtk.Entry(max=5)
        self.toentry.set_text( str(self.uicore.user_data['timeout']) )

        # Port label
        self.ptlabel = gtk.Label("Port:")
        self.ptlabel.set_alignment(0.0, 0.5)
        # Port Entry
        self.ptentry = gtk.Entry(max=5)
        self.ptentry.set_text(self.uicore.user_data['port'])

        # Horizontal Separator
        self.hsep = gtk.HSeparator()

        # Interval label
        self.intlabel = gtk.Label("Interval:")
        self.intlabel.set_alignment(0.0, 0.5)
        self.intentry = gtk.Entry(max=5)

        # Interface label
        self.iflabel = gtk.Label("Interface:")
        self.iflabel.set_alignment(0.0, 0.5)
        self.ifcombo = gtk.combo_box_new_text()
        for iface in self.uicore.getIfaceList():
            self.ifcombo.append_text(iface)

        # Open Port
        self.oplabel = gtk.Label("Open Port:")
        self.oplabel.set_alignment(0.0, 0.5)
        self.opentry = gtk.Entry(max=5)

        # Open Port
        self.cplabel = gtk.Label("Closed Port:")
        self.cplabel.set_alignment(0.0, 0.5)
        self.cpentry = gtk.Entry(max=5)

        #########################################################
        # Table
        table = gtk.Table(rows=3, columns=2, homogeneous=True)
        table.set_row_spacings(8)
        table.set_col_spacings(3)

        # Add lements to Table
        table.attach(self.tglabel, 0, 1, 0, 1)
        table.attach(self.combobox, 1, 2, 0, 1)
        table.attach(self.ptlabel, 0, 1, 1, 2)
        table.attach(self.ptentry, 1, 2, 1, 2)
        table.attach(self.tolabel, 0, 1, 2, 3)
        table.attach(self.toentry, 1, 2, 2, 3)
        # Separator
        table.attach(self.hsep, 0, 2, 3, 4)

        table.attach(self.intlabel, 0, 1, 4, 5)
        table.attach(self.intentry, 1, 2, 4, 5)
        table.attach(self.iflabel, 0, 1, 5, 6)
        table.attach(self.ifcombo, 1, 2, 5, 6)
        table.attach(self.oplabel, 0, 1, 6, 7)
        table.attach(self.opentry, 1, 2, 6, 7)
        table.attach(self.cplabel, 0, 1, 7, 8)
        table.attach(self.cpentry, 1, 2, 7, 8)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(table, False, False, 2)

        #########################################################
        # the cancel button
        self.butt_cancel = self.dialog.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.dialog.destroy())

        # the save button
        self.butt_save = self.dialog.action_area.get_children()[0]
        self.butt_save.connect("clicked", self.run_module)

        # Finish
        self.dialog.show_all()
        self.dialog.show()

    def run_module(self, widget):
        self.dialog.destroy()
        # Run gather module
        self.uicore.uiRunDiscover(self.module)
