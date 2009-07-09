#!/usr/bin/python

"""
Module Radare for Inguma
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

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
