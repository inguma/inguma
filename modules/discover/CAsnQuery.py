##      CAsnQuery.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import scapy.all as scapy
from lib.module import CIngumaDiscoverModule

name = "asn"
brief_description = "ASN whois database query"
type = "discover"

class CAsnQuery(CIngumaDiscoverModule):

    def help(self):
        self.gom.echo("target = <target host or comma-separated list of hosts>")

    def run(self):
        if self.timeout < 5:
            self.timeout = 5

        targets = []
        for i in self.target:
            targets.append(i)

        ips = {}
        for x in targets:
            ips[x] = None

        ASres = scapy.conf.AS_resolver
        ASN_query_list = dict.fromkeys(map(lambda x:x.rsplit(" ",1)[0],ips)).keys()
        ASNlist = ASres.resolve(*ASN_query_list)
        self.data = ASNlist

        return True

    def print_summary(self):
        self.gom.echo("------------------------")
        self.gom.echo("ASN database information")
        self.gom.echo("------------------------")
        self.gom.echo()
        for x in self.data:
            self.gom.echo( str(x[0]) + "\t" + str(x[1]) + "\t" + str(x[2]) )
            self.addToDict(str(x[0]) + "_asn", str(x[1]) + " " + str(x[2]))
    	self.gom.echo()
