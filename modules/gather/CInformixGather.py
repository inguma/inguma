#!/usr/bin/python

##      CInformixGather.py
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
import socket

from lib.module import CIngumaModule
from lib.libinformix import *

name = "ifxinfo"
brief_description = "Gather information from an Informix database server"
type = "gather"

globals = ["database", ]

class CInformixGather(CIngumaModule):
    
    informixResponse = None
    informixDatabases = None
    user = ""
    password = ""
    database = ""
    
    def help(self):
        """ This is the entry point for info <module> """
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"

    def run(self):

        self.informixResponse = None
        self.informixDatabases = None

        if self.target == "":
            self.gom.echo( "No target specified" )
            return False

        if self.port == 0 or self.port == None:
            self.gom.echo( "[!] Warning! Using port 9088" )
            self.port = 9088

        ifx = Informix()
        ifx.username = self.user
        ifx.password = self.password

        if self.database == "":
            ifx.databaseName = ""
        else:
            ifx.databaseName = self.database

        socket.setdefaulttimeout(self.timeout)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
        except:
            print sys.exc_info()[1]
            self.gom.echo( 'Module failed, no answer recived' )
            return False

        buf = ifx.getPacket()
        self.gom.echo( "[+] Sending login packet (User: %s, Password %s, Database: %s)" % (ifx.username,  ifx.password,  ifx.databaseName) )
        s.send(buf)
        data = s.recv(4096)
        self.gom.echo( "[+] Received %d byte(s)" % len(data) )
        self.informixResponse = InformixLoginResponse()
        self.informixResponse.parse(data)

        self.gom.echo( "[+] Searching databases ... " )
        ifxCmd = InformixCommand()
        ifxCmd.opcode = IFX_OPCODE_DBLIST
        buf = ifxCmd.getPacket()
        self.gom.echo( "[+] Sending DBLIST command ... " )
        s.send(buf)
        self.gom.echo( "[+] Receiving list of databases ... " )
        data = s.recv(4096)

        self.informixDatabases = InformixDbListResponse()
        self.informixDatabases.databases = []
        self.informixDatabases.parse(data)

        return True

    def printSummary(self):
        self.gom.echo( "[+] Gathered information from Informix Database Server" )
        self.gom.echo( "" )
        self.gom.echo( "    Is valid user".ljust(18),  repr(self.informixResponse.isValidUser) )
        self.addToDict(self.target + "_informix",  {"ValidUser":self.informixResponse.isValidUser})

        if self.database != "":
            self.gom.echo( "    Is valid db".ljust(18),  repr(self.informixResponse.isValidDatabase) )
            self.addToDict(self.target + "_informix",  {"ValidDatabase":self.informixResponse.isValidDatabase})

        self.gom.echo( "    IEEE".ljust(18),  repr(self.informixResponse.ieee) )
        self.addToDict(self.target + "_informix",  {"IEEE":self.informixResponse.ieee})
        self.gom.echo( "    Name".ljust(18),  repr(self.informixResponse.name) )
        self.addToDict(self.target + "_informix",  {"Name":self.informixResponse.name})
        self.gom.echo( "    Banner".ljust(18),  repr(self.informixResponse.banner) )
        self.addToDict(self.target + "_informix",  {"Banner":self.informixResponse.banner})
        self.gom.echo( "    Serial Number".ljust(18),  repr(self.informixResponse.serialNumber) )
        self.addToDict(self.target + "_informix",  {"SerialNumber":self.informixResponse.serialNumber})
        self.gom.echo( "    Db Path".ljust(18),  repr(self.informixResponse.databasePath) )
        self.addToDict(self.target + "_informix",  {"DBPath":self.informixResponse.databasePath})
        self.gom.echo( "    Protocol".ljust(18),  repr(self.informixResponse.protocol) )
        self.addToDict(self.target + "_informix",  {"Protocol":self.informixResponse.protocol})
        self.gom.echo( "    Hostname".ljust(18),  repr(self.informixResponse.hostname) )
        self.addToDict(self.target + "_informix",  {"Hostname":self.informixResponse.hostname})
        self.gom.echo( "    Terminal".ljust(18),  repr(self.informixResponse.terminal) )
        self.addToDict(self.target + "_informix",  {"Terminal":self.informixResponse.terminal})
        self.gom.echo( "    Home Path".ljust(18),  repr(self.informixResponse.homePath) )
        self.addToDict(self.target + "_informix",  {"HomePath":self.informixResponse.homePath})
        self.gom.echo( "" )
        self.gom.echo( "Discovered databases" )
        self.gom.echo( "--------------------" )
        self.gom.echo( "" )
        for db in self.informixDatabases.databases:
            self.gom.echo( "    %s" % db )
            self.addToDict(self.target + "_informix", {"Database":db})
        self.gom.echo( "" )
