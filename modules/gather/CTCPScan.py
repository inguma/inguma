#!/usr/bin/python

##      CTCPScan.py
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

"""
NOTE: Not directly related *BUT* an UDP scanner should be added!
"""
import sys
import time
import socket

from lib.module import CIngumaModule

name = "tcpscan"
brief_description = "Simple TCP port scanner"
type = "gather"

class CTCPScan(CIngumaModule):
    opened = {}
    closed = {}
    exploitType = 1

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"

    def run(self):
        self.opened = {}
        self.closed = {}

        try:
            totalPorts = len(self.ports)
            i = 0
            for port in self.ports:
                i += 1
                sys.stdout.write("\b"*80)
                sys.stdout.write("Scanning port %d (%d/%d)\n" % (port, i, totalPorts))
                sys.stdout.flush()

                try:
                    
                    socket.setdefaulttimeout(self.timeout)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.target, port))
                    s.close()
    
                    self.opened[port] = "open"
                    self.addToDict(self.target + "_tcp_ports", port)
                except:
                    self.closed[port] = "close"
        except KeyboardInterrupt:
            self.gom.echo( "" )
            self.gom.echo( "Cancelled." )
            return True

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Open Ports" )
        self.gom.echo( "----------" )
        self.gom.echo( "" )
        for opened in self.opened:
            try:
                port_name = socket.getservbyport(opened)
                port_name = str(opened) + "/" + port_name
            except:
                port_name = str(opened)

            self.gom.echo( "Port " + port_name + " is open" )

        self.gom.echo( "" )
