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

        # create dict to store threads
        self.threads = {}

        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(int, int, str, str, str)

        #self.modelfilter = self.liststore.filter_new()

        # create the TreeView
        self.treeview = gtk.TreeView(self.liststore)

        # create the TreeViewColumns to display the data
        self.treeview.columns = [None]*5
        self.treeview.columns[0] = gtk.TreeViewColumn('No.')
        self.treeview.columns[1] = gtk.TreeViewColumn('State')
        self.treeview.columns[1].set_min_width(150)
        self.treeview.columns[2] = gtk.TreeViewColumn('Description')
        self.treeview.columns[2].set_min_width(300)
        self.treeview.columns[3] = gtk.TreeViewColumn('Start')
        self.treeview.columns[3].set_min_width(100)
        self.treeview.columns[4] = gtk.TreeViewColumn('End')
        self.treeview.columns[4].set_min_width(100)

        # Lets control right click on treeview
        self.treeview.connect('button_press_event', self.on_treeview_button_press_event )

        # make ui layout
        self.scrolledwindow = gtk.ScrolledWindow()
        # remove hscrollbar
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        #Always on bottom on change
        self.vajd = self.scrolledwindow.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.scrolledwindow: self.rescroll(a,s))

        for n in [0,2,3,4]:
            # add columns to treeview
            self.treeview.append_column(self.treeview.columns[n])
            # create a CellRenderers to render the data
            self.treeview.columns[n].cell = gtk.CellRendererText()
            # add the cells to the columns
            self.treeview.columns[n].pack_start(self.treeview.columns[n].cell, True)
            # set the cell attributes to the appropriate liststore column
            self.treeview.columns[n].set_attributes(self.treeview.columns[n].cell, text=n)

        # add columns to treeview
        self.treeview.insert_column(self.treeview.columns[1], 1)
        # create a CellRenderers to render the data
        self.cellpb = gtk.CellRendererProgress()
        # add the cells to the columns - 2 in the first
        self.treeview.columns[1].pack_start(self.cellpb, True)
        # set the cell attributes to the appropriate liststore column
        self.treeview.columns[1].add_attribute(self.cellpb, "value", 1)

        self.scrolledwindow.add(self.treeview)

        self.counter = 0

    def add_action(self, module, target, threadid):
        """ Adds a new action to the list """

        print "Adding new content for:", module
        iter = self.liststore.append([self.counter, 0, "Running " + module + " against " + target, time.strftime("%H:%M:%S", time.gmtime()), ''])
        self.threads[self.counter] = threadid
        self.counter += 1
        gobject.timeout_add(1000, self.check_thread, threadid, iter)

    def check_thread(self, threadid, iter):
        model = self.treeview.get_model()
        if threadid.is_alive():
            model.set_value(iter, 1, 75)
            return True
        else:
            model.set_value(iter, 4, time.strftime("%H:%M:%S", time.gmtime()))
            model.set_value(iter, 1, 100)
            return False

    def get_widget(self):
        return self.scrolledwindow

    def rescroll(self, adj, scroll):
        adj.set_value(adj.upper-adj.page_size)
        scroll.set_vadjustment(adj)

    def on_treeview_button_press_event(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)

                print "Right Clicked!"
#                treeiter = self.liststore.get_iter(path)
#                threadid = self.liststore.get_value(treeiter ,0)
#
#                t = self.threads[threadid]

            return True
