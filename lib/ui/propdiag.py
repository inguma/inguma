##      propdiag.py
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

from . import core

TITLE = "Inguma - Main Properties"

class PropertiesDialog:

    def __init__(self, tv):

        self.tv = tv
        self.uicore = core.UIcore()
        #self.textview = kbwin.KBwindow()

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.resize(325, 200)

        # Create Labels and boxes
        # FIXME For bucle not posible FIXME

        # TARGET
        # A new Label
        self.tglabel = gtk.Label('Target: ')
        self.tglabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.tgentry = gtk.Entry(max=15)
        self.tgentry.set_text(self.uicore.get_kbfield('target'))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.tglabel, False, False, 0)
        hbox.pack_start(self.tgentry, False, False, 0)
        self.tgentry.set_sensitive(False)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.tgentry.show()
        self.tglabel.show()

        # PORT
        # A new Label
        self.ptlabel = gtk.Label('Port: ')
        self.ptlabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.ptentry = gtk.Entry(max=5)
        self.ptentry.set_text(self.uicore.get_kbfield('port'))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.ptlabel, False, False, 0)
        hbox.pack_start(self.ptentry, False, False, 0)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.ptentry.show()
        self.ptlabel.show()

        # COVERT
        # A new Label
        self.cvlabel = gtk.Label('Covert level: ')
        self.cvlabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.cventry = gtk.Entry(max=2)
        self.cventry.set_text(str(self.uicore.get_kbfield('covert')))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.cvlabel, False, False, 0)
        hbox.pack_start(self.cventry, False, False, 0)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.cventry.show()
        self.cvlabel.show()

        # TIMEOUT
        # A new Label
        self.tolabel = gtk.Label('Timeout: ')
        self.tolabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.toentry = gtk.Entry(max=1)
        self.toentry.set_text(str(self.uicore.get_kbfield('timeout')))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.tolabel, False, False, 0)
        hbox.pack_start(self.toentry, False, False, 0)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.toentry.show()
        self.tolabel.show()

        # WAIT TIME
        # A new Label
        self.wtlabel = gtk.Label('Wait time: ')
        self.wtlabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.wtentry = gtk.Entry(max=1)
        self.wtentry.set_text(self.uicore.get_kbfield('waittime'))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.wtlabel, False, False, 0)
        hbox.pack_start(self.wtentry, False, False, 0)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.wtentry.show()
        self.wtlabel.show()

        # WIZARD MODE
        # A new Label
        self.wmlabel = gtk.Label('Wizard mode: ')
        self.wmlabel.set_justify(gtk.JUSTIFY_LEFT)

        # A new text entry
        self.wmentry = gtk.Entry(max=1)
        self.wmentry.set_editable(False)
        self.wmentry.set_text(str(self.uicore.get_kbfield('wizard')))

        # A new HBox
        hbox = gtk.HBox(True, 1)

        # Add self.tglabel and text entry to HBox
        hbox.pack_start(self.wmlabel, False, False, 0)
        hbox.pack_start(self.wmentry, False, False, 0)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(hbox, False, False, 0)

        # Show Hbox and Label
        hbox.show()
        self.wmentry.show()
        self.wmlabel.show()

        # the cancel button
        self.butt_cancel = self.dialog.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.dialog.destroy())

        # the save button
        self.butt_save = self.dialog.action_area.get_children()[0]
        #self.butt_save.set_sensitive(False)
        #self.butt_save.connect("clicked", self.insertData, data)
        self.butt_save.connect("clicked", self.insertData)

        # Finish
        self.dialog.show()

    def insertData(self, widget):
        '''Update KB properties'''

#        self.uicore.set_kbfield('target', str(self.tgentry.get_text()))
#        self.uicore.set_kbfield('hosts', str(self.tgentry.get_text()))
#        self.uicore.set_kbfield('port', self.ptentry.get_text())
#        self.uicore.set_kbfield('covert', self.cventry.get_text())
#        self.uicore.set_kbfield('timeout', self.toentry.get_text())
#        self.uicore.set_kbfield('waitime', self.wtentry.get_text())

        # Update KBwindow
        self.tv.updateWin()
        self.dialog.destroy()
