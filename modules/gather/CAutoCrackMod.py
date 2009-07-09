#!/usr/bin/python

"""
Module Autocrack for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys
import urllib
import urllib2

from lib.libexploit import CIngumaModule
from lib.libautocrack import CAutoCrack

name = "anticrypt"
brief_description = "Try to automagically guess the password algorithm"
type = "gather"

globals = ["hash", "debugLevel"]

class CAutoCrackMod(CIngumaModule):

    hash = ""
    debugLevel = 0

    def help(self):
        print "hash = <hash of the password>"
        print "password = <original unencrypted password>"

    def run(self):

        if self.hash == "":
            print "[!] No hash specified"
            return False

        if self.password == "":
            print "[!] No password specified"
            return False

        objCrack = CAutoCrack()
        objCrack.debugLevel = self.debugLevel
        objCrack.password = self.password
        objCrack.hash = self.hash
        print "[+] Trying to guess the encryption algorithm ..."
        ret = objCrack.run()
        
        if ret:
            print "  --> Algorigthm:", objCrack.algorithm
        
        return ret

    def printSummary(self):
        pass
