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

import pygtk
import gtk, gobject

import threading

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
            </popup>
        </ui>
        '''
        self.uicore = core

        # Add the accelerator group
        self.accel = self.get_accel_group()

        # Create an ActionGroup
        self.actiongroup = gtk.ActionGroup('Popup')

        # Add actions
        self.actiongroup.add_actions( [('Graph options', None, 'Graph Options')] )
        self.actiongroup.add_actions( [('options', None, 'Graph Options')] )
        self.actiongroup.add_actions( [('do_asn', gtk.STOCK_EXECUTE, 'Get ASN', None, 'ToolTip', self.doAsn )] )

        # Add the actiongroup to the uimanager
        self.insert_action_group(self.actiongroup, 0)

        # Add a UI description
        self.add_ui_from_string(self.graph_menu)

        # Menu
        ui_id = self.add_ui_from_string(self.graph_menu)
        #self.set_uiID(ui_id)
        self.popmenu = self.get_widget('/Popup')

    def doAsn(self, widget):
        #self.uicore.getDot(True)

        t = threading.Thread(target=self.uicore.getDot, args=(True,))
        t.start()

        gobject.timeout_add(1000, self.update_graph, t)

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False

