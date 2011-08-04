#!/usr/bin/python

##      CPortScan.py
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

import os
import sys
import time
import socket
import random
from lib.module import CIngumaModule

try:
    from scapy.all import IP, ICMP, TCP, sr, conf, getmacbyip, get_working_if

    hasScapy = True
except:
    hasScapy = False

name = "portscan"
brief_description = "A port scanner for SYN, ACK, XMAS and SYN+ACK scans"
type = "gather"

globals = ["sport", "stype"]

class CPortScan(CIngumaModule):

    SYN_SCAN = "S"
    TCP_SCAN = None
    ACK_SCAN = "A"
    XMAS_SCAN = "SAFRC"
    SA_SCAN = "SA"

    sport = random.randint(1024, 65535)
    closed = {}
    opened = {}
    randomizeWaitTime = False
    stype = SYN_SCAN
    exploitType = 1
    results = {}
    dict = None

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "sport = <source port>"
        print "stype = <S,A>"

    def report_ports(self, target, ports):
        ans,unans = sr(IP(dst=target)/TCP(sport=self.sport, dport=ports, flags=self.stype),timeout=self.timeout, iface=self.iface)

        for s,r in ans:
            if not r.haslayer(ICMP):
                try:
                    self.mac[r.src] = getmacbyip(r.src)
                except:
                    self.mac[r.src] = "ff:ff:ff:ff:ff"
                
                self.addToDict(r.src + "_mac", self.mac[r.src])
    
                if self.stype == self.SYN_SCAN:
                    if r.payload.flags == 0x12:
                        self.opened[r.sport] = r.src
                        self.addToDict(r.src + "_tcp_ports", r.sport)
                elif self.stype == self.ACK_SCAN:
                    if s[TCP].dport == r[TCP].sport:
                        #print str(s[TCP].dport) + " is unfiltered"
                        self.opened[r.sport] = r.src
                        self.addToDict(r.src + "_tcp_ports", r.sport)

        for s,r in ans:
            if r.haslayer(ICMP):
                self.closed[r.dport] = r.dst
            elif r.payload.flags != 0x12:
                self.closed[r.dport] = r.dst

        self.results = self.opened
        return True

    def runAsWizard(self):
        #try:
        if True:
            print 
            print "Default ports"
            print "-------------"
            print
            print self.ports
            print
            res = raw_input("Range to scan (1:65535) [default ports] ")
            
            if res != "":
                if res.find(":") > -1:
                    a, b = res.split(":")
                else:
                    a = b = int(res)

                self.ports = []

                for x in range(int(a), int(b)):
                    self.ports.append(x)

            print
            print "Scan type"
            print "---------"
            print
            print " 1   SYN scan"
            print " 2   No flags scan"
            print " 3   ACK scan"
            print " 4   XMAS scan"
            print " 5   SYN+ACK scan"
            print

            res = raw_input("Scan type (numeric) [1]: ")

            if res != "":
                if res == "1":
                    self.stype = self.SYN_SCAN
                elif res == "2":
                    self.stype = self.TCP_SCAN
                elif res == "3":
                    self.stype = self.ACK_SCAN
                elif res == "4":
                    self.stype = self.XMAS_SCAN
                elif res == "5":
                    self.stype = self.SA_SCAN
                else:
                    self.stype = self.SYN_SCAN

            res = raw_input("Source port [" + str(self.sport) + "]: ")

            if res != "":
                self.sport = int(res)

        """except:
            pass"""

    def run(self):
        self.opened = {}
        self.closed = {}
        mTargets = IP(dst=self.target)
        
        if self.sport == 0:
            self.sport = random.randint(1024, 65535)

        if self.wizard:
            self.runAsWizard()

        for target in mTargets:
#            for port in self.ports:
            self.report_ports(target.dst, self.ports)

#                if self.randomizeWaitTime:
#                    mTime = random.randint(0,float(self.waitTime))
#                else:
#                    mTime = float(self.waitTime)
#
#                time.sleep(mTime)

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Portscan results" )
        self.gom.echo( "----------------" )
        self.gom.echo( "" )

        self.addToDict("hosts", self.target)
        for port in self.opened:
            try:
                port_name = socket.getservbyport(port)
                port_name = str(port) + "/" + port_name
            except:
                port_name = str(port)
                #print sys.exc_info()[1]

            self.gom.echo( "Port " + port_name + " is opened at " + self.opened[port] )

        self.gom.echo( "" )

def main():

    import sys

    objScan = CPortScan()

    if len(sys.argv) == 1:
        objScan.target = "www.google.com"
    else:
        objScan.target = sys.argv[1]
        print "Scanning",sys.argv[1],"...\n"

    if len(sys.argv) == 2:
        objScan.stype = CPortScan.SYN_SCAN
    else:
        objScan.stype = sys.argv[2]

    if len(sys.argv) == 3:
        objScan.timeout = 0.1
    else:
        objScan.timeout = float(sys.argv[3])

    curTime = time.time()
    if objScan.run():
        for port in objScan.opened:
            try:
                port_name = socket.getservbyport(opened)
                port_name = str(opened) + "/" + port_name
            except:
                port_name = str(opened)
                print sys.exc_info()[1]

            print "Port",port_name,"is open at", objScan.opened[port]

    for host in objScan.mac:
        print "\nMAC Address for",host,"is",objScan.mac[host]

    print "Scan finished in about ", str((time.time() - curTime))

if __name__ == "__main__":
    main()
