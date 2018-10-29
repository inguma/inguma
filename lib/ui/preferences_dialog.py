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

from gi.repository import Gtk
from gi.repository import GObject

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
        self.prefs_nb = Gtk.Notebook()

        #########################################################
        # Main Table
        self.main_table = Gtk.Table(rows=3, columns=2, homogeneous=True)
        self.main_table.set_row_spacings(0)
        self.main_table.set_col_spacings(0)

        # Label to add table to Notebook
        self.main_lbl = Gtk.Label(label='Main')

        # Choose network iface
        self.iface_lbl = Gtk.Label(label='Network interface:')

        store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.iface_combo = Gtk.ComboBox(store)
        rendererText = Gtk.CellRendererText()
        rendererPix = Gtk.CellRendererPixbuf()
        self.iface_combo.pack_start(rendererPix, False)
        self.iface_combo.pack_start(rendererText, True)
        self.iface_combo.add_attribute(rendererPix, 'pixbuf', 0)
        self.iface_combo.add_attribute(rendererText, 'text', 1)
        self.iface_combo_align = Gtk.Alignment.new(yalign=0.5, xalign=0.5)
        self.iface_combo_align.add(self.iface_combo)

        # fill and select interfaces
        count = 0
        active_iface = self.uicore.get_interface()
        icon = Gtk.Image()
        #icon.set_from_stock(Gtk.STOCK_NETWORK, Gtk.IconSize.MENU)
        icon = icon.render_icon(Gtk.STOCK_NETWORK, Gtk.IconSize.MENU)
        for iface in self.uicore.get_interfaces():
            store.append([icon, iface])
            if iface == active_iface:
                i = count
            count += 1
        self.iface_combo.set_active(i)

        # IP address label
        self.ip_label = Gtk.Label()
        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        active_iface = model[active][1]
        ip_addr = self.uicore.get_iface_ip(active_iface)
        self.ip_label.set_text(ip_addr)
        #self.ip_label.set_padding(4, 0)
        ip_halign = Gtk.Alignment.new(xalign=0.5)
        ip_halign.add(self.ip_label)

        self.iface_combo.connect('changed', self.get_ip)

        # Apply and Cancel buttons
        btn_hbox = Gtk.HBox(False)

        image = Gtk.Image()
        #  (from http://www.pyGtk.org/docs/pygtk/gtk-stock-items.html)
        image.set_from_stock(Gtk.STOCK_APPLY, Gtk.IconSize.MENU)
        self.apply_btn = Gtk.Button()
        self.apply_btn.set_image(image)
        self.apply_btn.set_label("")
        self.apply_btn.connect("clicked", self.set_interface)

        image = Gtk.Image()
        #  (from http://www.pyGtk.org/docs/pygtk/gtk-stock-items.html)
        image.set_from_stock(Gtk.STOCK_CANCEL, Gtk.IconSize.MENU)
        self.cancel_btn = Gtk.Button()
        self.cancel_btn.set_image(image)
        self.cancel_btn.set_label("")
        self.cancel_btn.connect("clicked", self._bye)

        btn_hbox.pack_start(self.cancel_btn, False, False, 1)
        btn_hbox.pack_start(self.apply_btn, False, False, 1)

        btn_halign = Gtk.Alignment.new(yalign=1.0, xalign=1.0)
        btn_halign.add(btn_hbox)

        # Add elements to Table
        self.main_table.attach(self.iface_lbl, 0, 1, 0, 1)
        self.main_table.attach(self.iface_combo_align, 1, 2, 0, 1)
        self.main_table.attach(ip_halign, 1, 2, 1, 2)
        self.main_table.attach(btn_halign, 1, 2, 2, 3)

        # Add Table to Notebook
        self.prefs_nb.append_page(self.main_table, self.main_lbl)

        #########################################################
        # Update Table
        self.update_table = Gtk.Table(rows=4, columns=2, homogeneous=True)
        self.update_table.set_row_spacings(2)
        self.update_table.set_col_spacings(2)

        # Label to add table to Notebook
        self.update_lbl = Gtk.Label(label='Updates')

        # Add exploits and nikto update buttons
        self.exploit_lbl = Gtk.Label(label='Exploit DB')
        self.nikto_lbl = Gtk.Label(label='Nikto Rules')
        self.geo_lbl = Gtk.Label(label='GeoIP DB')
        self.dis_lbl = Gtk.Label(label='distorm64')
        self.exploit_bt = Gtk.Button('Update', Gtk.STOCK_REFRESH)
        self.exploit_bt.connect('clicked', self.update_exploits)
        self.nikto_bt = Gtk.Button('Update', Gtk.STOCK_REFRESH)
        self.nikto_bt.connect('clicked', self.update_nikto)
        self.geo_bt = Gtk.Button('Update', Gtk.STOCK_REFRESH)
        self.geo_bt.connect('clicked', self.update_geo)
        self.dis_bt = Gtk.Button('Update', Gtk.STOCK_REFRESH)
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

    def get_ip(self, widget):
        '''get IP address of selected iface and change ip label'''

        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        active_iface = model[active][1]
        ip_addr = self.uicore.get_iface_ip(active_iface)
        self.ip_label.set_text(ip_addr)

    def get_selected_iface(self):
        model = self.iface_combo.get_model()
        active = self.iface_combo.get_active()
        if active < 0:
            return None
        return model[active][1]

    def set_interface(self, widget):
        iface = self.get_selected_iface()
        if iface:
            self.uicore.set_interface(iface)
            ip = self.ip_label.get_text()
            self.gom.echo( "New active network interface: %s (%s)" % (iface, ip) , False)
        self._quit(widget)

    def update_exploits(self, widget):
        import lib.ui.exploits as exploits

        self.exploitsInst = exploits.Exploits(self.config)
        widget.set_sensitive(False)
        t = threading.Thread(target=self.exploitsInst.download_exploits, args=(self.gom,))
        t.start()
        GObject.timeout_add(1000, self.reactivate_button, t, widget)
        self.threadtv.add_action('Exploit-db Update', 'Exploits DB', t)

    def update_nikto(self, widget):
        command = 'python lib/libnikto.py'
        widget.set_sensitive(False)
        t = threading.Thread(target=self.uicore.run_system_command, args=(command,))
        t.start()
        GObject.timeout_add(1000, self.reactivate_button, t, widget)
        self.threadtv.add_action('Nikto Update', 'Nikto DB', t)

    def update_geo(self, widget):
        t = threading.Thread(target=self.download_geodb)
        widget.set_sensitive(False)
        t.start()
        GObject.timeout_add(1000, self.reactivate_button, t, widget)
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
            md = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE, message_format='Download distorm library installer for Windows at this site:\nhttp://breakingcode.wordpress.com/2009/08/31/using-distorm-with-python-2-6-and-python-3-x-revisited/')
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

    def _bye(self, widget):
        self._quit(widget)
