#!/usr/bin/python

##      CGetIpbyName.py
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

name = "ipaddr"
brief_description = "Get the host's ip address"
type = "discover"

class CGetIpbyName(CIngumaModule):

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
        host = socket.gethostbyname(self.target)
        self.results[0] = host

        return True

    def printSummary(self):
        i = 0
        self.gom.echo( "Target: " + self.target + " IP Address: " + self.results[0] )
        self.gom.echo( "Adding to discovered hosts " + self.results[0] )
        self.addToDict("hosts", self.results[0])
        self.addToDict(self.results[0] + "_name", self.target)
        self.addToDict("targets", self.results[0])
        #self.addToDict(self.results[0] + "_trace", self.results[0])
        #print self.results[0]
