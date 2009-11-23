#!/usr/bin/python
"""
Module udpscan for Inguma
Copyright (c) 2009 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

import sys
import time
import socket
from scapy.all import *

from lib.libexploit import CIngumaModule

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
