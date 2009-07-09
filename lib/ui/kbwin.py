##      kbwin.py
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

import pygtk
import gtk, gobject

import lib.ui.core as core

class KBwindow(gtk.TextView):

    def __init__(self):
        gtk.TextView.__init__(self)
        self.uicore = core.UIcore()

        #################################################################
        # Textview
        #################################################################
        #self.textview = gtk.TextView(buffer=None)
        self.set_wrap_mode(gtk.WRAP_NONE)
        self.set_editable(False)
        # Add by default empty KB
        kb = self.uicore.get_kbcontent()
        self.textbuffer = self.get_buffer()
        #self.textbuffer.set_text('Here will appear the Knowledge base\nbut untill then, be patient\nwe are WIP :P')
        self.textbuffer.set_text(kb)

    def updateWin(self):
        '''Reads KB and updates TextView'''

        kb = self.uicore.get_kbcontent()
        #self.textbuffer = self.get_buffer()
        #print "New KB:", kb
        self.textbuffer.set_text(kb)
