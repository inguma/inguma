##      CNated.py
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

""" CNated module, check if some target ports are NATed. """

from lib.module import CIngumaDiscoverModule

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

name = "isnated"
brief_description = "Check if the target's port is NATed"
type = "discover"

class CNated(CIngumaDiscoverModule):
    target = "192.168.1.0/24"
    port = 0
    probe_results = {}

    def help(self):
        self.gom.echo("target = <target host or network>")
        self.gom.echo("timeout = <timeout>")

    def probe_icmp(self):
        p = scapy.IP(dst=self.target)/scapy.ICMP()
        res = scapy.sr1(p, timeout = self.timeout)
        hops = None

        if res:
            hops = res.ttl
        
        self.probe_results["ICMP"] = hops
        return hops
    
    def probe_tcp_port(self, port):
        p = scapy.IP(dst=self.target)/scapy.TCP(dport=int(port), flags="S")
        res = scapy.sr1(p, timeout = self.timeout)
        hops = None

        if res:
            hops = res.ttl

        self.probe_results[port] = hops
        return hops

    def is_nated_port(self, port):
        icmpTtl = self.probe_icmp()
        tcpTtl = self.probe_tcp_port(port)
        
        if icmpTtl != tcpTtl and icmpTtl != None and tcpTtl != None:
            return True

    def check_is_nated(self):
        ttls = []
        res = self.probe_icmp() # Do it just one time
        
        if res:
            ttls.append(res)

        for port in self.dict[self.target + "_tcp_ports"]:
            res = self.probe_tcp_port(port)
            
            if res:
                ttls.append(res)
        
        minTtl = min(ttls)
        maxTtl = max(ttls)
        
        if minTtl != maxTtl:
            self.gom.echo("Ports are NATed")
            return True
        else:
            self.gom.echo("Ports are NOT NATed")
            return False

    def run(self):
        if hasScapy:
            if self.port == 0:
                if self.dict.has_key(self.target + "_tcp_ports"):
                    return self.check_is_nated()
                else:
                    self.gom.echo("Can't check NATed ports for " + self.target + " without ports scanned")
                    self.gom.echo("Perform a portscan or tcpscan over " + self.target)
            else:
                if self.is_nated_port(self.port):
                    self.gom.echo("Port " + self.port + " is NATed")
                else:
                    self.gom.echo("Port " + self.port + " is NOT NATed")

            return True
        else:
            self.gom.echo("No scapy support :(")
            return False

    def print_summary(self):
        for res in self.probe_results:
            if res == "ICMP":
                if self.probe_results[res]:
                    self.gom.echo("ICMP TTL: " + str(self.probe_results[res]))
                else:
                    self.gom.echo("Target refuses ICMP traffic")
            else:
                self.gom.echo("TCP Port " + str(res) + " TTL: " + str(self.probe_results[res]))
