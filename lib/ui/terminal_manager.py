##      terminal_manager.py
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
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
from gi.repository import GObject, Gtk, Pango
import pwd
import psutil

import lib.ui.config as config
import lib.ui.listener_shell as listener_shell

if config.HAS_VTE:
    from gi.repository import Vte

window = None
notebook = None

class TerminalNotebook(Gtk.Notebook):

    def __init__(self, main):
        GObject.GObject.__init__(self)

        self.pid = None
        self.pids = []
        self.main = main

        #set the tab properties
        # The 'homogeneous' property has been removed in GTK+3.
        #self.set_property('homogeneous', True)
        self.set_tab_pos(Gtk.PositionType.BOTTOM)

        # Add a tab from the begining
        self.add_new_tab(self)
        GObject.timeout_add(500, self._update_cwd)
        self.show_all()

        ####################### FIXME ###########################
#        # Just for testing!!! WILL BE REMOVED
#        self.l_shell = listener_shell.ListenerShell()
#        self.append_page(self.l_shell)
#
#        label = self.create_tab_label('Listener shell', self.l_shell)
#        label.show_all()
#
#        image = Gtk.Image()
#        self.set_tab_label_packing(image, True, True, Gtk.PACK_START)
#        self.set_tab_label(self.l_shell, label)
        ####################### FIXME ###########################

    def new_tab(self, command='', cwd='', args=[]):
        hbox = Gtk.HBox(False, 3)
        self.tools = Gtk.VBox(False)
        self.tools2 = Gtk.VBox(False)

        # FIXME!!!!! Terminals are broken!!
        return
        # FIXME: Even when vte is not present, this is still called (and causes an error).
        term = Vte.Terminal()

        term.set_font(Pango.FontDescription('mono 8'))
        term.set_pty(Vte.Pty())
        term.connect("child-exited", self.on_terminal_child_exit)
        if command:
            self.pid = term.pty.spawn_async(command=command, argv=args, working_directory=cwd)
        else:
            self.pid = term.pty.spawn_async(working_directory=cwd)
        self.pids.append(self.pid)
        term.set_scrollback_lines(1000)
        term.set_scroll_on_output = True
        term.set_size_request(200,200)
        term.show_all()
        self._create_term_buttons(term)
        hbox.pack_start(self.tools, False, False, 0)
        hbox.pack_start(term, True, True, 0)
        hbox.pack_start(self.tools2, False, False, 0)

        self.append_page(hbox)

        label = self.create_tab_label(command, hbox)
        label.show_all()

        image = Gtk.Image()
        self.set_tab_label_packing(image, True, True, Gtk.PACK_START)
        self.set_tab_label(hbox, label)
        term.show_all()
        if self.get_current_page() == -1:
            GObject.timeout_add(500, self._update_cwd)

    def create_tab_label(self, title, tab_child):
        box = Gtk.HBox(False, 1)
        # Tab text label
        #label = Gtk.Label(label='Terminal')
        label = Gtk.Label(label=title)
        small = Pango.AttrScale(Pango.SCALE_SMALL, 0, -1)
        label_attributes = Pango.AttrList()
        label_attributes.insert(small)
        label.set_attributes(label_attributes)
        label.set_ellipsize(Pango.EllipsizeMode.START)
        label.set_width_chars(9)

        # Tab terminal icon
        icon = Gtk.Image()
        icon.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'terminal.png'))
        # Tab pseudo-close button
        eb = Gtk.EventBox()
        cross = Gtk.Image()
        cross.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', 'cross.png'))
        cross.connect("realize", self._realize_cb)
        eb.add(cross)
        eb.connect('button_press_event', self.close_tab)

        # Pack en return the box
        box.pack_start(icon, False, False)
        box.pack_start(label, True, True)
        box.pack_start(eb, True, True)
        return box

    def _realize_cb(self, widget):
        """ method used to change mouse cursor for close pseudo-button """
        hand = Gdk.Cursor.new(Gdk.HAND2)
        widget.window.set_cursor(hand)

    def add_new_tab(self, widget, command='', cwd=''):
        self.new_tab(command, cwd=cwd)
        self.show_all()
        self.set_current_page(-1)
        self._update_cwd()

    def close_tab(self, widget, event):
        pagenum = self.get_current_page()
        tab = self.get_nth_page(pagenum)
        child = tab.get_children()

        if pagenum != -1 and self.get_n_pages() > 1:
            self.remove_page(pagenum)
            self.pids.pop(pagenum)
            # Destroy terminal
            child[1].destroy()

    def _create_term_buttons(self, term):
        self.browse_button = self.load_button('folder.png',
          'Browse working directory')
        self.shell_button = self.load_button('terminal.png',
          'Open a shell in working directory')
        self.bookmark_button = self.load_button('star.png',
          'Bookmark working directory')
        self.bookmark_button.set_sensitive(False)
        self.killer_button = self.load_button(
          'script_lightning.png', 'Send signal to children')
        self.killer_shell_button = self.load_button(
          'application_lightning.png', 'Send signal to shell')
        self.copy_button = self.load_button('page_white_copy.png',
          'Copy selection')
        self.paste_button = self.load_button('paste_plain.png',
          'Paste clipboard')
        self.selectall_button = self.load_button('textfield_add.png',
          'Select all')
        self.selectnone_button = self.load_button('textfield_delete.png',
          'Select None')
