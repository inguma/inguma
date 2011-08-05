#!/usr/bin/python

##      CMd5Rainbow.py
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

from lib.module import CIngumaModule

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
