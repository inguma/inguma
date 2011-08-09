##      Cdb2DiscoverModule.py
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

from lib.module import CIngumaDiscoverModule
from lib.libdb2 import CDb2Discover

name = "db2discover"
brief_description = "IBM DB2 database servers discover module"
type = "discover"

class CDb2DiscoverModule(CIngumaDiscoverModule):

    def help(self):
        self.gom.echo("target = <target host or network>")
        self.gom.echo("port = <target port>")
        self.gom.echo("timeout = <timeout>")

    def print_summary(self):
        for server in self.answer:
            self.gom.echo("[+] IBM DB2 Server at " + str(server[0][0]) + ": " + str(server[0][1]))
            self.gom.echo("  Version   : " + str(server[1]))
            self.gom.echo("  Hostname  : " + str(server[2]))
            self.gom.echo("  Servername: " + str(server[3]))
            self.gom.echo()
            self.add_data_to_kb("hosts",  server[0][0])
            self.add_data_to_kb(server[0][0] + "_db2server",  (server[1],  server[2],  server[3]))

        self.gom.echo("Total of " + str(len(self.answer)) + " IBM DB2 Server(s) found.")
        
        return len(ret) > 0

    def run(self):
        
        if self.target == "":
            self.target = "<broadcast>"
            self.gom.echo("[i] Using broadcast address 255.255.255.255")
        
        if self.port == 0 or self.port == None:
            self.port = 553
        
        if self.port != 553:
            self.gom.echo("[!] Warning! Using non-standard port " + self.port)
        
        db2Discover = CDb2Discover()
        db2Discover.target = self.target
        db2Discover.port = self.port
        db2Discover.verbose = False
        self.answer = db2Discover.discover()

        return True
