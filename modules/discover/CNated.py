#!/usr/bin/python

##      CNated.py
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

from lib.libexploit import CIngumaModule

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "isnated"
brief_description = "Check if the target's port is NATed"
type = "discover"

class CNated(CIngumaModule):
    target = "192.168.1.0/24"
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False
    probeResults = {}

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"

    def probeICMP(self):
        p = IP(dst=self.target)/ICMP()
        res = sr1(p, timeout = self.timeout)
        hops = None

        if res:
            hops = res.ttl
        
        self.probeResults["ICMP"] = hops
        return hops
    
    def probeTcpPort(self, port):
        p = IP(dst=self.target)/TCP(dport=int(port), flags="S")
        res = sr1(p, timeout = self.timeout)
        hops = None

        if res:
            hops = res.ttl

        self.probeResults[port] = hops
        return hops

    def isNatedPort(self, port):
        icmpTtl = self.probeICMP()
        tcpTtl = self.probeTcpPort(port)
        
        if icmpTtl != tcpTtl and icmpTtl != None and tcpTtl != None:
            return True

    def checkIsNated(self):
        ttls = []
        res = self.probeICMP() # Do it just one time
        
        if res:
            ttls.append(res)

        for port in self.dict[self.target + "_tcp_ports"]:
            res = self.probeTcpPort(port)
            
            if res:
                ttls.append(res)
        
        minTtl = min(ttls)
        maxTtl = max(ttls)
        
        if minTtl != maxTtl:
            self.gom.echo( "Ports are NATed" )
            return True
        else:
            self.gom.echo( "Ports are NOT NATed" )
            return False

    def run(self):
        if hasScapy:
            if self.port == 0:
                if self.dict.has_key(self.target + "_tcp_ports"):
                    return self.checkIsNated()
                else:
                    self.gom.echo( "Can't check NATed ports for " + self.target + " without ports scanned" )
                    self.gom.echo( "Perform a portscan or tcpscan over " + self.target )
            else:
                if self.isNatedPort(self.port):
                    self.gom.echo( "Port " + self.port + " is NATed" )
                else:
                    self.gom.echo( "Port " + self.port + " is NOT NATed" )

            return True
        else:
            self.gom.echo( "No scapy support :(" )
            return False

    def printSummary(self):
        for res in self.probeResults:
            if res == "ICMP":
                if self.probeResults[res]:
                    self.gom.echo( "ICMP TTL: " + str(self.probeResults[res]) )
                else:
                    self.gom.echo( "Target refuses ICMP traffic" )
            else:
                self.gom.echo( "TCP Port " + res + " TTL: " + self.probeResults[res] )

