#------------------------test.py------------------------------------------------------------------------------
#!/usr/bin/env python

# generic treeview

import pygtk
pygtk.require('2.0')
import gtk
import os

class test_tree:

   # close the window and quit
   def delete_event(self, widget, event, data=None):
       gtk.main_quit()
       return False

   def create_menu(self, window,event, data=None):
       item_factory = gtk.ItemFactory(gtk.Menu, "<main>", None)
       item_factory.create_items(self.menu_items)
       self.item_factory = item_factory

       return item_factory.get_widget("<main>")


   def button_press_callback(self, treeview, event, data=None):
       if event.button == 3:
           x = int(event.x)
           y = int(event.y)
           time = event.time
           pthinfo = self.treeview.get_path_at_pos(x,y)
           #   TreeSelection =
           self.treeview.get_selection().get_treeview()
           # tre = gtk.TreeSelection.get_treeview()
           #  print "***"
           # print treeselection
           # print "***"
           if pthinfo is not None:
               path,col,cellx,celly = pthinfo
               self.treeview.grab_focus()
               self.treeview.set_cursor(path,col,0)
               menu = self.create_menu(self,self.window,None)
               menu.popup(None,None,None,event.button,event.time)

           return 1
   def print_A(self, w, data):
       iter = self.menu_items.iter_children(self.menu_items.get_iter(self.menu_path))
       #iter = self.treeview.get_path()
       #aa = self.treestore.get_path(iter)
       print iter

       return 1

   def print_B(self, w, data):
       print "B"
       return 1

   def print_C(self, w, data):
       print "C"
       return 1

   def print_D(self, w, data):
       print "D"
       return 1

   def print_E(self, w, data):
       print "E"
       return 1


   def __init__(self):
       self.menu_items = (
                 ( "/_A",     "<control>O", self.print_A, 0, None ),
                 ( "/_B",    "<control>I", self.print_B, 0, None ),
                 ( "/_C",    "<control>H", self.print_C, 0, None ),
                 ( "/_D",    "<control>F", self.print_D, 0, None ),
                 ( "/_E",    "<control>U", self.print_E, 0, None ),
               )

       # Create a new window
       self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

       self.window.set_title("Project")

       self.window.set_size_request(200, 200)

       self.window.connect("delete_event", self.delete_event)

       # create a TreeStore with one string column to use as the model
       self.treestore = gtk.TreeStore(str)

       # add some data now - 4 rows with 2 child rows each
       for parent in range(4):
           piter = self.treestore.append(None, ['PARENT %i' % parent])
           for child in range(1):
               self.treestore.append(piter, ['CHILD1 %i' % parent])
               self.treestore.append(piter, ['CHILD2 %i' % parent])

       # create the TreeView using treestore
       self.treeview = gtk.TreeView(self.treestore)

       self.treeview.connect ("button_press_event",
       self.button_press_callback, None)
       iter = self.treestore.get_iter_first()

       # create the TreeViewColumn to display the data
       self.tvcolumn = gtk.TreeViewColumn('project')

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

       self.window.add(self.treeview)

       self.window.show_all()

def main():
   gtk.main()

if __name__ == "__main__":
   test_tree = test_tree()
   main()

