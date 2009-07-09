#!/usr/bin/python

"""
Module XXX for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys

from lib.libexploit import CIngumaModule

name = "example"
brief_description = "An example module"
type = "gather" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

class CExampleModule(CIngumaModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

    def help(self):
        """ This is the entry point for info <module> """
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"

    def run(self):
        """ This is the main entry point of the module """
        print "Honexek ez dau ezebe eitten, aldatu zeozer ein daian ostixe!"
        return False

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
