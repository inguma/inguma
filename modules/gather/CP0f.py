"""
p0f interface module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

import sys
from lib.module import CIngumaGatherModule

try:
    from scapy.modules.p0f import *
    import scapy.all as scapy

    scapy.conf.p0f_base = 'data/p0f/p0f.fp'
    scapy.conf.p0fa_base = 'data/p0f/p0fa.fp'
    scapy.conf.p0fo_base = 'data/p0f/p0fo.fp'
    scapy.conf.p0fr_base = 'data/p0f/p0fr.fp'

    bScapy = True
except:
    bScapy = False

name = "p0f"
brief_description = "Inguma's p0f interface -os detection-"
type = "gather"

class CP0f(CIngumaGatherModule):

    port = 0 # Port to be used
    waitTime = 0 # Time to wait between step and step
    timeout = 1 # Default timeout
    exploitType = 1
    services = {}
    results = {}
    dict = None
    iface = None
    filter = None

    def prnp0f(self, pkt):
        try:
            r = p0f(pkt)
        except:
            return
        if r == []:
            r = ("UNKNOWN", "[" + ":".join(map(str, packet2p0f(pkt)[1])) + ":?:?]", None)
        else:
            r = r[0]
            self.add_data_to_kb(pkt.sprintf("%IP.src%") + "_os", r[0:1])

        uptime = None
        try:
            uptime = pkt2uptime(pkt)
        except:
            pass
        if uptime == 0:
            uptime = None
        res = pkt.sprintf("%IP.src%:%TCP.sport% - " + r[0] + " " + r[1])
        self.add_data_to_kb("hosts", pkt.sprintf("%IP.src%"))

        if uptime is not None:
            res += pkt.sprintf(" (up: " + str(uptime/3600) + " hrs)\n  -> %IP.dst%:%TCP.dport%")
            self.add_data_to_kb(pkt.sprintf("%IP.src%") + "_uptime", str(uptime/3600))
        else:
            res += pkt.sprintf("\n  -> %IP.dst%:%TCP.dport%")

        if r[2] is not None:
            res += " (distance " + str(r[2]) + ")"
            self.add_data_to_kb(pkt.sprintf("%IP.src%") + "_distance", str(r[2]))

        self.gom.echo()
        self.gom.echo("P0F: " + str(res))
        self.gom.echo()

    def show_help(self):
        self.gom.echo()
        self.gom.echo("Inguma's p0f Interface Help")
        self.gom.echo("---------------------------")
        self.gom.echo()
        self.gom.echo("filter <pcap filter>         Specify a valid pcap filter")
        self.gom.echo("iface <iface>                Specify which interface will be used")
        self.gom.echo("run | p0f                    Start p0f-ing")
        self.gom.echo("help | h | ?                 Show this help")
        self.gom.echo("exit | quit | ..             Exit from the p0f interface")
        self.gom.echo()

    def p0fLoop(self):
        import lib.ui.cli.core as CLIcore

        while 1:
            res = CLIcore.unified_input_prompt(self, 'p0f')
            if res == None:
                break

            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "filter":
                buf = ""
                for word in words[1:]:
                    buf += word + " "

                self.filter = buf
                self.gom.echo("Filter is:", buf)
            elif words[0].lower()  in ["p0f", "run"]:
                try:
                    self.gom.echo("Sniffing in iface", self.iface, "...")
                    if bScapy:
                        self.data = scapy.sniff(prn = self.prnp0f, filter=self.filter, iface = self.iface)
                    else:
                        self.gom.echo("No scapy support :(")
                except KeyboardInterrupt:
                    break
                except:
                    self.gom.echo("Internal error.", sys.exc_info()[1])
            elif words[0].lower() == "iface":
                if len(words) > 1:
                    self.iface = words[1]

                self.gom.echo("Interface is:", self.iface)
            else:
                self.gom.echo("Unknown command or options '" + str(res) + "'")

        return True

    def run(self):
        return self.p0fLoop()
