##      addtarget.py
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

TITLE = "Inguma - Add new target"

class TargetDialog:

    def __init__(self):

        # Core instance for manage the KB
        self.uicore = core.UIcore()

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.resize(250, 75)

        # Radio buttons
        self.ip_rbutton= gtk.RadioButton(group=None, label='Single IP')
        self.ip_rbutton.connect("toggled", self.rbcallback, "IP")
        self.active = 'IP'
        self.ip_rbutton.set_active(True)
        self.net_rbutton = gtk.RadioButton(self.ip_rbutton, label='IP Range (CDIR)')
        self.net_rbutton.connect("toggled", self.rbcallback, "NET")

        # A new text entry
        self.tgentry = gtk.Entry(max=15)
        self.tgentry.set_focus = True

#        #########################################################
#        # DO Trace
#        self.doTrace = gtk.CheckButton('Perform Traceroute?')
#        #self.doTrace.set_active(True)
#        self.doTrace.set_sensitive(False)

        #########################################################
        # Table
        table = gtk.Table(rows=3, columns=2, homogeneous=True)
        table.set_row_spacings(2)
        table.set_col_spacings(2)

        # Add lements to Table
        table.attach(self.ip_rbutton, 0, 1, 0, 1)
        table.attach(self.net_rbutton, 1, 2, 0, 1)
        table.attach(self.tgentry, 0, 2, 1, 2)
#        table.attach(self.doTrace, 1, 2, 2, 3)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(table, False, False, 2)

        #########################################################
        # the cancel button
        self.butt_cancel = self.dialog.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.dialog.destroy())

        # the save button
        self.butt_save = self.dialog.action_area.get_children()[0]
        #self.butt_save.set_sensitive(False)
        #self.butt_save.connect("clicked", self.insertData, data)
        self.butt_save.connect("clicked", self.validateData)

        self.dialog.show_all()
        # Finish
        self.dialog.show()

    def validateData(self, widget):
        '''Update KB properties'''

        if self.active == 'IP':
            try:
                ip = IPy.IP( self.tgentry.get_text() )
                self.dialog.destroy()
            except:
                self.show_error_dlg( self.tgentry.get_text() + ' is not a valid IP address')
            self.insertData('ip', ip)
        elif self.active == 'NET':
            try:
                net = IPy.IP( self.tgentry.get_text() )
                self.dialog.destroy()
            except:
                self.show_error_dlg( self.tgentry.get_text() + ' is not a valid network range')
            self.insertData('net', net)

    def insertData(self, type, ip):
        if type == 'ip':
            self.uicore.set_kbfield( 'target', ip.strNormal() )
            self.uicore.set_kbfield( 'hosts', ip.strNormal() )
            #Add paths and generate dot
            self.uicore.set_kbfield( ip.strNormal() + '_trace', [self.uicore.getLocalIP(), ip.strNormal()] )
            self.uicore.getDot()
#            # Do traceroute
#            if self.doTrace.get_active():
#                self.uicore.uiRunModule('trace')
        elif type == 'net':
            # Do traceroute
#            if self.doTrace.get_active():
#                for ip in net:
#                    self.uicore.set_kbfield( 'target', ip )
#                    if self.doTrace.get_active():
#                        self.uicore.uiRunModule('trace')
#            else:
            self.uicore.set_kbfield( 'target', ip.strNormal() )

    def rbcallback(self, widget, data=None):
        self.active = data

    def show_error_dlg(self, error_string):
        """This Function is used to show an error dialog when
        an error occurs.
        error_string - The error string that will be displayed
        on the dialog.
        """
        error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
                    , message_format=error_string
                    , buttons=gtk.BUTTONS_OK)
        error_dlg.run()
        error_dlg.destroy()
