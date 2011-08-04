#!/usr/bin/python

##      CWebServer.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import os, urllib2, SimpleHTTPServer, SocketServer, re

from lib.module import CIngumaModule

name = "webserver"
brief_description = "A simple Web Server and Crawler, usefull if used with DnsSpoof module"
type = "gather" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

globals = ["crawl",  "path"]

class CWebServer(CIngumaModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

    crawl = False
    port = 80
    path = "data/web/"

    def help(self):
        """ This is the entry point for info <module> """
        print "crawl = <True/False>"
        print "target = <target URL to crawl if True>"
        print "port = <server port>"
        #print "directory = <path to web files>"

    def run(self):
        """ This is the main entry point of the module """
        print "Crawl %s" % self.crawl
        if self.crawl:
            print "Crawling page: " + self.target
            page = urllib2.urlopen(self.target)
            text = page.read()
            page.close()
            
            #Parse some links
            href = '<a href="(?!http://)'
            src = '<img src=(?!http://)'
            #Parse image links
            print "Parsing image links..."
            objRe = re.compile(src, re.IGNORECASE)
            text = objRe.sub('<img src=' + self.target, text)
            #Parse href links
            print "Parsing href links..."
            objRe = re.compile(href, re.IGNORECASE)
            text = objRe.sub('<a href=' + self.target, text)
            
            #FIXME: Hugo Fixme!!!
            os.chdir('data/web/')
            file = open("index.html",  'w')
            print "Crawled page saved at " + os.getcwd() + "/index.html"
            file.write(text)
            os.chdir('../../')
            file.close()
        
        os.chdir('./data/web/')
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", self.port), Handler)
        print "serving at port", self.port
        httpd.serve_forever()
        os.chdir('../../')
        
        return False
