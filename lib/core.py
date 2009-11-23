#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

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

try:
    import scapy.all as scapy
    from scapy.modules.nmap import *
    bHasScapy = True
except:
    bHasScapy = False

def int2hex(iNum):
    sNum = str(hex(iNum))
    sNum = sNum.replace("0x", "")
    
    if len(sNum) == 1:
        sNum = "0" + sNum

    return eval("'\\x" + str(sNum) + "'")

def str2uni(data):
    """ Convert a python string to unicode. NOT to a python unicode object """
    buf = ""

    for char in data:
        buf += char + "\x00"

    return buf

def regexp2pyre(regexp):
    """ Convert a perl regular expression to a python compatible regular expression """
    buf = regexp
    
    # Remove starting slash
    if buf.startswith("/"):
        buf = buf[1:]
    
    idx = len(buf)
    i = 0
    while 1:
        #
        # Remove ending slash plush modifiers, i.e.: /<regexp>/si
        #
        if buf[idx-i:idx-i+1] == "/":
            buf = buf[:idx-i]
            break

        i += 1

    return buf

def isIpAddr4(data):
    x = data.split("/")
    
    if len(x) == 1:
        x = data.split(".")
    else:
        x = x[0].split(".")

    if len(x) == 4:
        for y in x:
            if not y.isalpha():
                try:
                    if int(y) > 256:
                        return False
                except:
                    return False
        return True
    else:
        return False

def getMacVendor(mac):
    try:
        path = conf.nmap_base.replace('os-fingerprints', 'mac-prefixes')
        mac = mac.replace(":", "")

        f = file(path, "r")

        for line in f:
            if line.startswith("#"):
                pass # Ignore, just a comment
            elif line.replace(" ", "") == "":
                pass # Ignore, blank line
            else:
                prefix = line[0:6]
                vendor = line[7:]

                if mac.lower().startswith(prefix.lower()):
                    return vendor.replace("\r", "").replace("\n", "")
        
        return "Unknow"
    except:
        return "Unknow"# + str(sys.exc_info()[1])

def getProtocolName(proto):
    try:
        for x in scapy.conf.protocols.keys():
            if scapy.conf.protocols[x] == proto:
                return x
    except:
        pass

    return proto
