#!/usr/bin/python

##      CRainbow.py
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

name = "rainbow"
brief_description = "Get the password for a hash using public rainbow tables"
type = "gather"

globals = ["hash", ]

class CRainbow(CIngumaModule):

    hash = ""

    def help(self):
        print "hash = <hash of the password>"

    def findHash(self, hash):
        url = 'http://passcracking.com/index.php'
        values = {'admin' : 'false',
                  'admin2' : '77.php',
                  'datafromuser' : hash,
                  'DoIT' : '' }
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = str(response.read())

        magic = hash + "</td><td bgcolor=#FF0000>"
        pos = the_page.find(magic)

        if pos == -1 and the_page.find("<b>pass</b></td><td>hex</td></tr>") == -1:
            self.gom.echo( "[!] No match" )
            return False

        the_page = the_page[pos+len(magic):]
        data = the_page[:the_page.find("</td><td>")]
        self.addToDict(hash, data)
        self.gom.echo( "[+] Password: " + data )

        return True

    def run(self):

        if self.hash == "":
            self.gom.echo( "[!] No hash specified" )
            return False
        else:
            self.findHash(self.hash)

        return True
