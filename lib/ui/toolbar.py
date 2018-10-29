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
from gi.repository import Gtk

import bokken.throbber as throbber
import lib.ui.reportWin as reportWin
import lib.ui.preferences_dialog as preferences_dialog
import lib.ui.target_dialog as target_dialog
import lib.ui.listener_dialog as listener_dialog

import lib.ui.main_button as main_button
import lib.ui.menu_bar as menu_bar

class Toolbar(Gtk.HBox):
    '''Main Toolbar Buttons'''

    def __init__(self, main):
        super(Toolbar,self).__init__(False, 1)

        self.main = main
        self.gom = main.gom
        self.uicore = main.uicore
        self.toolbox = self
        # List to store popup dialogs
        self.popup_dialogs = []

        self.main_tb = Gtk.Toolbar()
        self.main_tb.set_style(Gtk.ToolbarStyle.ICONS)

        # Main Button
        self.menu = menu_bar.MenuBar(self.main)

        self.menu_button = main_button.MainMenuButton("Inguma", self.menu)
        self.menu_button.set_border_width(0)

        menu_toolitem = Gtk.ToolItem()

        menu_toolitem.add(self.menu_button)
        self.main_tb.insert(menu_toolitem, 0)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 1)

        # Editor button
        self.edit_tb = Gtk.ToolButton(Gtk.STOCK_EDIT)
        self.edit_tb.set_tooltip_text('Open editor')
        self.edit_tb.connect("clicked", self.load_editor)
        self.main_tb.insert(self.edit_tb, 2)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 3)

        # Proxy button
        self.proxy_tb = Gtk.ToolButton(Gtk.STOCK_CONNECT)
        self.proxy_tb.set_tooltip_text('Start TCP proxy')
        self.proxy_tb.connect("clicked", self._miau)
        self.proxy_tb.set_sensitive(False)
        self.main_tb.insert(self.proxy_tb, 4)

        # Web server button
        self.wserver_tb = Gtk.ToolButton(Gtk.STOCK_CONVERT)
        self.wserver_tb.set_tooltip_text('Run web server')
        self.wserver_tb.connect("clicked", self._miau)
        self.wserver_tb.set_sensitive(False)
        self.main_tb.insert(self.wserver_tb, 5)

        # Sniffer button
        self.sniffer_tb = Gtk.ToolButton(Gtk.STOCK_NETWORK)
        self.sniffer_tb.set_tooltip_text('Open network sniffer')
        self.sniffer_tb.connect("clicked", self.run_sniffer)
        self.main_tb.insert(self.sniffer_tb, 6)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 7)

        # Scapy button
        self.scapy_tb = Gtk.ToolButton(Gtk.STOCK_MEDIA_PLAY)
        self.scapy_tb.set_tooltip_text('Start Scapy')
        self.scapy_tb.connect("clicked", self.show_term)
        self.main_tb.insert(self.scapy_tb, 8)

        self.scapy_logo = Gtk.Image()
        self.scapy_logo.set_from_file(os.path.join('lib', 'ui', 'data', 'python-icon.png'))
        self.scapy_tb.set_icon_widget(self.scapy_logo)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 9)

        # Add target button
        self.add_tb = Gtk.ToggleToolButton(Gtk.STOCK_ADD)
        self.add_tb.set_tooltip_text('Add a new target')
        handler = self.add_tb.connect("toggled", self.add_target, self.add_tb)
        self.add_tb.handler = handler
        self.main_tb.insert(self.add_tb, 10)

        # Add new listener buttons
        self.listener_tb = Gtk.ToggleToolButton(Gtk.STOCK_DISCONNECT)
        self.listener_tb.set_tooltip_text('Create new listener')
        handler = self.listener_tb.connect("toggled", self.add_listener, self.listener_tb)
        self.listener_tb.handler = handler
        self.main_tb.insert(self.listener_tb, 11)

        # Preferences button
        self.prefs_tb = Gtk.ToggleToolButton(Gtk.STOCK_PREFERENCES)
        self.prefs_tb.set_tooltip_text('Open preferences dialog')
        handler = self.prefs_tb.connect("toggled", self.show_pref, self.prefs_tb)
        self.prefs_tb.handler = handler
        self.main_tb.insert(self.prefs_tb, 12)

