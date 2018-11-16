##      target_dialog.py
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

from gi.repository import Gtk

import lib.ui.popup_dialog as popup_dialog

import os, sys, threading
sys.path.append('../..')
import lib.IPy as IPy

class TargetDialog(popup_dialog.PopupDialog):
    '''Dialog for adding targets and running some modules'''

    def __init__(self, main, coord, button):

        super(TargetDialog, self).__init__(main, coord, button)

        datatypes = [
                ['Single IPv4', 'IPv4'],
                ['Single IPv6', 'IPv6'],
                ['Domain', 'DOM'],
                ]
        self.DISCOVERS = [
                'hostname',
                'tcptrace',
                'asn',
                #'netcraft',
                ]

        self.GATHERS = [
                'portscan',
                'identify',
                ]

        # Core instance for manage the KB
        self.main = main
        self.uicore = main.uicore
        self.gom = main.gom
        self.threadtv = main.threadsInst
        self.config = main.config
        self.xdotw = main.xdotw
        self.button = button

        # List of data types.

        self.combo_datatype = Gtk.ComboBoxText.new()
        datatype_store = Gtk.ListStore(str, str)
        for item in datatypes:
            datatype_store.append(item)
        self.combo_datatype = Gtk.ComboBox.new_with_model(datatype_store)
        # We need to make this to render a ListStore, and indicate the column.
        rendered_text = Gtk.CellRendererText()
        self.combo_datatype.pack_start(rendered_text, True)
        self.combo_datatype.add_attribute(rendered_text, "text", 0)

        self.combo_datatype.set_active(0)
        self.combo_datatype.set_focus = True

        # A target text entry
        self.tgentry = Gtk.Entry()
        self.tgentry.set_icon_from_stock(1, Gtk.STOCK_ADD)
        self.tgentry.connect('activate', self.validate_data)
        self.tgentry.connect('icon-press', self.validate_data)
        self.tgentry.set_icon_tooltip_text(1, 'Add new target')

        # Checkbox to use nmap
        self.nmap = Gtk.CheckButton("Use Nmap")
        if not self.config.HAS_NMAP:
            self.nmap.set_sensitive(False)

        # Checkbox to audit host
        self.audit = Gtk.CheckButton("Audit host")
        self.audit.set_active(True)

        #########################################################
        # Table
        table = Gtk.Table(rows=3, columns=2, homogeneous=True)
        table.set_row_spacings(2)
        table.set_col_spacings(2)

        # Add elements to Table
        table.attach(self.combo_datatype, 0, 1, 0, 1)
        table.attach(self.tgentry, 0, 2, 1, 2)
        table.attach(self.audit, 0, 1, 2, 3)
        table.attach(self.nmap, 1, 2, 2, 3)

        self.add_content(table)

        # Finish
        self.show_all()


    def validate_data(self, widget, icon_pos=None, event=None):
        '''Validate user input and call insert_data when done'''

        entry = self.tgentry.get_text()
        model = self.combo_datatype.get_model()
        active = model[self.combo_datatype.get_active_iter()][1]
        if active in ['IPv4', 'IPv6']:
            try:
                if entry:
                    entry = IPy.IP(entry)
            except:
                self.show_error_dlg('%s is not a valid %s address' % (entry, active))
                self._quit(widget)
                return

        self.insert_data(active, entry)
        self._quit(widget)


    def insert_data(self, datatype, ip):
        if datatype == 'IPv4':
            ip = ip.strNormal()
            self.uicore.set_kbfield('target', ip)
            self.uicore.set_kbfield('hosts', ip)
        elif datatype == 'DOM':
            self.uicore.set_kbfield('target', ip)

        if self.audit.get_active():
            if self.nmap.get_active():
                command = 'nmap -P0 -sS -F -A ' + ip + ' -oX /tmp/nmapxml.xml'
                #print "Will use Nmap:", command
                t = threading.Thread(target=self.uicore.run_system_command, args=(command,))
                t.start()
                self.threadtv.add_action('Nmap Scan', ip, t)
                GObject.timeout_add(1000, self.check_nmap_thread, t)
            else:
                # Run discover modules
                t = threading.Thread(target=self.run_modules, args=(datatype,))
                t.start()
        else:
            if datatype == 'DOM':
                self.gom.echo("Running ipaddr")
                self.uicore.uiRunDiscover('ipaddr', join=True)
                ip = self.uicore.get_kbfield('hosts')
                ip = ip[-1]

            self.uicore.set_kbfield('targets', ip)
            self.uicore.set_kbfield('hosts', ip)

            # Update graph
            self.uicore.getDot(doASN=False)
            self.xdotw.set_dotcode(self.uicore.get_last_dot())


    def run_modules(self, datatype):

        if datatype == 'DOM':
            self.gom.echo("Running ipaddr")
            self.uicore.uiRunDiscover('ipaddr', join=True)
            ipaddr = self.uicore.get_kbfield('hosts')
            ipaddr = ipaddr[-1]
            self.gom.echo("Running subdomainer")
            self.uicore.uiRunDiscover('subdomainer', join=True)
            self.gom.echo("\tDone, setting target to " + ipaddr)
            self.uicore.set_kbfield('target', ipaddr)

        for module in self.DISCOVERS:
            self.gom.echo("Running discover: " + module)
            self.uicore.uiRunDiscover(module, join=True)

        for module in self.GATHERS:
            self.gom.echo("Running gather: " + module)
            self.uicore.uiRunDiscover(module, join=True)

    def check_nmap_thread(self, thread):
        if thread.isAlive() == True:
            return True
        else:
            self.parse_data()
            return False

    def parse_data(self):

            import lib.ui.nmapParser as nmapParser

            self.gom.echo('Parsing scan results...', False)
            nmapData = nmapParser.parseNmap('/tmp/nmapxml.xml')
            os.remove('/tmp/nmapxml.xml')
            self.gom.echo('Inserting data in KB...', False)
            nmapParser.insertData(self.uicore, nmapData)

            self.gom.echo('Loaded\nUpdating graph', False)

            self.uicore.getDot(doASN=False)

            self.gom.kbwin.update_tree()
            self.gom.update_graph()

    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return None
        return model[active][0]

    def show_error_dlg(self, error_string):
        """This function is used to show an error dialog when
        an error occurs.
        error_string - The error string that will be displayed
        on the dialog.
        """
        error_dlg = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                message_format=error_string,
                buttons=Gtk.ButtonsType.OK)
        error_dlg.run()
        error_dlg.destroy()
