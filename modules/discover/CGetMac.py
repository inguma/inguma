##      CGetMac.py
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

try:
    from scapy.all import getmacbyip
    bHasScapy = True
except:
    bHasScapy = False

from lib.core import getMacVendor
from lib.module import CIngumaDiscoverModule

name = "getmac"
brief_description = "Get the host's MAC address"
type = "discover"

class CGetMac(CIngumaDiscoverModule):

    def help(self):
        self.gom.echo("target = <target host or network>")
    
    def print_summary(self):
        self.gom.echo(self.target + " MAC: " + self.mac +" " + getMacVendor(self.mac))

    def run(self):
        if self.target == "":
            self.gom.echo("No target specified")
            return False

        self.mac = getmacbyip(self.target)
        self.add_data_to_kb(self.target + "_mac", self.mac)
        self.add_data_to_kb(self.target + "_mac_vendor", getMacVendor(self.mac))
        return True
