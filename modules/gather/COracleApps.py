#!/usr/bin/python

"""
Module Oracle Applications Scanner for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import sys
import socket
import urllib2

from lib.libvulnoas import VULNERABLE_PAGES
from lib.libexploit import CIngumaModule

name = "oascheck"
brief_description = "Check an Oracle App. Server for the most common vulnerable URLs."
type = "gather"

class COracleApps(CIngumaModule):
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
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"
        print "ssl = True|False"

    def doAssessment(self):

        socket.setdefaulttimeout(self.timeout)

        if self.port == 0 or self.port == None:
            self.port = 80
            print "Using port 80"
        else:
            print "Using port %d" % int(self.port)

        if self.ssl:
            baseurl = "https://"
        else:
            baseurl = "http://"
        baseurl += self.target + ":" + str(self.port)

        print "Checking url list..."
        print

        for page in VULNERABLE_PAGES:
            page = page.strip("\r").strip("\n")
            try:
                x = urllib2.urlopen(baseurl + page)
                del x
                self.addToDict("oas_vulnerable_urls", page)
                print "Adding vulnerable URL '%s'..." % page
                self._urls.append(page)
            except urllib2.HTTPError:
                pass # Just ignore
            except urllib2.URLError:
                print "Cannot connect to target. Exiting..."
                return False
            except KeyboardInterrupt:
                print "Aborted."
                return
            except:
                print "Exception:", sys.exc_info()[0], sys.exc_info()[1]

        print "Done."

    def run(self):
        if self.port is None or self.port == 0:
            self.port = 80

        if self.target == "" or self.target is None:
            self.target = "localhost"
        
        self.doAssessment()

        return True

    def printSummary(self):
        print "The following vulnerable Oracle Application Server's URL(s) were found:"
        print

        for url in self._urls:
            print "\t\t%s" % url
        print
        print
