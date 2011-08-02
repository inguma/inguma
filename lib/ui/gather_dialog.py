##      gatherDialog.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
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

import sys
sys.path.append('../..')

import lib.ui.config as config

class GatherDialog(gtk.Dialog):
    '''Dialog for adding gather modules required data'''

    def __init__(self, title, stockok, options, core):
        super(GatherDialog,self).__init__(title, None, gtk.DIALOG_MODAL,
                      (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,stockok,gtk.RESPONSE_OK))

        self.set_resizable(False)
        TITLE = "Specify data for " + title

        # Core instance for manage the KB
        self.uicore = core
        self.kblist = self.uicore.get_kbList()
        # Module to be launched after insert the data
        self.module = title
        # Dict for textentry descriptions
        self.descs = config.descriptions

        # the text entries
        self.entries = []
        # kb fields
        self.titles = []
        table = gtk.Table(len(options), 2)
        table.set_row_spacings(5)
        table.set_col_spacings(5)

        for row,tit in enumerate(options):
            self.titles.append(tit)
            titlab = gtk.Label(tit.capitalize() + ":\t")
            titlab.set_alignment(0.0, 0.5)
            table.attach(titlab, 0,1,row,row+1)
            entry = gtk.Entry()
            try:
                entry.set_text( str(self.kblist[tit]) )
            except:
                pass
            table.attach(entry, 1,2,row,row+1)
            self.entries.append(entry)

            # Let's add tooltips at entries
            if self.descs.has_key(tit):
                entry.set_has_tooltip(True)
                entry.connect('query-tooltip', self.add_tooltip, self.descs[tit])
            # Let's add autocompletion
            if tit == 'target':
                self.set_completion(entry)

        self.vbox.pack_start(table)

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # the saveas button
        self.butt_saveas = self.action_area.get_children()[0]
        #self.butt_saveas.set_sensitive(False)
        self.butt_saveas.connect("clicked", self._setInputText)

        self.inputtexts = None
        self.show_all()

    def add_tooltip(self, widget, x, y, keyboard_mode, tooltip, text):
        
        tooltip.set_text(text)
        tooltip.set_icon_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        return True

    def set_completion(self, entry):
        # Seek entry EntryCompletion
        self.completion = gtk.EntryCompletion()
        self.liststore = gtk.ListStore(str)
        # Add function names to the list
        for target in self.kblist['hosts']:
            self.liststore.append([target])

        self.completion.set_model(self.liststore)
        entry.set_completion(self.completion)
        self.completion.set_text_column(0)

    def _setInputText(self, widget, close=False):
        '''Checks the entry to see if it has text.
        
        @param close: If True, the Dialog will be closed.
        '''
#        if not self._allWithText():
#            return
        self.inputtexts = [x.get_text() for x in self.entries]
        count = 0
        for tit in self.titles:
            if self.inputtexts[count].isdigit():
                self.uicore.set_kbfield(tit, int(self.inputtexts[count]))
            else:
                self.uicore.set_kbfield(tit, self.inputtexts[count])
            count += 1
        self._run_module()
        if close:
            self.response(gtk.RESPONSE_OK)

    def _allWithText(self):
        '''Checks if the entries has text.

        @return: True if all have text.
        '''
        for e in self.entries:
            if not e.get_text():
                return False
        return True

    def _run_module(self):
        self.destroy()
        # Run gather module
        self.uicore.uiRunDiscover(self.module)
