##      CUnicornScan.py
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

import re
import os

from lib.module import CIngumaGatherModule

name = "unicornscan"
brief_description = "A wrapper for the unicornscan tool"
type = "gather"

class CUnicornScan(CIngumaGatherModule):
    sport = "-1"        #-B, --source-port port (-1 random by default)
    dport = ""           #-p, --ports string
    mode = ""           #-m,  --mode (U, T, A and sf for Udp scanning, Tcp scanning, Arp scanning, and Tcp Connect scannin)
    prate = ""           #[-r, --pps
    saddr = ""           #-s, --source-addr
    opened = {}
    closed = {}

    def help(self):

        self.gom.echo("target = <target host or network>")
        self.gom.echo("source = <source address>")
        self.gom.echo("port   = <target port>")
        self.gom.echo("sport  = <source port>")
        self.gom.echo("mode   = <scan mode>")
        self.gom.echo("""
          TCP (SYN) scan is default, U for UDP, T for TCP, 'sf' for TCP connect scan and A for ARP.
          For -mT you can also specify TCP flags following the T like -mTsFpU for example
          that would send TCP SYN packets with (NO SYN|FIN|NO PSH|URG)""")
        self.gom.echo("pps    = <packets per second>")

    def run(self):
        self.opened = {}
        self.closed = {}

        try:
            scanres = os.popen('unicornscan ' +  self.target)
            for res in scanres.readlines():
                portmatch = re.search("[0-9]*\]", res)
                #portfrom = re.search("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*", res)
                port = portmatch.group(0)[:-1]

                self.opened[port] = "open"
                self.add_data_to_kb(self.target + "_tcp_ports", port)
            return True
        except:
            return False

    def print_summary(self):
        self.gom.echo()
        self.gom.echo("Portscan results")
        self.gom.echo("----------------")
        self.gom.echo()

        for opened in self.opened:
            port_name = str(opened)
            self.gom.echo('Port ' + port_name + 'is open.')
        self.gom.echo()
