#!/usr/bin/python

##      XSQLExecFuzzer.py
#       
#       Copyright 2010 Joxean Koret <joxeankoret@yahoo.es>
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

from lib.module import CIngumaModule
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
