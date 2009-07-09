#!/usr/bin/python

"""
Module HexDump2 for Inguma
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

import sys
from lib.libexploit import CIngumaModule
from lib.libhexdump import Display

name = "hexedit"
brief_description = "An interactive HexDump"
type = "rce" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

globals = ['lines', ]

class CHexEdit(CIngumaModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

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

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
