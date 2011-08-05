#!/usr/bin/python

##      CAutoCrackMod.py
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

import sys
import urllib
import urllib2

from lib.module import CIngumaModule
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
