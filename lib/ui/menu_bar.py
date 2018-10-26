##      menu_bar.py
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

from gi.repository import GObject, Gtk
import threading
import webbrowser

import lib.ui.about as about
import lib.ui.libAutosave as libAutosave

class MenuBar(Gtk.Menu):
    '''Main button menu elements'''

    def __init__(self, main):
        super(MenuBar,self).__init__()

        self.main = main
        self.gom = self.main.gom
        self.uicore = self.main.uicore

        agr = Gtk.AccelGroup()
        #self.main.window.add_accel_group(agr)

        # New KB item
        newi = Gtk.ImageMenuItem(Gtk.STOCK_NEW, agr)
        #newi.connect("activate", self.new_file)
        key, mod = Gtk.accelerator_parse("<Control>N")
        newi.add_accelerator("activate", agr, key,
            mod, Gtk.AccelFlags.VISIBLE)
        newi.set_sensitive(False)
        self.append(newi)

        # Save KB item
        savei = Gtk.ImageMenuItem(Gtk.STOCK_SAVE)
        savei.get_children()[0].set_label('Save')
        key, mod = Gtk.accelerator_parse("<Control>S")
        savei.add_accelerator("activate", agr, key,
            mod, Gtk.AccelFlags.VISIBLE)
        savei.connect("activate", self.save_kb)

        self.append(savei)

        # Load KB item
        loadi = Gtk.ImageMenuItem(Gtk.STOCK_OPEN)
        loadi.get_children()[0].set_label('Load')
        key, mod = Gtk.accelerator_parse("<Control>O")
        loadi.add_accelerator("activate", agr, key,
            mod, Gtk.AccelFlags.VISIBLE)
        loadi.connect("activate", self.load_kb)

        self.append(loadi)

        # Recent KB items
        self.manager = Gtk.RecentManager.get_default()
        filter = Gtk.RecentFilter()
        filter.add_pattern("*.kb")

        recent_menu = Gtk.RecentChooserMenu.new_for_manager(self.manager)
        recent_menu.add_filter(filter)

        recentm = Gtk.MenuItem('Recent KB')
        recentm.set_submenu(recent_menu)
        recent_menu.connect('item-activated', self.recent_kb)

        self.append(recentm)

        # Separator
        sep = Gtk.SeparatorMenuItem()
        self.append(sep)

        # Imports: nmap, host list, w3af and burp...
        impi = Gtk.ImageMenuItem(Gtk.STOCK_CONVERT)
        #impi.get_children()[0].set_label('Import')
        label = impi.get_children()[0]
        label.set_markup('<b>Import</b>')
        impi.connect('activate', self.import_scan, None)

        self.append(impi)

        # Host list
        imp_hostsi = Gtk.MenuItem('Host list')
        imp_hostsi.connect('activate', self.import_scan, 'hosts')

        self.append(imp_hostsi)

        # Nmap scan
        imp_nmapi = Gtk.MenuItem('Nmap XML')
        imp_nmapi.connect('activate', self.import_scan, 'nmap')

        self.append(imp_nmapi)

        # w3af XML
        imp_w3afi = Gtk.MenuItem('w3af XML')
        imp_w3afi.set_sensitive(False)

        self.append(imp_w3afi)

        # Burp XML
        imp_burpi = Gtk.MenuItem('Burp XML')
        imp_burpi.set_sensitive(False)

        self.append(imp_burpi)

        # Separator
        sep = Gtk.SeparatorMenuItem()
        self.append(sep)

        # Documentation
        helpi = Gtk.ImageMenuItem(Gtk.STOCK_HELP, agr)
        helpi.get_children()[0].set_label('Documentation')
#        key, mod = Gtk.accelerator_parse("<Control>Q")
#        helpi.add_accelerator("activate", agr, key,
#            mod, Gtk.AccelFlags.VISIBLE)
        helpi.connect("activate", self.show_wiki)

        self.append(helpi)

        # About item
        abouti = Gtk.ImageMenuItem(Gtk.STOCK_ABOUT, agr)
        key, mod = Gtk.accelerator_parse("<Control>A")
        abouti.add_accelerator("activate", agr, key,
            mod, Gtk.AccelFlags.VISIBLE)
        abouti.connect("activate", self.create_about_dialog)

        self.append(abouti)

        # Separator
        sep = Gtk.SeparatorMenuItem()
        self.append(sep)

        # Exit item
        exit = Gtk.ImageMenuItem(Gtk.STOCK_QUIT, agr)
        key, mod = Gtk.accelerator_parse("<Control>Q")
        exit.add_accelerator("activate", agr, key,
            mod, Gtk.AccelFlags.VISIBLE)

        exit.connect("activate", self._bye)

        self.append(exit)

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

    def recent_kb(self, widget):
        """Activated when an item from the recent projects menu is clicked"""

        uri = widget.get_current_item().get_uri()
        # Strip 'file://' from the beginning of the uri
        file_to_open = uri[7:]
        self.load_kb(None, file_to_open)

    def load_kb(self, widget, file=''):
        '''Creates dialogs to load a KB.'''

#        import lib.globals as glob

