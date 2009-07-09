#!/usr/bin/python

"""
Module Wifi for Inguma
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

import sys
from lib.scapy import *
from lib.libexploit import CIngumaModule
from lib.libwifi import *

name = "wifi"
brief_description = "A simple passive information gathering tool for wireless networks"
type = "discover" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

globals = ['mode', ]

class CWifi(CIngumaModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

    interface = 'wlan0'
    mode = 'Beacon'

    def help(self):
        """ This is the entry point for info <module> """
        print "WARNING: Be sure to put your card in mode monitor!!"
        print "Channel hopping must be done externaly (Kismet)"
        print
        print "interface = <e.g. wlan0>"
        print "mode = <Beacon|NonBeacon|MAC|arpip>"
        print "       <Beacon: show devices that emit beacon>"
        print "       <NonBeacon: try to show 'hidden'devices>"
        print "       <MAC: list MAC addresses of AP and clients>"
        print "       <arpip: show device's MAC and IP when possible>"

    def run(self):
        """ This is the main entry point of the module """
        if self.mode == 'Beacon':
            sniff(iface=self.interface,prn=sniffBeacon)
        elif self.mode == 'NonBeacon':
            sniff(iface=self.interface,prn=sniffNonBeacon)
        elif self.mode == 'MAC':
            sniff(iface=self.interface,prn=sniffMAC)
        elif self.mode == 'arpip':
            sniff(iface=self.interface,prn=sniffarpip)
        else:
            print "Mode %s non valid" % (self.mode)
        return False

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
