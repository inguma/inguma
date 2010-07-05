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
""" Python RMI very basic interface """

""" For RMI Output Streams """
RMI_PROT_VERSION_0 = "\x00\x00"
RMI_PROT_VERSION_1 = "\x00\x01"

RMI_PROTO_STREAM = "\x4b"
RMI_PROTO_SINGLEOP = "\x4c"
RMI_PROTO_MULTIPLEX = "\x4d"

""" For RMI Input Streams """
RMI_PROTO_RESPONSE_ACK = "\x4e"
RMI_PROTO_RESPONSE_NOT_SUPPORTED = "\x4f"

RMI_RETURN_VALUE_OPT = "\x51"
RMI_RETURN_VALUE_ACK = "\x53"

""" For RMI Ouptput Streams Responses """
RMI_OUTPUT_RESPONSE_MAGIC = "\xac\xed"

class RMIOutputStream:

    header = "\x4a\x52\x4d\x49" # JRMI
    version = RMI_PROT_VERSION_0
    protocol = RMI_PROTO_SINGLEOP
    message = "PING"

    def getPacket(self):
        return self.header + self.version + self.protocol + self.message

    def readPacket(self,  pkt):
        if len(pkt) < 6:
            raise Exception("Invalid RMI packet")
    
        self.header = pkt[:4]
        self.version = pkt[4:5]
        self.protocol = pkt[5:6]
        self.message = pkt[6:]

class RMIInputStream:

    header = RMI_PROTO_RESPONSE_ACK
    message = RMI_RETURN_VALUE_ACK

    def getPacket(self):
        return str(self.header) + str(self.message)

    def readPacket(self,  pkt):
        pass

class RMIResponse:
    
    header = ""
    version = ""
    data = ""

    def __init__(self):
        pass

    def readPacket(self, pkt):
        if len(pkt)<4:
            raise Exception("Invalid RMI Packet")

        if pkt[:2] != RMI_OUTPUT_RESPONSE_MAGIC:
            raise Exception("Invalid RMI Header")

        self.header = pkt[:2]
        self.major = pkt[2:3]
        self.minor = pkt[3:4]
        self.version = str(ord(self.minor))
        self.data = pkt[4:]

class RMI:
    
    inStream = None
    outStream = None
    
    def __init__(self):
        self.inStream = RMIInputStream()
        self.outStream = RMIOutputStream()

def main():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.65.100", 1099))
    data = s.recv(1024)
    response = RMIResponse()
    response.readPacket(data)
    print "Remote RMI Server Version " + response.version

    rmi = RMI()
    rmi.outStream.message = "INVALID DATA"

    pkt = rmi.outStream.getPacket()
    print repr(pkt)
    s.sendall(pkt)

    data = s.recv(1024)
    print repr(data)

    s.close()

if __name__ == '__main__':
    main()
