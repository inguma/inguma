##      right_tree.py
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
from gi.repository import Gdk, GdkPixbuf, Gtk

import lib.globals as glob
import lib.ui.config as config
import lib.ui.vulns_menu as vulns_menu
import lib.ui.listeners_menu as listeners_menu

class KBtree(Gtk.TreeView):

    def __init__(self, main, core):
        # TreeStore
        self.treestore = Gtk.TreeStore(GdkPixbuf.Pixbuf, str, str)
        # create the TreeView using treestore
        super(KBtree,self).__init__(self.treestore)

        self.main = main
        glob.gom = self.main.gom
        self.uicore = core
        self.node_menu = main.uiman

        self.active_mode = 'Targets'

        self.handler = None

        self.vuln_popup = vulns_menu.VulnsMenu(self.main)
        self.listener_popup = listeners_menu.ListenersMenu(self.main, self)

        self.xdot = None
        # nodes will store graph nodes used for automove on kbtree click
        self.nodes = {}

        # To keep track of listeners that received connection
        self.connections = []

        # Tree icons
        self.default_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'generic.png'))
        self.node_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'node.png'))
        self.value_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'value.png'))
        self.vuln_icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'bug.png'))

        # Main VBox to store right panel elements
        self.right_vbox = Gtk.VBox(False)

        # OS visibility
        self.os_visible = {}
        self.os_visible['generic'] = True
        for oss in config.ICONS:
            self.os_visible[oss.lower()] = True

        # OS buttons bar
        self.oss_bar = Gtk.Toolbar()
        self.oss_bar.set_show_arrow(True)
        self.oss_bar.set_style(Gtk.ToolbarStyle.ICONS)
        self.create_os_buttons()

        #################################################################
        # Scrolled Window and Co
        #################################################################

        # Target filter text entry
        # expand/collapse buttons
        self.tgt_hbox = Gtk.HBox(False)

        self.expand_btn = Gtk.Button()
        self.expand_icon = Gtk.Image()
        self.expand_icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
        self.expand_btn.set_image(self.expand_icon)
        self.expand_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.expand_btn.set_tooltip_text('Expand all nodes')
        self.expand_btn.connect('clicked', self._expand_all)

        self.collapse_btn = Gtk.Button()
        self.collapse_icon = Gtk.Image()
        self.collapse_icon.set_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.MENU)
        self.collapse_btn.set_image(self.collapse_icon)
        self.collapse_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.collapse_btn.set_tooltip_text('Collapse all nodes')
        self.collapse_btn.connect('clicked', self._collapse_all)

        sep = Gtk.VSeparator()

        self.tgt_entry = Gtk.Entry()
        self.tgt_entry.set_icon_from_stock(1, Gtk.STOCK_CLEAR)
        self.tgt_entry.set_icon_tooltip_text(1, 'Clear entry')
        self.tgt_entry.connect('icon-press', self._clear_entry)
        self.tgt_entry.connect('changed', self._do_filter)

        self.tgt_hbox.pack_start(self.expand_btn, False, False, 0)
        self.tgt_hbox.pack_start(self.collapse_btn, False, False, 0)
        self.tgt_hbox.pack_start(sep, False, False, 2)
        self.tgt_hbox.pack_start(self.tgt_entry, True, True, 0)

        self.right_vbox.pack_start(self.tgt_hbox, False, False, 1)

        # Scrolledwindow/Treeview
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_size_request(250,-1)

        self.modelfilter = self.treestore.filter_new()

        self.modelfilter.set_visible_func(self.visible_cb)
        self.set_model(self.modelfilter)

        self.set_rules_hint(True)
        self.set_enable_tree_lines(True)

        # Fill by default with targets info
        self.create_targets_tree()
        self.update_targets_tree()
        self.expand_all()

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self)

        self.right_vbox.pack_start(self.scrolled_window, True, True, 0)

    def create_os_buttons(self):
        # OS filter buttons

        self.remove_os_buttons()

        counter = 0
        added_os = []
        kb = self.uicore.get_kbList()
        targets = kb['targets']
        for target in targets:
            if kb.has_key(target + '_os'):
                oss = kb[target + '_os'][0].lower()
                for os_icon in config.ICONS:
                    if os_icon in oss and os_icon not in added_os:
                        btn = self.create_os_button(os_icon)
                        self.oss_bar.insert(btn, counter)
                        counter += 1
                        added_os.append(os_icon)
            else:
                if 'generic' not in added_os:
                    btn = self.create_os_button('generic', True)
                    self.oss_bar.insert(btn, counter)
                    counter += 1
                    added_os.append('generic')

        if len(self.oss_bar.get_children()) > 1:
            self.right_vbox.pack_start(self.oss_bar, False, False, 1)
            self.oss_bar.show_all()

    def create_os_button(self, oss, generic=False):
        if not generic:
            btn = Gtk.ToggleToolButton(oss)
            btn.set_label(oss.capitalize())
            btn.set_tooltip_text(oss.capitalize())
            icon = Gtk.Image()
            icon.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', oss + '.png'))
            btn.set_icon_widget(icon)
            btn.set_active(True)
            self.os_visible[oss.lower()] = True
            btn.connect('toggled', self._filter_on_toggle)
        else:
            btn = Gtk.ToggleToolButton()
            btn.set_label('Generic')
            btn.set_tooltip_text('Generic')
            self.os_visible['generic'] = True
            icon = Gtk.Image()
            icon.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'generic.png'))
            btn.set_icon_widget(icon)
            btn.set_active(True)
            btn.connect('toggled', self._filter_on_toggle)

        return btn

    def update_model(self):
        self.create_model(self.active_mode)

    def create_model(self, mode):
        # Clear before changing contents
        self.treestore.clear()
        self.remove_columns()

        if mode == 'Targets':
            self.create_targets_tree()
            self.update_targets_tree()
            self.active_mode = 'Targets'
        elif mode == 'Vulnerabilities':
            self.create_targets_tree()
            self.create_vulns_tree()
            self.active_mode = 'Vulnerabilities'
        elif mode == 'Listeners':
            self.create_listeners_list()
            self.fill_listeners_list()
            self.active_mode = 'Listeners'

        # Update all
        self.expand_all()

    def remove_columns(self):
        columns = self.get_columns()
        for column in columns:
            self.remove_column(column)

    def remove_os_buttons(self):
        for child in self.oss_bar.get_children():
            self.oss_bar.remove(child)
        if self.oss_bar in self.right_vbox:
            self.right_vbox.remove(self.oss_bar)

    def create_listeners_list(self):
        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        rendererPix = Gtk.CellRendererPixbuf()
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("File")
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
        self.append_column(column)

        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Port", rendererText, text=2)
        self.treestore.set_sort_column_id(2,Gtk.SortType.ASCENDING)
        column.set_sort_column_id(2)
        self.append_column(column)

        self.set_headers_visible(False)
        self.set_model(self.liststore)

    def fill_listeners_list(self):
        self.liststore.clear()
        conn = Gtk.Image()
        conn = conn.render_icon(Gtk.STOCK_CONNECT, Gtk.IconSize.MENU)
        disconn = Gtk.Image()
        disconn = disconn.render_icon(Gtk.STOCK_DISCONNECT, Gtk.IconSize.MENU)
        if glob.listeners:
            for listener in glob.listeners:
                host, port = listener.split(':')
                if listener in self.connections:
                    self.liststore.append([conn, host, port])
                else:
                    self.liststore.append([disconn, host, port])
        else:
            icon = Gtk.Image()
            icon = icon.render_icon(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
            self.liststore.append([icon, 'No active listeners', None])

        if self.handler:
            self.disconnect(self.handler)
        self.handler = self.connect('button-press-event', self.listener_menu)

    def update_listener(self, host, port):
        listener_id = host + ':' + port
        if glob.listeners[listener_id].connected:
            self.connections.append(listener_id)
        else:
            if listener_id in self.connections:
                self.connections.remove(listener_id)

        if self.active_mode == 'Listeners':
            self.fill_listeners_list()

    def create_vulns_tree(self):
        ids = {}
        kb = self.uicore.get_kbList()
        # Add all hosts
        targets = kb['targets']
        targets.sort()
        for host in targets:
            target_def = [self.default_icon, host, 'generic']
            if host + '_os' in kb:
                target_os = kb[host + '_os'][0]
                for oss in config.ICONS:
                    if oss.capitalize() in target_os:
                        icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', oss + '.png'))
                        target_def = [icon, host, oss]
            piter = self.treestore.append(None, target_def)
            if host + '_tcp_ports' in kb:
                for port in kb[host + '_tcp_ports']:
                    icon = Gtk.Image()
                    icon = icon.render_icon(Gtk.STOCK_CONNECT, Gtk.IconSize.MENU)
                    port_iter = self.treestore.append(piter, [icon, str(port) + '/TCP', None])
                    if host + '_'+ str(port) + '-web-vulns' in kb.keys():
                        for id, vuln in kb[host + '_' + str(port) + '-web-vulns']:
                            if id not in ids.keys():
                                #print "Set element:", element
                                iditer = self.treestore.append(port_iter, [self.node_icon, 'OSVDB: ' + id, host + ':' + str(port)])
                                self.treestore.append(iditer, [self.vuln_icon, vuln,  id + '-' + host + ':' + str(port)])
                                ids[id] = iditer
                            else:
                                self.treestore.append(ids[id], [self.vuln_icon, vuln, id + '-' + host + ':' + str(port)])
                    else:
                        icon = Gtk.Image()
                        icon = icon.render_icon(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
                        self.treestore.append(port_iter, [icon, 'No vulnerabilities found yet', None])
            else:
                icon = Gtk.Image()
                icon = icon.render_icon(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
                self.treestore.append(piter, [icon, 'No opened ports found yet', None])

        self.set_model(self.modelfilter)
        if self.handler:
            self.disconnect(self.handler)
        self.handler = self.connect('button-press-event', self.popup_vuln_menu)

    def create_targets_tree(self):

        # create the TreeViewColumn to display the data
        self.tvcolumn = Gtk.TreeViewColumn('Hosts')

        # add tvcolumn to treeview
        self.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = Gtk.CellRendererText()
        self.rendererPix = Gtk.CellRendererPixbuf()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.rendererPix, False)
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.set_attributes(self.rendererPix, pixbuf=0)
        self.tvcolumn.set_attributes(self.cell, text=1)
        #self.tvcolumn.add_attribute(self.cell, 'text', 1)

        # make it searchable
        self.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(1)

        # Allow drag and drop reordering of rows
        self.set_reorderable(True)

        self.set_model(self.modelfilter)
        # Connect right click popup search menu
        if self.handler:
            self.disconnect(self.handler)
        self.handler = self.connect('button-press-event', self.popup_menu)

    def update_targets_tree(self):
        '''Reads KB and updates TreeView'''

        self.treestore.clear()

        kb = self.uicore.get_kbList()
        # Add all hosts
        targets = kb['targets']
        targets.sort()
        for host in targets:
            target_def = [self.default_icon, host, 'generic']
            if host + '_os' in kb:
                target_os = kb[host + '_os'][0]
                for oss in config.ICONS:
                    if oss.capitalize() in target_os:
                        icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join('lib', 'ui', 'data', 'icons', oss + '.png'))
                        target_def = [icon, host, oss]
            piter = self.treestore.append(None, target_def)
            for element in kb:
                if element.__contains__(host + '_'):
                    #self.treestore.append(piter, [element.split('_')[-1].capitalize()])
                    #print "Set element:", element
                    eiter = self.treestore.append(piter, [self.node_icon, element.split('_')[-1].capitalize(), None])

                    for subelement in kb[element]:
                        if subelement is list:
                            #print "\tSet subelement list:", subelement
                            for x in subelement:
                                self.treestore.append(eiter, [self.value_icon, x, None] )
                        else:
                            #print "\tSet subelement not list:", subelement
                            self.treestore.append(eiter, [self.value_icon, subelement, None] )

            if self.xdot:
                #function = ''
                for node in self.xdot.graph.nodes:
                    if node.url:
                        target = node.url
                        self.nodes[target] = [node.x, node.y]
        # Update OS bar
        self.create_os_buttons()

    def _expand_all(self, widget):
        self.expand_all()

    def _collapse_all(self, widget):
        self.collapse_all()

    def _clear_entry(self, entry, icon_pos, event):
        entry.set_text('')
        self.modelfilter.refilter()

    def _do_filter(self, widget):
        '''filter treeview while user types'''
        self.modelfilter.refilter()

    def _filter_on_toggle(self, widget):
        os_name = widget.get_label().lower()
        self.os_visible[os_name] = widget.get_active()
        self.modelfilter.refilter()

    def visible_cb(self, model, iter, data):
        text = self.tgt_entry.get_text()
        # Just filter root nodes, so we check iter path
        if len(model.get_path(iter)) == 1:
            # Check os filter buttons
            if model.get_value(iter, 2) and self.os_visible:
                if not model.get_value(iter, 2) in self.os_visible.keys():
                    return True
                elif not self.os_visible[model.get_value(iter, 2)]:
                    return False
                else:
                    # Just filter if text entry is filled
                    if text:
                        return text in model.get_value(iter, 1)

        return True

    def popup_menu(self, tree, event):
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            #(path, column) = tree.get_cursor()
            var = tree.get_path_at_pos(int(event.x), int(event.y))
            if var:
                (path, column, x, y) = var
                # Is it over a plugin name?
                # Get the information about the click
                if path is not None and len(path) == 1 and self.nodes:
                    node = self.treestore[path][1]
                    if node in self.nodes:
                        self.xdot.animate_to(int(self.nodes[node][0]), int(self.nodes[node][1]) )
        elif event.button == 3:
            #(path, column) = tree.get_cursor()
            var = tree.get_path_at_pos(int(event.x), int(event.y))
            if var:
                (path, column, x, y) = var
                # Is it over a plugin name?
                # Get the information about the click
                if path is not None and len(path) == 1:
                    node = self.treestore[path][1]
                    self.node_menu.set_data(node)
                    self.node_menu.popmenu.popup(None, None, None, 1, event.time)

    def popup_vuln_menu(self, tree, event):
        if event.button == 3:
            #(path, column) = tree.get_cursor()
            var = tree.get_path_at_pos(int(event.x), int(event.y))
            if var:
                (path, column, x, y) = var
                # Is it over a plugin name?
                # Get the information about the click
                if path is not None and len(path) == 4:
                    node = self.treestore[path][1]
                    menu = self.vuln_popup.create_menu(node, self.treestore[path][2])
                    menu.popup(None, None, None, 1, event.time)
                    menu.show_all()

    def listener_menu(self, tree, event):
        if event.button == 3:
            #(path, column) = tree.get_cursor()
            var = tree.get_path_at_pos(int(event.x), int(event.y))
            if var:
                (path, column, x, y) = var
                # Is it over a plugin name?
                # Get the information about the click
                if path is not None and glob.listeners:
                    node = self.liststore[path][1]
                    menu = self.listener_popup.create_menu(node, self.liststore[path][2])
                    menu.popup(None, None, None, 1, event.time)
                    menu.show_all()

    def update_tree(self):
        self.create_model(self.active_mode)
