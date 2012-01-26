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

from lib.module import CIngumaGatherModule

name = "webserver"
brief_description = "A simple web server and Crawler, useful if used with DnsSpoof module"
type = "gather"

globals = ["crawl",  "path"]

class CWebServer(CIngumaGatherModule):

    crawl = False
    port = 80
    path = "data/web/"

    def help(self):
        """ This is the entry point for info <module> """
        self.gom.echo("crawl = <True/False>")
        self.gom.echo("target = <target URL to crawl if True>")
        self.gom.echo("port = <server port>")
        #self.gom.echo("directory = <path to web files>")

    def run(self):
        """ This is the main entry point of the module """
        self.gom.echo("Crawl %s" % self.crawl)
        if self.crawl:
            self.gom.echo("Crawling page: " + self.target)
            page = urllib2.urlopen(self.target)
            text = page.read()
            page.close()

            #Parse some links
            href = '<a href="(?!http://)'
            src = '<img src=(?!http://)'
            #Parse image links
            self.gom.echo("Parsing image links...")
            objRe = re.compile(src, re.IGNORECASE)
            text = objRe.sub('<img src=' + self.target, text)
            #Parse href links
            self.gom.echo("Parsing href links...")
            objRe = re.compile(href, re.IGNORECASE)
            text = objRe.sub('<a href=' + self.target, text)

            #FIXME: Hugo Fixme!!!
            os.chdir('data/web/')
            file = open("index.html",  'w')
            self.gom.echo("Crawled page saved at " + os.getcwd() + "/index.html")
            file.write(text)
            os.chdir('../../')
            file.close()

        os.chdir('./data/web/')
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", self.port), Handler)
        self.gom.echo("serving at port", self.port)
        httpd.serve_forever()
        os.chdir('../../')

        return False
