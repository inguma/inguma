#!/usr/bin/python

##      CSidGuess.py
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
import urllib
import string

import cx_Oracle

from lib.module import CIngumaModule
from lib.liboracleexploit import STANDARD_SIDS

name = "sidguess"
brief_description = "A simple Oracle SID guessing tool"
type = "brute"

globals = ["sid", ]

class CSidGuess(CIngumaModule):

    exploitType = 3
    services = ""
    results = {}
    user = ""
    sid = ""
    ssl = False
    connection = None

    def help(self):
        print "target = <Target ip or hostname>"
        print "port = <Target port>"
        print

    def bruteForce(self):
        for sid in STANDARD_SIDS:
            time.sleep(self.waitTime)
            try:
                self.gom.echo( "Trying SID " + sid + "..." )
                ret = self.guess(sid)
                sys.stdout.write("\b"  * 80)
                
                if ret:
                    self.addToDict(self.target + "_sid", sid)
                    self.results[self.target] = sid
                    self.gom.echo( "" )
                    self.gom.echo( "[+] Guessed SID " + sid )

                    return True

            except KeyboardInterrupt:
                self.gom.echo( "Aborted." )
                return False
            except:
                pass

        return False

    def guess(self, sid):
        link    = "system/manager@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%d)))"
        link += "(CONNECT_DATA=(SERVICE_NAME=%s)))"
        link    = link % (self.target, int(self.port), sid)

        try:
            self.connection = cx_Oracle.connect(link)
            self.close()

            self.addToDict(self.target + "_sid", sid)

            self.gom.echo( "" )
            self.gom.echo( "[+] We guess also a username/password!" )
            self.addToDict(self.target + "_passwords", "system/manager")
            self.gom.echo( "[+] Guessed: system/manager" )
        except:
            data = str(sys.exc_info()[1])

            if data.find("TNS:") > -1:
                raise
            else:
                return True

    def close(self):
        pass

    def tryEm(self):
        """ 
        Get the Database's SID from the Enterprise Manager web page.
        Thanks to Alexander Kornbrust.
        """
        target= self.target
        if not self.dict.has_key(target + "_tcp_ports"):
            return False

        if 1158 in self.dict[target + "_tcp_ports"]:
            port = 1158
        elif 5560 in self.dict[target + "_tcp_ports"]:
            port = 5560
        else:
            return False

        magic = '<table cellpadding="0" cellspacing="0" border="0" width="100%"><tr><td width="100%" class="x14">'
        url = self.target + ":" + str(port) + "/em/console/home"

        if self.ssl:
            url = "https://" + url
        else:
            url = "http://" + url
        
        try:
            data = urllib.urlopen(url).read()
            pos = data.find(magic)
            
            if pos > -1:
                tmp = data[pos:]
                tmp = tmp[:tmp.find('</td></tr><tr><td class="x9"><img src="/em/cabo/images/t.gif">')]
                tmp = tmp.split(":")

                if len(tmp) > 0:
                    self.addToDict(self.target + "_sid", tmp[1])
                    sid = tmp[1]
                    self.gom.echo( "" )
                    self.gom.echo( "[+] Guessed SID " + sid )
                    self.gom.echo( "" )
                    return True
        except:
            pass

    def run(self):
        if self.target == "":
            self.gom.echo( "No target specified" )
            return False

        if self.port == 0 or self.port == "":
            self.port = 1521

        if not self.tryEm():
            self.bruteForce()

        return True
