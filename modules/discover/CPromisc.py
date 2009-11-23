#!/usr/bin/python

"""
Module "promisc" for Inguma based in the Scapy's implementation
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import os
import sys
import time

from lib.libexploit import CIngumaModule

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "ispromisc"
brief_description = "Check if the target is in promiscous mode"
type = "discover"

class CPromisc(CIngumaModule):
    target = "192.168.1.0/24"
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False

    def help(self):
        print "target = <target host or network>"

    def run(self):
        if hasScapy:
            self.ret = scapy.is_promisc(self.target)
            self.addToDict(self.target + "_promisc", self.ret)
            #print self.ret
            self.gom.echo( "Target " + self.target + " is promiscuous: " + str(self.ret) )

            return True
        else:
            #print "No scapy support :("
            self.gom.echo( "No scapy support :(" )
            return False

    def printSummary(self):
        pass

