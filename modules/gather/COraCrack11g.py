#!/usr/bin/python

"""
Module Oracle11g password cracker for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import os
import sys
import hashlib
import binascii

from lib.libexploit import CIngumaModule

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

    def printSummary(self):
        pass
