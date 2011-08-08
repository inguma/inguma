##      CNetcraft.py
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

import sys
import urllib

from HTMLParser import HTMLParser
from lib.module import CIngumaDiscoverModule

name = "netcraft"
brief_description = "Query Netcraft database"
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

class CNetcraft(CIngumaDiscoverModule):

    def NetcraftHtmlParser(self, data):
        
        html_parser = SimpleHTMLParser()
        html_parser.feed(data)
        html_parser.close()

        return html_parser.data

    def parse_netcraft_data(self, data):
        baseStr = "<h1>site report for "
        pos = data.lower().find(baseStr)

        if pos > -1:
            data = data[pos+len(baseStr):]
            data = data[:data.lower().find("</table>")]

            return self.NetcraftHtmlParser(data)
        else:
            return "Error parsing Netcraft data."

    def help(self):
        """ Method called when 'help <module> is executed from the command line. """
        self.gom.echo("target = \"<target host or network>\"")

    def run(self):
        try:
            data = urllib.urlopen("http://toolbar.netcraft.com/site_report?url=http://" + self.target)
            tmp = data.read()
            self.data = self.parse_netcraft_data(tmp)

            return True
        except:
            self.gom.echo("Internal error: " + str(sys.exc_info()[1]))
            return False

        return True

    def print_summary(self):
        self.gom.echo("Netcraft database information")
        self.gom.echo("-----------------------------")
        self.gom.echo()

        start = self.data.index('Site')
        end = len(self.data)
        for x in range(start, end):
            try:
                self.gom.echo( str(self.data[start]) + ':\t\t' + str(self.data[start + 1]) )
                self.addToDict(self.target + "_netcraft", [self.data[start], self.data[start + 1]])
                start = start + 2
            except:
                return False

