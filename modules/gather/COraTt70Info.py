##      COraTt70Info.py
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
from lib.module import CIngumaGatherModule

name = "oratt70info"
brief_description = "Gather information from Oracle Times Ten 70"
type = "gather"

class COraTt70Info(CIngumaGatherModule):

    exploitType = 1

    banner = ""
    instanceName = ""
    osType = ""
    ttBackend = ""
    cacheAgent = ""
    dateTime = ""

    def help(self):
        self.gom.echo("target = <target host or network>")
        self.gom.echo("port = <target port>")

    def isCacheConnect(self, base):
        data = urllib.urlopen(url=base + "/cache/").read()

        if data.find("Oracle TimesTen") > -1:
            self.gom.echo("[+] Oracle TimesTen instance found")

        self.banner = data[data.find("<title>")+7:data.find("</title>")]
        self.gom.echo(self.banner)

        return True

    def gatherInstanceName(self, base):
        data = urllib.urlopen(url=base + "/cgi-bin/cache/login.pl").read()
        pos = data.find('id="instance_name">')

        if pos > -1:
            data = data[pos:]
            data = data[19:data.find("</label>")]
            self.gom.echo("[+] Instance name %s" % data)
            self.instanceName = data

    def gatherOsInfo(self, base):
        data = urllib.urlopen(url=base + "/cgi-bin/cache/ttBackend").read()

        if data.lower().find("cgi program") > -1:
            self.osType = "unix"
            self.gom.echo("[+] OS type Unix")
        else:
            data = urllib.urlopen(url=base + "/cgi-bin/cache/ttBackend.exe").read()

            if data.lower().find("cgi program") > -1:
                self.osType = "win32"
                self.gom.echo("[+] OS type Windows")

        data = data[data.find("CGI program '")+13:]
        data = data[:data.find("'")]
        self.gom.echo("[+] ttBackend CGI found")
        self.gom.echo(data)
        self.ttBackend = data

    def gatherCacheAgent(self, base):
        data = urllib.urlopen(url=base + "/cgi-bin/cache/oragents.pl").read()

        if data.find("Cache agent for ") > -1:
            data = data[data.find("Cache agent for "):]
            aux = data[data.find("is <b>")+6:data.find("</b><br>")]

            self.gom.echo("[+] Cache agent is %s" % aux)
            self.cacheAgent = aux

            data = data[data.find("&nbsp;as of <i>")+15:data.find("</i>.<p />")]
            self.gom.echo("[+] Cache agent date/time is %s" % data)
            self.dateTime = data

    def gatherInformation(self):
        if self.port == 0 or self.port == None:
            self.port = 17004

        baseUrl = "http://" + self.target + ":" + str(self.port)

        if not self.isCacheConnect(baseUrl):
            return False

        self.gatherInstanceName(baseUrl)
        self.gatherOsInfo(baseUrl)
        self.gatherCacheAgent(baseUrl)

        return True

    def updateDict(self):
        if self.banner != "":
            self.add_data_to_kb(self.target + "_ttbanner", self.banner)

        if self.instanceName != "":
            self.add_data_to_kb(self.target + "_ttinstance", self.instanceName)

        if self.osType != "":
            self.add_data_to_kb(self.target + "_ostype", self.osType)

        if self.ttBackend != "":
            self.add_data_to_kb(self.target + "_ttbackend", self.ttBackend)

        if self.cacheAgent != "":
            self.add_data_to_kb(self.target + "_ttagent", self.cacheAgent)

        if self.dateTime != "":
            self.add_data_to_kb(self.target + "_ttdatetime", self.dateTime)

    def run(self):
        res = self.gatherInformation()

        if res:
            self.updateDict()

        return res
