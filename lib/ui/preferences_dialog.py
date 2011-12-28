##      preferences_dialog.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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
import gobject

import os, sys, threading, urllib, gzip
sys.path.append('../..')

from lib.core import get_profile_file_path
import lib.ui.popup_dialog as popup_dialog

class PropDialog(popup_dialog.PopupDialog):
    '''Preferences dialog'''

    def __init__(self, main, coord, button):
        super(PropDialog, self).__init__(main, coord, button)

        # Core instance for manage the KB
        self.main = main
        self.uicore = main.uicore
        self.gom = main.gom
        self.threadtv = main.threadsInst
        self.config = main.config
        self.button = button

        # Notebook
        self.prefs_nb = gtk.Notebook()

        #########################################################
        # Main Table
        self.main_table = gtk.Table(rows=3, columns=2, homogeneous=True)
        self.main_table.set_row_spacings(2)
        self.main_table.set_col_spacings(2)

        # Label to add table to Notebook
        self.main_lbl = gtk.Label('Main')

        # Choose network iface
        self.iface_lbl = gtk.Label('Network interface')
        self.iface_combo = gtk.combo_box_new_text()

        # fill and select interfaces
        count = 0
        active_iface = self.uicore.get_interface()
        for iface in self.uicore.get_interfaces():
            self.iface_combo.append_text(iface)
            if iface == active_iface:
                i = count
            count += 1
        self.iface_combo.set_active(i)

        # Add elements to Table
        self.main_table.attach(self.iface_lbl, 0, 1, 0, 1)
        self.main_table.attach(self.iface_combo, 1, 2, 0, 1)

        # Add Table to Notebook
        self.prefs_nb.append_page(self.main_table, self.main_lbl)

        #########################################################
        # Update Table
        self.update_table = gtk.Table(rows=4, columns=2, homogeneous=True)
        self.update_table.set_row_spacings(2)
        self.update_table.set_col_spacings(2)

        # Label to add table to Notebook
        self.update_lbl = gtk.Label('Updates')

        # Add exploits and nikto update buttons
        self.exploit_lbl = gtk.Label('Exploit DB')
        self.nikto_lbl = gtk.Label('Nikto Rules')
        self.geo_lbl = gtk.Label('GeoIP DB')
        self.dis_lbl = gtk.Label('distorm64')
        self.exploit_bt = gtk.Button('Update', gtk.STOCK_REFRESH)
        self.exploit_bt.connect('clicked', self.update_exploits)
        self.nikto_bt = gtk.Button('Update', gtk.STOCK_REFRESH)
        self.nikto_bt.connect('clicked', self.update_nikto)
        self.geo_bt = gtk.Button('Update', gtk.STOCK_REFRESH)
        self.geo_bt.connect('clicked', self.update_geo)
        self.dis_bt = gtk.Button('Update', gtk.STOCK_REFRESH)
        self.dis_bt.connect('clicked', self.download_distorm)

        # Add elements to Table
        self.update_table.attach(self.exploit_lbl, 0, 1, 0, 1)
        self.update_table.attach(self.exploit_bt, 1, 2, 0, 1)
        self.update_table.attach(self.nikto_lbl, 0, 1, 1, 2)
        self.update_table.attach(self.nikto_bt, 1, 2, 1, 2)
        self.update_table.attach(self.geo_lbl, 0, 1, 2, 3)
        self.update_table.attach(self.geo_bt, 1, 2, 2, 3)
        self.update_table.attach(self.dis_lbl, 0, 1, 3, 4)
        self.update_table.attach(self.dis_bt, 1, 2, 3, 4)

        # Add Table to Notebook
        self.prefs_nb.append_page(self.update_table, self.update_lbl)

        # Add NoteBook to Popup dialog
        self.add_content(self.prefs_nb)

        # Finish
        self.show_all()

    def get_selected_iface(self):
        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        if active < 0:
            return None
        return model[active][0]

    def set_interface(self, widget):
        iface = self.get_selected_iface()
        if iface:
            self.uicore.set_interface(iface)
        self.dialog.destroy()

    def update_exploits(self, widget):
        import lib.ui.exploits as exploits

        self.exploitsInst = exploits.Exploits(self.config)
        widget.set_sensitive(False)
        t = threading.Thread(target=self.exploitsInst.download_exploits, args=(self.gom,))
        t.start()
        gobject.timeout_add(1000, self.reactivate_button, t, widget)
        self.threadtv.add_action('Exploit-db Update', 'Exploits DB', t)

    def update_nikto(self, widget):
        command = 'python lib/libnikto.py'
        widget.set_sensitive(False)
        t = threading.Thread(target=self.uicore.run_system_command, args=(command,))
        t.start()
        gobject.timeout_add(1000, self.reactivate_button, t, widget)
        self.threadtv.add_action('Nikto Update', 'Nikto DB', t)

    def update_geo(self, widget):
        t = threading.Thread(target=self.download_geodb)
        widget.set_sensitive(False)
        t.start()
        gobject.timeout_add(1000, self.reactivate_button, t, widget)
        self.threadtv.add_action('GeoIP-DB Update', 'GeoIP DB', t)

    def download_geodb(self):
        self.GEOIP_DIR='data/'        
        self.INGUMA_DIR = os.getcwd()

        page = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"
        self.gom.echo( "Downloading " + page, False )
        geoip_db_path = get_profile_file_path('data/');
        urllib.urlretrieve(page, geoip_db_path + "GeoLiteCity.dat.gz")

        # Extract DB and remove original file
        self.gom.echo( "Extracting files...", False )
        gz = gzip.open(geoip_db_path + "GeoLiteCity.dat.gz")
        db = gz.read()
        gz.close()
        os.remove(geoip_db_path + "GeoLiteCity.dat.gz")
        geodb = open(geoip_db_path + 'GeoLiteCity.dat', 'w')
        geodb.write(db)
        geodb.close()
        self.gom.echo( "Operation Complete", False )

    def download_distorm(self, widget):

        self.dis_bt.set_sensitive(False)
        import platform
        path = get_profile_file_path('data' + os.sep)

        if platform.system() != 'Linux':
            md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format='Download distorm library installer for Windows at this site:\nhttp://breakingcode.wordpress.com/2009/08/31/using-distorm-with-python-2-6-and-python-3-x-revisited/')
            md.run()
            md.destroy()
            return False
        elif platform.machine() == 'x86_64':
            page = "http://inguma.eu/attachments/download/68/libdistorm64-64.so"
        else:
            page = "http://inguma.eu/attachments/download/69/libdistorm64-32.so"
        self.gom.echo( "Downloading " + page, False )
        urllib.urlretrieve(page, path + "libdistorm64.so")
        self.gom.echo( "Operation Complete", False )
        self.dis_bt.set_sensitive(True)

    def reactivate_button(self, threadid, widget):
        if threadid.is_alive():
            return True
        else:
            widget.set_sensitive(True)
            return False
