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
"""
The MIBS commands
"""
rootMibs = {}
rootMibs[".1.3.6.1.2.1.1."] = "system"
rootMibs[".1.3.6.1.2.1.2."] = "interfaces"
rootMibs[".1.3.6.1.2.1.3."] = "at"
rootMibs[".1.3.6.1.2.1.4."] = "ip"
rootMibs[".1.3.6.1.2.1.5."] = "icmp"
rootMibs[".1.3.6.1.2.1.6."] = "tcp"
rootMibs[".1.3.6.1.2.1.7."] = "udp"
rootMibs[".1.3.6.1.2.1.8."] = "egp"
rootMibs[".1.3.6.1.2.1.10."] = "transmission"
rootMibs[".1.3.6.1.2.1.11."] = "snmp"
# Berezia. Is not strictly a "root" but I think is better to put here than in a subtree
rootMibs[".1.3.6.1.4.1."] = "sysObjectId"

systemMibs= {}
systemMibs[".1.3.6.1.2.1.1.1."] = "sysDescr"
systemMibs[".1.3.6.1.4.1."] = "sysObjectId"
systemMibs[".1.3.6.1.2.1.1.3."] = "sysUptime"
systemMibs[".1.3.6.1.2.1.1.4."] = "sysContact"
systemMibs[".1.3.6.1.2.1.1.5."] = "sysName"
systemMibs[".1.3.6.1.2.1.1.6."] = "sysLocation"
systemMibs[".1.3.6.1.2.1.1.7."] = "sysServices"

interfacesMibs = {}
interfacesMibs[".1.3.6.1.2.1.2.1."] = "ifNumber"
interfacesMibs[".1.3.6.1.2.1.2.2."] = "ifTable"

ifTableMibs = {}
ifTableMibs[".1.3.6.1.2.1.2.2.1."] = "ifEntry"

ifEntryMibs = {}
ifEntryMibs[".1.3.6.1.2.1.2.2.1.1."] = "ifIndex"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.2."] = "ifDescr"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.3."] = "ifType"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.4."] = "ifMtu"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.5."] = "ifSpeed"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.6."] = "ifPhysAddress"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.7."] = "ifAdminStatus"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.8."] = "ifOperStatus"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.9."] = "ifLastChange"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.10."] = "ifInOctets"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.11."] = "ifInUcastPkts"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.12."] = "ifInNUcastPkts"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.13."] = "ifInDiscards"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.14."] = "ifInErrors"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.15."] = "ifInUnknownProtos"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.16."] = "ifOutOctets"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.17."] = "ifOutUcastPkts"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.18."] = "ifOutNUcastPkts"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.19."] = "ifOutDiscards"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.20."] = "ifOutErrors"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.21."] = "ifOutQLen"
ifEntryMibs[".1.3.6.1.2.1.2.2.1.22."] = "ifSpecific"

atTableMibs = {}
atTableMibs[".1.3.6.1.2.1.3.1."] = "atTable"

atEntryMibs = {}
atEntryMibs[".1.3.6.1.2.1.3.1.1."] = "atEntry"
atEntryMibs[".1.3.6.1.2.1.3.1.1.1."] = "atIfIndex"
atEntryMibs[".1.3.6.1.2.1.3.1.1.2."] = "atPhysAddress"
atEntryMibs[".1.3.6.1.2.1.3.1.1.3."] = "atNetAddress"

ipMibs = {}
ipMibs[".1.3.6.1.2.1.4.1."] = "ipForwarding"
ipMibs[".1.3.6.1.2.1.4.2."] = "ipDefaultTTL"
ipMibs[".1.3.6.1.2.1.4.3."] = "ipInReceives"
ipMibs[".1.3.6.1.2.1.4.4."] = "ipInHdrErrors"
ipMibs[".1.3.6.1.2.1.4.5."] = "ipInAddrErrors"
ipMibs[".1.3.6.1.2.1.4.6."] = "ipForwDatagrams"
ipMibs[".1.3.6.1.2.1.4.7."] = "ipInUnknownProtos"
ipMibs[".1.3.6.1.2.1.4.8."] = "ipInDiscards"
ipMibs[".1.3.6.1.2.1.4.9."] = "ipInDelivers"
ipMibs[".1.3.6.1.2.1.4.10."] = "ipOutRequests"
ipMibs[".1.3.6.1.2.1.4.11."] = "ipOutDiscards"
ipMibs[".1.3.6.1.2.1.4.12."] = "ipOutNoRoutes"
ipMibs[".1.3.6.1.2.1.4.13."] = "ipReasmTimeout"
ipMibs[".1.3.6.1.2.1.4.14."] = "ipReasmReqds"
ipMibs[".1.3.6.1.2.1.4.15."] = "ipReasmOKs"
ipMibs[".1.3.6.1.2.1.4.16."] = "ipReasmFails"
ipMibs[".1.3.6.1.2.1.4.17."] = "ipFragOKs"
ipMibs[".1.3.6.1.2.1.4.18."] = "ipFragFails"
ipMibs[".1.3.6.1.2.1.4.19."] = "ipFragCreates"

ipAddrTableMibs = {}
ipAddrTableMibs[".1.3.6.1.2.1.4.20."] = "ipAddrTable"

