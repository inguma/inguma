#!/usr/bin/python

"""
Module MD5 Rainbow Tables for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys
import urllib

from lib.libexploit import CIngumaModule

name = "rainbowmd5"
brief_description = "Get the password for a MD5 hash using public rainbow tables"
type = "gather"

globals = ["hash", ]

class CMd5Rainbow(CIngumaModule):

    hash = ""

    def help(self):
        print "hash = <hash of the password>"

    def findHash(self, hash):
        res = urllib.urlopen("http://md5.thekaine.de/index.php?hash=" + str(self.hash)).read()
        magic = '<td colspan="2"><br><br><b>'
        pos = res.find(magic)

        if pos > -1 and res.find("Converting " + hash) == -1:
            data = res[pos+len(magic):res.find("</b></td><td></td>")]
            self.addToDict(hash, data)
            print "[+] Password:", data
            return True
        else:
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
