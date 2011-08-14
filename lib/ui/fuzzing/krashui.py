##      krashui.py
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
import threading

import lib.krash as krash

class KrashUI(gtk.Frame):
    def __init__(self, ip_entry, port_entry):
        super(KrashUI,self).__init__()

        self.ip_entry = ip_entry
        self.port_entry = port_entry

        self.label = gtk.Label()
        quote = "<b>Krash Fuzzer</b>"
        self.label.set_markup(quote)
        self.set_label_widget(self.label)

        # VBox
        self.vbox = gtk.VBox(False, 2)

        # HBox for file selection entry and button
        self.file_hbox = gtk.HBox(False, 2)

        # File selector
        self.info_hbox = gtk.HBox(False, 2)
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.file_label = gtk.Label('Step 2: Select a file:')
        self.file_label.set_padding(0, 3)
        self.info_hbox.pack_start(self.info, False, False, 2)
        self.info_hbox.pack_start(self.file_label, False, False, 2)

        self.vbox.pack_start(self.info_hbox, False, False, 2)

        self.filechooserbutton = gtk.FileChooserButton('Select a file', backend=None)
        self.filechooserbutton.set_current_folder('krash/audits/')
        self.filechooserbutton.connect('selection-changed', self._new_file)

        self.vbox.pack_start(self.filechooserbutton, False, False, 2)

        # File editor
        self.info2_hbox = gtk.HBox(False, 2)
        self.info2 = gtk.Image()
        self.info2.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.edit_label = gtk.Label('Step 3: If necessary, edit the selected file:')
        self.edit_label.set_alignment(0.01, 0.5)
        self.info2_hbox.pack_start(self.info2, False, False, 2)
        self.info2_hbox.pack_start(self.edit_label, False, False, 2)
        self.vbox.pack_start(self.info2_hbox, False, False, 2)

        self.file_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.file_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.file_text = gtk.TextView()
        self.file_text.set_editable(True)
        self.file_text.set_wrap_mode(gtk.WRAP_NONE)
        self.file_text.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(16400, 16400, 16440))
        self.file_text.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(60535, 60535, 60535, 0))

        self.file_sw.add(self.file_text)
        self.vbox.pack_start(self.file_sw, True, True, 2)

        self.hseparator = gtk.HSeparator()
        self.vbox.pack_start(self.hseparator, False, False, 2)

        # HBox for Flags
        self.flags_hbox = gtk.HBox(False, 10)

        # 1st VBox for Flags
        self.first_hbox = gtk.VBox(False, 1)

        self.index_label = gtk.Label('Start Index:')
        self.line_label = gtk.Label('Line mode: ')
        self.ssl_label = gtk.Label('SSL mode: ')

        self.first_hbox.pack_start(self.index_label, True, True, 0)
        self.first_hbox.pack_start(self.line_label, True, True, 0)
        self.first_hbox.pack_start(self.ssl_label, True, True, 0)

        # 2nd VBox for Flags
        self.second_hbox = gtk.VBox(False, 1)

        self.index_adj = gtk.Adjustment(value=0, lower=0, upper=10000, step_incr=1, page_incr=10, page_size=0)
        self.index_spin = gtk.SpinButton(adjustment=self.index_adj, climb_rate=0.0, digits=0)
        self.index_spin.set_max_length(5)
        self.line_check = gtk.CheckButton(label=None, use_underline=False)
        self.ssl_check = gtk.CheckButton(label=None, use_underline=False)

        self.second_hbox.pack_start(self.index_spin, True, True, 0)
        self.second_hbox.pack_start(self.line_check, True, True, 0)
        self.second_hbox.pack_start(self.ssl_check, True, True, 0)

        # 3rd VBox for Flags
        self.third_hbox = gtk.VBox(False, 1)

        self.verbose_label = gtk.Label('Verbosity: ')
        self.verbose_label.set_alignment(0, 0.5)
        self.url_label = gtk.Label('URL mode: ')
        self.url_label.set_alignment(0, 0.5)
        self.health_label = gtk.Label('Health checks: ')
        self.health_label.set_alignment(0, 0.5)

        self.third_hbox.pack_start(self.verbose_label, True, True, 0)
        self.third_hbox.pack_start(self.url_label, True, True, 0)
        self.third_hbox.pack_start(self.health_label, True, True, 0)

        # 4th VBox for Flags
        self.fourth_hbox = gtk.VBox(False, 1)

        self.verbose_check = gtk.CheckButton(label=None, use_underline=False)
        self.verbose_check.set_active(True)
        self.url_check = gtk.CheckButton(label=None, use_underline=False)
        self.health_check = gtk.CheckButton(label=None, use_underline=False)
        self.health_check.set_sensitive(False)

        self.fourth_hbox.pack_start(self.verbose_check, True, True, 0)
        self.fourth_hbox.pack_start(self.url_check, True, True, 0)
        self.fourth_hbox.pack_start(self.health_check, True, True, 0)

        # Pack VBoxes into Flags HBox
        self.flags_hbox.pack_start(self.first_hbox, False, False, 5)
        self.flags_hbox.pack_start(self.second_hbox, False, False, 5)
        self.flags_hbox.pack_start(self.third_hbox, False, False, 5)
        self.flags_hbox.pack_start(self.fourth_hbox, True, True, 5)

        self.vbox.pack_start(self.flags_hbox, False, False, 1)

