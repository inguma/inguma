#!/usr/bin/python
# -*- coding: latin1 -*-

"""
Inguma Penetration Testing Toolkit 0.1.0
Copyright (c) 2008 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import time
import struct
import base64

# Platform type values
INFORMIX_TYPE_IEEEI = 'IEEEI'
INFORMIX_TYPE_IEEEM = 'IEEEM'
INFORMIX_TYPE_DECALPHA = 'DECALPHA'

#
# For OPCODE commands (jmpsql[edx*4])
#
# If the response to any of them is INFORMIX_RESPONSE_ERROR
# the command sent is incorrect.
#
# In example, a call to PREPARE or ID would response with the
# constant INFORMIX_RESPONSE_VALID to be valid.
#

INFORMIX_RESPONSE_ERROR = '\x008'
INFORMIX_RESPONSE_VALID = '\x00\x0c'

#
# List of OPCODES (Not yet complete)
#
# Extracted from jmpsql array
#
IFX_OPCODE_DUMMY     = "\x00"
IFX_OPCODE_CMND      = "\x01"
IFX_OPCODE_PREPARE   = "\x02"
IFX_OPCODE_CURNAME   = "\x03"
IFX_OPCODE_ID        = "\x04"
IFX_OPCODE_BIND      = "\x05"
IFX_OPCODE_OPEN      = "\x06"
IFX_OPCODE_EXECUTE   = "\x07"
IFX_OPCODE_DESCRIBE  = "\x08"
IFX_OPCODE_NFETCH    = "\x09"
IFX_OPCODE_CLOSE     = "\x10"
IFX_OPCODE_RELEASE   = "\x11"
IFX_OPCODE_EOT       = "\x12"
IFX_OPCODE_EXSELECT  = chr(16)
IFX_OPCODE_PUTINSERT = chr(17)
IFX_OPCODE_COMMIT    = chr(19)
IFX_OPCODE_ROLLBACK  = chr(20)
IFX_OPCODE_SAVEPOINT = chr(21)
IFX_OPCODE_NDESCRIBE = chr(22)
IFX_OPCODE_SFETCH    = chr(23)
IFX_OPCODE_SCROLL    = chr(24)
IFX_OPCODE_DBLIST    = chr(26)
IFX_OPCODE_BEGINWORK = chr(35)
IFX_OPCODE_DBOPEN    = chr(36)
IFX_OPCODE_DBCLOSE   = chr(37)
IFX_OPCODE_FETCHBLOB = chr(38)
IFX_OPCODE_BBIND     = chr(41)
IFX_OPCODE_DPREPARE  = chr(42)
IFX_OPCODE_HOLD      = chr(43)
IFX_OPCODE_DCATALOG  = chr(44)
IFX_OPCODE_ISOLEVEL  = chr(47)
IFX_OPCODE_LOCKWAIT  = chr(48)
IFX_OPCODE_WANTDONE  = chr(49)
IFX_OPCODE_REMVIEW   = chr(50)
IFX_OPCODE_REMPERMS  = chr(51)
IFX_OPCODE_SBBIND    = chr(52)
IFX_OPCODE_VERSION   = chr(53)
IFX_OPCODE_DEFER     = chr(54)
IFX_OPCODE_EXIT      = chr(56)
IFX_OPCODE_REMPROC   = chr(58)
IFX_OPCODE_EXPROC    = chr(59)
IFX_OPCODE_REMDML    = chr(60)
IFX_OPCODE_TXPREPARE = chr(61)
IFX_OPCODE_TXFORGET  = chr(63)
IFX_OPCODE_KPREPARE  = "\x86"
IFX_OPCODE_PROTOCOLS = "\x7e"
IFX_OPCODE_INFO      = "Q"

def toStringTypeC(str):
    return chr(len(str)) + str + "\x00"

def str2c(str):
    fmt = "h%ds" % (len(str))
    return struct.pack(fmt, len(str), str)

class InformixInfoCommand:
    header = '\x00Q\x00\x06\x01\x18\x00\x0c\x00\xb6'
    dbTemp = '\x00\x06DBTEMP\x00'
    tmpDir = '\x04/tmp\x00'
    shell = '\x05SHELL\x00'
    shellPath = '\x00\t/bin/bash\x00'
    null2 = '\x00'
    subqcache = '\x0bSUBQCACHESZ\x00'
    null3 = '\x00'
    unknown_value = '\x0210\x00'
    ifxUpdesc = '\x0bIFX_UPDDESC\x00'
    null4 = '\x00'
    unknown_value2 = '\x011\x00'
    null5 = '\x00'
    path = '\x04PATH\x00'
    pathDesc = '\xb5/opt/IBM/informix/bin:/home/joxean/bin:/home/joxean/devel/java/jre1.5.0_10//bin:/home/joxean/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/bin/X11:/usr/games\x00'
    null6 = '\x00'
    noDefDac = '\x08NODEFDAC\x00'
    noDefDacValue = '\x02no\x00'
    footer = '\x00\x00\x00\x00\x0c'

    def getPacket(self):
        buf  = self.header
        buf += str2c(self.dbTemp)
        buf += toStringTypeC(self.tmpDir)
        buf += toStringTypeC(self.shell)
        buf += str2c(self.shellPath)
        buf += str2c(self.subqcache)
        buf += str2c(self.unknown_value)
        buf += toStringTypeC(self.ifxUpdesc)
        buf += str2c(self.unknown_value2)
        buf += str2c(self.path)
        buf += str2c(self.pathDesc)
        buf += toStringTypeC(self.noDefDac)
        buf += toStringTypeC(self.noDefDacValue)
        buf += self.footer

        return buf

class InformixDbListResponse:

    isValidUser = False
    databases = []

    def parse(self, buf):
        buf = buf[3:]
        while 1:
            if len(buf) == 0:
                break

            size = ord(buf[0])

            if size == 0:
                buf = buf[1:]
                continue
            else:
                size += 1

            self.databases.append(buf[1:size])
            #print "[+] Adding database %s" % buf[1:size]
            buf = buf[size+1:]

class InformixCommand:
    """ Constructs a valid SQL statement's packet """
    opcode = IFX_OPCODE_CMND
    header = "\x00%s\x00\x00\x00"
    footer = "\x00\x00\x16\x00\x31\x00\x0c"
    sql = ""

    def getPacket(self):
        buf = self.header % self.opcode
        
        if type(self.sql) is list:
            for sql in self.sql:
                buf += chr(len(sql))
                buf += sql
        else:
            buf += chr(len(self.sql))
            buf += self.sql

        buf += self.footer

        return buf

