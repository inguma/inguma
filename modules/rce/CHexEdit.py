##      CHexEdit.py
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

from lib.module import CIngumaRCEModule
from lib.libhexdump import Display

name = "hexedit"
brief_description = "An interactive HexDump"
type = "rce"

globals = ['lines', ]

class CHexEdit(CIngumaRCEModule):

    def help(self):
        """ This is the entry point for info <module> """
        print "target = < Target file >"
        print "lines = <Lines per page of dump>"

    def run(self):
        """ This is the main entry point of the module """
        d = Display()
        d.file = self.target
        d.SetClear()
        d.lines = 40
        d.Process()
