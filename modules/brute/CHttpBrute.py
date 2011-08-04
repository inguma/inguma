#!/usr/bin/python

##      CHttpBrute.py
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

import os
import sys
import time
import string
import urllib2

from lib.libhttp import CIngumaHttp
from lib.module import CIngumaModule

name = "brutehttp"
brief_description = "A simple HTTP brute force tool"
type = "gather"

globals = ["url", ]

class CHttpBrute(CIngumaModule):

    exploitType = 3
    services = ""
    results = {}
    user = ""
    transport = None
    url = ""
    ssl = False

    def help(self):
        print "target = <target host or network>"
        print "port = <port>"
        print "user = <username>"
        print "url = <url>"

    def bruteForce(self):
        userList = [self.user, ]
        self.open()

        try:
            self.gom.echo( "Trying " + self.user + "/" + self.user )
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
                    self.gom.echo( "Trying " + user + "/" + passwd + "..." )
                    #self.gom.echo( "\b"  * 80 + "Trying " + user + "/" + passwd + "..." )
                    self.login(user, passwd)
                    sys.stdout.write("\b"  * 80)
                    self.addToDict(self.target + "_passwords", self.user + "/" + passwd)
                    self.results[user] = passwd
            
                    return True
                except KeyboardInterrupt:
                    self.gom.echo( "Aborted." )
                    return False
                except urllib2.HTTPError, e:
                    if e.code != 401:
                        raise
                except:
                    pass

        return False

    def open(self):
        try:
            self.transport = CIngumaHttp(self.url)
            self.transport.buildUrl(self.target, self.port, self.ssl, self.url)
        except:
            self.gom.echo( sys.exc_info()[1] )

    def login(self, user, thepassword):
        self.transport.open(webuser=user, webpass=thepassword)

    def close(self):
        try:
            self.transport.close()
        except:
            sys.exc_info()[1]

    def run(self):
        if self.target == "":
            self.gom.echo( "No target specified" )
            return False
        
        if self.user == "":
            self.gom.echo( "No user specified" )
            return False

        if self.port == 0 or self.port == "":
            self.port = 22
        
        if self.url == "":
            self.gom.echo( "No URL specified" )
            return False

        self.bruteForce()
        return True

    def printSummary(self):
        self.gom.echo( "" )
        for x in self.results:
            self.gom.echo( "[+] User guessed: " + x + "/" + self.results[x] )
