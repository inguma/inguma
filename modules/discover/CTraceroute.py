##      CTraceroute.py
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

import random

from lib.module import CIngumaDiscoverModule

try:
    from scapy.all import IP, TCP, sr, conf, TracerouteResult

    bHasScapy = True
except:
    bHasScapy = False

name = "tcptrace"
brief_description = "Trace a route to a host(s)"
type = "discover"

class CTraceroute(CIngumaDiscoverModule):

    ports = [21, 22, 23, 80, 443, 135, 139, 445, 1521, 1526, 1531, 1541, 1551, 1561, 7777, 7999, 8000, 8001, 8002, 8888]
    sport = random.randint(1024, 65535)
    dport = 80
    hosts = {}
    timeout = 10
    iface = conf.iface
    tcp = 1
    minttl = 1
    maxttl = 20
    exploitType = 0
    results = {}
    wizard = False
    packets = None
    dict = None

    def help(self):
        self.gom.echo('target = <target host or network>')
        self.gom.echo('timeout = <timeout>')
        self.gom.echo('minttl = <minimum ttl>')
        self.gom.echo('maxttl = <maximum ttl>')
        self.gom.echo('sport = <source port>')
        self.gom.echo('dport = <destination port>')
        self.gom.echo('iface = <interface to use>')

    def run(self):
        if not bHasScapy:
            self.gom.echo('No scapy support :(')
            return False

        self.hosts = {}
        #mwaaaaaaaaaaaaaaaaaaaaaaaaaa
        #self.dict["hosts"] = []

        if self.tcp == 1:
            a,b = sr(IP(dst=self.target, ttl=(self.minttl,self.maxttl))/TCP(sport=self.sport, dport=self.dport), timeout=self.timeout, iface = self.iface, retry = 0)
        else:
            a,b = sr(IP(dst=self.target, ttl=(self.minttl,self.maxttl)), retry=0)

        a = TracerouteResult(a.res)
        #a.make_graph()
        self.packets = a

        start = 0
        for x in a:
            i = 0
            for y in x:
                if start == 0:
                    start = 1
                    self.hosts[len(self.hosts)+1] = y.src
                    self.add_data_to_kb("hosts", y.src)

                    continue

                if i == 0:
                    i = 1
                    continue

                self.hosts[len(self.hosts)+1] = y.src
                self.add_data_to_kb("hosts", y.src)

        try:
            self.hosts[len(self.hosts)+1] = y.src
            self.add_data_to_kb("hosts", y.src)
        except:
            # Ugly hack
            pass

        self.results = self.hosts
        return True

    def print_summary(self):
        idx = 0
        prevHost = ""

        if self.wizard:
            res = raw_input("Show graph (y/n) [y]: ")

            if res == "" or res.lower() == "y":
                res = raw_input("Path to file (otherwise display using ImageMagick): ")
                res3d = raw_input("Graphic 3D (y/n) [n]?: ")

                if res == "":
                    if res3d == "y":
                        self.packets.trace3D()
                    else:
                        self.packets.graph()
                else:
                    if res3d == "y":
                        self.packets.trace3D(target="> " + str(res))
                    else:
                        self.packets.graph(target="> " + str(res))

                return True

        self.gom.echo()
        self.gom.echo("Trace to target(s)")
        self.gom.echo("------------------")
        self.gom.echo()

        self.trace = []
        for res in self.results:
            idx += 1

            if prevHost == "":
                prevHost = self.results[res]
            elif prevHost == self.results[res]:
                self.gom.echo("Prev host: " + prevHost + " actual host: " + self.results[res])
                continue
            else:
                prevHost = self.results[res]

            self.gom.echo("host " + str(idx) + "\t" + str(self.results[res]))
            self.trace.append(self.results[res])

        self.gom.echo()
        for element in self.trace:
            self.add_data_to_kb(self.target + "_trace", element)
            self.add_data_to_kb("targets", self.target)
