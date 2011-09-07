#!/usr/bin/python

##      CWifi.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

from lib.module import CIngumaModule
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
