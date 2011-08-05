#!/usr/bin/python

##      CWhois.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import os
import sys
import time
import socket

from lib.module import CIngumaModule

name = "whois"
brief_description = "Query multiple whois databases"
type = "discover"

globals = ['db', ]

class CWhois(CIngumaModule):
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False
    db = 'internic'

    def help(self):
        print "target = <target host or network>"
        print """db = <internic|ripe|arin|lacnic|apnic|afrinic>

    Internic - Internet Network Information Center
    RIPE     - Reseaux IP Europeens - Network Cooedination Centre User Link
    ARIN     - American Registry for Internet Numbers User Link
    LACNIC   - Latin America and Caribbean Network Information Centre User Link
    APNIC    - Asia Pacific Network Information Centre User Link
    AFRINIC  - African Network Information Centre User Link
    """

    def run(self, theServer=""):
        if self.timeout < 5:
            self.timeout = 5

        if not self.target:
            self.gom.echo( "No target for the query specified." )
            sys.exit()

        if not theServer:
            theServer = 'whois.' + self.db + '.net'

        socket.setdefaulttimeout(self.timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gom.echo( "Connecting to server: " + theServer + " ..." )
        s.connect((theServer, 43))
        self.gom.echo( "Connected, sending query: " + self.target + " ..." )
        s.send(self.target + "\n\n")

        self.data = ""

        while 1:
            line = s.recv(4096)
            
            if not line:
                break
            else:
                pos = line.lower().find("whois server: ")
                if pos > -1:
                    server = line[pos:]
                    server = server[14:server.find("\n")]

                    self.gom.echo( "Redirected to server %s ... " + server )
                    self.gom.echo( "" )

                    return self.run(theServer=server)

                self.data += line + "\n"

        s.close()

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "--------------------------" )
        self.gom.echo( "Whois database information" )
        self.gom.echo( "--------------------------" )
        self.gom.echo( "" )
        self.gom.echo( self.data )

