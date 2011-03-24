##      altNodeMenu.py
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
                <menu action="Node options" position="top"></menu>
                <menuitem action="options" position="top"/>
                <separator/>
                <menuitem action="remove_node"/>
            </popup>
        </ui>
        '''
        self.uicore = core

        # Add the accelerator group
        self.accel = self.get_accel_group()

        # Create an ActionGroup
        self.actiongroup = gtk.ActionGroup('Popup')

        # Add actions
        self.actiongroup.add_actions( [('Node options', None, ' Node Options ')] )
        self.actiongroup.add_actions( [('options', None, ' Graph Options ')] )
        self.actiongroup.add_actions( [('remove_node', gtk.STOCK_DIALOG_WARNING, ' Remove Node ', None, 'ToolTip', self.remove_node )] )

        # Add the actiongroup to the uimanager
        self.insert_action_group(self.actiongroup, 0)

        # Add a UI description
        self.add_ui_from_string(self.graph_menu)

        # Menu
        ui_id = self.add_ui_from_string(self.graph_menu)
        #self.set_uiID(ui_id)
        self.popmenu = self.get_widget('/Popup')

    def set_data(self, ip=None):
        ''' called on click to prepend target info on the popup menu'''

        self.ip = ip

    def remove_node(self, widget):

        askRemove = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO, message_format="Are you sure you want ro remove that node?")
        do_remove = askRemove.run()

        if do_remove == gtk.RESPONSE_YES:
            print "Let's remove data for node:", self.ip
#            self.uicore.remove_node(self.ip)
            t = threading.Thread(target=self.uicore.remove_node, args=(self.ip,))
            t.start()
            self.threadtv.add_action('Removing node', self.ip, t)
    
            gobject.timeout_add(1000, self.update_graph, t)
        else:
            pass
        askRemove.destroy()

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.uicore.getDot(True)
            self.xdot.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False
