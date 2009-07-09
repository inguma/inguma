#!/usr/bin/python
"""
Module hostname for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import socket
from lib.libexploit import CIngumaModule

name = "hostname"
brief_description = "Get the host's name"
type = "discover"

class CGetHostbyAddr(CIngumaModule):

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
        try:
            host = socket.gethostbyaddr(self.target)
        except:
            host = self.target

        self.results[0] = host

        return True
    
    def printSummary(self):
        self.addToDict(self.target + "_name", self.results[0][0] )
        self.gom.echo( self.target + " name: " + str(self.results[0][0]) )
