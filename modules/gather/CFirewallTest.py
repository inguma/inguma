#!/usr/bin/python

##      CFirewallTest.py
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
import scapy.all as scapy
import socket
import random

from lib.module import CIngumaModule

try:
    from scapy.all import IP, ICMP, TCP, sr, conf, getmacbyip, get_working_if

    hasScapy = True
except:
    hasScapy = False

name = "firetest"
brief_description = "A firewall testing tool"
type = "gather"

class CFirewallTest(CIngumaModule):

    SYN_SCAN = "S"
    TCP_SCAN = None
    ACK_SCAN = "A"
    XMAS_SCAN = "SAFRC"
    SA_SCAN = "SA"
    SF_SCAN = "SF"

    filtered = {}
    sport = random.randint(1024, 65535)
    scanType = SYN_SCAN
    exploitType = 1

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"
        print "iface = <interface to use>"

    def report_ports(self, target, ports):
        ans,unans = sr(IP(dst=target)/TCP(sport=self.sport, dport=ports, flags=self.scanType),timeout=self.timeout, iface=self.iface)

        for s,r in ans:
            if not r.haslayer(ICMP):
                try:
                    self.mac[r.src] = getmacbyip(r.src)
                except:
                    self.mac[r.src] = "ff:ff:ff:ff:ff"
                
                self.addToDict(r.src + "_mac", self.mac[r.src])

                if r.payload.flags == 0x12:
                    self.opened[r.sport] = r.src
                    self.gom.echo( "  Discovered open port " + str(r.sport) )
                    self.addToDict(r.src + "_tcp_ports", r.sport)

        for s,r in ans:
            if r.haslayer(ICMP):
                self.closed[r.dport] = r.dst
            elif r.payload.flags != 0x12:
                self.closed[r.dport] = r.dst

        self.results = self.opened
        return True

    def scan(self):
        mTargets = IP(dst=self.target)

        for target in mTargets:
            for port in self.ports:
                self.report_ports(target.dst, port)

                if self.randomizeWaitTime:
                    mTime = random.randint(0,float(self.waitTime))
                else:
                    mTime = float(self.waitTime)

                time.sleep(mTime)

    def run(self):
        self.opened = {}
        self.closed = {}
        self.set_om()

        self.gom.echo( "[+] Scanning for available IP protocols at " + str(self.target) )
        self.runCommand("protoscan")

        self.gom.echo( "[+] Tracing route to " + str(self.target) )
        self.runCommand("trace")

        self.gom.echo( "[+] Arpinging host " + str(self.target) )
        self.runCommand("arping")

        self.gom.echo( "[+] ICMP probes with a MTU of 16" )
        oldMTU = scapy.MTU
        scapy.MTU = 16
        self.doIcmpScan()

        self.gom.echo( "[+] Restoring to the old MTU " + str(oldMTU) )
        scapy.MTU = oldMTU

        self.gom.echo( "[+] ICMP probes" )
        self.doIcmpScan()

        self.gom.echo( "[+] TCP/IP probes" )
        self.doScan()

        for port in self.opened:
            self.gom.echo( "" )
            self.gom.echo( "Setting source port " + str(port) )
            self.sport = port
            self.doScan()
            
            self.gom.echo( "[+] Checking if port " + str(port) + " is NATed: " + str(self.runCommand("ispromisc")) )

        return True

    def doIcmpScan(self):
        packets = {
        "ECHO_REPLY":0,
        "DEST_UNREACH":3,
        "SOURCE_QUENCH":4,
        "REDIRECT":5,
        "ECHO_REQUEST":8,
        "ROUTER_ADVERTISEMENT":9,
        "ROUTER_SOLICITATION":10,
        "TIME_EXCEEDED":11,
        "PARAMETER_PROBLEM":12,
        "TIMESTAMP_REQUEST":13,
        "TIMESTAMP_REPLY":14,
        "INFORMATION_REQUEST":15,
        "INFORMATION_RESPONSE":16,
        "ADDRESS_MASK_REQUEST":17,
        "ADDRESS_MASK_REPPLY":18
        }

        for packet in packets:
            self.gom.echo( "[+] Sending packet ICMP_" + str(packet) + " ... " )
            self.runCommand("ping", {"packetType":packets[packet]})

    def doScan(self):
        self.gom.echo( "[+] SYN scan against " + str(self.target) )
        self.scan()

        self.gom.echo( "[+] SYN+FIN scan against " + str(self.target) )
        self.scanType = self.SF_SCAN
        self.scan()

        self.gom.echo( "[+] ACK scan against " + str(self.target) )
        self.scanType = self.ACK_SCAN
        self.scan()

        self.gom.echo( "[+] NULL scan (no flags) against " + str(self.target) )
        self.scanType = ""
        self.scan()

        self.gom.echo( "[+] XMAS scan against " + str(self.target) )
        self.scanType = self.XMAS_SCAN
        self.scan()

        self.gom.echo( "[+] SYN+ACK scan against " + str(self.target) )
        self.scanType = self.SA_SCAN
        self.scan()

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Firetest results" )
        self.gom.echo( "----------------" )
        self.gom.echo( "" )

        for port in self.opened:
            try:
                port_name = socket.getservbyport(port)
                port_name = str(port) + "/" + port_name
            except:
                port_name = str(port)

            self.gom.echo( "Port " + str(port_name) + " is opened at " + str(self.opened[port]) )

        self.gom.echo( "" )
