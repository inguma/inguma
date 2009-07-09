#!/usr/bin/python

"""
Module "netcraft" for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import os
import sys
import time
import urllib

from HTMLParser import HTMLParser
from lib.libexploit import CIngumaModule

name = "netcraft"
brief_description = "Query netcraft database"
type = "discover"

class SimpleHTMLParser(HTMLParser):

    ignoreIt = False
    data = []

    def handle_starttag(self, tag, attrs):
        if str.upper(tag) == "SCRIPT":
            self.ignoreIt = True

    def handle_endtag(self, tag):
        if str.upper(tag) == "SCRIPT":
            self.ignoreIt = False

    def handle_data(self, data):
    
        if len(data) > 1 and data.lower().find("uptime graph") == -1:

            if data[0:1] == '\r' or data[0:1] == '\n':
                data = data[1:]

            self.data.append(data)

class CNetcraft(CIngumaModule):
    target = ""
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    ret = False

    def help(self):
        print "target = <target host or network>"

    def netCraftHtmlParser(self, data):
        
        htmParser = SimpleHTMLParser()
        htmParser.feed(data)
        htmParser.close()

        return htmParser.data

    def parseNetcraftData(self, data):
        baseStr = "<h1>site report for "
        pos = data.lower().find(baseStr)

        if pos > -1:
            data = data[pos+len(baseStr):]
            data = data[:data.lower().find("</table>")]

            return self.netCraftHtmlParser(data)
        else:
            return "Error parsing netcraft data"

    def run(self):
        try:
            data = urllib.urlopen("http://toolbar.netcraft.com/site_report?url=http://" + self.target)
            tmp = data.read()
            self.data = self.parseNetcraftData(tmp)

            return True
        except:
            print sys.exc_info()[1]
            return False

        return True

    def printSummary(self):
        self.gom.echo( "Netcraft database information" )
        self.gom.echo( "-----------------------------" )
        self.gom.echo( "" )

        start = self.data.index('Site')
        end = len(self.data)
        for x in range(start, end):
            try:
                self.gom.echo( str(self.data[start]) + ':\t\t' + str(self.data[start + 1]) )
                self.addToDict(self.target + "_netcraft", [self.data[start], self.data[start + 1]])
                start = start + 2
            except:
                return False
        
