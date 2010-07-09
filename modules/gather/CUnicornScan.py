#!/usr/bin/python

"""
Module Unicornscan for Inguma
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

    2007??? Are you sure Hugo? ;)

License is GPL
"""

import sys
import re
import os

from lib.libexploit import CIngumaModule

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
