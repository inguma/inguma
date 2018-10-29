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
from gi.repository import GdkPixbuf, Gtk

class FileManagerNotebook(Gtk.Notebook):

    def __init__(self, main):
        super(FileManagerNotebook,self).__init__()
        # TreeStore
        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        # create the TreeView using liststore
        self.file_tree = Gtk.TreeView(self.liststore)
        self.file_tree.set_headers_visible(False)
        self.handler = self.file_tree.connect('button-press-event', self.on_dir__button_press_event)
        self.handler = self.file_tree.connect('row-activated', self.on_dir__key_press_event)

        self.main = main
        self.term_nb = self.main.term_notebook
        self.uicore = main.uicore

        self.set_tab_pos(Gtk.PositionType.BOTTOM)
        self.handler = None
        self.path = os.getcwd()

        # Tree icons
        self.folder_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'folder.png'))
        self.file_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'page_white.png'))
        self.term_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'terminal.png'))
        self.mark_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'star.png'))
        self.shell_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'computer_link.png'))
        self.import_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'arrow_join.png'))

        #################################################################
        # Scrolled Window and Co
        #################################################################

        # Navigation uuttons and search box
        self.nav_hbox = Gtk.HBox(False)

        self.home_btn = Gtk.Button()
        self.home_icon = Gtk.Image()
        self.home_icon.set_from_stock(Gtk.STOCK_HOME, Gtk.IconSize.MENU)
        self.home_btn.set_image(self.home_icon)
        self.home_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.home_btn.set_tooltip_text('Go home directory')
        self.home_btn.connect('clicked', self._go_home)

        self.go_up_btn = Gtk.Button()
        self.go_up_icon = Gtk.Image()
        self.go_up_icon.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
        self.go_up_btn.set_image(self.go_up_icon)
        self.go_up_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.go_up_btn.set_tooltip_text('Go UP one directory')
        self.go_up_btn.connect('clicked', self._go_up)

        self.hidden_btn = Gtk.ToggleButton()
        self.hidden_icon = Gtk.Image()
        self.hidden_icon.set_from_stock(Gtk.STOCK_FIND_AND_REPLACE, Gtk.IconSize.MENU)
        self.hidden_btn.set_image(self.hidden_icon)
        self.hidden_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.hidden_btn.set_tooltip_text('Show/Hide hidden elements')
        self.hidden_btn.set_active(True)
        self.hidden_btn.connect('toggled', self._set_show_hidden)

        sep = Gtk.VSeparator()

        self.new_term_btn = Gtk.Button()
        self.new_term_icon = Gtk.Image()
        self.new_term_icon.set_from_pixbuf(self.term_icon)
        self.new_term_btn.set_image(self.new_term_icon)
        self.new_term_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.new_term_btn.set_tooltip_text('Open terminal in current directory')
        self.new_term_btn.connect('clicked', self._new_term)

        sep2 = Gtk.VSeparator()

        self.tgt_entry = Gtk.Entry()
        self.tgt_entry.set_icon_from_stock(1, Gtk.STOCK_CLEAR)
        self.tgt_entry.set_icon_tooltip_text(1, 'Clear entry')
        self.tgt_entry.connect('icon-press', self._clear_entry)
        #self.tgt_entry.connect('changed', self._do_filter)
        self.tgt_entry.set_sensitive(False)

        self.nav_hbox.pack_start(self.home_btn, False, False, 0)
        self.nav_hbox.pack_start(self.go_up_btn, False, False, 0)
        self.nav_hbox.pack_start(self.hidden_btn, False, False, 0)
        self.nav_hbox.pack_start(sep, False, False, 2)
        self.nav_hbox.pack_start(self.new_term_btn, False, False, 0)
        self.nav_hbox.pack_start(sep2, False, False, 2)
        self.nav_hbox.pack_start(self.tgt_entry, True, True, 0)

        # Scrolledwindow/Treeview
        self.file_vb = Gtk.VBox(False, 0)
        self.file_sw = Gtk.ScrolledWindow()
        self.file_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.mark_sw = Gtk.ScrolledWindow()
        self.mark_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.term_sw = Gtk.ScrolledWindow()
        self.term_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.shell_sw = Gtk.ScrolledWindow()
        self.shell_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.file_sw.set_size_request(200,-1)

        #self.set_rules_hint(True)

        # Fill by default with targets info
        self.create_model('files')

        # Add Textview to Scrolled Window
        self.file_sw.add_with_viewport(self.file_tree)
        self.file_vb.pack_start(self.nav_hbox, False, False, 1)
        self.file_vb.pack_start(self.file_sw, True, True, 1)

        self._create_tabs()
        #self.create_dir_menu()

    def on_dir__key_press_event(self, tree, path, column):
        if path is not None:
            node = self.liststore[path][1]
            dir = os.path.join(self.path, node)
            if os.path.isdir(dir):
                self.fill_file_list(dir)

    def on_dir__button_press_event(self, terminal, event):
        if event.button == 3:
            var = self.file_tree.get_path_at_pos(int(event.x), int(event.y))
            if var:
                (path, column, x, y) = var
                if path is not None:
                    node = self.liststore[path][1]
                    dir = os.path.join(self.path, node)
                    if os.path.isdir(dir):
                        self.create_dir_menu(dir)
                        self.dir_menu.popup(None, None, None, 1, event.time)
                    else:
                        self.create_file_menu(dir)
                        self.file_menu.popup(None, None, None, 1, event.time)

    def _go_home(self, widget):
        home = os.path.expanduser('~')
        self.fill_file_list(home)

    def _go_up(self, widget):
        self.update_file_list(widget, os.path.join(self.path, '..'))

    def _set_show_hidden(self, widget):
        self.update_file_list(widget, self.path)

    def _clear_entry(self, entry, icon_pos, event):
        entry.set_text('')
        #self.modelfilter.refilter()

    def _new_term(self, widget):
        self._start_term(widget, self.path)

    def create_file_menu(self, file):
        self.file_menu = Gtk.Menu()
        actions = [[self.import_icon, 'Import Nmap scan', self._import_scan_file], [self.import_icon, 'Import Hosts list', self._import_scan_file]]

        for action in actions:
            menuitem = Gtk.ImageMenuItem()
            menuitem.set_label('{0}'.format(action[1]))
            icon = Gtk.Image()
            icon.set_from_pixbuf(action[0])
            menuitem.set_image(icon)
            menuitem.connect('activate', action[2], file)
            self.file_menu.append(menuitem)
        self.file_menu.show_all()

    def create_dir_menu(self, dir):
        self.dir_menu = Gtk.Menu()
        actions = [[self.term_icon, 'Terminal in directory', self._start_term], [self.folder_icon, 'Browse directory', self.update_file_list]]

        for action in actions:
            menuitem = Gtk.ImageMenuItem()
            menuitem.set_label('{0}'.format(action[1]))
            icon = Gtk.Image()
            icon.set_from_pixbuf(action[0])
            menuitem.set_image(icon)
            menuitem.connect('activate', action[2], dir)
            self.dir_menu.append(menuitem)
        self.dir_menu.show_all()

    def _start_term(self, widget, dir):
        self.term_nb.add_new_tab(widget, '', dir)

    def _create_tabs(self):
        icon = Gtk.Image()
        icon.set_from_pixbuf(self.folder_icon)
        self.append_page(self.file_vb, icon)
        icon = Gtk.Image()
        icon.set_from_pixbuf(self.mark_icon)
        self.append_page(self.mark_sw, icon)
        icon = Gtk.Image()
        icon.set_from_pixbuf(self.term_icon)
        self.append_page(self.term_sw, icon)
        icon = Gtk.Image()
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
        rendererPix = Gtk.CellRendererPixbuf()
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn()
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
        self.file_tree.append_column(column)

        self.file_tree.set_model(self.liststore)

    def update_file_list(self, widget, path):
        self.fill_file_list(path)

    def fill_file_list(self, path=os.getcwd()):
        self.liststore.clear()

        elements = os.listdir(path)
        if elements:
            elements.sort()
        files = []
        folders = ['..']
        for filename in elements:
            if self.hidden_btn.get_active() and filename[0] == '.':
                continue
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

        self.path = path

#        self.handler = self.connect('button-press-event', self.listener_menu)

    def _import_scan_file(self, widget, file):
        type = widget.get_children()[0].get_text()
        if 'Nmap' in type:
            self.main.toolbar.menu.import_scan(self, 'nmap', file)
        else:
            self.main.toolbar.menu.import_scan(self, 'hosts', file)
