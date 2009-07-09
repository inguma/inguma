#!/usr/bin/python

"""
Module MS SQL Server (2000) password cracker for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import os
import sys
import sha # Yes, I known, will be replaced someday...
import binascii

from lib.libexploit import CIngumaModule
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

    def printSummary(self):
        pass
