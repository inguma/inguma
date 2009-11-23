#!/usr/bin/python
"""
Module getmacaddress for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

try:
    from scapy.all import getmacbyip
    bHasScapy = True
except:
    bHasScapy = False

from lib.core import getMacVendor
from lib.libexploit import CIngumaModule

name = "getmac"
brief_description = "Get the host's MAC address"
type = "discover"

class CGetMac(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    wizard = False
    mac = ""
    dict = None

    def help(self):
        print "target = <target host or network>"

    def run(self):
        if self.target == "":
            self.gom.echo( "No target specified" )
            return False

        self.mac = getmacbyip(self.target)
        self.addToDict(self.target + "_mac", self.mac)
        self.addToDict(self.target + "_mac_vendor", getMacVendor(self.mac))
        return True
    
    def printSummary(self):
        self.gom.echo( self.target + " MAC: " + self.mac +" " + getMacVendor(self.mac) )
