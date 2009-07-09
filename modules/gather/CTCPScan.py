#!/usr/bin/python
"""
Module tcpscan for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

"""
NOTE: Not directly related *BUT* an UDP scanner should be added!
"""
import sys
import time
import socket

from lib.libexploit import CIngumaModule

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
                sys.stdout.write("Scanning port %d (%d/%d)" % (port, i, totalPorts))
                sys.stdout.flush()

                try:
                    
                    socket.setdefaulttimeout(self.timeout)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.target, port))
                    s.close()
    
                    self.opened[port] = "open"
                    self.addToDict(self.target + "_ports", port)
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
