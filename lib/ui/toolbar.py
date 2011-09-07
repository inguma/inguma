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
import gobject
import threading

import lib.ui.about as about
import bokken.throbber as throbber
import lib.ui.reportWin as reportWin
import lib.ui.preferences_dialog as preferences_dialog
import lib.ui.libAutosave as libAutosave
import lib.ui.target_dialog as target_dialog

class Toolbar(gtk.HBox):
    '''Main Toolbar Buttons'''

    def __init__(self, main):
        super(Toolbar,self).__init__(False, 1)

        self.main = main
        self.toolbox = self

        self.main_tb = gtk.Toolbar()
        self.main_tb.set_style(gtk.TOOLBAR_ICONS)

        # New KB button
        self.new_tb = gtk.ToolButton(gtk.STOCK_NEW)
        self.new_tb.set_tooltip_text('Create new KB')
        self.new_tb.connect("clicked", self._miau)
        self.main_tb.insert(self.new_tb, 0)
        self.new_tb.set_sensitive(False)

        # Load KB button
        self.load_tb = gtk.MenuToolButton(gtk.STOCK_OPEN)
        self.load_tb.set_tooltip_text('Load KB')
        self.load_tb.connect("clicked", self.load_kb)
        self.main_tb.insert(self.load_tb, 1)

        # Rcent files menu
        self.manager = gtk.recent_manager_get_default()
        self.recent_menu = gtk.RecentChooserMenu(self.manager)
        filter = gtk.RecentFilter()
        filter.add_pattern("*.kb")
        self.recent_menu.add_filter(filter)
        self.load_tb.set_menu(self.recent_menu)
        self.load_tb.set_arrow_tooltip_text('Recent opened KB')
        self.recent_menu.connect('item-activated', self.recent_kb)

        # Save KB button
        self.save_tb = gtk.ToolButton(gtk.STOCK_SAVE)
        self.save_tb.set_tooltip_text('Save current KB')
        self.save_tb.connect("clicked", self.save_kb)
        self.main_tb.insert(self.save_tb, 2)

        # Import button
        self.import_tb = gtk.ToolButton(gtk.STOCK_CONVERT)
        self.import_tb.set_tooltip_text('Import Nmap/CSV file')
        self.import_tb.connect("clicked", self.import_scan)
        self.main_tb.insert(self.import_tb, 3)

        # Editor button
        self.edit_tb = gtk.ToolButton(gtk.STOCK_EDIT)
        self.edit_tb.set_tooltip_text('Open editor')
        self.edit_tb.connect("clicked", self.load_editor)
        self.main_tb.insert(self.edit_tb, 4)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 5)

        # Proxy button
        self.proxy_tb = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.proxy_tb.set_tooltip_text('Start TCP proxy')
        self.proxy_tb.connect("clicked", self._miau)
        self.proxy_tb.set_sensitive(False)
        self.main_tb.insert(self.proxy_tb, 6)

        # Web server button
        self.wserver_tb = gtk.ToolButton(gtk.STOCK_CONVERT)
        self.wserver_tb.set_tooltip_text('Run web server')
        self.wserver_tb.connect("clicked", self._miau)
        self.wserver_tb.set_sensitive(False)
        self.main_tb.insert(self.wserver_tb, 7)

        # Sniffer button
        self.sniffer_tb = gtk.ToolButton(gtk.STOCK_NETWORK)
        self.sniffer_tb.set_tooltip_text('Open network sniffer')
        self.sniffer_tb.connect("clicked", self.run_sniffer)
        self.main_tb.insert(self.sniffer_tb, 8)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 9)

        # Scapy button
        self.scapy_tb = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        self.scapy_tb.set_tooltip_text('Start Scapy')
        self.scapy_tb.connect("clicked", self.show_term)
        self.main_tb.insert(self.scapy_tb, 10)

        self.scapy_logo = gtk.Image()
        self.scapy_logo.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'python-icon.png')
        self.scapy_tb.set_icon_widget(self.scapy_logo)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 11)

        # Add target button
        self.add_tb = gtk.ToolButton(gtk.STOCK_ADD)
        self.add_tb.set_tooltip_text('Add a new target')
        self.add_tb.connect("clicked", self.add_target)
        self.main_tb.insert(self.add_tb, 12)

        # Preferences button
        self.prefs_tb = gtk.ToolButton(gtk.STOCK_PREFERENCES)
        self.prefs_tb.set_tooltip_text('Open preferences dialog')
        self.prefs_tb.connect("clicked", self.show_pref)
        self.main_tb.insert(self.prefs_tb, 13)

        # Log  button
        self.log_tb = gtk.ToggleToolButton(gtk.STOCK_LEAVE_FULLSCREEN)
        self.log_tb.set_tooltip_text('Show/Hide Log panel')
        self.log_tb.connect("toggled", self.show_log)
        self.main_tb.insert(self.log_tb, 14)

        # KB button
        self.kb_tb = gtk.ToggleToolButton(gtk.STOCK_LEAVE_FULLSCREEN)
        self.kb_tb.set_tooltip_text('Show/Hide KB panel')
        self.kb_tb.connect("toggled", self.show_kb)
        self.main_tb.insert(self.kb_tb, 15)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.main_tb.insert(self.sep, 16)

        # Report button
        self.report_tb = gtk.ToolButton(gtk.STOCK_INDEX)
        self.report_tb.set_tooltip_text('Show KB report')
        self.report_tb.connect("clicked", self.report)
        self.main_tb.insert(self.report_tb, 17)

        # Exit button
        self.exit_tb = gtk.ToolButton(gtk.STOCK_QUIT)
        self.exit_tb.connect("clicked", self._bye)
        self.exit_tb.set_tooltip_text('Have a nice day ;-)')
        self.main_tb.insert(self.exit_tb, 18)

        # Separator
        self.sep = gtk.SeparatorToolItem()
        self.sep.set_expand(True)
        self.sep.set_draw(False)
        self.main_tb.insert(self.sep, 19)

        # About button
        self.about_tb = gtk.ToolButton(gtk.STOCK_ABOUT)
        self.about_tb.connect("clicked", self.create_about_dialog)
        self.about_tb.set_tooltip_text('About Inguma')
        self.main_tb.insert(self.about_tb, 20)

        # Throbber
        self.throbber = throbber.Throbber()
        self.throbber_tb = gtk.ToolItem()
        self.throbber_tb.add(self.throbber)
        self.main_tb.insert(self.throbber_tb, 21)

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

    def recent_kb(self, widget):
        """Activated when an item from the recent projects menu is clicked"""

        uri = widget.get_current_item().get_uri()
        # Strip 'file://' from the beginning of the uri
        file_to_open = uri[7:]
        self.load_kb(None, file_to_open)

    def load_kb(self, widget, file=''):

        self.gom = self.main.gom
        self.uicore = self.main.uicore
        self.textview = self.main.textview
        self.treeview = self.main.treeview
        self.xdotw = self.main.xdotw

        if not file:
            from lib.core import get_profile_file_path
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.set_current_folder(get_profile_file_path('data/'))
            chooser.resize(100,100)
            response = chooser.run()

            if response == gtk.RESPONSE_OK:
                res = chooser.get_filename()
                chooser.destroy()

            elif response == gtk.RESPONSE_CANCEL:
                self.gom.echo( 'Closed, no files selected', False)
                chooser.destroy()
                return False

            elif response == gtk.RESPONSE_DELETE_EVENT:
                chooser.destroy()
                return False

        else:
            res = file

        self.gom.echo( 'Loading KB...', False)
        self.gom.echo(  res + ' selected' , False)
        self.manager.add_item('file://' + res)
        self.uicore.loadKB(res)
    
        # Update KB textview
        self.textview.updateWin()
        self.treeview.updateTree()
        # Update Map
        self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
        self.xdotw.zoom_image(1.0)
    
        # Adding text to Log window
        self.gom.echo( 'Loaded' , False)
        self.main.kbfile = res

        # Add text to the statusbar
        self.main.statusbar._set_message(res)

    def save_kb(self, widget):
        from lib.core import get_profile_file_path
        if self.main.kbfile == '':
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.set_current_folder(get_profile_file_path('data/'))
            response = chooser.run()

            self.gom = self.main.gom
            self.uicore = self.main.uicore

            if response == gtk.RESPONSE_OK:
                filename = chooser.get_filename()
                self.uicore.saveKB(filename)
                self.gom.echo( filename + ' selected' , False)
                libAutosave.remove_kb()
                self.manager.add_item('file://' + filename)
                self.main.kbfile = filename
            elif response == gtk.RESPONSE_CANCEL:
                self.gom.echo( 'Closed, no files selected' , False)
            chooser.destroy()
        else:
            self.uicore.saveKB(self.main.kbfile)
            self.gom.echo( self.main.kbfile + ' selected' , False)
            libAutosave.remove_kb()

        # Add text to the statusbar
        self.main.statusbar._set_message(self.main.kbfile)

    def import_scan(self, widget):
        """ Parse and import nmap scan """

        self.gom = self.main.gom
        self.uicore = self.main.uicore
        self.xdotw = self.main.xdotw

        # Choose nmap scan file
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        
        filter = gtk.FileFilter()
        filter.set_name('Nmap scan')
        filter.add_pattern('*.xml')
        chooser.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name('Host list')
        filter.add_pattern('*.csv')
        chooser.add_filter(filter)

        # Try to parse and import data
        response = chooser.run()
        filter = chooser.get_filter()
        if response == gtk.RESPONSE_OK and filter.get_name() == 'Nmap scan':
            self.gom.echo( 'Loading Nmap Scan...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()

            import lib.ui.nmapParser as nmapParser
            try:
                self.gom.echo( 'Parsing scan results...', False)
                nmapData = nmapParser.parseNmap(res)
                self.gom.echo( 'Inserting data in KB...', False)
                nmapParser.insertData(self.uicore, nmapData)

                askASN = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Resolve ASN of IP addresses?")
                do_asn = askASN.run()

                self.gom.echo( 'Loaded\nUpdating Graph', False)

                if do_asn == gtk.RESPONSE_YES:
                    doASN=True
                else:
                    doASN=False

                t = threading.Thread(target=self.uicore.getDot, args=(doASN,))
                t.start()

                askASN.destroy()

                gobject.timeout_add(1000, self.update_graph, t)

            except:
                md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Error loading file")
                md.run()
                md.destroy()

        elif response == gtk.RESPONSE_OK and filter.get_name() == 'Host list':
            self.gom.echo( 'Loading Host list...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()
            try:
                hfile = open(res, 'r')
                hlist = hfile.readlines()
                hfile.close()
                hlist = hlist[0].split(',')

                self.gom.echo( 'Inserting data in KB...', False)
                for host in hlist:
                    self.uicore.set_kbfield('targets', host.strip())
                    self.uicore.set_kbfield('hosts', host.strip())

                # Update graph
                self.uicore.getDot(doASN=False)
                self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            except:
                print "Your lack of faith on my parsing capabilities is disturbing..."

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)

        chooser.destroy()

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdotw = self.main.xdotw
            self.uicore = self.main.uicore

            self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False

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
            self.log_tb.set_stock_id(gtk.STOCK_FULLSCREEN)
        else:
            self.log_tb.set_stock_id(gtk.STOCK_LEAVE_FULLSCREEN)

    def show_kb(self, widget):
        ''' Show/hide KB panel'''

        self.scrolled_window = self.main.scrolled_window
        self.textview = self.main.textview
        self.treeview = self.main.treeview

        if self.scrolled_window.is_visible == True:
            self.scrolled_window.hide()
            self.scrolled_window.is_visible = False

        else:
            self.scrolled_window.show()
            self.textview.updateWin()
            self.treeview.updateTree()
            self.scrolled_window.is_visible = True

        if self.kb_tb.get_active():
            self.kb_tb.set_stock_id(gtk.STOCK_FULLSCREEN)
        else:
            self.kb_tb.set_stock_id(gtk.STOCK_LEAVE_FULLSCREEN)

    def report(self, widget):

        reportWin.reportWin(self.main.uicore)

    def create_about_dialog(self, widget):
        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