class InformixLoginResponse:
    
    """ Read and parse a login response """
    isValidUser = False
    isValidDatabase = False
    ieee = None
    name = None
    banner = None
    serialNumber = None
    databasePath = None
    protocol = None
    hostname = None
    terminal = None
    homePath = None

    def parse(self,  buf):
        try:
            if len(buf) < 50:
                raise Exception("Invalid packet")
            
            self.isValidUser = buf[0] == "\x01"
            self.isValidDatabase = buf[1:3] == "\x05\x02"
            
            #
            # IEEE is the platform type. This can be IEEEI, IEEEM or DECALPHA
            #
            ieeeLen = ord(buf[15:16])
            self.ieee = buf[16:16+ieeeLen-1]
            self.name = buf[23:37].strip("\x00")
            
            bannerLen = ord(buf[37:38])
            self.banner = buf[38:bannerLen+38-1]
            
            curPos = bannerLen+38+2
            lastPos = buf[curPos:].find("\x00")
            
            if lastPos > -1:
                self.serialNumber = buf[curPos:curPos+lastPos]
            else:
                raise Exception("Invalid serial number in packet")
            
            curPos = curPos+lastPos+2
            dbPathLen = ord(buf[curPos])
            self.databasePath = buf[curPos+1:curPos+dbPathLen]
            
            curPos = curPos+dbPathLen+30+1
            lastPos = buf[curPos:].find("\x00")
            
            if lastPos > -1:
                self.protocol = buf[curPos:curPos+lastPos]
            else:
                raise Exception("Invalid protocol in packet")
                
            curPos = curPos+lastPos
            lastPos = 37
            hostnameLen = ord(buf[curPos+lastPos])
            curPos = curPos+lastPos
            self.hostname = buf[curPos+1:curPos+hostnameLen]
            curPos = curPos + hostnameLen + 2
            terminalLen = ord(buf[curPos])
            
            self.terminal = buf[curPos+1:curPos+terminalLen]
            
            curPos = curPos+terminalLen+2
            installLen = ord(buf[curPos])
            
            self.homePath = buf[curPos+1:curPos+installLen]
        except:
            print "***Error:", sys.exc_info()[1]
            print "Packet is:"
            print repr(buf)
            print

