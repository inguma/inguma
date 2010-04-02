##      threadstv.py
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

import time

class ThreadsTv:

    def __init__(self):
        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(int, str, str, str, str)

        #self.modelfilter = self.liststore.filter_new()

        # create the TreeView
        self.treeview = gtk.TreeView(self.liststore)

        # create the TreeViewColumns to display the data
        self.treeview.columns = [None]*5
        self.treeview.columns[0] = gtk.TreeViewColumn('No.')
        self.treeview.columns[1] = gtk.TreeViewColumn('State')
        self.treeview.columns[2] = gtk.TreeViewColumn('Description')
        self.treeview.columns[3] = gtk.TreeViewColumn('Start')
        self.treeview.columns[4] = gtk.TreeViewColumn('End')

        # create a CellRenderers to render the data
        self.cellpb = gtk.CellRendererPixbuf()
        # add the cells to the columns - 2 in the first
        self.treeview.columns[1].pack_start(self.cellpb, False)
        # set the cell attributes to the appropriate liststore column
        self.treeview.columns[1].set_attributes(self.cellpb, stock_id=1)

        # make ui layout
        self.scrolledwindow = gtk.ScrolledWindow()


        for n in range(5):
            self.treeview.append_column(self.treeview.columns[n])
            self.treeview.columns[n].cell = gtk.CellRendererText()
            self.treeview.columns[n].pack_start(self.treeview.columns[n].cell, True)
            self.treeview.columns[n].set_attributes(self.treeview.columns[n].cell, text=n)

        self.scrolledwindow.add(self.treeview)

        self.counter = 0

    def add_action(self, module):
        """ Adds a new action to the list """

        print "Adding new content for:", module
        self.liststore.append([self.counter, gtk.STOCK_EXECUTE, module, time.strftime("%H:%M:%S", time.gmtime()), '' ])
        self.counter += 1

    def get_widget(self):
        return self.scrolledwindow

    def load_exploits(self, gom):
        if self.exploits_loaded == 0:
            gom.echo( 'Loading Exploits DDBB...' , False)
            # load exploits from csv
            ifile  = open('data/exploits/files.csv', "rb")
            reader = csv.reader(ifile, delimiter=';')
            headerList = reader.next()
    
            # add bug data
            self.states = []
            for line in reader:
                self.liststore.append([ int(line[0]), line[1], line[2], line[3], line[4], line[5], line[6], line[7] ])
    #            if not line[5] in self.states:
    #                print "Adding button for: '", line[5], "'"
    #                self.states.append(line[5])
    
            self.show_states = self.states[:]
            self.modelfilter.set_visible_func(self.visible_cb, self.show_states)
    
            self.treeview.set_model(self.modelfilter)
    
            for n in range(8):
                # add columns to treeview
                self.treeview.append_column(self.treeview.columns[n])
                # create a CellRenderers to render the data
                self.treeview.columns[n].cell = gtk.CellRendererText()
                # add the cells to the columns
                self.treeview.columns[n].pack_start(self.treeview.columns[n].cell, True)
                # set the cell attributes to the appropriate liststore column
                self.treeview.columns[n].set_attributes(
                    self.treeview.columns[n].cell, text=n)
    
            # make treeview searchable
            self.treeview.set_search_column(5)
    
            self.exploits_loaded = 1
