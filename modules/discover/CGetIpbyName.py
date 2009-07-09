#!/usr/bin/python
"""
Module ipaddr for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import socket

from lib.libexploit import CIngumaModule

name = "ipaddr"
brief_description = "Get the host's ip address"
type = "discover"

class CGetIpbyName(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    exploitType = 0
    results = {}
    wizard = False
    dict = None

    def help(self):
        print "target = <target host or network>"

    def run(self):
        self.results = {}
        host = socket.gethostbyname(self.target)
        self.results[0] = host

        return True

    def printSummary(self):
        i = 0
        self.gom.echo( "Target: " + self.target + " IP Address: " + self.results[0] )
        self.gom.echo( "Adding to discovered hosts " + self.results[0] )
        self.addToDict("hosts", self.results[0])
        #self.addToDict(self.results[0] + "_trace", self.results[0])
        #print self.results[0]