#        self.textview = self.main.textview
        self.treeview = self.main.treeview
        self.xdotw = self.main.xdotw

        if not file:
            from lib.core import get_profile_file_path
            chooser = Gtk.FileChooserDialog(title=None,action=Gtk.FileChooserAction.OPEN, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
            chooser.set_current_folder(get_profile_file_path('data/'))
            chooser.resize(100,100)
            response = chooser.run()

            if response == Gtk.ResponseType.OK:
                res = chooser.get_filename()
                chooser.destroy()

            elif response == Gtk.ResponseType.CANCEL:
                self.gom.echo( 'Closed, no files selected', False)
                chooser.destroy()
                return False

            elif response == Gtk.ResponseType.DELETE_EVENT:
                chooser.destroy()
                return False

        else:
            res = file

        self.gom.echo( 'Loading KB...', False)
        self.gom.echo(  res + ' selected' , False)
        self.manager.add_item('file://' + res)
        #glob.kb.load(res)
        self.uicore.loadKB(res)

        # Update Map
        self.uicore.getDot(doASN=False)
        self.xdotw.set_dotcode( self.uicore.get_last_dot() )
        self.xdotw.zoom_image(1.0)
        # Update KB Tree
        self.treeview.update_tree()

        # Adding text to Log window
        self.gom.echo( 'Loaded' , False)
        self.main.kbfile = res

        # Add text to the statusbar
        self.main.statusbar._set_message(res)

    def save_kb(self, widget):
        '''Creates dialogs to save a KB.'''

        #import lib.globals as glob
        from lib.core import get_profile_file_path

        if self.main.kbfile == '':
            chooser = Gtk.FileChooserDialog(title=None,action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
            chooser.set_current_folder(get_profile_file_path('data/'))
            response = chooser.run()

            self.gom = self.main.gom
            self.uicore = self.main.uicore

            if response == Gtk.ResponseType.OK:
                filename = chooser.get_filename()
                self.uicore.saveKB(filename)
                #glob.kb.save(filename)
                self.gom.echo(filename + ' selected' , False)
                libAutosave.remove_kb()
                self.manager.add_item('file://' + filename)
                self.main.kbfile = filename
            elif response == Gtk.ResponseType.CANCEL:
                self.gom.echo('Closed, no files selected', False)
            chooser.destroy()
        else:
            self.uicore.saveKB(self.main.kbfile)
            #glob.kb.save(self.main.kbfile)
            self.gom.echo(self.main.kbfile + ' selected', False)
            libAutosave.remove_kb()

        # Add text to the statusbar
        self.main.statusbar._set_message(self.main.kbfile)

    def import_scan(self, widget, type = None, file = None):
        """ Parse and import nmap scan """

        self.gom = self.main.gom
        self.uicore = self.main.uicore
        self.xdotw = self.main.xdotw

        # Choose nmap scan file
        chooser = Gtk.FileChooserDialog(title=None,action=Gtk.FileChooserAction.OPEN, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))

        if file:
            chooser.set_filename(file)

        # Try to parse and import data
        response = chooser.run()
        filter = chooser.get_filter()
        if response == Gtk.ResponseType.OK and type == 'nmap':
            self.gom.echo( 'Loading Nmap Scan...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()

            import lib.ui.nmapParser as nmapParser
            try:
                self.gom.echo( 'Parsing scan results...', False)
                nmapData = nmapParser.parseNmap(res)
                self.gom.echo( 'Inserting data in KB...', False)
                nmapParser.insertData(self.uicore, nmapData)

                askASN = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, message_format="Resolve ASN of IP addresses?")
                askASN.set_default_response(Gtk.ResponseType.YES)
                do_asn = askASN.run()

                self.gom.echo( 'Loaded\nUpdating Graph', False)

                if do_asn == Gtk.ResponseType.YES:
                    doASN=True
                else:
                    doASN=False

                t = threading.Thread(target=self.uicore.getDot, args=(doASN,))
                t.start()

                askASN.destroy()

                GObject.timeout_add(1000, self.update_graph, t)

            except:
                md = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE, message_format="Error loading file")
                md.run()
                md.destroy()

        elif response == Gtk.ResponseType.OK and type == 'hosts':
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
                self.xdotw.set_dotcode( self.uicore.get_last_dot() )
                self.gom.kbwin.update_tree()
            except:
                print "Your lack of faith on my parsing capabilities is disturbing..."

        elif response == Gtk.ResponseType.CANCEL:
            self.gom.echo( 'Closed, no files selected', False)

        chooser.destroy()

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdotw = self.main.xdotw
            self.uicore = self.main.uicore

            self.uicore.getDot(doASN=False)
            self.xdotw.set_dotcode( self.uicore.get_last_dot() )
            self.gom.kbwin.update_tree()
            return False

    def show_wiki(self, widget):
        webbrowser.open_new_tab('http://inguma.eu/projects/inguma/wiki/Wiki')

    def create_about_dialog(self, widget):
        about_dlg = about.AboutDialog()
        dialog = about_dlg.create_dialog()

        dialog.run()
        dialog.destroy()