###################################################################################

        self.hseparator = gtk.HSeparator()
        self.vbox.pack_start(self.hseparator, False, False, 2)

        # HBoxes for buttons
        self.buttons_hbox = gtk.HBox(False, 3)
        self.buttons_left_hbox = gtk.HBox(False, 3)
        self.buttons_right_hbox = gtk.HBox(True, 1)

        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 4: Start fuzzing!')
        self.desc_label.set_padding(0, 4)
        self.buttons_left_hbox.pack_start(self.info, False, False, 2)
        self.buttons_left_hbox.pack_start(self.desc_label, False, False, 2)

        # Start/stop buttons
        self.start = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_PLAY)
        self.start_image = gtk.Image()
        self.start_image.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
        self.start.set_size_request(60, 30)
        self.start.connect('clicked', self._get_flags)
        self.stop = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_STOP)
        self.stop.set_size_request(60, 30)
        self.stop.connect('clicked', self._stop_fuzzing)

        # Remove labels from buttons... sigh
        label = self.start.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')
        label = self.stop.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')

        self.buttons_right_hbox.add(self.start)
        self.buttons_right_hbox.add(self.stop)
        self.halign = gtk.Alignment(0.97, 0, 0, 0)
        self.halign.add(self.buttons_right_hbox)

        # Throbber image
        self.throbber = gtk.Image()
        self.img_path = 'lib' + os.sep + 'ui' + os.sep + 'data' + os.sep
        self.throbber.set_from_file(self.img_path + 'throbber_animat_small.gif')

        self.buttons_hbox.pack_start(self.buttons_left_hbox)
        self.buttons_hbox.pack_start(self.halign)

        self.vbox.pack_start(self.buttons_hbox, False, False, 3)

        self.add(self.vbox)

    def _stop_fuzzing(self, widget):

        self.krashlib.stop = True

        # Change start button image
        self.start.set_image(self.start_image)
        self.start.set_use_stock(True)
        label = self.start.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')

    def _new_file(self, filechooser):
        filename = filechooser.get_filename()
        if filename:
            f = file(filename, 'r')
            file_contents = f.read()
            f.close()
            buffer = self.file_text.get_buffer()
            buffer.set_text(file_contents)

    def _get_flags(self, widget):

        self.target = self.ip_entry.get_text()
        self.port = self.port_entry.get_text()

        if not self.target or not self.port:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "Fill IP address and Port entries")
            md.run()
            md.destroy()
        else:
            self.bottom_nb.set_current_page(0)
            buffer = self.file_text.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            text = buffer.get_text(start_iter, end_iter)
            if text:
                # Change start button image
                self.start.set_image(self.throbber)
                label = self.start.get_children()[0]
                label = label.get_children()[0].get_children()[1]
                label = label.set_label('')

                if not self.gom:
                    self.gom = gom

                self.krashlib = krash.KrashLib(self.gom)

                # Parse flags
                self.sindex = self.index_spin.get_digits()
                self.krashlib.line_mode = self.line_check.get_active()
                self.krashlib.url_mode = self.url_check.get_active()
                self.krashlib.ssl_mode = self.ssl_check.get_active()
                self.krashlib.verbose = self.verbose_check.get_active()

                # Go go go!
                self.krashlib.stop = False
                t = threading.Thread(target=self.krashlib.fuzz, args=(text, self.target, self.port, self.sindex))
                t.start()
            else:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "Select a file")
                md.run()
                md.destroy()

