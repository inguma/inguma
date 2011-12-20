# -*- coding: utf-8 -*-
#       toolbar.py
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
import gtk

import bokken.throbber as throbber
import lib.ui.reportWin as reportWin
import lib.ui.preferences_dialog as preferences_dialog
import lib.ui.target_dialog as target_dialog

import lib.ui.main_button as main_button
import lib.ui.menu_bar as menu_bar

class Toolbar(gtk.HBox):
    '''Main Toolbar Buttons'''

    def __init__(self, main):
        super(Toolbar,self).__init__(False, 1)

        self.main = main
        self.toolbox = self

        self.main_tb = gtk.Toolbar()
        self.main_tb.set_style(gtk.TOOLBAR_ICONS)

        # Main Button
        self.menu = menu_bar.MenuBar(self.main)

        self.menu_button = main_button.MainMenuButton("Inguma", self.menu)
        self.menu_button.set_border_width(0)

        menu_toolitem = gtk.ToolItem()

        menu_toolitem.add(self.menu_button)
        self.main_tb.insert(menu_toolitem, 0)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 1)

        # Editor button
        self.edit_tb = gtk.ToolButton(gtk.STOCK_EDIT)
        self.edit_tb.set_tooltip_text('Open editor')
        self.edit_tb.connect("clicked", self.load_editor)
        self.main_tb.insert(self.edit_tb, 2)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 3)

        # Proxy button
        self.proxy_tb = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.proxy_tb.set_tooltip_text('Start TCP proxy')
        self.proxy_tb.connect("clicked", self._miau)
        self.proxy_tb.set_sensitive(False)
        self.main_tb.insert(self.proxy_tb, 4)

        # Web server button
        self.wserver_tb = gtk.ToolButton(gtk.STOCK_CONVERT)
        self.wserver_tb.set_tooltip_text('Run web server')
        self.wserver_tb.connect("clicked", self._miau)
        self.wserver_tb.set_sensitive(False)
        self.main_tb.insert(self.wserver_tb, 5)

        # Sniffer button
        self.sniffer_tb = gtk.ToolButton(gtk.STOCK_NETWORK)
        self.sniffer_tb.set_tooltip_text('Open network sniffer')
        self.sniffer_tb.connect("clicked", self.run_sniffer)
        self.main_tb.insert(self.sniffer_tb, 6)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 7)

        # Scapy button
        self.scapy_tb = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        self.scapy_tb.set_tooltip_text('Start Scapy')
        self.scapy_tb.connect("clicked", self.show_term)
        self.main_tb.insert(self.scapy_tb, 8)

        self.scapy_logo = gtk.Image()
        self.scapy_logo.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'python-icon.png')
        self.scapy_tb.set_icon_widget(self.scapy_logo)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 9)

        # Add target button
        self.add_tb = gtk.ToolButton(gtk.STOCK_ADD)
        self.add_tb.set_tooltip_text('Add a new target')
        self.add_tb.connect("clicked", self.add_target)
        self.main_tb.insert(self.add_tb, 10)

        # Preferences button
        self.prefs_tb = gtk.ToolButton(gtk.STOCK_PREFERENCES)
        self.prefs_tb.set_tooltip_text('Open preferences dialog')
        self.prefs_tb.connect("clicked", self.show_pref)
        self.main_tb.insert(self.prefs_tb, 11)

        # Log  button
        self.log_tb = gtk.ToggleToolButton(gtk.STOCK_GOTO_BOTTOM)
        self.log_tb.set_tooltip_text('Show/Hide Log panel')
        self.log_tb.connect("toggled", self.show_log)
        self.main_tb.insert(self.log_tb, 12)

        # KB button
        self.kb_tb = gtk.ToggleToolButton(gtk.STOCK_GOTO_LAST)
        self.kb_tb.set_tooltip_text('Show/Hide KB panel')
        self.kb_tb.connect("toggled", self.show_kb)
        self.main_tb.insert(self.kb_tb, 13)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 14)

        # Report button
        self.report_tb = gtk.ToolButton(gtk.STOCK_INDEX)
        self.report_tb.set_tooltip_text('Show KB report')
        self.report_tb.connect("clicked", self.report)
        self.main_tb.insert(self.report_tb, 15)

        # Exit button
        self.exit_tb = gtk.ToolButton(gtk.STOCK_QUIT)
        self.exit_tb.connect("clicked", self._bye)
        self.exit_tb.set_tooltip_text('Have a nice day ;-)')
        self.main_tb.insert(self.exit_tb, 16)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 17)

        # Toggle Full screen
        self.full_tb = gtk.ToggleToolButton(gtk.STOCK_FULLSCREEN)
        self.full_tb.connect("toggled", self._toggle_fullscreen)
        self.full_tb.set_tooltip_text('Toggle full screen')
        self.main_tb.insert(self.full_tb, 18)


        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = gtk.ToolItem()
        self.throbber_tb.add(self.throbber)
        self.main_tb.insert(self.throbber_tb, 19)

        self.toolbox.pack_start(self.main_tb, True, True)

        self.show_all()

    #
    # Functions
    #

    # Private methods
    #
    def _bye(self, widget):
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        gtk.main_quit()
        return False

    def _miau(self):
        pass

    def disable_all(self):
        for child in self:
            try:
                if child.label.label not in ['New', 'Quit', 'About']:
                    child.set_sensitive(False)
            except:
                pass

    def enable_all(self):
        for toolbar in self:
            for child in toolbar:
                child.set_sensitive(True)

    def load_editor(self, widget):
        """ Loads module editor """

        import lib.ui.editor as editor
        editor.main()

    def add_target(self, event):

        addtgt = target_dialog.TargetDialog(self.main.uicore, self.main.gom, self.main.threadsInst, self.main.config, self.main.xdotw)

    def show_pref(self, widget):
        # FIXME: Change propWhatever to prefWhatever.
        preferences_dialog.propDialog(self.main.uicore, self.main.gom, self.main.threadsInst, self.main.config)

    def show_term(self, widget):
        self.new_tab('scapy', 'scapy')

    def run_sniffer(self, widget):
        self.new_tab('sniffer', 'tools/sniffer')

    def new_tab(self, widget, command=''):
        self.main.term_notebook.new_tab(command)
        self.main.notebook.set_current_page(1)

    def show_log(self, widget):
        ''' Show/hide log panel'''

        self.bottom_nb = self.main.bottom_nb

        if self.bottom_nb.is_visible == True:
            self.bottom_nb.hide()
            self.bottom_nb.is_visible = False

        else:
            self.bottom_nb.show()
            self.bottom_nb.is_visible = True

        if self.log_tb.get_active():
            self.log_tb.set_stock_id(gtk.STOCK_GOTO_TOP)
        else:
            self.log_tb.set_stock_id(gtk.STOCK_GOTO_BOTTOM)

    def show_kb(self, widget):
        ''' Show/hide KB panel'''

        self.scrolled_window = self.main.scrolled_window
        self.right_vbox = self.main.right_vbox
        self.treeview = self.main.treeview

        if self.scrolled_window.is_visible == True:
            self.right_vbox.hide_all()
            self.scrolled_window.is_visible = False

        else:
            self.right_vbox.show_all()
            self.treeview.updateTree()
            self.scrolled_window.is_visible = True

        if self.kb_tb.get_active():
            self.kb_tb.set_stock_id(gtk.STOCK_GOTO_FIRST)
        else:
            self.kb_tb.set_stock_id(gtk.STOCK_GOTO_LAST)

    def _toggle_fullscreen(self, widget):
        if self.full_tb.get_active():
            self.main.window.fullscreen()
            self.full_tb.set_stock_id(gtk.STOCK_LEAVE_FULLSCREEN)
        else:
            self.main.window.unfullscreen()
            self.full_tb.set_stock_id(gtk.STOCK_FULLSCREEN)

    def report(self, widget):

        reportWin.reportWin(self.main.uicore)
