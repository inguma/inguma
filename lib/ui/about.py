#       about.py
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

class AboutDialog():
    '''About dialog'''

    def create_dialog(self):
        from lib.core import get_inguma_version

        about = gtk.AboutDialog()
        about.set_program_name("Inguma")
        about.set_version(get_inguma_version())
        about.set_copyright("(c) 2006-2008 Joxean Koret <joxeankoret@yahoo.es>\n"+
                "(c) 2009-2011 Hugo Teso <hteso@inguma.eu>")
        about.set_comments("A penetration testing and vulnerability research toolkit")
        about.set_website("http://inguma.eu")
        about.set_authors(['Hugo Teso <hteso@inguma.eu>', 'David Martinez Moreno <ender@inguma.eu>'])
        about.set_artists(['Ana Muniesa <ana.muniesa@gmail.com>', 'Juanje <juanje@gmail.com>', ' * Web: http://www.puntodepartida.com'])
        about.set_logo(gtk.gdk.pixbuf_new_from_file("lib" + os.sep + "ui" + os.sep + "data" + os.sep + "logo.png"))
        about.set_modal(True)

        return about
