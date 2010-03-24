#!/usr/bin/python

"""
Module Nmap Fingerprinting for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

"""
NOTE: It works depending on the moon.
"""

import os
import sys

from lib.libexploit import CIngumaModule

try:
    from scapy.modules.nmap import *

    hasScapy = True
except:
    hasScapy = False

name = "nmapfp"
brief_description = "Os detect with Nmap fingerprinting"
type = "gather"

globals = ["oport", "cport"]

class CNmapFp(CIngumaModule):

    target = ""  # Main target
    port = 0 # Port to be used
    waitTime = 0 # Time to wait between step and step
    timeout = 1 # Default timeout
    exploitType = 1
    services = {}
    results = {}
    dict = None
    oport = 80
    cport = 81
    conf.nmap_base='data/nmap-os-fingerprints'

    def help(self):
        print "target = <target host or network>"
        print "oport = <opened port>"
        print "cport = <closed port>"

    def run(self):
        if not hasScapy:
            self.gom.echo( "[!] No scapy support :( " )
            return False
        
        try:
            res = nmap_fp(target=self.target, oport = self.oport, cport = self.cport)
        except:
            self.gom.echo( "An error ocurred, may be user has not enough privileges or" )
            self.gom.echo( "Couldn't find nmap OS fingerprint DB at " + conf.nmap_base )
            return False
        self.accuracy = res[0]
        data = res[1]
        self.results = data
        self.addToDict(self.target + "_os", self.results[0])

        return True

    def printSummary(self):
        self.gom.echo( "Possible Operative System List" )
        self.gom.echo( "------------------------------" )
        self.gom.echo( "" )
        for os in self.results:
            self.gom.echo( "  " + os )
        
        self.gom.echo( "" )
        self.gom.echo( 'Accuracy: ' + str( self.accuracy * 100 ) + " %" )
        self.gom.echo( "" )
