#!/usr/bin/python

##      CSniffer.py
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
NOTE: Can it be enhanced with an automatic fuzzer and traffic's graphics generator?
"""

import os
import sys
from lib.module import CIngumaModule

try:
    from scapy.modules.p0f import *
    import scapy.all as scapy

    bScapy = True
except:
    bScapy = False

try:
    from scapereal import *
    hasScapereal = True
except:
    hasScapereal = False

name = "sniffer"
brief_description = "A simple sniffer"
type = "gather"

class CSniffer(CIngumaModule):

    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    data = None
    filter = ""
    iface = None
    wizard = True

    def prnp0f(self, pkt):
        try:
            r = p0f(pkt)
            if r == []:
                r = ("UNKNOWN", "[" + ":".join(map(str, packet2p0f(pkt))) + ":?:?]", None)
            else:
                r = r[0]
        except:
            return
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

    def showPacket(self, packet):
        buf = None

        for x in packet:
            print x.summary()
            aux = scapy.PacketList(x, "packet")
            aux.rawhexdump()

        self.prnp0f(packet)

    def showHelp(self):
        print 
        print "Inguma's Sniffer Help"
        print "---------------------"
        print
        print "filter <pcap filter>         Specify a valid pcap filter"
        print "iface <iface>                Specify which iface will be used"
        print "run                          Start sniffing"
        print "save                         Save the packets to a file"
        print "help                         Show this help"
        print "exit                         Exit from the sniffer"
        print
        print "Sniffed packets commands"
        print "------------------------"
        print

        if not self.data:
            print "No sniffed data"
            print
        else:
            for command in dir(self.data):
                if command.startswith("_"):
                    continue
                else:
                    print "packets " + str(command)
            
            print 
            print "Commonly used commands are 'packets afterglow' and 'packets conversations'"
            print

            if hasScapereal:
                print "Scapereal commands (needs PyGTK)"
                print "--------------------------------"
                print
                print "ethereal                 Show in an ethereal like window"
                print

    def runPacketListCommand(self, args):
        try:
            if callable(eval("self.data." + args[0])):
                exec("self.data." + args[0] + "()")
            else:
                print eval("self.data." + args[0])
        except:
            print "Error.", sys.exc_info()[1]

    def doSaveFile(self):
        try:
            filename = raw_input("Output filename:")
            scapy.wrpcap(filename, self.data)
        except:
            print sys.exc_info()[1]

    def run(self):
        while 1:
            try:
                res = raw_input("SNIFFER> ")
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
            elif words[0].lower() == "sniff" or words[0] == "run":
                try:
                    print "Sniffing in iface", self.iface, "..."
                    self.data = scapy.sniff(prn = self.showPacket, filter=self.filter, iface = self.iface)
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
            elif words[0].lower() == "ethereal" and hasScapereal:
                ethereal(self.data)
            elif words[0].lower() == "save":
                self.doSaveFile()
            else:
                print "Unknown command or options '" + str(res) + "'"

        return True

    def printSummary(self):
        if self.data:
            self.data.show()
            print
            print "Sniffed a total of", len(self.data), "packet(s)"

