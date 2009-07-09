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
class CSlp:
    """
    Library for the Service Location Protocol
    
    It's used, i.e., by IBM Corporation (IBM Director, etc...).
    """
    version = 0x2
    function = 0x1
    packetLength = 0x67
    flags = "20 00"
    nextExtensionOffset = "00 00 39"
    xid = "nU"
    langTagLen = "00 02"
    langTag = "en"
    previousResponseListLength = "00 0C"
    previousResponseList = "192.168.1.22"
    serviceTypeLength = "00 0c"
    serviceTypeList = "service:WBEM"
    scopeListLength = "00 07"
    scopeList = "DEFAULT"
    predicateLength = "00"
    predicate = ""
    slpSpiLength = "00 00"
    slpSpi = ""
