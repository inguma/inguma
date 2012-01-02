##      filemanager_notebook.py
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

import os
import gtk

class FileManagerNotebook(gtk.Notebook):

    def __init__(self, main):
        super(FileManagerNotebook,self).__init__()
        # TreeStore
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str)
        # create the TreeView using liststore
        self.file_tree = gtk.TreeView(self.liststore)
        self.file_tree.set_headers_visible(False)

        self.main = main
        self.uicore = main.uicore

        self.handler = None

        # Tree icons
        self.folder_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'folder.png')
        self.file_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'page_white.png')
        self.term_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'terminal.png')
        self.mark_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'star.png')
        self.shell_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'computer_link.png')

        #################################################################
        # Scrolled Window and Co
        #################################################################

        # Scrolledwindow/Treeview
        self.file_sw = gtk.ScrolledWindow()
        self.file_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.mark_sw = gtk.ScrolledWindow()
        self.mark_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.term_sw = gtk.ScrolledWindow()
        self.term_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.shell_sw = gtk.ScrolledWindow()
        self.shell_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.file_sw.set_size_request(200,-1)

        #self.set_rules_hint(True)

        # Fill by default with targets info
        self.create_model('files')

        # Add Textview to Scrolled Window
        self.file_sw.add_with_viewport(self.file_tree)

        self._create_tabs()

    def _create_tabs(self):
        icon = gtk.Image()
        icon.set_from_pixbuf(self.folder_icon)
        self.append_page(self.file_sw, icon)
        icon = gtk.Image()
        icon.set_from_pixbuf(self.mark_icon)
        self.append_page(self.mark_sw, icon)
        icon = gtk.Image()
        icon.set_from_pixbuf(self.term_icon)
        self.append_page(self.term_sw, icon)
        icon = gtk.Image()
        icon.set_from_pixbuf(self.shell_icon)
        self.append_page(self.shell_sw, icon)

    def create_model(self, mode):
        # Clear before changing contents
        self.liststore.clear()
        self.remove_columns()

        if mode == 'files':
            self.create_file_list()
            self.fill_file_list()

    def remove_columns(self):
        columns = self.file_tree.get_columns() 
        for column in columns:
            self.remove_column(column)

    def create_file_list(self):
        rendererPix = gtk.CellRendererPixbuf()
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
        self.file_tree.append_column(column)

        self.file_tree.set_model(self.liststore)

    def fill_file_list(self, path=os.getcwd()):
        self.liststore.clear()

        elements = os.listdir(path)
        if elements:
            elements.sort()
        files = []
        folders = ['..']
        for filename in elements:
            filepath = os.path.join(path, filename)
            if os.path.isdir(filepath):
                folders.append(filename)
            else:
                files.append(filename)

        for folder in folders:
            icon = self.folder_icon
            self.liststore.append([icon, folder])
        for file in files:
            icon = self.file_icon
            self.liststore.append([icon, file])

#        self.handler = self.connect('button-press-event', self.listener_menu)
