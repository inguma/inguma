#!/usr/bin/python

##      CProtoScan.py
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

from lib.core import getProtocolName
from lib.module import CIngumaModule

try:
    from scapy.all import sr, IP

    hasScapy = True
except:
    hasScapy = False

name = "protoscan"
brief_description = "An IP protocol scanner"
type = "gather"

class CProtoScan(CIngumaModule):

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

