#!/usr/bin/python

"""
Module "whois" for Inguma based in the Scapy's implementation
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
Some modifications by Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""
import os
import sys
import time
import socket

from lib.libexploit import CIngumaModule

name = "whois"
brief_description = "Query multiple whois databases"
type = "discover"

globals = ['db', ]

class CWhois(CIngumaModule):
    target = ""
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False
    db = 'internic'

    def help(self):
        print "target = <target host or network>"
        print """db = <internic|ripe|arin|lacnic|apnic|afrinic>

    Internic - Internet Network Information Center
    RIPE     - Reseaux IP Europeens - Network Cooedination Centre User Link
    ARIN     - American Registry for Internet Numbers User Link
    LACNIC   - Latin America and Caribbean Network Information Centre User Link
    APNIC    - Asia Pacific Network Information Centre User Link
    AFRINIC  - African Network Information Centre User Link
    """

    def run(self, theServer=""):
        if self.timeout < 5:
            self.timeout = 5

        if not self.target:
            self.gom.echo( "No target for the query specified." )
            sys.exit()

        if not theServer:
            theServer = 'whois.' + self.db + '.net'

        socket.setdefaulttimeout(self.timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gom.echo( "Connecting to server: " + theServer + " ..." )
        s.connect((theServer, 43))
        self.gom.echo( "Connected, sending query: " + self.target + " ..." )
        s.send(self.target + "\n\n")

        self.data = ""

        while 1:
            line = s.recv(4096)
            
            if not line:
                break
            else:
                pos = line.lower().find("whois server: ")
                if pos > -1:
                    server = line[pos:]
                    server = server[14:server.find("\n")]

                    self.gom.echo( "Redirected to server %s ... " + server )
                    self.gom.echo( "" )

                    return self.run(theServer=server)

                self.data += line + "\n"

        s.close()

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "--------------------------" )
        self.gom.echo( "Whois database information" )
        self.gom.echo( "--------------------------" )
        self.gom.echo( "" )
        self.gom.echo( self.data )

