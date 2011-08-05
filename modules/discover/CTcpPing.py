#!/usr/bin/python

##      CTcpPing.py
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

import os
import time
from lib.module import CIngumaModule

try:
    import scapy.all as scapy
    bHasScapy = True
except:
    bHasScapy = False

name = "tcping"
brief_description = "TCP Ping"
type = "discover"

#globals = ["packetType", ]

class CTcpPing(CIngumaModule):

    port = 80
    waitTime = 0
    up = {}
    down = {}
    timeout = 2
    exploitType = 0
    results = {}
    iface = scapy.get_working_if()
    wizard = False
    dict = None

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"
        print "waitTime = <wait time between packets>"
        print "port = <destination port to ping>"
        print "iface = <iface>"

    def run(self):
        if not bHasScapy:
            print "No scapy support :("
            return False
        self.results = {}
        self.up = {}
        self.down = {}

        if not self.port:
            self.port = 80

        target = scapy.IP(dst=self.target)
        
        self.gom.echo( "Sending probe to\t" + str(target.dst) + "\tusing port\t" + str(self.port) )
        p = scapy.IP(dst=target.dst)/scapy.TCP(dport=self.port,flags="S")

        ans, unans = scapy.sr(p, timeout=self.timeout, iface=self.iface, retry=0)

#        self.gom.echo( ans.summary( lambda(s,r) : r.sprintf("%IP.src% is alive") ) )

        if ans:
            for a in ans:
                self.up[len(self.up)+1] = a[0][0].dst
                self.addToDict("alive", a[0][0].dst)
                self.addToDict("hosts", a[0][0].dst)
                self.addToDict("targets", a[0][0].dst)
                #self.addToDict(ans[0][0].dst + "_trace", ans[0][0].dst)
#                else:
#                    self.down[len(self.up)+1] = ans[0][0].dst
#                    self.gom.echo( "Answer of type " + str(icmptypes[ans[0][0].type]) + " from " + str(ans[0][0].dst) )

        self.results = self.up
        return True
    
    def printSummary(self):
        if len(self.results) == 0:
            return

        i = 0
        self.gom.echo( "" )
        self.gom.echo( "Discovered hosts" )
        self.gom.echo( "----------------" )
        self.gom.echo( "" )

        for res in self.results:
            i += 1
            self.gom.echo( "Found host " + str(i) + "\t" + str(self.results[res]) )

        print

if __name__ == "__main__":
    import sys
    objHostUp = CHostUp()
    objHostUp.iface = "eth0"

    if len(sys.argv) == 1:
        objHostUp.target = "192.168.1.1"
    else:
        objHostUp.target = sys.argv[1]

    objHostUp.run()

    for host in objHostUp.up:
        self.gom.echo( "Host " + str(host) +" is up" )
