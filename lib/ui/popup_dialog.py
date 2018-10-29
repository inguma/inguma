##      popup_dialog.py
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

from gi.repository import Gtk

class PopupDialog(Gtk.Window):
    '''Generic windows used as toolbar popup dialog'''

    def __init__(self, main, window, button):

        super(PopupDialog, self).__init__()

        self.connect("destroy", self._quit)

        self.eb = Gtk.EventBox()
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("black"))

        # Add an VBox to store contents
        self.set_border_width(1)
        self.vbox = Gtk.VBox(False)
        self.vbox.set_border_width(5)
        self.eb.add(self.vbox)
        self.add(self.eb)

        self.main = main
        self.win = window
        self.button = button

        # Place window at desired position below button
        x, y = self._get_coord()
        self.move(x, y)

        # Change window look
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.set_keep_above(True)
        self.set_transient_for(self.main)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        # Top content with arrow and separators
        halign = Gtk.Alignment.new(0, 1, 0, 0)
        self.arrow = Gtk.Arrow(Gtk.ArrowType.UP, Gtk.ShadowType.OUT)
        halign.add(self.arrow)

        top_left_sep = Gtk.HSeparator()
        top_left_sep.set_size_request(13, 5)
        top_right_sep = Gtk.HSeparator()
        bottom_sep = Gtk.HSeparator()

        self.top_hbox = Gtk.HBox(False)
        self.top_hbox.pack_start(top_left_sep, False, False, 0)
        self.top_hbox.pack_start(halign, False, False, 0)
        self.top_hbox.pack_start(top_right_sep, True, True, 0)

        # Add contents
        self.vbox.pack_start(self.top_hbox, False, False, 0)
        self.vbox.pack_start(bottom_sep, False, False, 0)

    def update_position(self):
        x, y = self._get_coord()
        self.move(x, y)

    def _get_coord(self):
        x, y = self.win.get_origin()
        return  x +self. button.allocation[0] - 5, y + self.button.allocation.height + 10

    def add_content(self, content):
        self.vbox.pack_start(content, False, False, 5)
        self.vbox.reorder_child(content, 1)

    def _quit(self, widget):
        #self.button.handler_block(self.button.handler)
        self.button.set_active(False)
        #self.button.handler_unblock(self.button.handler)

        self.destroy()
