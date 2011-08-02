##      discover_dialog.py
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

import gtk

import sys
sys.path.append('../..')
import lib.IPy as IPy

class DiscoverDialog:
    '''Dialog for add targets to the KB'''

    def __init__(self, module, core):

        TITLE = "Specify target for " + module

        # Core instance for manage the KB
        self.uicore = core
        # Module to be launched after insert the data
        self.module = module

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.set_resizable(False)

        # Radio buttons
        self.ip_rbutton= gtk.RadioButton(group=None, label='Single IP')
        self.ip_rbutton.connect("toggled", self.rbcallback, "IP")
        self.active = 'IP'
        self.ip_rbutton.set_active(True)
        self.net_rbutton = gtk.RadioButton(self.ip_rbutton, label='IP Range (CDIR)')
        self.net_rbutton.connect("toggled", self.rbcallback, "NET")
        self.ip_rbutton.set_active(True)
        self.dom_rbutton = gtk.RadioButton(self.ip_rbutton, label='Domain')
        self.dom_rbutton.connect("toggled", self.rbcallback, "DOM")

        # A target text entry
        self.tgentry = gtk.Entry(max=20)

        # Auto fill with selected node IP
        target = self.uicore.get_kbfield('target')
        self.tgentry.set_text(target)

        self.tgentry.set_focus = True

        # A domain text entry
        self.domainentry = gtk.Entry(max=40)
        self.domainentry.set_sensitive(False)

        # Domain separator
        self.domainsep = gtk.HSeparator()

        # Port separator
        self.portsep = gtk.HSeparator()

        # Label and textextry for port
        self.portlab = gtk.Label('Port:\t')
        self.portlab.set_alignment(0.21, 0.5)

        self.portentry = gtk.Entry(max=5)
        self.portentry.set_text( str(self.uicore.user_data['port']) )

        # A ComboBox
        self.combobox = gtk.combo_box_new_text()
        #for host in self.uicore.user_data['hosts']:
        self.uicore.get_kbfield('hosts').sort()
        for host in self.uicore.get_kbfield('hosts'):
            self.combobox.append_text(host)

        #########################################################
        # Table
        table = gtk.Table(rows=6, columns=2, homogeneous=False)
        table.set_row_spacings(3)
        table.set_col_spacings(3)

        # Add lements to Table
        table.attach(self.ip_rbutton, 0, 1, 0, 1)
        table.attach(self.net_rbutton, 1, 2, 0, 1)
        table.attach(self.tgentry, 0, 1, 1, 2)
        table.attach(self.combobox, 1, 2, 1, 2)
        table.attach(self.domainsep, 0, 2, 2, 3)
        table.attach(self.dom_rbutton, 0, 1, 3, 4)
        table.attach(self.domainentry, 1, 2, 3, 4)
        table.attach(self.portsep, 0, 2, 4, 5)
        table.attach(self.portlab, 0, 1, 5, 6)
        table.attach(self.portentry, 1, 2, 5, 6)

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

        # Finish
        self.dialog.show_all()
        self.dialog.show()

    def validateData(self, widget):
        '''Validate user input and call insertData when done'''

        if self.active == 'IP':
            try:
                if self.tgentry.get_text():
                    ip = IPy.IP( self.tgentry.get_text() )
                elif self.get_active_text(self.combobox):
                    ip = IPy.IP( self.get_active_text(self.combobox) )
                self.dialog.destroy()
                self.insertData('ip', ip)
            except:
                self.show_error_dlg( self.tgentry.get_text() + ' is not a valid IP address')
        elif self.active == 'NET':
            try:
                net = IPy.IP( self.tgentry.get_text() )
                self.dialog.destroy()
                self.insertData('net', net)
            except:
                self.show_error_dlg( self.tgentry.get_text() + ' is not a valid network range')
        elif self.active == 'DOM':
                self.insertData('dom', self.domainentry.get_text())
                self.dialog.destroy()

    def rbcallback(self, widget, data=None):
        self.active = data
        if data == 'NET':
            self.tgentry.set_sensitive(True)
            self.combobox.set_sensitive(False)
            self.domainentry.set_sensitive(False)
        elif data == 'DOM':
            self.combobox.set_sensitive(False)
            self.tgentry.set_sensitive(False)
            self.domainentry.set_sensitive(True)
        else:
            self.combobox.set_sensitive(True)
            self.tgentry.set_sensitive(True)
            self.domainentry.set_sensitive(False)

    def insertData(self, type, ip):
        if type == 'ip':
            self.uicore.set_kbfield( 'target', ip.strNormal() )
            self.uicore.set_kbfield( 'hosts', ip.strNormal() )
            #Add paths and generate dot
            #self.uicore.set_kbfield( ip.strNormal() + '_trace', [self.uicore.getLocalIP(), ip.strNormal()] )
            #self.uicore.getDot()
        elif type == 'net':
            self.uicore.set_kbfield( 'target', ip.strNormal() )
        elif type == 'dom':
            self.uicore.set_kbfield( 'target', ip )

        if self.portentry.get_text() != '':
            port =  int(self.portentry.get_text())
            print "Port:", port
            self.uicore.set_kbfield( 'port', port )
        # Run discover module
        self.uicore.uiRunDiscover(self.module)

    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return None
        return model[active][0]

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