#        # KB button
#        self.kb_tb = Gtk.ToggleToolButton(Gtk.STOCK_GOTO_LAST)
#        self.kb_tb.set_tooltip_text('Show/Hide KB panel')
#        self.kb_tb.connect("toggled", self.show_kb)
#        self.main_tb.insert(self.kb_tb, 13)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 13)

        # Report button
        self.report_tb = Gtk.ToolButton(Gtk.STOCK_INDEX)
        self.report_tb.set_tooltip_text('Show KB report')
        self.report_tb.connect("clicked", self.report)
        self.main_tb.insert(self.report_tb, 14)

        # Exit button
        self.exit_tb = Gtk.ToolButton(Gtk.STOCK_QUIT)
        self.exit_tb.connect("clicked", self._bye)
        self.exit_tb.set_tooltip_text('Have a nice day ;-)')
        self.main_tb.insert(self.exit_tb, 15)

        # Separator
        self.sep = Gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 16)

        # Toggle Full screen
        self.full_tb = Gtk.ToggleToolButton(Gtk.STOCK_FULLSCREEN)
        self.full_tb.connect("toggled", self._toggle_fullscreen)
        self.full_tb.set_tooltip_text('Toggle full screen')
        self.main_tb.insert(self.full_tb, 17)


        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = Gtk.ToolItem()
        self.throbber_tb.add(self.throbber)
        self.main_tb.insert(self.throbber_tb, 18)

        self.toolbox.pack_start(self.main_tb, True, True, 0)

        self.show_all()

    #
    # Functions
    #

    # Private methods
    #
    def _bye(self, widget):
        msg = ("Do you really want to quit?")
        dlg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, msg)
        dlg.set_default_response(Gtk.ResponseType.YES)
        opt = dlg.run()
        dlg.destroy()

        if opt != Gtk.ResponseType.YES:
            return True

        self.gom.echo( 'Killing all listeners', False)
        self.uicore.kill_all_listeners()
        self.uicore.remove_dot_file()
        Gtk.main_quit()
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

    def add_target(self, event, button):
        self._clean_popup_dialogs()
        if button.get_active():
            self.addtgt = target_dialog.TargetDialog(self.main, self.window, button)
            self.popup_dialogs.append(self.addtgt)
        else:
            if self.addtgt in self.popup_dialogs:
                self.popup_dialogs.remove(self.addtgt)
            self.addtgt.destroy()

    def add_listener(self, event, button):
        self._clean_popup_dialogs()
        if button.get_active():
            self.add_listener = listener_dialog.ListenerDialog(self.main, self.window, button)
            self.popup_dialogs.append(self.add_listener)
        else:
            if self.add_listener in self.popup_dialogs:
                self.popup_dialogs.remove(self.add_listener)
            self.add_listener.destroy()

    def show_pref(self, event, button):
        self._clean_popup_dialogs()
        if button.get_active():
            self.prefs_dialog = preferences_dialog.PropDialog(self.main, self.window, button)
            self.popup_dialogs.append(self.prefs_dialog)
        else:
            if self.prefs_dialog in self.popup_dialogs:
                self.popup_dialogs.remove(self.prefs_dialog)
            self.prefs_dialog.destroy()

    def _clean_popup_dialogs(self):
        if self.popup_dialogs:
            for popup in self.popup_dialogs:
                if popup in self.popup_dialogs:
                    self.popup_dialogs.remove(popup)
                popup._quit(self)

    def show_term(self, widget):
        self.new_tab('scapy', 'scapy')

    def run_sniffer(self, widget):
        self.new_tab('sniffer', 'tools/sniffer')

    def new_tab(self, widget, command=''):
        self.main.term_notebook.add_new_tab(widget, command)
        self.main.notebook.set_current_page(1)

#    def show_kb(self, widget):
#        ''' Show/hide KB panel'''
#
#        self.scrolled_window = self.main.scrolled_window
#        self.right_vbox = self.main.right_vbox
#        self.treeview = self.main.treeview
#
#        if self.scrolled_window.is_visible == True:
#            self.right_vbox.hide_all()
#            self.scrolled_window.is_visible = False
#
#        else:
#            self.right_vbox.show_all()
#            self.treeview.update_tree()
#            self.scrolled_window.is_visible = True
#
#        if self.kb_tb.get_active():
#            self.kb_tb.set_stock_id(Gtk.STOCK_GOTO_FIRST)
#        else:
#            self.kb_tb.set_stock_id(Gtk.STOCK_GOTO_LAST)

    def _toggle_fullscreen(self, widget):
        if self.full_tb.get_active():
            self.main.fullscreen()
            self.full_tb.set_stock_id(Gtk.STOCK_LEAVE_FULLSCREEN)
        else:
            self.main.unfullscreen()
            self.full_tb.set_stock_id(Gtk.STOCK_FULLSCREEN)

    def report(self, widget):

        reportWin.reportWin(self.main.uicore)
