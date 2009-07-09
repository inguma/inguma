#!/usr/bin/python

"""
Module DTSPC for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys
import socket

from lib.libexploit import CIngumaModule
from lib.libdtspc import getDtspcInformation

name = "dtspc"
brief_description = "Gather information from DTSPCD"
type = "gather"

class CDtspcGather(CIngumaModule):

    target = None
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

