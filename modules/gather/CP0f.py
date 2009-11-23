#!/usr/bin/python

"""
p0f interface module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
"""
import os
import sys
from lib.libexploit import CIngumaModule

try:
    from scapy.modules.p0f import *
    import scapy.all as scapy

    bScapy = True
except:
    bScapy = False

name = "p0f"
brief_description = "Inguma's p0f interface -os detection-"
type = "gather"

class CP0f(CIngumaModule):

    target = ""  # Main target
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
            r = scapy.p0f(pkt)
        except:
            return
        if r == []:
            r = ("UNKNOWN", "[" + ":".join(map(str, scapy.packet2p0f(pkt))) + ":?:?]", None)
        else:
            r = r[0]
        
        self.addToDict(pkt.sprintf("%IP.src%") + "_os", r)

        uptime = None
        try:
            uptime = scapy.pkt2uptime(pkt)
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

    def showHelp(self):
        print
        print "Inguma's p0f Interfaces Help"
        print "----------------------------"
        print
        print "filter <pcap filter>         Specify a valid pcap filter"
        print "iface <iface>                Specify which iface will be used"
        print "run                          Start p0f-ing"
        print "help                         Show this help"
        print "exit                         Exit from the p0f interface"
        print

    def p0fLoop(self):
        while 1:
            try:
                res = raw_input("P0F> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
                
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "filter":
                buf = ""
                for word in words[1:]:
                    buf += word + " "

                self.filter = buf
                print "Filter is:", buf
            elif words[0].lower() == "p0f" or words[0] == "run":
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
                    
                    if self.iface == "":
                        self.iface = None

                    print "Interface is:", self.iface
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() == "quit" or words[0].lower() == "exit":
                break
            elif words[0].lower() == "packets":
                self.runPacketListCommand(words[1:])
            else:
                print "Unknown command or options '" + str(res) + "'"

        return True

    def run(self):
        return self.p0fLoop()

    def printSummary(self):
        pass
