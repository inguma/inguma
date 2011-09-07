#!/usr/bin/python

##      CIkeScan.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import re
import sys
import binascii
import random

from lib.module import CIngumaModule

try:
    from scapy.all import *

    hasScapy = True
except:
    hasScapy = False

name = "ikescan"
brief_description = "An IKE Scan module to locate and identify VPN concentrators"
type = "gather"

class CIkeScan(CIngumaModule):

    sport = random.randint(1024, 65535)
    port = 500
    ntransforms = 8
    vendorID = {}
    vendorIDS = {}

    def __init__(self):
        self.readVendors()

    def readVendors(self):
        try:
            f = file("data/ike-vendor-ids", "r")
            lines = f.readlines()
            f.close()
    
        except:
            print sys.exc_info()[1]
            pass
    
        for line in lines:
            line = line.strip("\r").strip("\n") # Remove the 0x0d and 0x0a chars
            if not line.startswith('#') and len(line) > 0: #if the line is a comment or empty
                line = line.split("\t")
                if len(line) == 2:
                    idkey = line[1]
                    vendor = line[0]
                    self.vendorIDS[idkey] = vendor

    def help(self):

        print "target = <target host or network>"
        print "port = <target port>"

    def run(self):

        if self.target == "":
            self.gom.echo( "[+] No target specified" )
            return False

        if self.port == 0 or self.port is None:
            self.port = 500

        ans, unans = sr(IP(dst=self.target)/UDP(sport=self.port)/ISAKMP(exch_type=2,init_cookie=RandString(8))/ISAKMP_payload_SA(prop=ISAKMP_payload_Proposal(proto=1, res=0, next_payload=0, SPI='',trans_nb=8, SPIsize=0, trans=ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=1, transforms=[('Encryption', '3DES-CBC'), ('Hash', 'SHA'), ('Authentication', 'PSK'), ('GroupDesc', '1024MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=2, transforms=[('Encryption', '3DES-CBC'), ('Hash', 'MD5'), ('Authentication', 'PSK'), ('GroupDesc', '1024MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=3, transforms=[('Encryption', 'DES-CBC'), ('Hash', 'SHA'), ('Authentication', 'PSK'), ('GroupDesc', '1024MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=4, transforms=[('Encryption', 'DES-CBC'), ('Hash', 'MD5'), ('Authentication', 'PSK'), ('GroupDesc', '1024MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=5, transforms=[('Encryption', '3DES-CBC'), ('Hash', 'SHA'), ('Authentication', 'PSK'), ('GroupDesc', '768MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=6, transforms=[('Encryption', '3DES-CBC'), ('Hash', 'MD5'), ('Authentication', 'PSK'), ('GroupDesc', '768MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=3, num=7, transforms=[('Encryption', 'DES-CBC'), ('Hash', 'SHA'), ('Authentication', 'PSK'), ('GroupDesc', '768MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1)/ISAKMP_payload_Transform(res2=0, res=0, next_payload=0, num=8, transforms=[('Encryption', 'DES-CBC'), ('Hash', 'MD5'), ('Authentication', 'PSK'), ('GroupDesc', '768MODPgr'), ('LifeType', 'Seconds'), ('LifeDuration', 28800L)], id=1), proposal=1)),  timeout=self.timeout)

        if not ans:
            self.gom.echo( "No response recived from " + str(self.target) )
        else:
            for s, r in ans:
                if r.haslayer(ISAKMP_payload_VendorID):
                    self.vendorID[r.src] = r.vendorID
                    self.gom.echo( "Adding to discovered hosts " + str(r.src) )
                    self.addToDict("hosts", r.src)
                    return True
                else:
                    self.gom.echo( "No vendorID received :(\n" )
                    return False

    def getVendor(self, fingerprinting):
        for key in self.vendorIDS:
            objRe = re.compile(key, re.IGNORECASE)
            
            if objRe.search(fingerprinting):
                return self.vendorIDS[key]

    def printSummary(self):

        self.gom.echo( "" )
        self.gom.echo( "IKE Scan results" )
        self.gom.echo( "----------------" )
        self.gom.echo( "" )

        for host in self.vendorID:
        
            fingerprinting = binascii.b2a_hex(self.vendorID[host])
            vendor = self.getVendor(fingerprinting)

            self.gom.echo( "Host     : " + str(host) )
            self.gom.echo( "Vendor   :" + str(vendor) )
            self.gom.echo( "Vendor Id: " + str(fingerprinting) )
            
            self.addToDict(self.target + "_ikevendor", vendor)
            self.addToDict(self.target + "_ikefingerprinting", fingerprinting)

