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

import gtk, gobject
import pygtk

import sys
sys.path.append('../..')
import lib.IPy as IPy

#from . import core

class GatherDialog(gtk.Dialog):
    '''Dialog for adding gather modules required data'''
    import gtk, gobject
    import pygtk

    def __init__(self, title, stockok, options, core):
        super(GatherDialog,self).__init__(title, None, gtk.DIALOG_MODAL,
                      (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,stockok,gtk.RESPONSE_OK))

        TITLE = "Specify data for " + title

        # Core instance for manage the KB
        self.uicore = core
        self.kblist = self.uicore.get_kbList()
        # Module to be launched after insert the data
        self.module = title

        # the text entries
        self.entries = []
        # kb fields
        self.titles = []
        # Numeric fields
        self.numerics = ['port', 'timeout', 'oport', 'cport']
        table = gtk.Table(len(options), 2)
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

    def _setInputText(self, widget, close=False):
        '''Checks the entry to see if it has text.
        
        @param close: If True, the Dialog will be closed.
        '''
#        if not self._allWithText():
#            return
        self.inputtexts = [x.get_text() for x in self.entries]
        count = 0
        for tit in self.titles:
            # FIXME horrible, horrible FIXME
            if self.numerics.__contains__(tit):
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
