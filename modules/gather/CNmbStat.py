#!/usr/bin/python

##      CNmbStat.py
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

import sys

from lib.core import getMacVendor
from impacket import smb, nmb
from lib.module import CIngumaModule

name = "nmbstat"
brief_description = "Gather NetBIOS information for target"
type = "gather"

class CNmbStat(CIngumaModule):
    port = 8000
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    url = None
    interactive = True
    data = []
    isWin32 = False
    macVendor = ""
    masterBrowser = False

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"

    def showHelp(self):
        print 

    def run(self):
        FIXED_SIZE = 17
        if self.target == "":
            self.gom.echo( "[!] No target specified, using localhost as target" )
            self.target = "localhost"

        objNmb = nmb.NetBIOS()
        self.data = []

        for node in objNmb.getnodestatus("*", self.target):
            data = node.get_nbname()

            data = data.replace("\x02", "").replace("\x01", "")

            if len(data) < FIXED_SIZE:
                data += " "*(FIXED_SIZE - len(data))
            else:
                data = data[:FIXED_SIZE]
            
            if data.find("__MSBROWSE__") > -1:
                self.masterBrowser = True

            x = nmb.NAME_TYPES.get(node.get_nametype(), "?")
            if len(x) < FIXED_SIZE:
                x += " "*(FIXED_SIZE - len(x))
            else:
                x = x[:FIXED_SIZE]

            data += x
            mac = objNmb.getmacaddress()
            if mac == "00-00-00-00-00-00":
                self.isWin32 = False
            else:
                self.isWin32 = True
                self.macVendor = getMacVendor(mac.replace("-", ""))
            self.mac = mac
            data += " " + mac

            if node.is_active():
                data += " ACTIVE "
            if node.is_group():
                data += " GROUP "
            if node.is_deleting():
                data += " DELETING"
            if node.is_conflict():
                data += " CONFLICT "
            if node.is_permanent():
                data += " PERMANENT "

            self.data.append(data)

        return True

    def printSummary(self):
        self.gom.echo( "NetBIOS Information" )
        self.gom.echo( "-------------------" )
        self.gom.echo( "" )

        for line in self.data:
            self.gom.echo( line )
        self.gom.echo( "" )

        if self.masterBrowser:
            self.gom.echo( "Is a Master Browser." )

        if self.isWin32:
            self.gom.echo( "MAC Address: " + self.mac.replace("-", ":") + " (" + self.macVendor + ")" )
            self.gom.echo( "Is a Windows based server." )
        else:
            self.gom.echo( "Is an Unix based server (Samba)." )

