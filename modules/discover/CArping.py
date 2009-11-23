#!/usr/bin/python

"""
Module arping for Inguma based in the Scapy's implementation
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import os
import sys
import time

from lib.core import getMacVendor
from lib.libexploit import CIngumaModule

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "arping"
brief_description = "Send an arp who has message to discover hosts"
type = "discover"

class CArping(CIngumaModule):
    target = "192.168.1.0/24"
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ans = []

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"

    def getMacVendor(self, mac):
        try:
            # TODO fix get path from scapy
            #path = scapy.conf.nmap_base.replace('os-fingerprints', 'mac-prefixes')
            path = "/usr/share/nmap/nmap-mac-prefixes"
            mac = mac.replace(":", "")

            f = file(path, "r")

            for line in f:
                if line.startswith("#"):
                    pass # Ignore, just a comment
                elif line.replace(" ", "") == "":
                    pass # Ignore, blank line
                else:
                    prefix = line[0:6]
                    vendor = line[7:]

                    if mac.lower().startswith(prefix.lower()):
                        return vendor.replace("\r", "").replace("\n", "")
            
            return "Unknow"
        except:
            return "Unknow"# + str(sys.exc_info()[1])

    def arping(self, net):
        scapy.conf.verb = 0
        ans,unans = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=net),
                        filter="arp and arp[7] = 2", timeout=self.timeout)
        ret = scapy.ARPingResult(ans.res)

        flag = 0

        for x, y in ret:
            flag += 1
            ip = y.sprintf("%ARP.psrc%")
            self.gom.echo(  "Adding to discovered hosts " + ip )
            self.addToDict("hosts", ip)
            self.addToDict(ip + "_mac", y.sprintf("%Ether.src%"))
        print

        self.ans = ret
        return True

    def run(self):
        if hasScapy:
            return self.arping(self.target)
        else:
            self.gom.echo( "No scapy support :(" )
            return False

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "List of discovered hosts" )
        self.gom.echo( "------------------------" )
        self.gom.echo( "" )

        for x, y in self.ans:
            ip = y.sprintf("%ARP.psrc%")
            mac = y.sprintf("%Ether.src%")
            vendor = getMacVendor(mac)
            self.gom.echo( str(mac) + " " + str(ip).ljust(15) + "(" + str(vendor) + ")" )
        self.gom.echo( "" )


