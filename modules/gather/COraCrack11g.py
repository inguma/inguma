#!/usr/bin/python

##      COraCrack11g.py
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

name = "oracrack11g"
brief_description = "Crack an Oracle 11g password"
type = "gather"

globals = ["hash", ]

class COraCrack11g(CIngumaModule):

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

        if len(hash) not in [60, 62]:
            print "[!] Invalid hash: You need the full 60 characters long hash"
            return False

        hash = hash.lower()
        if hash.startswith("s:"):
            hash = hash[2:]

        thepasswd = hash[:40]
        salt = hash[40:]

        if not salt.isalnum():
            print "[!] Invalid hash: Non alphanumeric salt"
            return False

        salt = binascii.a2b_hex(salt)
        for passwd in self.getPasswordList():
            passwd = passwd.strip()
            x = hashlib.sha1(passwd + salt).hexdigest()

            if x == thepasswd:
                self.addToDict(hash, passwd)
                print "[+] Password:", passwd
                return True

        print "[!] No match"
        return False

    def run(self):

        if self.hash == "":
            print "[!] No hash specified"
            return False
        else:
            self.findHash(self.hash)

        return True
