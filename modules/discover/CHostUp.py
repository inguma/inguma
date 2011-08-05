#!/usr/bin/python

##      CHostUp.py
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
import time
from lib.module import CIngumaModule

try:
    from scapy.all import IP, ICMP, sr, conf, getmacbyip, get_working_if, get_if_list, icmptypes
    bHasScapy = True
except:
    bHasScapy = False

name = "icmping"
brief_description = "Ping a host"
type = "discover"

globals = ["packetType", ]

class CHostUp(CIngumaModule):

    ECHO_REPLY = 0
    DEST_UNREACH = 3
    SOURCE_QUENCH = 4
    REDIRECT = 5
    ECHO_REQUEST = 8
    ROUTER_ADVERTISEMENT = 9
    ROUTER_SOLICITATION = 10
    TIME_EXCEEDED = 11
    PARAMETER_PROBLEM = 12
    TIMESTAMP_REQUEST = 13
    TIMESTAMP_REPLY = 14
    INFORMATION_REQUEST = 15
    INFORMATION_RESPONSE = 16
    ADDRESS_MASK_REQUEST = 17
    ADDRESS_MASK_REPPLY = 18

    waitTime = 0
    up = {}
    down = {}
    timeout = 2
    packetType = ECHO_REQUEST
    exploitType = 0
    results = {}
    iface = get_working_if()
    wizard = False
    dict = None

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"
        print "waitTime = <wait time between packets>"
        print "packetType = <numeric packet type> (Default to ECHO_REQUEST)"
        print "iface = <iface>"

    def runAsWizard(self):
        try:
            print
            print "Interface list"
            print "--------------"
            print
            for miface in get_if_list():
                print miface

            print

            res = raw_input("Interface [" + get_working_if() + "]: ")
            
            if res != "":
                iface = res

            res = raw_input("Timeout [" + str(self.timeout) + "]: ")

            if res != "":
                self.timeout = int(res)

        except:
            pass

    def run(self):
        if not bHasScapy:
            print "No scapy support :("
            return False
        self.results = {}
        self.up = {}
        self.down = {}

        target = IP(dst=self.target)
        
        if self.wizard:
            self.runAsWizard()

        self.gom.echo( "Sending probe to\t" + str(target.dst) )
        p = IP(dst=target.dst)/ICMP(type=self.packetType)
        ans, unans = sr(p, timeout=self.timeout, iface=self.iface, retry=0)

        if ans:
            for a in ans:
                if a[0][0].type == 8:
                    self.up[len(self.up)+1] = a[0][0].dst
                    self.addToDict("alive", a[0][0].dst)
                    self.addToDict("hosts", a[0][0].dst)
                    self.addToDict("targets", a[0][0].dst)
                    #self.addToDict(ans[0][0].dst + "_trace", a[0][0].dst)
                else:
                    self.down[len(self.up)+1] = a[0][0].dst
                    self.gom.echo( "Answer of type " + str(icmptypes[a[0][0].type]) + " from " + str(a[0][0].dst) )

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
