##      graphMenu.py
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

import gtk, gobject

import os, threading

import lib.ui.config as config

from lib.core import get_profile_file_path

class UIManager(gtk.UIManager):

    def __init__(self, gom, core):
        gtk.UIManager.__init__(self)

        self.ui_id = 0
        self.gom = gom
        self.uicore = core

        self.graph_menu = '''
        <ui>
            <popup name="Popup">
                <menu action="Graph options" position="top"></menu>
                <menuitem action="options" position="top"/>
                <separator/>
                <menuitem action="do_asn"/>
                <separator/>
                <menuitem action="asn_cluster"/>
                <menuitem action="geoip"/>
                <menuitem action="get_to_from"/>
                <menuitem action="get_from_to"/>
                <menuitem action="get_vulns_ip"/>
                <separator/>
                <menuitem action="get_weighted_ip"/>
                <menuitem action="get_weighted_port"/>
            </popup>
        </ui>
        '''
        self.uicore = core

        # Add the accelerator group
        self.accel = self.get_accel_group()

        # Create an ActionGroup
        self.actiongroup = gtk.ActionGroup('Popup')

        # Add actions
        self.actiongroup.add_actions( [('Graph options', None, ' Graph Options ')] )
        self.actiongroup.add_actions( [('options', None, ' Graph Options ')] )
        self.actiongroup.add_actions( [('do_asn', gtk.STOCK_EXECUTE, ' Get ASN ', None, 'ToolTip', self.doAsn )] )
        self.actiongroup.add_actions( [('asn_cluster', gtk.STOCK_CONVERT, ' ASN Clustered ', None, 'ToolTip', self.doNormal )] )
        self.actiongroup.add_actions( [('geoip', gtk.STOCK_CONVERT, ' GeoIP Map ', None, 'ToolTip', self.geoIp)] )
        self.actiongroup.add_actions( [('get_to_from', gtk.STOCK_CONVERT, ' Ports per IP ', None, 'ToolTip', self.doToFrom )], ['ports_ip'] )
        self.actiongroup.add_actions( [('get_from_to', gtk.STOCK_CONVERT, ' IP per Port ', None, 'ToolTip', self.doToFrom )], ['ip_ports'] )
        self.actiongroup.add_actions( [('get_vulns_ip', gtk.STOCK_CONVERT, ' Vulns per Port ', None, 'ToolTip', self.doToFrom )], ['ports_vuln'] )
        self.actiongroup.add_actions( [('get_weighted_ip', gtk.STOCK_CONVERT, ' Weighted IP ', None, 'ToolTip', self.doWeighted )], ['ip'] )
        self.actiongroup.add_actions( [('get_weighted_port', gtk.STOCK_CONVERT, ' Weighted Ports ', None, 'ToolTip', self.doWeighted )], ['port'] )

        # Add the actiongroup to the uimanager
        self.insert_action_group(self.actiongroup, 0)

        # Add a UI description
        self.add_ui_from_string(self.graph_menu)

        # Menu
        ui_id = self.add_ui_from_string(self.graph_menu)
        #self.set_uiID(ui_id)
        self.popmenu = self.get_widget('/Popup')

    def doNormal(self, widget):
        self.uicore.getDot(False)
        self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )

    def geoIp(self, widget):
        geodb_path = get_profile_file_path( 'data' + os.sep + 'GeoLiteCity.dat')
        print geodb_path
        if os.path.exists(geodb_path):
            if config.HAS_GEOIP:
                import lib.ui.geoip as geoip
                geoip.Gui(self.uicore)
        else:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "GeoIP Database not found!\n\nDownload it at the preferences dialog\nunder the Update tab")
            md.run()
            md.destroy()

    def doAsn(self, widget):
        #self.uicore.getDot(True)

        t = threading.Thread(target=self.uicore.getDot, args=(True,))
        t.start()
        self.threadtv.add_action('Get ASN', 'all nodes', t)

        gobject.timeout_add(1000, self.update_graph, t)

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False

    def doToFrom(self, widget, type):
        self.xdot.on_zoom_100(None)
        self.uicore.getToFromDot(type[0])
        self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )

    def doWeighted(self, widget, type):
        self.xdot.on_zoom_100(None)
        self.uicore.getWeighted(type[0])
        self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )
