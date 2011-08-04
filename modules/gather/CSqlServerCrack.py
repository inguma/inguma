#!/usr/bin/python

##      CSqlServerCrack.py
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
import hashlib
import binascii

from lib.module import CIngumaModule
from lib.libSQLServerPassword import CSQLServerPassword

name = "mssqlcrack"
brief_description = "Crack a MS SQL Server 7 or 2000 password"
type = "gather"

globals = ["hash", ]

class CSqlServerCrack(CIngumaModule):

    hash = ""

    def help(self):
        print "hash = <hash of the password>"

    def getPasswordList(self):
        fname = self.dict["base_path"]
        if fname != "" :
            fname += os.sep + "data" + os.sep + "dict"
        else:
            fname = "data" + os.sep + "dict"

        f = file(fname, "r")
        return f.readlines()

    def findHash(self, hash):

        if not hash.isalnum():
            print "[!] Invalid hash: Non alphanumeric characters"
            return False

        objMSSQL = CSQLServerPassword(self.hash)
        objMSSQL.printSummary()

        for passwd in self.getPasswordList():
            passwd = passwd.strip()
            x = objMSSQL.encrypt(passwd)[2:]

            if hash.find(x) > -1:
                self.addToDict(hash, passwd)
                print "[+] Password:", passwd
                return True

        print "[!] No match"
        print objMSSQL.encrypt("sa")
        print self.hash
        return False

    def run(self):

        if self.hash == "":
            print "[!] No hash specified"
            return False
        else:
            self.findHash(self.hash)

        return True
