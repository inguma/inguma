#!/usr/bin/python
"""
Module externip for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import urllib
import socket

from lib.libexploit import CIngumaModule

name = "externip"
brief_description = "Get your external ip address (even when using proxies)"
type = "discover"

class CExtIp(CIngumaModule):

    target = ""
    waitTime = 0
    timeout = 2
    exploitType = 0
    results = {}
    wizard = False
    dict = None

    def help(self):
        pass

    def run(self):
        self.results = {}
        host = urllib.urlopen("http://inguma.sourceforge.net/php/ip.php").read()
        self.results[0] = host
        self.addToDict("external_ip", [self.target, host])
        self.addToDict("hosts", host)

        return True

    def printSummary(self):
        i = 0
        self.gom.echo( str(self.results[0]) )
