#!/usr/bin/python

"""
Module protoscan for Inguma based in the Scapy's implementation
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import os
import sys
import time
import socket
import random

from lib.core import getProtocolName
from lib.libexploit import CIngumaModule

try:
    from scapy.all import sr, IP

    hasScapy = True
except:
    hasScapy = False

name = "protoscan"
brief_description = "An IP protocol scanner"
type = "gather"

class CProtoScan(CIngumaModule):

    target = ""
    exploitType = 1
    results = {}
    protocols = []
    dict = None

    def help(self):
        print "target = <target host or network>"

    def run(self):
        try:
            a, u = sr(IP(dst=self.target, proto=(1, 254)), timeout=self.timeout)
        except:
            self.gom.echo( "protoscan: " + str(sys.exc_info()[1]) )
            return False

        for x in u:
            self.addToDict(self.target + "_protocols", x.proto)
            self.protocols.append([self.target, x.proto])

        self.protocols.sort()
        
        if len(self.protocols) == 254:
            self.gom.echo( "[!] Target appears to have all protocols enabled!" )
            return False

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Protocol scan results" )
        self.gom.echo( "---------------------" )
        self.gom.echo( "" )

        for x in self.protocols:
            self.gom.echo( "Protocol " + str(getProtocolName(x[1])) + " enabled at " + str(x[0]) )

        self.gom.echo( "" )

