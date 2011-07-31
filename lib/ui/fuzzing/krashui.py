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

import gtk

class KrashUI(gtk.Frame):
    def __init__(self):
        super(KrashUI,self).__init__()

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
#        self.file_sw.set_size_request(75,225)

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
        self.health_label = gtk.Label('Disable health: ')
        self.health_label.set_alignment(0, 0.5)

        self.third_hbox.pack_start(self.verbose_label, True, True, 0)
        self.third_hbox.pack_start(self.url_label, True, True, 0)
        self.third_hbox.pack_start(self.health_label, True, True, 0)

        # 4th VBox for Flags
        self.fourth_hbox = gtk.VBox(False, 1)

        self.verbose_check = gtk.CheckButton(label=None, use_underline=False)
        self.url_check = gtk.CheckButton(label=None, use_underline=False)
        self.health_check = gtk.CheckButton(label=None, use_underline=False)

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
        self.start.set_size_request(60, 30)
        self.stop = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_STOP)
        self.stop.set_size_request(60, 30)

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

        self.buttons_hbox.pack_start(self.buttons_left_hbox)
        self.buttons_hbox.pack_start(self.halign)

        self.vbox.pack_start(self.buttons_hbox, False, False, 3)

        self.add(self.vbox)
