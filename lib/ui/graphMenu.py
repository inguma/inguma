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

from gi.repository import GdkPixbuf, Gtk, GObject

import os, threading

import lib.ui.config as config

from lib.core import get_profile_file_path

# FIXME
# Ugly hacks to make MenuItems look better
# MUST rewrite the whole menu away from UImanager to normal menu widget
# FIXME

class UIManager(Gtk.UIManager):

    def __init__(self, main):
        GObject.GObject.__init__(self)

        self.ui_id = 0
        self.main = main
        self.gom = main.gom
        self.uicore = main.uicore

        graph_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'chart_organisation.png'))
        graph_icon_add = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'chart_organisation_add.png'))
        asn_search = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'asn_group.png'))
        geomap_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'map_icon.png'))
        datalist_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'sitemap_color.png'))
        weight_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'chart_line.png'))

        self.graph_menu = '''
        <ui>
            <popup name="Popup">
                <menu action="Graph options"></menu>
                <menuitem action="options"/>
                <separator/>
                <menuitem action="add_target"/>
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
        # Add the accelerator group
        self.accel = self.get_accel_group()

        # Create an ActionGroup
        self.actiongroup = Gtk.ActionGroup('Popup')

        # Add actions
        self.actiongroup.add_actions( [('Graph options', None, '')] )
        self.actiongroup.add_actions( [('options', None, '')] )
        self.actiongroup.add_actions( [('add_target', Gtk.STOCK_ADD, ' Add new target ', None, 'ToolTip', self.add_target )] )
        self.actiongroup.add_actions( [('do_asn', Gtk.STOCK_EXECUTE, ' Get nodes ASN ', None, 'ToolTip', self.doAsn )] )
        self.actiongroup.add_actions( [('asn_cluster', None, ' ASN Clustered ', None, 'ToolTip', self.doNormal )] )
        self.actiongroup.add_actions( [('geoip', None, ' GeoIP Map ', None, 'ToolTip', self.geoIp)] )
        self.actiongroup.add_actions( [('get_to_from', None, ' Ports per IP ', None, 'ToolTip', self.doToFrom )], ['ports_ip'] )
        self.actiongroup.add_actions( [('get_from_to', None, ' IP per Port ', None, 'ToolTip', self.doToFrom )], ['ip_ports'] )
        self.actiongroup.add_actions( [('get_vulns_ip', None, ' Vulns per Port ', None, 'ToolTip', self.doToFrom )], ['ports_vuln'] )
        self.actiongroup.add_actions( [('get_weighted_ip', None, ' Weighted IP ', None, 'ToolTip', self.doWeighted )], ['ip'] )
        self.actiongroup.add_actions( [('get_weighted_port', None, ' Weighted Ports ', None, 'ToolTip', self.doWeighted )], ['port'] )

        # Add the actiongroup to the uimanager
        self.insert_action_group(self.actiongroup, 0)

        # Add a UI description
        self.add_ui_from_string(self.graph_menu)

        # Menu
        #ui_id = self.add_ui_from_string(self.graph_menu)
        #self.set_uiID(ui_id)
        self.popmenu = self.get_widget('/Popup')

        # Decorate Menu items...
        items = self.popmenu.get_children()
        bold_title = items[1].get_children()[0]
        bold_title.set_markup("<b> Graph options </b>")
        items[3].set_image(Gtk.Image.new_from_pixbuf(graph_icon_add))
        items[4].set_image(Gtk.Image.new_from_pixbuf(asn_search))
        items[6].set_image(Gtk.Image.new_from_pixbuf(graph_icon))
        items[7].set_image(Gtk.Image.new_from_pixbuf(geomap_icon))
        for item in items[8:11]:
            if type(item) is not Gtk.SeparatorMenuItem:
                item.set_image(Gtk.Image.new_from_pixbuf(datalist_icon))
        for item in items[11:]:
            if type(item) is not Gtk.SeparatorMenuItem:
                item.set_image(Gtk.Image.new_from_pixbuf(weight_icon))

    def doNormal(self, widget):
        self.uicore.getDot(False)
        self.xdot.set_dotcode( self.uicore.get_last_dot() )

    def geoIp(self, widget):
        geodb_path = get_profile_file_path( 'data' + os.sep + 'GeoLiteCity.dat')
        print geodb_path
        if os.path.exists(geodb_path):
            if config.HAS_GEOIP:
                import lib.ui.geoip as geoip
                geoip.Gui(self.uicore)
        else:
            md = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, "GeoIP Database not found!\n\nDownload it at the preferences dialog\nunder the Update tab")
            md.run()
            md.destroy()

    def doAsn(self, widget):
        #self.uicore.getDot(True)

        t = threading.Thread(target=self.uicore.getDot, args=(True,))
        t.start()
        self.threadtv.add_action('Get nodes ASN', 'all nodes', t)

        GObject.timeout_add(1000, self.update_graph, t)

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdot.set_dotcode( self.uicore.get_last_dot() )
            self.gom.kbwin.update_tree()
            return False

    def doToFrom(self, widget, type):
        self.xdot.on_zoom_100(None)
        self.uicore.getToFromDot(type[0])
        self.xdot.set_dotcode( self.uicore.get_last_dot() )

    def doWeighted(self, widget, type):
        self.xdot.on_zoom_100(None)
        self.uicore.getWeighted(type[0])
        self.xdot.set_dotcode( self.uicore.get_last_dot() )

    def add_target(self, widget):
        self.main.toolbar.add_tb.set_active(True)
