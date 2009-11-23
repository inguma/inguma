#!/usr/bin/python
"""
Module Fake ARP Server for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""


try:
    from scapy.all import get_if_addr, get_working_if, farpd, conf
    bHasScapy = True
except:
    bHasScapy = False

from lib.core import getMacVendor
from lib.libexploit import CIngumaModule

name = "fakearp"
brief_description = "Fake ARP server"
type = "gather"

globals = ["interval", ]

class CFakeArpServer(CIngumaModule):

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
        conf.verb = 2
        self.address = get_if_addr(get_working_if())
        self.gom.echo( "[+] Using " + str(self.address) )
        farpd()
        return True
    
    def printSummary(self):
        pass
