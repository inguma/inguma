##      CPromisc.py
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

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "ispromisc"
brief_description = "Check if the target is in promiscuous mode"
type = "discover"

class CPromisc(CIngumaDiscoverModule):
    target = "192.168.1.0/24"
    exploitType = 1
    results = {}
    dict = None
    ret = False

    def help(self):
        self.gom.echo('target = <target host or network>')

    def run(self):
        if hasScapy:
            self.ret = scapy.is_promisc(self.target)
            self.add_data_to_kb(self.target + "_promisc", self.ret)
            self.gom.echo('Target ' + self.target + ' is promiscuous: ' + str(self.ret) )

            return True
        else:
            self.gom.echo('No scapy support :(')
            return False