#        self.find_button = self.load_button('find.png',
#          'Search for text', Gtk.ToggleButton)

        self.tools.pack_start(self.browse_button, False, True, 0)
        self.tools.pack_start(self.shell_button, False, True, 0)
        self.tools.pack_start(self.bookmark_button, False, True, 0)
        self.tools.pack_start(self.killer_button, False, True, 0)
        self.tools.pack_start(self.killer_shell_button, False, True, 0)
        self.tools2.pack_start(self.copy_button, False, True, 0)
        self.tools2.pack_start(self.paste_button, False, True, 0)
        self.tools2.pack_start(self.selectall_button, False, True, 0)
        self.tools2.pack_start(self.selectnone_button, False, True, 0)
        #self.copy_button.set_sensitive(False)

        self.create_killer()

        self.shell_button.connect('clicked', self.add_new_tab)
        self.copy_button.connect('clicked', self.copy_clipboard, term)
        self.paste_button.connect('clicked', self.paste_clipboard, term)
        self.selectall_button.connect('clicked', self.select_all, term)
        self.selectnone_button.connect('clicked', self.select_none, term)
        self.browse_button.connect('clicked', self.browse_directory, term)
        self.killer_button.connect('button-press-event', self.on_killer_button__button_press_event)
        self.killer_shell_button.connect('button-press-event', self.on_killer_shell_button__button_press_event)

    def create_killer(self):
        self.killer_menu = Gtk.Menu()
        signums = [
            ('SIGTERM', 15),
            ('SIGKILL', 9),
            ('SIGINT', 2),
            ('SIGABRT', 6),
        ]
        for signame, signum in signums:
            menuitem = Gtk.MenuItem()
            menuitem.set_label('{0} ({1})'.format(signame, signum))
            self.killer_menu.append(menuitem)
            menuitem.set_data('signum', signum)
            menuitem.connect('activate', self.on_killer_activate)
        self.killer_menu.show_all()
        self.killer_shell_menu = Gtk.Menu()
        for signame, signum in signums:
            menuitem = Gtk.MenuItem()
            menuitem.set_label('{0} ({1})'.format(signame, signum))
            self.killer_shell_menu.append(menuitem)
            menuitem.set_data('signum', signum)
            menuitem.connect('activate', self.on_killer_shell_activate)
        self.killer_shell_menu.show_all()

    def load_button(self, icon, tip):
        button = Gtk.Button()
        button.set_image(self.load_icon(icon))
        button.set_tooltip_text(tip)
        return button

    def load_icon(self, name):
        """Create an image from an icon name."""
        img = Gtk.Image()
        img.set_from_file(os.path.join('lib', 'ui', 'data', 'icons', name))
        return img

    def copy_clipboard(self, widget, term):
        term.copy_clipboard()

    def paste_clipboard(self, button, term):
        term.paste_clipboard()

    def select_all(self, button, term):
        term.select_all()

    def select_none(self, button, term):
        term.select_none()

    def _update_cwd(self):
        """Calculate and update the CWD for the running process."""
        pagenum = self.get_current_page()
        if pagenum > -1:
            pid = self.pids[pagenum]
            if pid is None:
                # The return value indicates whether gobject should continue polling.
                return False
            else:
                try:
                    cwd = psutil.Process(pid).getcwd()
                    tab = self.get_nth_page(pagenum)
                    box = self.get_tab_label(tab)
                    label = box.get_children()[1]
                    label.set_text(cwd)
                    return True
                except psutil.error.AccessDenied:
                    # The process already vanished
                    return False

    def browse_directory(self, button, terminal):
        tab = self.get_current_page()
        cwd = psutil.Process(self.pids[tab]).getcwd()
        self.main.file_notebook.fill_file_list(cwd)

    def on_killer_button__button_press_event(self, button, event):
        self.killer_menu.popup(None, None, None, event.button, event.time)

    def on_killer_shell_button__button_press_event(self, button, event):
        self.killer_shell_menu.popup(None, None, None, event.button, event.time)

    def on_killer_activate(self, menuitem):
        signum = menuitem.get_data('signum')
        pid = self.pids[self.get_current_page()]
        for child in psutil.Process(pid).get_children():
            child.send_signal(signum)

    def on_killer_shell_activate(self, menuitem):
        signum = menuitem.get_data('signum')
        pid = self.pids[self.get_current_page()]
        psutil.Process(pid).send_signal(signum)

    def on_terminal_child_exit(self, terminal):
        box = terminal.get_parent()
        pagenum = self.page_num(box)

#        if pagenum != -1 and self.get_n_pages() > 1:
        self.remove_page(pagenum)
        self.pids.pop(pagenum)
        terminal.destroy()

    def get_default_shell():
        """Returns the default shell for the user"""
        # Environ, or fallback to login shell
        return os.environ.get('SHELL', pwd.getpwuid(os.getuid())[-1])

