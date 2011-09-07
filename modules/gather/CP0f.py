#!/usr/bin/python

"""
p0f interface module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
"""

import sys
from lib.module import CIngumaModule

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

class CP0f(CIngumaModule):

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
            self.addToDict(pkt.sprintf("%IP.src%") + "_os", r[0:1])

        uptime = None
        try:
            uptime = pkt2uptime(pkt)
        except:
            pass
        if uptime == 0:
            uptime = None
        res = pkt.sprintf("%IP.src%:%TCP.sport% - " + r[0] + " " + r[1])
        self.addToDict("hosts", pkt.sprintf("%IP.src%"))

        if uptime is not None:
            res += pkt.sprintf(" (up: " + str(uptime/3600) + " hrs)\n  -> %IP.dst%:%TCP.dport%")
            self.addToDict(pkt.sprintf("%IP.src%") + "_uptime", str(uptime/3600))
        else:
            res += pkt.sprintf("\n  -> %IP.dst%:%TCP.dport%")

        if r[2] is not None:
            res += " (distance " + str(r[2]) + ")"
            self.addToDict(pkt.sprintf("%IP.src%") + "_distance", str(r[2]))

        print
        print "P0F: " + str(res)
        print 

    def show_help(self):
        print
        print "Inguma's p0f Interface Help"
        print "---------------------------"
        print
        print "filter <pcap filter>         Specify a valid pcap filter"
        print "iface <iface>                Specify which interface will be used"
        print "run | p0f                    Start p0f-ing"
        print "help | h | ?                 Show this help"
        print "exit | quit | ..             Exit from the p0f interface"
        print

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
                print "Filter is:", buf
            elif words[0].lower()  in ["p0f", "run"]:
                try:
                    print "Sniffing in iface", self.iface, "..."
                    if bScapy:
                        self.data = scapy.sniff(prn = self.prnp0f, filter=self.filter, iface = self.iface)
                    else:
                        print "No scapy support :("
                except KeyboardInterrupt:
                    break
                except:
                    print "Internal error.", sys.exc_info()[1]
            elif words[0].lower() == "iface":
                if len(words) > 1:
                    self.iface = words[1]
                    
                print "Interface is:", self.iface
            else:
                print "Unknown command or options '" + str(res) + "'"

        return True

    def run(self):
        return self.p0fLoop()
