#!/usr/bin/python

"""
Module "asn" for Inguma based in the Scapy's implementation
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""
import os
import sys
import time
import socket

import scapy.all as scapy
from lib.libexploit import CIngumaModule

name = "asn"
brief_description = "ASN whois database query"
type = "discover"

class CAsnQuery(CIngumaModule):
    target = ""
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False

    def help(self):
        print "target = <target host or coma separated list of hosts>"

    def run(self):
        if self.timeout < 5:
            self.timeout = 5

        targets = []
        targets.append(self.target)

        ips = {}
        #for x in self.target:
        for x in targets:
            ips[x] = None

        ASres = scapy.conf.AS_resolver
        ASN_query_list = dict.fromkeys(map(lambda x:x.rsplit(" ",1)[0],ips)).keys()
        ASNlist = ASres.resolve(*ASN_query_list)
        self.data = ASNlist

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "------------------------" )
        self.gom.echo( "ASN database information" )
        self.gom.echo( "------------------------" )
        self.gom.echo( "" )
        for x in self.data:
            self.gom.echo( str(x[0]) + "\t" + str(x[1]) + "\t" + str(x[2]) )
            self.addToDict(str(x[0]) + "_asn", str(x[1]) + " " + str(x[2]))
    	self.gom.echo( "" )
