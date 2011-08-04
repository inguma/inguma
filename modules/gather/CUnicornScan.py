#!/usr/bin/python

##      CUnicornScan.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import sys
import re
import os

from lib.module import CIngumaModule

name = "unicornscan"
brief_description = "A wrapper for the unicornscan tool"
type = "gather"

class CUnicornScan(CIngumaModule):
    sport = "-1"        #-B, --source-port port (-1 random by default)
    dport = ""           #-p, --ports string
    mode = ""           #-m,  --mode (U, T, A and sf for Udp scanning, Tcp scanning, Arp scanning, and Tcp Connect scannin)
    prate = ""           #[-r, --pps
    saddr = ""           #-s, --source-addr
    opened = {}
    closed = {}
    
    def help(self):

        print "target = <target host or network>"
        print "source = <source address>"
        print "port   = <target port>"
        print "sport  = <source port>"
        print "mode   = <scan mode>"
        print """          tcp (syn) scan is default, U for udp, T for tcp, 'sf' for tcp connect scan and A for arp.
          For -mT you can also specify tcp flags following the T like -mTsFpU for example
          that would send tcp syn packets with (NO Syn|FIN|NO Push|URG)"""
        print "pps    = <packets per second>"

    def run(self):
        self.opened = {}
        self.closed = {}
        
        try:
            scanres = os.popen('unicornscan ' +  self.target)
            for res in scanres.readlines():
                portmatch = re.search("[0-9]*\]", res)
                portfrom = re.search("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*", res)
                port = portmatch.group(0)[:-1]
                
                self.opened[port] = "open"
                self.addToDict(self.target + "_tcp_ports", port)
            return True
        except:
            return False

    def printSummary(self):
        print
        print "Portscan results"
        print "----------------"
        print

        for opened in self.opened:
            port_name = str(opened)
            print "Port",port_name,"is open"
        print
