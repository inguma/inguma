#!/usr/bin/python

import sys
import time
import struct
import socket

import libfuzz

"""
00000000 03 00 00 2c 27 e0 00 00 00 00 00 43 6f 6f 6b 69     ...,'......Cooki
00000010 65 3a 20 6d 73 74 73 68 61 73 68 3d 65 6c 74 6f     e: mstshash=elto
00000020 6e 73 0d 0a 01 00 08 00 00 00 00 00                 ns..........

03 -> TPKT Header: version = 3
00 -> TPKT Header: Reserved = 0
00 -> TPKT Header: Packet length - high part
2c -> TPKT Header: Packet length - low part (total = 44 bytes)
27 -> X.224: Length indicator (39 bytes)
e0 -> X.224: Type (high nibble) = 0xe = CR TPDU; credit (low nibble)	= 0
00 00 -> X.224: Destination reference = 0
00 00 -> X.224: Source reference = 0
00 -> X.224: Class and options = 0

43 6f 6f 6b 69 65 3a 20 6d 73 74 73 68 61 73 68 
3d 65 6c 74 6f 6e 73 -> "Cookie: mstshash=eltons"
0d -> CR (carriage return)
0a -> LF (line feed)

01 -> RDP_NEG_REQ::type (TYPE_RDP_NEG_REQ)
00 -> RDP_NEG_REQ::flags (0)
08 00 -> RDP_NEG_REQ::length (8 bytes)
00 00 00 00 -> RDP_NEG_REQ: Requested protocols (PROTOCOL_RDP)
"""

secondPacket = '\x03\x00\x01\x96\x02\xf0\x80\x7fe\x82\x01\x8a\x04\x01\x01\x04\x01\x01\x01\x01\xff0 \x02\x02\x00"\x02\x02\x00\x02\x02\x02\x00\x00\x02\x02\x00\x01\x02\x02\x00\x00\x02\x02\x00\x01\x02\x02\xff\xff\x02\x02\x00\x020 \x02\x02\x00\x01\x02\x02\x00\x01\x02\x02\x00\x01\x02\x02\x00\x01\x02\x02\x00\x00\x02\x02\x00\x01\x02\x02\x04 \x02\x02\x00\x020 \x02\x02\xff\xff\x02\x02\xfc\x17\x02\x02\xff\xff\x02\x02\x00\x01\x02\x02\x00\x00\x02\x02\x00\x01\x02\x02\xff\xff\x02\x02\x00\x02\x04\x82\x01\x17\x00\x05\x00\x14|\x00\x01\x81\x0e\x00\x08\x00\x10\x00\x01\xc0\x00Duca\x81\x00\x01\xc0\xd4\x00\x04\x00\x08\x00\x00\x04\x00\x03\x01\xca\x03\xaa\n\x04\x00\x00(\n\x00\x00j\x00o\x00x\x00e\x00a\x00n\x00-\x00d\x00e\x00s\x00k\x00t\x00o\x00p\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xca\x01\x00\x00\x00\x00\x00\x18\x00\x07\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\xc0\x0c\x00\t\x00\x00\x00\x00\x00\x00\x00\x02\xc0\x0c\x00\x03\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x14\x00\x01\x00\x00\x00cliprdr\x00\xc0\xa0\x00\x00'


global times
times = 0

class CRdpClientX224:

    header = "\x03"
    reserved = "\x00"
    length = "\x00\x2c"
    x224length = "\x27"
    x224type = "\xe0"
    x224destination = "\x00\x00"
    x224source = "\x00\x00"
    x224class = "\x00"
    data = "Cookie: mstshash=eltons"
    dataPadding = "\r\n"
    rdpNegReqType = "\x01"
    rdpNegReqFlags = "\x00"
    rdpNegReqLength = "\x08\x00"
    rdpNegReqProto = "\x00\x00\x00\x00"

    properties = ["header", "reserved", "x224type", "x224destination", "x224source",
                  "x224class", "data", "dataPadding", "rdpNegReqType", "rdpNegReqFlags",
                  "rdpNegReqProto"]

    def getPacket(self):
        # Compose basic header
        prebuf  = self.header
        prebuf += self.reserved

        # Compose message's body
        buf  = self.x224type
        buf += self.x224destination
        buf += self.x224source
        buf += self.x224class
        buf += self.data
        buf += self.dataPadding

        # Compose the final RDP flags
        postbuf1  = self.rdpNegReqType
        postbuf1 += self.rdpNegReqFlags
        postbuf2  = self.rdpNegReqProto

        # Calculate the rdpNegReqLength
        rdpDataLen = struct.pack("<h", len(postbuf1 + postbuf2)+2)
        rdpNegReqBuf = postbuf1 + rdpDataLen + postbuf2

        # Generate the final packet
        data  = prebuf + struct.pack(">h", len(prebuf + buf + rdpNegReqBuf)+2)

        # This is a hack!
        data += "\xff"#struct.pack("b", len(buf + rdpNegReqBuf))
        data += buf + rdpNegReqBuf

        return data

def main():

    rdpClient = CRdpClientX224()

    for prop in rdpClient.properties:
        for i in libfuzz.sizes:
            for str in libfuzz.strings:
                time.sleep(0.1)
                rdpClient = CRdpClientX224()
                print "Fuzzing RDP: Property %s - string %s - size %d" % (prop, str, i)
                exec("rdpClient." + prop + " = str*i")
                buf = rdpClient.getPacket()

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("192.168.1.16", 3389))
                print "Sending packet %s", repr(buf)
                s.send(buf)

def callback(data, var):
    global times

    times += 1

    if times % 500 == 0:
        print "........ Waiting for a second or so ......."
        time.sleep(0.5)

    try:
        print "[+] Fuzzing 2nd RDP packet - Var %d" % var
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.1.16", 3389))
        rdpClient = CRdpClientX224()
        print "  --> Sending initial connect PDU"
        s.send(rdpClient.getPacket())
        print "  --> Received response %d byte(s)" % len(s.recv(4096))
        print "  --> Sending fuzzy data ... "
        print "--- THE BUF ---"
        print 
        print repr(data)
        print 
        print "--- END BUF ---"
        try:
            s.sendall(data)
            s.close()
        except:
            print "***Error:", sys.exc_info()[1]
            s.close()
        print
        print
    except:
        print "Life sucks: ", sys.exc_info()[1]
        #time.sleep(1)

def fuzz():
    libfuzz.fuzzCallback(callback, secondPacket, 0, 2181)

if __name__ == "__main__":
    main()
    fuzz()

