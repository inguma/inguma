#       menu_bar.py
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

import gtk
import gobject
import threading
import webbrowser

import lib.ui.about as about
import lib.ui.libAutosave as libAutosave

class MenuBar(gtk.Menu):
    '''Main button menu elements'''

    def __init__(self, main):
        super(MenuBar,self).__init__()

        self.main = main

        agr = gtk.AccelGroup()
        #self.main.window.add_accel_group(agr)

        # New KB item
        newi = gtk.ImageMenuItem(gtk.STOCK_NEW, agr)
        #newi.connect("activate", self.new_file)
        key, mod = gtk.accelerator_parse("<Control>N")
        newi.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        newi.set_sensitive(False)
        self.append(newi)

        # Save KB item
        savei = gtk.ImageMenuItem(gtk.STOCK_SAVE)
        savei.get_children()[0].set_label('Save')
        key, mod = gtk.accelerator_parse("<Control>S")
        savei.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        savei.connect("activate", self.save_kb)

        self.append(savei)

        # Load KB item
        loadi = gtk.ImageMenuItem(gtk.STOCK_OPEN)
        loadi.get_children()[0].set_label('Load')
        key, mod = gtk.accelerator_parse("<Control>O")
        loadi.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        loadi.connect("activate", self.load_kb)

        self.append(loadi)

        # Recent KB items
        self.manager = gtk.recent_manager_get_default()
        filter = gtk.RecentFilter()
        filter.add_pattern("*.kb")

        recent_menu = gtk.RecentChooserMenu(self.manager)
        recent_menu.add_filter(filter)

        recentm = gtk.MenuItem('Recent KB')
        recentm.set_submenu(recent_menu)
        recent_menu.connect('item-activated', self.recent_kb)

        self.append(recentm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        self.append(sep)

        # Imports: nmap, host list, w3af and burp...
        impi = gtk.ImageMenuItem(gtk.STOCK_CONVERT)
        #impi.get_children()[0].set_label('Import')
        label = impi.get_children()[0]
        label.set_markup('<b>Import</b>')
        impi.connect('activate', self.import_scan, None)

        self.append(impi)

        # Host list
        imp_hostsi = gtk.MenuItem('Host list')
        imp_hostsi.connect('activate', self.import_scan, 'csv')

        self.append(imp_hostsi)

        # Nmap scan
        imp_nmapi = gtk.MenuItem('Nmap XML')
        imp_nmapi.connect('activate', self.import_scan, 'namp')

        self.append(imp_nmapi)

        # w3af XML
        imp_w3afi = gtk.MenuItem('w3af XML')
        imp_w3afi.set_sensitive(False)

        self.append(imp_w3afi)

        # Burp XML
        imp_burpi = gtk.MenuItem('Burp XML')
        imp_burpi.set_sensitive(False)

        self.append(imp_burpi)

        # Separator
        sep = gtk.SeparatorMenuItem()
        self.append(sep)

        # Preferences
        pref_menu = gtk.Menu()
        prefm = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        prefm.set_submenu(pref_menu)

        self.append(prefm)

        # Separator
        sep = gtk.SeparatorMenuItem()
        self.append(sep)

        # Documentation
        helpi = gtk.ImageMenuItem(gtk.STOCK_HELP, agr)
        helpi.get_children()[0].set_label('Documentation')
#        key, mod = gtk.accelerator_parse("<Control>Q")
#        helpi.add_accelerator("activate", agr, key, 
#            mod, gtk.ACCEL_VISIBLE)
        helpi.connect("activate", self.show_wiki)

        self.append(helpi)

        # About item
        abouti = gtk.ImageMenuItem(gtk.STOCK_ABOUT, agr)
        key, mod = gtk.accelerator_parse("<Control>A")
        abouti.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)
        abouti.connect("activate", self.create_about_dialog)

        self.append(abouti)

        # Separator
        sep = gtk.SeparatorMenuItem()
        self.append(sep)

        # Exit item
        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("<Control>Q")
        exit.add_accelerator("activate", agr, key, 
            mod, gtk.ACCEL_VISIBLE)

        exit.connect("activate", self._bye)
        
        self.append(exit)

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

    def recent_kb(self, widget):
        """Activated when an item from the recent projects menu is clicked"""

        uri = widget.get_current_item().get_uri()
        # Strip 'file://' from the beginning of the uri
        file_to_open = uri[7:]
        self.load_kb(None, file_to_open)

    def load_kb(self, widget, file=''):

        self.gom = self.main.gom
        self.uicore = self.main.uicore
#        self.textview = self.main.textview
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
    
        # Update KB Tree
#        self.textview.updateWin()
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

    def import_scan(self, widget, type = None):
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

                # Update graph and KB tree
                self.uicore.getDot(doASN=False)
                self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
                self.gom.kbwin.updateTree()
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

    def show_wiki(self, widget):
        webbrowser.open_new_tab('http://inguma.eu/projects/inguma/wiki/Wiki')

    def create_about_dialog(self, widget):
        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
