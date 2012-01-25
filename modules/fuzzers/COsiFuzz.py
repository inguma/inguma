"""
Fuzzer interface for OSI layer 2 and 3 protocols
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

"""
NOTE: Many fuzzers *ARE NOT* implemented
"""

import sys
from lib.module import CIngumaFuzzerModule

try:
    from scapy.all import *

    bScapy = True
except:
    bScapy = False

name = "osifuzz"
brief_description = "Fuzzing interface for IP, ICMP and ARP protocols (Random)"
type = "fuzzer"

global src
global dst
global dport
global sport
global ttl
global tos
global flags
global seq

src=None
dst=None
dport=None
sport=None
ttl=None
tos=None
flags=None
seq=None

class COsiFuzz(CIngumaFuzzerModule):

    port = 0 # Port to be used
    waitTime = 0 # Time to wait between step and step
    timeout = 1 # Default timeout
    exploitType = 1
    services = {}
    results = {}
    dict = None
    iface = None
    filter = None

    def help_interactive(self):
        self.gom.echo()
        self.gom.echo("Inguma's OSI fuzzing Interface Help")
        self.gom.echo("-----------------------------------")
        self.gom.echo()
        self.gom.echo("iface <iface>                Specify which iface will be used")
        self.gom.echo("timeout <timeout>            Specify the timeout")
        self.gom.echo("src=<target>                 Set the source address")
        self.gom.echo("dst=<target>                 Set the destination to fuzz (default target)")
        self.gom.echo("dport=<dport>                Set the destination port")
        self.gom.echo("sport=<sport>                Set the source port")
        self.gom.echo("ttl=<ttl>                    Set the packet's TTL")
        self.gom.echo("tos=<tos>                    Set the packet's TOS")
        self.gom.echo("seq=<seq>                    Set the sequence")
        self.gom.echo("IP                           Send fuzzed IP frames")
        self.gom.echo("TCP                          Send fuzzed TCP frames")
        self.gom.echo("UDP                          Send fuzzed UDP frames")
        self.gom.echo("ARP                          Send fuzzed ARP frames")
        self.gom.echo("ICMP                         Send fuzzed ICMP frames")
        self.gom.echo("help                         Show this help")
        self.gom.echo("exit                         Exit from the OSI fuzz interface")
        self.gom.echo()

    def fuzzCommand(self, command):
        global src
        global dst
        global dport
        global sport
        global ttl
        global tos
        global flags
        global seq

        command = command.lower()

        if dst != None and dst != "":
            self.target = dst

        idx = 0

        if command == "arp":
            self.gom.echo("Sending ethernet frames to the broadcast address (ff:ff:ff:ff:ff:ff) ... ")

        while 1:
            try:
                if command == "ip":
                    p=fuzz(IP(dst=self.target, ttl=ttl, tos=tos))
                elif command == "icmp":
                    p=IP(dst=self.target, ttl=ttl, tos=tos)/fuzz(ICMP())
                elif command == "arp":
                    p = Ether(dst="ff:ff:ff:ff:ff:ff")/fuzz(ARP(pdst=self.target))

                if command in ["ip", "icmp"]:
                    ans, unans = sr(p, timeout = self.timeout)
                elif command in ["arp"]:
                    ans, unans = srp(p, timeout = self.timeout)

                idx += 1

                #self.gom.echo("Sent %d packets" % idx)

                if ans:
                    self.gom.echo("-----> Sent")
                    self.gom.echo(p.summary())
                    hexdump(str(p))

                    self.gom.echo("-----> Got reponse")
                    ans.display()
                    ans.rawhexdump()
                    self.gom.echo()

            except KeyboardInterrupt:
                self.gom.echo("Stoped.")
                break
            except:
                self.gom.echo("Error.", sys.exc_info()[1])

    def osiFuzzLoop(self):
        global src
        global dst
        global dport
        global sport
        global ttl
        global tos
        global flags
        global seq

        while 1:
            try:
                res = raw_input("osifuzz> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                self.gom.echo("raw_input:", sys.exc_info()[1])

            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "filter":
                buf = ""
                for word in words[1:]:
                    buf += word + " "

                self.filter = buf
                self.gom.echo("Filter is:", buf)
            elif words[0].lower() == "iface":
                if len(words) > 1:
                    self.iface = words[1]

                    if self.iface == "":
                        self.iface = None

                    self.gom.echo("Interface is:", self.iface)
            elif words[0].lower() == "timeout":
                if len(words) > 1:
                    self.timeout = float(words[1])
            elif words[0].lower() == "help":
                self.help_interactive()
            elif words[0].lower() == "quit" or words[0].lower() == "exit":
                break
            elif words[0].lower() in ["ip", "icmp", "arp"]:
                self.fuzzCommand(words[0])
            else:
                try:
                    exec(res)
                except:
                    self.gom.echo("Error.", sys.exc_info()[1])

        return True

    def run(self):
        global src
        global dst
        global dport
        global sport
        global ttl
        global tos
        global flags
        global seq

        dst = self.target

        if self.port != 0:
            sport = self.port

        return self.osiFuzzLoop()