class Informix:

    """ Login stuff """
    # Private properties
    __sqlexec2nd = "\x00\x7e\x00\x07\xff\xfe\x9f\xfe\x74\xaa\x52\x00\x00\x0c"

    header = 'sq'
    encodedSize = 'Abg'
    fixedHeader = 'BPQAAsqlexec'
    username = 'test'
    password = 'test'
    version = '9.350'
    serialNumber = 'AAA#B000000'
    databaseName = 'testdb'
    ieee = 'IEEEI'
    databasePath = '//demo_on'
    databaseMoney = '$.'
    clientLocale = 'en_US.8859-1'
    singleLevel = 'no'
    lkNotify = 'yes'
    lockDown = 'no'
    noDefDac = 'no'
    clientPamCapable = '1'
    encodedData = ':AG0AAAA9b24AAAAAAAAAAAA9c29jdGNwAAAAAAABAAABPAAAAAAAAAAAc3FsZXhlYwAAAAAAAAVzcWxpAAALAAAAAwAIZGVtb19vbgAAawAAAAAAAAfwAAAAAAAPam94ZWFuLWRlc2t0b3AAAAsvZGV2L3B0cy81AAAwL2hvbWUvam94ZWFuL3Byb3llY3Rvcy90b29sL3Rvb2xzL2Z1enovaW5mb3JtaXgAAHQACAAAA.gAAAPoAH8'

    def getPacket(self):
        buf = self.header
        buf += 'KK'
        buf += self.fixedHeader

        data  = ' %s -p%s %s %s -d%s -f%s DBPATH=%s DBMONEY=%s CLIENT_LOCALE=%s SINGLELEVEL=%s '
        data += 'LKNOTIFY=%s LOCKDOWN=%s NODEFDAC=%s CLNT_PAM_CAPABLE=%s '
        data  = data % (self.username, self.password, self.version, self.serialNumber, self.databaseName,
                             self.ieee, self.databasePath, self.databaseMoney, self.clientLocale, 
                             self.singleLevel, self.lkNotify, self.lockDown, self.noDefDac,
                             self.clientPamCapable)
        data += self.encodedData
        buf += data

        self.encodedSize = base64.b64encode(struct.pack(">h", len(buf)-3))
        self.encodedSize = self.encodedSize.strip("=")

        buf = buf.replace("sqKK", "sq" + self.encodedSize)

        return buf

    def getLoginPacket(self):
        return self.getPacket()
    
    def get2ndPacket(self):
        return self.__sqlexec2nd

    def login(self, s, username = None, password = None):
        if not s:
            raise Exception("Unitialized socket")

        if username:
            self.username = username

        if password:
            self.password = password

        buf = self.getPacket()
        s.send(buf)
        res = s.recv(1024)

        # 14 03 -> Invalid dbname but valid username+password
        # 05 02 -> Username, password and dbname are valid
        if res.startswith("\x00\x14\x03\x3d") or res.startswith("\x01\x05\x02\x3d"):
            return True
        else:
            return False

def simpleFuzzer(target="192.168.1.11",  port=9088,  timeout=500):
    """ A simple SQLEXEC protocol fuzzer """
    import socket
    import libfuzz
    
    properties = ["version", "serialNumber","databaseName", "databasePath", "databaseMoney",
                  "clientLocale", "singleLevel", "lkNotify", "lockDown", "noDefDac",
                  "clientPamCapable"]

    socket.setdefaulttimeout(timeout)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target,  port))
        s.close()
        # Target appears to be up and running
    except:
        # Target is down
        raise

    for prop in properties:
        for i in libfuzz.sizes:
            for str in libfuzz.strings:
                ifx = Informix()
                exec('ifx.' + prop + '= str*i')
                print "[+] Fuzzing property %s with size %d and string %s" % (prop, i,  str)
                data = ifx.getPacket()

                print "[+] Sending packet: %s" % repr(data)
                
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((target,  port))
                    s.send(data)
                except:
                    print "[+] Target appears to be down. Good!"
                    return True
                try:
                    print "[+] Response: %s" % repr(s.recv(8192))
                    s.close()
                except:
                    print "***Error:",  sys.exc_info()[1]
    
    return False
