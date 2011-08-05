#!/usr/bin/python

##      CDtspcGather.py
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
from lib.libdtspc import getDtspcInformation

name = "dtspc"
brief_description = "Gather information from DTSPCD"
type = "gather"

class CDtspcGather(CIngumaModule):

    port = 6112
    result = None

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"

    def run(self):
        if self.target == "" or self.target is None:
            self.gom.echo( "[!] No target specified" )
            return False
        
        if self.port == 0 or self.port is None:
            self.port = 6112

        socket.setdefaulttimeout(self.timeout)
        ret = getDtspcInformation(self.target, self.port)

        if ret != {}:
            self.addToDict(self.target + "_dtspc", ret)
            self.result = ret
            return True

        return False

    def printSummary(self):
        self.gom.echo( "Hostname : " + str(self.result["hostname"]) )
        self.gom.echo( "OS       :" + str(self.result["os"]) + " " + str(self.result["version"]) )
        self.gom.echo( "Arch.    :" + str(self.result["arch"]) )
        self.gom.echo( "" )

