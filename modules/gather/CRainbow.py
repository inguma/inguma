#!/usr/bin/python

"""
Module Rainbow Tables for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys
import urllib
import urllib2

from lib.libexploit import CIngumaModule

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

    def printSummary(self):
        pass
