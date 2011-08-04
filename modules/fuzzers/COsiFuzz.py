#!/usr/bin/python

"""
Fuzzer interface for OSI layer 2 and 3 protocolos
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
"""

"""
NOTE: Many fuzzers *ARE NOT* implemented
"""

import sys
from lib.module import CIngumaModule

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

class COsiFuzz(CIngumaModule):

    port = 0 # Port to be used
    waitTime = 0 # Time to wait between step and step
    timeout = 1 # Default timeout
    exploitType = 1
    services = {}
    results = {}
    dict = None
    iface = None
    filter = None

    def showHelp(self):
        print
        print "Inguma's OSI fuzzing Interface Help"
        print "-----------------------------------"
        print
        print "iface <iface>                Specify which iface will be used"
        print "timeout <timeout>            Specify the timeout"
        print "src=<target>                 Set the source address"
        print "dst=<target>                 Set the destination to fuzz (default target)"
        print "dport=<dport>                Set the destination port"
        print "sport=<sport>                Set the source port"
        print "ttl=<ttl>                    Set the packet's TTL"
        print "tos=<tos>                    Set the packet's TOS"
        print "seq=<seq>                    Set the sequence"
        print "IP                           Send fuzzed IP frames"
        print "TCP                          Send fuzzed TCP frames"
        print "UDP                          Send fuzzed UDP frames"
        print "ARP                          Send fuzzed ARP frames"
        print "ICMP                         Send fuzzed ICMP frames"
        print "help                         Show this help"
        print "exit                         Exit from the OSI fuzz interface"
        print

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
            print "Sending ethernet frames to the broadcast address (ff:ff:ff:ff:ff:ff) ... "

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

                #print "Sended %d packets" % idx

                if ans:
                    print "-----> Sent"
                    print p.summary()
                    hexdump(str(p))

                    print "-----> Got reponse"
                    ans.display()
                    ans.rawhexdump()
                    print

            except KeyboardInterrupt:
                print "Stoped."
                break
            except:
                print "Error.", sys.exc_info()[1]

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
            elif words[0].lower() == "iface":
                if len(words) > 1:
                    self.iface = words[1]
                    
                    if self.iface == "":
                        self.iface = None

                    print "Interface is:", self.iface
            elif words[0].lower() == "timeout":
                if len(words) > 1:
                    self.timeout = float(words[1])
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() == "quit" or words[0].lower() == "exit":
                break
            elif words[0].lower() in ["ip", "icmp", "arp"]:
                self.fuzzCommand(words[0])
            else:
                try:
                    exec(res)
                except:
                    print "Error.", sys.exc_info()[1]

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
