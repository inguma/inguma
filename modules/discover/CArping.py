##      CArping.py
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

import sys

from lib.core import getMacVendor
from lib.module import CIngumaDiscoverModule

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "arping"
brief_description = "Send an ARP who-has message to discover hosts."
type = "discover"

class CArping(CIngumaDiscoverModule):
    target = "192.168.1.0/24"

    def help(self):
        self.gom.echo("target = <target host or network>")
        self.gom.echo("timeout = <timeout>")

    def getMacVendor(self, mac):
        try:
            # TODO fix get path from scapy
            #path = scapy.conf.nmap_base.replace('os-fingerprints', 'mac-prefixes')
            path = "/usr/share/nmap/nmap-mac-prefixes"
            mac = mac.replace(":", "")

            f = file(path, "r")

            for line in f:
                if line.startswith("#"):
                    pass # Ignore, just a comment
                elif line.replace(" ", "") == "":
                    pass # Ignore, blank line
                else:
                    prefix = line[0:6]
                    vendor = line[7:]

                    if mac.lower().startswith(prefix.lower()):
                        return vendor.replace("\r", "").replace("\n", "")
            
            return "Unknown vendor."
        except:
            return "Internal error: " + str(sys.exc_info()[1])

    def arping(self, net):
        scapy.conf.verb = 0
        ans,unans = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=net),
                        filter="arp and arp[7] = 2", timeout=self.timeout)
        ret = scapy.ARPingResult(ans.res)

        flag = 0

        for x, y in ret:
            flag += 1
            ip = y.sprintf("%ARP.psrc%")
            self.gom.echo("Adding to discovered hosts " + ip )
            self.add_data_to_kb("hosts", ip)
            self.add_data_to_kb("targets", ip)
            self.add_data_to_kb(ip + "_mac", y.sprintf("%Ether.src%"))

        self.ans = ret
        return True

    def run(self):
        if hasScapy:
            return self.arping(self.target)
        else:
            self.gom.echo("No scapy support :(")
            return False

    def print_summary(self):
        self.gom.echo("List of discovered hosts")
        self.gom.echo("------------------------")
        self.gom.echo()

        for x, y in self.ans:
            ip = y.sprintf("%ARP.psrc%")
            mac = y.sprintf("%Ether.src%")
            vendor = getMacVendor(mac)
            self.gom.echo( str(mac) + " " + str(ip).ljust(15) + "(" + str(vendor) + ")" )
        self.gom.echo()