ipAddrEntryMibs = {}
ipAddrEntryMibs[".1.3.6.1.2.1.4.20.1.1."] = "ipAdEntAddr"
ipAddrEntryMibs[".1.3.6.1.2.1.4.20.1.2."] = "ipAdEntIfIndex"
ipAddrEntryMibs[".1.3.6.1.2.1.4.20.1.3."] = "ipAdEntNetMask"
ipAddrEntryMibs[".1.3.6.1.2.1.4.20.1.4."] = "ipAdEntBcastAddr"
ipAddrEntryMibs[".1.3.6.1.2.1.4.20.1.5."] = "ipAdEntReasmMaxSize"

mibs = []
mibs.append(ipAddrEntryMibs)
mibs.append(ipAddrTableMibs)
mibs.append(ipMibs)
mibs.append(ipAddrTableMibs)
mibs.append(atEntryMibs)
mibs.append(atTableMibs)
mibs.append(ifEntryMibs)
mibs.append(ifTableMibs)
mibs.append(systemMibs)
mibs.append(rootMibs)

"""
Interface types
"""
IF_TYPE_OTHER = 1
IF_TYPE_REGULAR1822 = 2
IF_TYPE_HDH1822 = 3
IF_TYPE_DDN_X25 = 4
IF_TYPE_RFC877_X25 = 5
IF_TYPE_ETHERNET_CSMACD = 6
IF_TYPE_ISO88023_CSMACD = 7
IF_TYPE_ISO88024_TOKENBUS = 8
IF_TYPE_ISO88025_TOKENRING = 9
IF_TYPE_ISO88026_MAN = 10
IF_TYPE_STARLAN = 11
IF_TYPE_PROTEON_10MBIT = 12
IF_TYPE_PROTEON_80MBIT = 13
IF_TYPE_HYPERCHANNEL = 14
IF_TYPE_FDDI = 15
IF_TYPE_LAPB = 16
IF_TYPE_SDLC = 17
IF_TYPE_DS1 = 18
IF_TYPE_E1 = 19
IF_TYPE_BASICISDN = 20
IF_TYPE_PRIMARYISDN = 21
IF_TYPE_PROPPOINTTOPOINTSERIAL = 22
IF_TYPE_PPP = 23
IF_TYPE_SOFTWARELOOPBACK = 24
IF_TYPE_EON = 25
IF_TYPE_ETHERNET_3MBIT = 26
IF_TYPE_NSIP = 27
IF_TYPE_SLIP = 28
IF_TYPE_ULTRA = 29
IF_TYPE_DS3 = 30
IF_TYPE_SIP = 31
IF_TYPE_FRAME_RELAY = 32

"""
Administrative/Operative Interface Status
"""
IF_STATUS_UP = 1
IF_STATUS_DOWN = 2
IF_STATUS_TESTING = 3

def layerValue(layer):
    """ Returns the value of the layer applying 2^ (LAYER_VALUE - 1) """
    return pow(layer-1, 2)

"""
The layers that the device supports:

    1  physical (e.g., repeaters)
    2  datalink/subnetwork (e.g., bridges)
    3  internet (e.g., IP gateways)
    4  end-to-end  (e.g., IP hosts)
    7  applications (e.g., mail relays)

The value assigned to the {var}_VALUE is:

    2^(LAYER_VALUE-1)

"""
LAYER_PHYSICAL = 1
LAYER_DATALINK = 2
LAYER_INTERNET = 3
LAYER_END_TO_END = 4
LAYER_OS_PROTOCOLS_1 = 5
LAYER_OS_PROTOCOLS_2 = 6
LAYER_APPLICATIONS = 7

LAYERS = [LAYER_PHYSICAL, LAYER_DATALINK, LAYER_INTERNET, LAYER_END_TO_END, LAYER_OS_PROTOCOLS_1, LAYER_OS_PROTOCOLS_2,
                    LAYER_APPLICATIONS]

LAYER_PHYSICAL_VALUE = layerValue(LAYER_PHYSICAL)
LAYER_DATALINK_VALUE = layerValue(LAYER_DATALINK)
LAYER_INTERNET_VALUE = layerValue(LAYER_INTERNET)
LAYER_END_TO_END_VALUE = layerValue(LAYER_END_TO_END)
LAYER_OS_PROTOCOLS_1_VALUE = layerValue(LAYER_OS_PROTOCOLS_1)
LAYER_OS_PROTOCOLS_2_VALUE = layerValue(LAYER_OS_PROTOCOLS_2)
LAYER_APPLICATIONS_VALUE = layerValue(LAYER_APPLICATIONS)

LAYER_VALUES = [LAYER_PHYSICAL_VALUE, LAYER_DATALINK_VALUE, LAYER_INTERNET_VALUE, LAYER_END_TO_END_VALUE,
                                LAYER_OS_PROTOCOLS_1_VALUE, LAYER_OS_PROTOCOLS_2_VALUE, LAYER_APPLICATIONS_VALUE]

def valueToLayers(values):
    """ Returns the supported layers according to the response to the command sysServices """

    if str(values) == "":
        return ""

    try:
        mValue = int(values)
    except:
        raise Exception("Invalid value for supported layers")

    for i in range(1, len(LAYER_VALUES)):
        if LAYER_VALUES[i] > mValue:
            return LAYER_VALUES[:i]
    
    return None

def oidToHuman(oid):
    for x in mibs:
        if type(x) is dict:
            for y in x:
                if y == oid:
                    return x[y]
                elif oid.startswith(y) or oid.find(y) > -1:
                    return oid.replace(y, x[y]) + "."
        else:
            if x == oid:
                return mibs[x]
            elif oid.startswith(x) or oid.find(x) > -1:
                return oid.replace(x, mibs[x]) + "."

    return oid
