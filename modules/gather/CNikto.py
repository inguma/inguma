#!/usr/bin/python

##      CNikto.py
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

"""
Sullo, a member of the Nikto project gives us permission to use Nikto's
database in Inguma. To obtain updated databases of Nikto navigate to
http://www.cirt.net and/or to get more information.

Thanks you Sullo!
"""
import sys
import socket
import urllib2

from lib import libnikto
from lib.module import CIngumaModule

name = "nikto"
brief_description = "Nikto web server scanner module for Inguma"
type = "gather"

class CNikto(CIngumaModule):
    target = ""  # Main target
    port = 80
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    interactive = False
    _urls = []
    ssl = False

    def help(self):
        print "target = <target host or URL (without prefix http/s)>"
        print "port = <target port>"
        print "timeout = <timeout>"
        print "ssl = True|False"

    def doAssessment(self):

        socket.setdefaulttimeout(self.timeout)

        if self.port == 0 or self.port == None:
            self.port = 80
            self.gom.echo( "Using port 80" )
        else:
            self.gom.echo( "[+] Using port %d" % int(self.port) )

        if self.ssl:
            baseurl = "https://"
        else:
            baseurl = "http://"
        baseurl += self.target + ":" + str(self.port) + "/"

        # Read signatures and/or download databases
        self.gom.echo( "[+] Reading signatures ... " )
        self.gom.echo( "[i] To upgrade signatures run python lib/libnikto.py" )
        res = libnikto.getDatabases()

        if not res:
            return False

        self.gom.echo( "Checking url list..." )
        self.gom.echo( "" )

        self._urls = []

        for rule in libnikto.SIGNATURES:
            niktoRule = libnikto.CNiktoRule(rule)
            page = niktoRule.uri

            try:
                x = urllib2.urlopen(baseurl + page)
                if x.read().find(niktoRule.match1) > -1:
                    del x
                    #self.addToDict(self.target + "_vulnerable-urls", page)
                    self.addToDict(self.target + "_" + str(self.port) + "-web-vulns", [niktoRule.osvdbId, page] )

                    self.gom.echo( "Adding vulnerable URL '%s'..." % page )
                    self.gom.echo( "-"*40 )
                    self.gom.echo( "OSVDB: %s" % niktoRule.osvdbId )
                    self.gom.echo( "URI: %s" % niktoRule.uri )
                    self.gom.echo( "Match: '%s'" % niktoRule.match1 )
                    self.gom.echo( "Summary: %s" % niktoRule.summary )
                    self.gom.echo( "-"*40 )
                    self.gom.echo( "" )
                    self._urls.append(page)
            except urllib2.HTTPError:
                pass # Just ignore
            except urllib2.URLError:
                pass # Just ignore
            except KeyboardInterrupt:
                self.gom.echo( "Aborted." )
                return
            except:
                self.gom.echo( "Exception:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) )

        self.gom.echo( "Done." )

    def run(self):
        if self.port is None or self.port == 0:
            self.port = 80

        if self.target == "" or self.target is None:
            self.target = "localhost"
        
        self.doAssessment()

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "The following vulnerable URL(s) were found:" )
        self.gom.echo( "" )

        for url in self._urls:
            self.gom.echo( "\t\t%s" % url )
        self.gom.echo( "" )
        self.gom.echo( "" )
