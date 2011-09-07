#!/usr/bin/python

##      CUDPScan.py
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

import socket
from scapy.all import *

from lib.module import CIngumaModule

name = "udpscan"
brief_description = "Simple UDP port scanner"
type = "gather"

class CUDPScan(CIngumaModule):
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
                self.gom.echo( "Scanning port " + str(port) +  " (" + str(i) + "/" + str(totalPorts) + ")" )

                ans,unans=sr(IP(dst=self.target)/UDP(dport=port))

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
