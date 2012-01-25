##      COracleApps.py
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
import socket
import urllib2

from lib.libvulnoas import VULNERABLE_PAGES
from lib.module import CIngumaGatherModule

name = "oascheck"
brief_description = "Check an Oracle App. Server for the most common vulnerable URLs."
type = "gather"

class COracleApps(CIngumaGatherModule):
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
        self.gom.echo("target = <target host or network>")
        self.gom.echo("port = <target port>")
        self.gom.echo("timeout = <timeout>")
        self.gom.echo("ssl = True|False")

    def doAssessment(self):

        socket.setdefaulttimeout(self.timeout)

        if self.port == 0 or self.port == None:
            self.port = 80
            self.gom.echo("Using port 80")
        else:
            self.gom.echo("Using port %d" % int(self.port))

        if self.ssl:
            baseurl = "https://"
        else:
            baseurl = "http://"
        baseurl += self.target + ":" + str(self.port)

        self.gom.echo("Checking url list...")
        self.gom.echo()

        for page in VULNERABLE_PAGES:
            page = page.strip("\r").strip("\n")
            try:
                x = urllib2.urlopen(baseurl + page)
                del x
                self.add_data_to_kb("oas_vulnerable_urls", page)
                self.gom.echo("Adding vulnerable URL '%s'..." % page)
                self._urls.append(page)
            except urllib2.HTTPError:
                pass # Just ignore
            except urllib2.URLError:
                self.gom.echo("Cannot connect to target. Exiting...")
                return False
            except KeyboardInterrupt:
                self.gom.echo("Aborted.")
                return
            except:
                self.gom.echo("Exception:", sys.exc_info()[0], sys.exc_info()[1])

        self.gom.echo("Done.")

    def run(self):
        if self.port is None or self.port == 0:
            self.port = 80

        if self.target == "" or self.target is None:
            self.target = "localhost"

        self.doAssessment()

        return True

    def print_summary(self):
        self.gom.echo("The following vulnerable Oracle Application Server's URL(s) were found:")
        self.gom.echo()

        for url in self._urls:
            self.gom.echo("\t\t%s" % url)
        self.gom.echo()
        self.gom.echo()
