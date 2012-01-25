##      CIds.py
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

"""
NOTE: Subject to be removed.
"""

import re
import sys

from lib.module import CIngumaGatherModule

try:
    from libsnort import *
    snortSupport = True
except:
    snortSupport = False
try:
    import scapy.all as scapy

    bScapy = True
except:
    bScapy = False

name = "nids"
brief_description = "A simple network based Intrusion Detection System (IDS)"
type = "gather"

class CIds(CIngumaGatherModule):

    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    data = None
    filter = ""
    iface = None
    wizard = True
    rules = []
    realRules = None
    dict = None

    def checkRule(self, packet):
        aux = scapy.PacketList(packet, "packet")
        data = aux.__iter__().next().build()
        data = data.replace("\x00", "")
        idx = -1

        for rule in self.rules:
            idx += 1

            if rule.findall(data):
                self.gom.echo("*****************************************************************************")
                self.gom.echo("Attack detected by rule id %d:" % idx)
                self.gom.echo(aux.sprintf("%.time% %-15s,IP.src% -> %-15s,IP.dst%"))
                self.gom.echo()
                try:
                    self.gom.echo(self.realRules[idx]["attack"])
                except:
                    pass
                self.gom.echo()
                try:
                    self.gom.echo("Tip:", self.realRules[idx]["ids"])
                except:
                    pass
                self.gom.echo("*****************************************************************************")
                self.gom.echo()

    def runIds(self, mrules = False):
        try:
            if not mrules:
                from rules import rules
                mrules = rules

            self.realRules = mrules

            for rule in mrules:
                self.rules.append(re.compile(rule["data"], re.IGNORECASE))

            if snortSupport:
                try:
                    snortRuleParser = CSnortRuleParser()
                    snortRuleParser.parse("oracle.rules")

                    for rule in snortRuleParser.rules:

                        if rule.pcre != "" or len(rule.contents) > 0:

                            try:
                                if rule.pcre != "":
                                    data = rule.pcre
                                else:
                                    continue # Ignore. At the moment there is no good support for content and content! rules
                                    data = ".*" + rule.contents[0] + ".*"

                                p = re.compile(data, re.IGNORECASE)

                                arule = {}
                                arule["data"] = data
                                arule["name"] = rule.msg
                                arule["description"] = rule.msg
                                arule["type"] = rule.classtype
                                arule["attack"] = rule.msg
                                arule["tip"] = ""
                                arule["ids"] = ""
                                arule["default_port"] = ""

                                self.rules.append(p)
                                self.realRules.append(arule)
                            except:
                                self.gom.echo("Rule does not compile:", sys.exc_info()[1])
                except:
                    #
                    # Ignore the exception, we can continue anyway
                    #
                    self.gom.echo("Snort:", sys.exc_info()[1])
        except:
            self.gom.echo("Can't read rules.py file. No rules.")
            self.gom.echo(sys.exc_info()[1])
            return

        self.gom.echo("Running Intrusion Detection System ... ")
        scapy.sniff(iface = self.iface, filter = self.filter, prn= self.checkRule)

    def show_help(self):
        self.gom.echo()
        self.gom.echo("Inguma's Intrusion Detection System Help")
        self.gom.echo("----------------------------------------")
        self.gom.echo()
        self.gom.echo("run                          Run the Intrusion Detection System")
        self.gom.echo("help | h | ?                 Show this help")
        self.gom.echo("exit | quit | ..             Exit from the IDS interface")
        self.gom.echo("filter <pcap filter>         Specify a valid pcap filter")
        self.gom.echo("iface <iface>                Specify which iface will be used")
        self.gom.echo()

    def runIdsLoop(self):
        import lib.ui.cli.core as CLIcore

        while 1:
            res = CLIcore.unified_input_prompt(self, 'nids')
            if res == None:
                break

            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "run":
                self.runIds()
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
            else:
                self.gom.echo("Unknown command or option '" + str(res) + "'")

    def run(self):
        self.runIdsLoop()
        return True
