#!/usr/bin/python

"""
Module nids for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

"""
NOTE: Subject to be removed.
"""

import os
import re
import sys

from lib.libexploit import CIngumaModule

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

class CIds(CIngumaModule):

    target = ""
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
                print "*****************************************************************************"
                print "Attack detected by rule id %d:" % idx
                print aux.sprintf("%.time% %-15s,IP.src% -> %-15s,IP.dst%")
                print
                try:
                    print self.realRules[idx]["attack"]
                except:
                    pass
                print
                try:
                    print "Tip:", self.realRules[idx]["ids"]
                except:
                    pass
                print "*****************************************************************************"
                print

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
                                print "Rule does not compile:", sys.exc_info()[1]
                except:
                    #
                    # Ignore the exception, we can continue anyway
                    #
                    print "Snort:", sys.exc_info()[1]
        except:
            print "Can't read rules.py file. No rules."
            print sys.exc_info()[1]
            return

        print "Running Intrusion Detection System ... "
        scapy.sniff(iface = self.iface, filter = self.filter, prn= self.checkRule)

    def showHelp(self):
        print 
        print "Inguma's Intrusion Detection System Help"
        print "----------------------------------------"
        print
        print "run                          Run the Intrusion Detection System"
        print "help                         Show this help"
        print "exit                         Exit from the IDS interface"
        print "filter <pcap filter>         Specify a valid pcap filter"
        print "iface <iface>                Specify which iface will be used"
        print

    def runIdsLoop(self):
        while 1:
            try:
                res = raw_input("IDS> ")
                words = res.split(" ")

                if len(words) == 1 and words[0] == "":
                    continue
                elif words[0].lower() == "help":
                    self.showHelp()
                elif words[0].lower() == "run":
                    self.runIds()
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
                elif words[0].lower() == "exit" or words[0].lower() == "quit":
                    break
                else:
                    print "Unknow command or option '" + str(res) + "'"

            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "IDS Error.", sys.exc_info()[1]

    def run(self):
        self.runIdsLoop()
        return True

    def printSummary(self):
        pass
        #print "Not yet implemented"
