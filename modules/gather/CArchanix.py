#!/usr/bin/python

"""
Module Archanix for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys
import socket

from lib.libexploit import CIngumaModule

name = "archanix"
brief_description = "Gather information from archaic Unix systems"
type = "gather"

class CArchanix(CIngumaModule):

    netstat = None
    sysstat = None
    finger = None
    _servicesList = {11:"sysstat", 15:"netstat", 79:"finger"}

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"

    def execOldcommand(self, port, tosend = "\n\n"):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, port))
            s.send(tosend)
            data = s.recv(8192)
            
            self.addToDict(self.target + "_netstat", data)
            return data
        except:
            print sys.exc_info()[1]
            return False

    def run(self):
        if self.dict.has_key(self.target + "_tcp_ports"):
            mList = self.dict[self.target + "_tcp_ports"]
            for service in mList:
                if self._servicesList.has_key(service):
                    if service != "finger":
                        buf = self.execOldcommand(service)
                    else:
                        buf = self.execOldcommand(port=service, tosend="/W\n")
                    cmd = "self." + self._servicesList[service] + " = buf"
                    exec(cmd)
        else:
            if self.port == 0:
                self.gom.echo( "No ports detected with a portscanner and the value of port is 0." )
                return False
            else:
                self.gom.echo( "Port " + self.port )

        return True

    def printSummary(self):
        self.gom.echo( "SYSSTAT" )
        self.gom.echo( "-------" )
        self.gom.echo( "" )
        self.gom.echo( str(self.sysstat) )
        self.gom.echo( "" )
        
        self.gom.echo( "NETSTAT" )
        self.gom.echo( "-------" )
        self.gom.echo( "" )
        self.gom.echo( str(self.netstat) )
        self.gom.echo( "" )
        
        self.gom.echo( "FINGER" )
        self.gom.echo( "------" )
        self.gom.echo( "" )
        self.gom.echo( str(self.finger) )
        self.gom.echo( "" )
