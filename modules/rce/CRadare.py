#!/usr/bin/python

##      CRadare.py
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

import sys

from lib.libexploit import CIngumaModule
from lib.libradare import *

name = "radare"
brief_description = "A simple wrapper for Radare"
type = "rce"

globals = ['debug', 'gui',]

class CRadare(CIngumaModule):

    target = ""
    debug = False
    gui = False

    def help(self):
        """ This is the entry point for info <module> """
        print "target = <target binary>"
        print "debug = <True|False>"
        print "gui = <True|False>"

    def run(self):
        """ This is the main entry point of the module """
        r = Radare()
        r.radare(self.target, self.debug, self.gui)
        return False

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
