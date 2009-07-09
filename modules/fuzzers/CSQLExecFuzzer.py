#!/usr/bin/python

"""
Module Informix SQLEXEC fuzzer for Inguma
Copyright (c) 2008 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys

from lib.libexploit import CIngumaModule
from lib.libinformix import simpleFuzzer

name = "ifxfuzz"
brief_description = "An Informix SQLEXEC fuzzer"
type = "fuzzer"

class CSQLExecFuzzer(CIngumaModule):

    def help(self):
        """ This is the entry point for info <module> """
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"

    def run(self):
        if self.target == "":
            print "[+] No target specified, using 'localhost'"
            self.target = "localhost"
        
        if self.port == 0 or self.port == None:
            print "[+] No port specified, using 9088 (sqlexec)"
            self.port = 9088
        
        return simpleFuzzer(self.target,  self.port,  self.timeout)

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
