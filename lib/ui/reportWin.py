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

from gi.repository import Gtk

from reports import generateReport

class reportWin(Gtk.Window):
    ''' Report output window '''

    def __init__(self, core, host=''):

        super(reportWin, self).__init__()

        self.TITLE = "Report"
        self.uicore = core
        self.host = host

        # Window properties
        self.connect("destroy", self.win_destroy)
        self.set_size_request(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title(self.TITLE)

        # VBox for Menu and Textview
        self.vbox = Gtk.VBox()

        # Menu
        self.mb = Gtk.MenuBar()

        agr = Gtk.AccelGroup()
        self.add_accel_group(agr)

        filemenu = Gtk.Menu()
        filem = Gtk.MenuItem("_File")
        filem.set_submenu(filemenu)

        savi = Gtk.ImageMenuItem(Gtk.STOCK_SAVE, agr)
        key, mod = Gtk.accelerator_parse("S")
        savi.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
        filemenu.append(savi)

        savi.connect("activate", self.save_report)

        sep = Gtk.SeparatorMenuItem()
        filemenu.append(sep)

        exit = Gtk.ImageMenuItem(Gtk.STOCK_QUIT, agr)
        key, mod = Gtk.accelerator_parse("Q")
        exit.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
        filemenu.append(exit)

        exit.connect("activate", self.win_destroy)

        self.mb.append(filem)
        # Add Menu to VBox
        self.vbox.pack_start(self.mb, False, False, 0)

        # Textview
        self.reporttv = Gtk.TextView()

        self.reporttv.set_wrap_mode(Gtk.WrapMode.NONE)
        self.reporttv.set_editable(False)
        #self.reporttv.set_cursor_visible(False)

        # Change text font
        fontdesc = Pango.FontDescription("MonoSpace 10")
        #fontdesc = Pango.FontDescription("Purisa 10")
        self.reporttv.modify_font(fontdesc)

        # Scrolled Window for Textview
        self.sw = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
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
        chooser = Gtk.FileChooserDialog(title=None,action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            file = open(filename, 'w')
            file.write(self.report_data)
            file.close()
        elif response == Gtk.ResponseType.CANCEL:
            pass
        chooser.destroy()

