##      reportWin.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import pygtk, pango
import gtk, gobject

from reports import generateReport

class reportWin(gtk.Window):
    ''' Report output window '''

    def __init__(self, core, host=''):

        super(reportWin, self).__init__()

        self.TITLE = "Report"
        self.uicore = core
        self.host = host

        # Window properties
        self.connect("destroy", self.win_destroy)
        self.set_size_request(800, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title(self.TITLE)

        # VBox for Menu and Textview
        self.vbox = gtk.VBox()

        # Menu
        self.mb = gtk.MenuBar()

        agr = gtk.AccelGroup()
        self.add_accel_group(agr)

        filemenu = gtk.Menu()
        filem = gtk.MenuItem("_File")
        filem.set_submenu(filemenu)

        savi = gtk.ImageMenuItem(gtk.STOCK_SAVE, agr)
        key, mod = gtk.accelerator_parse("S")
        savi.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        filemenu.append(savi)

        savi.connect("activate", self.save_report)

        sep = gtk.SeparatorMenuItem()
        filemenu.append(sep)

        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("Q")
        exit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        filemenu.append(exit)

        exit.connect("activate", self.win_destroy)

        self.mb.append(filem)
        # Add Menu to VBox
        self.vbox.pack_start(self.mb, False, False, 0)

        # Textview
        self.reporttv = gtk.TextView()

        self.reporttv.set_wrap_mode(gtk.WRAP_NONE)
        self.reporttv.set_editable(False)
        #self.reporttv.set_cursor_visible(False)

        # Change text font
        fontdesc = pango.FontDescription("MonoSpace 10")
        #fontdesc = pango.FontDescription("Purisa 10")
        self.reporttv.modify_font(fontdesc)

        # Scrolled Window for Textview
        self.sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.sw.add_with_viewport(self.reporttv)

        # Get KB to parse for report
        self.textbuffer = self.reporttv.get_buffer()
        if self.host:
            self.report_data = generateReport( self.uicore.get_kbList(), self.host )
        else:
            self.report_data = generateReport( self.uicore.get_kbList() )
        self.textbuffer.set_text(self.report_data)
        # Add Textview to VBox
        self.vbox.pack_start(self.sw, True, True, 0)

        # Show all
        self.add(self.vbox)
        self.show_all()

    def win_destroy(self, widget, data=None):
        self.destroy()

    def save_report(self, widget):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            file = open(filename, 'w')
            file.write(self.report_data)
            file.close()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        chooser.destroy()
        
