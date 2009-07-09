
from struct import *

class Formatter:
    """
    A class for modular memory formatter registration.
    They return (addresstext, datatext, chartext).
    """

    def __init__(self, vdb):
        self.vdb = vdb
        self.chunksize = 16 # Default

    def format(self, address, memory):
        pass

    def normalAddrBuf(self, address, memlen, chunksize):
        addrbuf = ""
        for i in range(address, address+memlen, chunksize):
            addrbuf += "%.8x\n" % i
        return addrbuf

    def normalCharBuf(self, memory, chunksize):
        charbuf = ""
        for i in range(0,len(memory),chunksize):
            buf = memory[i:i+chunksize]
            # Handle the charbuf
            for ch in buf:
                if ord(ch) > 0x7e or ord(ch) < 0x20:
                    ch = '.'
                charbuf += ch
            charbuf += "\n"
        return charbuf

class StringTableFormatter(Formatter):

    def format(self, address, memory):
        addrbuf = ""
        databuf = ""
        charbuf = ""

        offset = 0

        for name in memory.split("\x00"):
            addrbuf += hex(address+offset)+"\n"
            databuf += repr(name)+"\n"
            charbuf += "strlen: %d\n" % len(name)
            offset += len(name)+1

        return addrbuf,databuf,charbuf

class IntelStackFormatter(Formatter):
    """
    Ollydbg style stack view with ESP/EBP/Frame notation
    and de-referencing
    """
    def format(self, address, memory):
        offset = 0
        addrbuf = ""
        databuf = ""
        charbuf = ""
        t = self.vdb.getTrace()
        try:
            esp = t.getRegisterByName("esp")
            ebp = t.getRegisterByName("ebp")
        except:
            return "","ERROR - You're probably not on intel",""

        fcount = 0
        nextname = None
        oldebp = 0xffffffff

        while offset < len(memory):
            val = unpack("<I", memory[offset:offset+4])[0]
            try:
                bytes = t.readMemory(val, 32)
                for byte in bytes:
                    obyte = ord(byte)
                    if obyte >= 0x20 and obyte < 0x7f:
                        charbuf += byte
                    else:
                        charbuf += "."
                charbuf += "\n"
            except:
                charbuf += "\n"
            databuf += "%s\n" % hex(val)
            addr = offset + address
            if nextname:
                addrbuf += "%s\n" % nextname
                nextname = None
            elif addr == esp:
                addrbuf += "STACK POINTER ->\n"
            elif addr == ebp:
                addrbuf += "FRAME [%d] ->\n" % fcount
                fcount += 1
                oldebp = ebp
                ebp = val
                nextname = "SAVED EIP"
            elif addr > oldebp:
                addrbuf += "EBP +%d\n" % (addr-oldebp)
            elif addr > esp:
                addrbuf += "ESP +%d\n" % (addr-esp)
            else:
                addrbuf += "ESP -%d\n" % (esp-addr)

            offset += 4
        return addrbuf, databuf, charbuf

class NormalFormatter(Formatter):

    def format(self, address, memory):
        chunksize = self.chunksize
        addrbuf = self.normalAddrBuf(address, len(memory),chunksize)
        charbuf = self.normalCharBuf(memory, chunksize)
        databuf = ""

        for i in range(0, len(memory), chunksize):
            buf = memory[i:i+chunksize]
            if len(buf) < chunksize:
                buf += "\x00"*(chunksize-len(buf))
            databuf += self.formatDataChunk(buf) + "\n"

        return addrbuf, databuf, charbuf

class CFormatter(NormalFormatter):
    def formatDataChunk(self, buf):
        bytes = unpack("%dB"%self.chunksize, buf)
        return '"' + (("\\x%.2x" * self.chunksize) % bytes) + '"'

class ReprFormatter(NormalFormatter):
    def formatDataChunk(self, buf):
        return '"%s"' % repr(buf)

class Uint64LeFormatter(NormalFormatter):
    def formatDataChunk(self, buf):
        lcount = self.chunksize/8
        quads = unpack("<%dQ"%lcount, buf)
        return ("%.16x " * lcount) % quads

class Uint32LeFormatter(NormalFormatter):
    def formatDataChunk(self, buf):
        lcount = self.chunksize/4
        longs = unpack("<%dI"%lcount, buf)
        return ("%.8x " * lcount) % longs

class Uint16LeFormatter(NormalFormatter):

    def formatDataChunk(self, buf):
        lcount = self.chunksize/2
        shorts = unpack("<%dH"%lcount, buf)
        return ("%.4x " * lcount) % shorts

class ByteFormatter(NormalFormatter):
    """
    Format in hexdump style bytes.
    """
    def formatDataChunk(self, buf):
        bytes = unpack("<%dB"%self.chunksize, buf)
        return ("%.2x " * self.chunksize) % bytes

class InstructionFormatter(Formatter):
    """
    Show a disassembly view.
    """

    def format(self, address, memory):
        addrbuf = ""
        databuf = ""
        charbuf = ""

        offset = 0
        while offset < len(memory):
            size = 1
            try:
                op = self.vdb.arch.makeOpcode(memory[offset:])
                databuf += self.vdb.arch.reprOpcode(op, va=address+offset)+"\n"
                size = len(op)
            except Exception, msg:
                databuf += "%s\n" % msg

            addrbuf += "%.8x\n" % (address+offset)
            bytes = memory[offset:offset+size]
            bytes = unpack("B"*len(bytes), bytes)
            for byte in bytes:
                charbuf += "%.2x " % byte
            charbuf += "\n"
            offset += size

        return addrbuf,databuf,charbuf

class StructFormatter(Formatter):
    """
    Extend from this to easily define
    structure parser based formatters.
    (See Win32TebFormatter for an example)
    """
    def format(self, address, memory):
        addrbuf = ""
        databuf = ""
        x = calcsize(self.formatstr)
        if len(memory) < x:
            return "","ERROR - This format requires at least %d bytes" % x,""

        values = unpack(self.formatstr, memory[:x])
        for i in range(len(values)):
            addrbuf += "%s\n" % self.names[i]
            databuf += "0x%.8x\n" % values[i]
        return addrbuf,databuf,""

def setupFormatters(vdb):
    """
    Add all the current formatters to the specified vdb
    instance.
    """
    vdb.registerFormatter("Bytes",ByteFormatter(vdb))
    vdb.registerFormatter("u_int_16",Uint16LeFormatter(vdb))
    vdb.registerFormatter("u_int_32",Uint32LeFormatter(vdb))
    vdb.registerFormatter("u_int_64",Uint64LeFormatter(vdb))
    vdb.registerFormatter("ASM",InstructionFormatter(vdb))
    vdb.registerFormatter("C", CFormatter(vdb))
    vdb.registerFormatter("Python", ReprFormatter(vdb))
    vdb.registerFormatter("String Table", StringTableFormatter(vdb))
    vdb.registerFormatter("Intel Stack View", IntelStackFormatter(vdb))

