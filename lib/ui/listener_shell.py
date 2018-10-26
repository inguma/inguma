##      listener_shell.py
#
#       Copyright 2012 Hugo Teso <hugo.teso@gmail.com>
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
from gi.repository import Gtk

import bokken.throbber as throbber

class ListenerShell(Gtk.VBox):

    def __init__(self):
        GObject.GObject.__init__(self, False)

        # Toolbar
        #
        self.listener_tb = Gtk.Toolbar()
        self.listener_tb.set_style(Gtk.ToolbarStyle.ICONS)

        # Upload button
        self.upload_tb = Gtk.ToolButton(Gtk.STOCK_GO_UP)
        self.upload_tb.set_tooltip_text('Upload file')
        #self.upload_tb.connect("clicked", self.load_editor)
        self.listener_tb.insert(self.upload_tb, 0)

        # Download button
        self.download_tb = Gtk.ToolButton(Gtk.STOCK_GO_DOWN)
        self.download_tb.set_tooltip_text('Download file')
        #self.upload_tb.connect("clicked", self.load_editor)
        self.listener_tb.insert(self.download_tb, 1)

        # Directory list button
        self.dirlist_tb = Gtk.ToolButton(Gtk.STOCK_DIRECTORY)
        self.dirlist_tb.set_tooltip_text('List directories')
        #self.upload_tb.connect("clicked", self.load_editor)
        self.listener_tb.insert(self.dirlist_tb, 2)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.listener_tb.insert(self.sep, 3)

        # Connect
        self.connect_tb = Gtk.ToolButton(Gtk.STOCK_CONNECT)
        self.connect_tb.set_tooltip_text('Connect to target')
        #self.upload_tb.connect("clicked", self.load_editor)
        self.listener_tb.insert(self.connect_tb, 4)

        # Disconnect
        self.disconnect_tb = Gtk.ToolButton(Gtk.STOCK_DISCONNECT)
        self.disconnect_tb.set_tooltip_text('Disconnect to target')
        #self.upload_tb.disconnect("clicked", self.load_editor)
        self.listener_tb.insert(self.disconnect_tb, 5)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.listener_tb.insert(self.sep, 6)

        # Post-exploit label
        self.post_label_tb = Gtk.ToolItem()
        self.post_label_align = Gtk.Alignment.new(yalign=0.5)
        self.post_label = Gtk.Label(label='Post exploitation commands:\t')
        self.post_label_align.add(self.post_label)
        self.post_label_tb.add(self.post_label_align)
        self.listener_tb.insert(self.post_label_tb, 7)

        # Search components
        self.postxpl_combo_tb = Gtk.ToolItem()
        self.postxpl_combo_align = Gtk.Alignment.new(yalign=0.5)
        store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.postxpl_combo = Gtk.ComboBox(store)
        rendererText = Gtk.CellRendererText()
        rendererPix = Gtk.CellRendererPixbuf()
        self.postxpl_combo.pack_start(rendererPix, False)
        self.postxpl_combo.pack_start(rendererText, True)
        self.postxpl_combo.add_attribute(rendererPix, 'pixbuf', 0)
        self.postxpl_combo.add_attribute(rendererText, 'text', 1)

        options = {
            'Windows':GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icons' + os.sep + 'windows.png'),
            'Linux':GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icons' + os.sep + 'linux.png'),
            'MacOS':GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(__file__) + os.sep + 'data' + os.sep + 'icons' + os.sep + 'apple.png'),
        }

        for option in options.keys():
            store.append([options[option], option])
        self.postxpl_combo.set_active(0)
        self.postxpl_combo_align.add(self.postxpl_combo)
        self.postxpl_combo_tb.add(self.postxpl_combo_align)

        self.listener_tb.insert(self.postxpl_combo_tb, 8)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.sep.set_draw(False)
        self.listener_tb.insert(self.sep, 9)

        # Combobox Entry for command selection and edit
        self.comm_combo_tb = Gtk.ToolItem()
        self.comm_combo_align = Gtk.Alignment.new(yalign=0.5)
        self.comm_store = Gtk.ListStore(GObject.TYPE_STRING)
        self.comm_combo = Gtk.ComboBoxEntry(self.comm_store, 0)

        self.comm_combo_entry = self.comm_combo.get_child()
        self.comm_combo_entry.set_icon_from_stock(1, Gtk.STOCK_EXECUTE)

        #self.comm_store.append(['netstat -an'])
        self.comm_combo_align.add(self.comm_combo)
        self.comm_combo_tb.add(self.comm_combo_align)

        self.listener_tb.insert(self.comm_combo_tb, 10)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.listener_tb.insert(self.sep, 11)

        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = Gtk.ToolItem()
        self.throbber_tb.add(self.throbber)

        self.listener_tb.insert(self.throbber_tb, 12)

        self.pack_start(self.listener_tb, False, False, 0)

        # Textview
        #
        self.listener_tv = Gtk.TextView(buffer=None)

        # Some eye candy
        self.listener_tv.modify_base(Gtk.StateType.NORMAL, Gdk.Color(16400, 16400, 16440))
        self.listener_tv.modify_text(Gtk.StateType.NORMAL, Gdk.Color(60535, 60535, 60535, 0))
        self.listener_tv.set_left_margin(10)

        self.listener_tv.set_wrap_mode(Gtk.WrapMode.NONE)
        self.listener_tv.set_editable(False)
        self.textbuffer = self.listener_tv.get_buffer()
        self.textbuffer.set_text('C:\\WINNT\\system32>\n')
        self.listener_tv.show()

        # Scrolled Window
        #
        self.listener_sw = Gtk.ScrolledWindow()
        self.listener_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listener_sw.is_visible = True

        #Always on bottom on change
        self.vajd = self.listener_sw.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.listener_sw: self.rescroll(a,s))

        # Add Textview to Scrolled Window
        self.listener_sw.add_with_viewport(self.listener_tv)

        self.pack_start(self.listener_sw, True, True, 0)

        # Commands Entry
        self.comm_entry = Gtk.Entry(max=0)
        self.comm_entry.set_icon_from_stock(1, Gtk.STOCK_EXECUTE)
        self.comm_entry.set_icon_from_stock(0, Gtk.STOCK_CLEAR)

        self.comm_entry.modify_base(Gtk.StateType.NORMAL, Gdk.Color(16400, 16400, 16440))
        self.comm_entry.modify_text(Gtk.StateType.NORMAL, Gdk.Color(60535, 60535, 60535, 0))

        self.pack_start(self.comm_entry, False, False, 0)

        self.show_all()

    def rescroll(self, adj, scroll):
        adj.set_value(adj.props.upper-adj.props.page_size)
        scroll.set_vadjustment(adj)

