#       splash.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
#       Based on code from w3af by Andres Riancho (w3af.sourceforge.net)
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

class Splash(gtk.Window):
    '''Builds the Splash window.
    
    @author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    '''
    def __init__(self):
        super(Splash,self).__init__()
        vbox = gtk.VBox()
        self.add(vbox)

        # content
        img = gtk.image_new_from_file('lib/ui/data/splash.png')
        vbox.pack_start(img)
        self.label = gtk.Label()
        vbox.pack_start(self.label)

        # color and position
        self.set_decorated(False)
        color = gtk.gdk.color_parse('#f2f2ff')
        self.modify_bg(gtk.STATE_NORMAL, color)
        self.set_position(gtk.WIN_POS_CENTER)
        #self.set_size_request(600,295)
        self.set_size_request(600,150)

        # ensure it is rendered immediately
        self.show_all()
        
        while gtk.events_pending():
            gtk.main_iteration()

    def push(self, text):
        '''New text to be shown in the Splash.'''
        self.label.set_text(text)
        while gtk.events_pending():
            gtk.main_iteration()
