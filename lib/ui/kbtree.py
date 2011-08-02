##      kbtree.py
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

import lib.ui.core as core

class KBtree:

    def __init__(self):
        self.uicore = core.UIcore()

    def createTree(self):

        #################################################################
        # TreeStore
        #################################################################
        self.treestore = gtk.TreeStore(str)
#        # Add local IPs
#        localip = self.uicore.getLocalIP()
#        piter = self.treestore.append(None, [localip] )
#        gateway = self.uicore.getLocalGW()
#        piter = self.treestore.append(None, [gateway] )

        #################################################################
        # TreeView
        #################################################################
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        self.treeview.set_rules_hint(True)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Hosts')

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        return self.treeview

    def updateTree(self):
        '''Reads KB and updates TreeView'''

        self.treestore.clear()

#        # Add local IPs
#        localip = self.uicore.getLocalIP()
#        piter = self.treestore.append(None, [localip] )
#        gateway = self.uicore.getLocalGW()
#        piter = self.treestore.append(None, [gateway] )

        kb = self.uicore.get_kbList()
        # Add all hosts
        targets = kb['targets']
        targets.sort()
        for host in targets:
            piter = self.treestore.append(None, [ host ])
            for element in kb:
                if element.__contains__(host + '_'):
#                    self.treestore.append( piter, [element.split('_')[-1].capitalize()])
                    #print "Set element:", element
                    eiter = self.treestore.append( piter, [element.split('_')[-1].capitalize()])

                    for subelement in kb[element]:
                        if subelement is list:
                            #print "\tSet subelement list:", subelement
                            for x in subelement:
                                self.treestore.append( eiter, [x] )
                        else:
                            #print "\tSet subelement not list:", subelement
                            self.treestore.append( eiter, [subelement] )





