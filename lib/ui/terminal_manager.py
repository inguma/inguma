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
import gtk, pango
import pwd
import psutil
import lib.ui.config as config

if config.HAS_VTE:
    import vte

window = None
notebook = None

class TerminalNotebook(gtk.Notebook):

    def __init__(self, main):
        gtk.Notebook.__init__(self)

        self.pid = None
        self.pids = []
        self.main = main

        #set the tab properties
        self.set_property('homogeneous', True)
        self.set_tab_pos(gtk.POS_BOTTOM)

        # Add a tab from the begining
        self.add_new_tab(self)

        self.show_all()

    def new_tab(self, command='', args=[]):
        hbox = gtk.HBox(False, 3)
        self.tools = gtk.VBox()
        self.tools2 = gtk.VBox()

        term = vte.Terminal()

        term.set_font(pango.FontDescription('mono 8'))
        if command:
            self.pid = term.fork_command(command=command, argv=args)
        else:
            self.pid = term.fork_command()
        self.pids.append(self.pid)
        term.set_scrollback_lines(500)
        term.set_scroll_on_output = True
        term.connect("child-exited", lambda w: term.destroy())
        term.show_all()
        self._create_term_buttons(term)
        hbox.pack_start(self.tools, False, False, 0)
        hbox.pack_start(term, True, True, 0)
        hbox.pack_start(self.tools2, False, False, 0)

        self.append_page(hbox)
        
        label = self.create_tab_label(command, hbox)
        label.show_all()
        
        image = gtk.Image()
        self.set_tab_label_packing(image, True, True, gtk.PACK_START)
        self.set_tab_label(hbox, label)
        term.show_all()

    def create_tab_label(self, title, tab_child):
        box = gtk.HBox(False, 3)
        label = gtk.Label('Terminal')
        icon = gtk.Image()
        icon.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'terminal.png')
        box.pack_start(icon, False, False)
        box.pack_start(label, True, True)
        return box

    def add_new_tab(self, widget, command=''):
        self.new_tab(command)
        self.show_all()
        self.set_current_page(-1)

    def close_tab(self, widget, child):
        box = child.get_parent()
        pagenum = self.page_num(box)
        self.pids.pop(pagenum)

        if pagenum != -1 and self.get_n_pages() > 1:
            self.remove_page(pagenum)
            child.destroy()

    def _create_term_buttons(self, term):
        self.close_button = self.load_button('cross.png',
          'Close terminal window')
        self.browse_button = self.load_button('folder.png',
          'Browse working directory')
        self.shell_button = self.load_button('terminal.png',
          'Open a shell in working directory')
        self.bookmark_button = self.load_button('star.png',
          'Bookmark working directory')
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
#          'Search for text', gtk.ToggleButton)

        self.tools2.pack_start(self.close_button, expand=False)
        self.tools.pack_start(self.browse_button, expand=False)
        self.tools.pack_start(self.shell_button, expand=False)
        self.tools.pack_start(self.bookmark_button, expand=False)
        self.tools.pack_start(self.killer_button, expand=False)
        self.tools.pack_start(self.killer_shell_button, expand=False)
        self.tools2.pack_start(self.copy_button, expand=False)
        self.tools2.pack_start(self.paste_button, expand=False)
        self.tools2.pack_start(self.selectall_button, expand=False)
        self.tools2.pack_start(self.selectnone_button, expand=False)
        #self.copy_button.set_sensitive(False)

        self.shell_button.connect('clicked', self.add_new_tab)
        self.close_button.connect('clicked', self.close_tab, term)
        self.copy_button.connect('clicked', self.copy_clipboard, term)
        self.paste_button.connect('clicked', self.paste_clipboard, term)
        self.selectall_button.connect('clicked', self.select_all, term)
        self.selectnone_button.connect('clicked', self.select_none, term)
        self.browse_button.connect('clicked', self.browse_directory, term)

    def load_button(self, icon, tip):
        button = gtk.Button()
        button.set_image(self.load_icon(icon))
        button.set_tooltip_text(tip)
        return button

    def load_icon(self, name):
        """Create an image from an icon name."""
        img = gtk.Image()
        img.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + name)
        return img

    def copy_clipboard(self, widget, term):
        term.copy_clipboard()

    def paste_clipboard(self, button, term):
        term.paste_clipboard()

    def select_all(self, button, term):
        term.select_all()

    def select_none(self, button, term):
        term.select_none()

    def browse_directory(self, button, terminal):
        tab = self.get_current_page()
        cwd = psutil.Process(self.pids[tab]).getcwd()
        self.main.file_notebook.fill_file_list(cwd)

    def get_default_shell():
        """Returns the default shell for the user"""
        # Environ, or fallback to login shell 
        return os.environ.get('SHELL', pwd.getpwuid(os.getuid())[-1])

