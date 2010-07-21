#!/usr/bin/python

##      CExtIp.py
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
