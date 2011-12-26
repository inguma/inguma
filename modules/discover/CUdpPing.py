##      CUdpPing.py
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

from lib.module import CIngumaDiscoverModule

try:
    import scapy.all as scapy
    bHasScapy = True
except:
    bHasScapy = False

name = "udping"
brief_description = "UDP Ping"
type = "discover"

class CUdpPing(CIngumaDiscoverModule):

    port = 135
    waitTime = 0
    up = {}
    down = {}
    timeout = 2
    exploitType = 0
    results = {}
    iface = scapy.get_working_if()
    wizard = False
    dict = None

    def help(self):
        self.gom.echo('target = <target host or network>')
        self.gom.echo('timeout = <timeout>')
        self.gom.echo('waitTime = <wait time between packets>')
        self.gom.echo('port = <destination port to ping>')
        self.gom.echo('iface = <iface>')

    def run(self):
        if not bHasScapy:
            self.gom.echo('No scapy support :(')
            return False
        self.results = {}
        self.up = {}
        self.down = {}

        target = scapy.IP(dst=self.target)

        self.gom.echo("Sending probe to\t" + str(target.dst) + "\tusing port\t" + str(self.port))
        p = scapy.IP(dst=target.dst)/scapy.UDP(dport=self.port)

        ans, unans = scapy.sr(p, timeout=self.timeout, iface=self.iface, retry=0)

#            self.gom.echo(ans.summary( lambda(s,r) : r.sprintf("%IP.src% is alive") ))

        if ans:
            for a in ans:
                self.up[len(self.up)+1] = a[0][0].dst
                self.add_data_to_kb("alive", a[0][0].dst)
                self.add_data_to_kb("hosts", a[0][0].dst)
                self.add_data_to_kb("targets", a[0][0].dst)
                #self.add_data_to_kb(ans[0][0].dst + "_trace", ans[0][0].dst)
#                else:
#                    self.down[len(self.up)+1] = ans[0][0].dst
#                    self.gom.echo("Answer of type " + str(icmptypes[ans[0][0].type]) + " from " + str(ans[0][0].dst))

        self.results = self.up
        return True

    def print_summary(self):
        if len(self.results) == 0:
            return

        i = 0
        self.gom.echo()
        self.gom.echo("Discovered hosts")
        self.gom.echo("----------------")
        self.gom.echo()

        for res in self.results:
            i += 1
            self.gom.echo("Found host " + str(i) + "\t" + str(self.results[res]))

        self.gom.echo()
