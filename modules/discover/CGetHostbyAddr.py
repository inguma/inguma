#!/usr/bin/python

##      CGetHostbyAddr.py
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

import socket
from lib.libexploit import CIngumaModule

name = "hostname"
brief_description = "Get the host's name"
type = "discover"

class CGetHostbyAddr(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    exploitType = 0
    results = {}
    wizard = False
    dict = None

    def help(self):
        print "target = <target host or network>"

    def run(self):
        self.results = {}
        try:
            host = socket.gethostbyaddr(self.target)
        except:
            host = self.target

        self.results[0] = host

        return True
    
    def printSummary(self):
        self.addToDict(self.target + "_name", self.results[0][0] )
        self.gom.echo( self.target + " name: " + str(self.results[0][0]) )
