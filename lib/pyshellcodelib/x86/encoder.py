#!/usr/bin/python

import sys

"""
The following functions are extracted from the fantastic Shellforge project (which is also GPL).

Copyright (C) 2003  Philippe Biondi <phil@secdev.org>
"""

def mkcpl(x):
    x = ord(x)
    set="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    for c in set:
        d = ord(c)^x
        if chr(d) in set:
            return 0,c,chr(d)
        if chr(0xff^d) in set:
            return 1,c,chr(0xff^d)
    raise Exception,"No encoding found for %#02x"%x

def x86AlphaEncode(shcode):
    s="hAAAAX5AAAAHPPPPPPPPa"
    shcode=list(shcode)
    shcode.reverse()
    shcode = "".join(shcode)
    shcode += "\x90"*((-len(shcode))%4)
    for b in range(len(shcode)/4):
        T,C,D = 0,"",""
        for i in range(4):
            t,c,d = mkcpl(shcode[4*b+i])
            T += t << i
            C = c+C
            D = d+D
        s += "h%sX5%sP" % (C,D)
        if T > 0:
            s += "TY"
            T = (2*T^T)%16
            for i in range(4):
                if T & 1:
                    s += "19"
                T >>= 1
                if T == 0:
                    break
                s += "I"
    return s+"T\xc3"

def alphaEncode(shcode):
    return x86AlphaEncode(shcode)

def x86XorEncode(shcode, avoid="\x00"):
        avd = []
        for a in avoid.split(","):
            if a.startswith("0x") and len(a) == 4:
                avd.append(int(a[2:],16))
            else:
                avd += map(lambda x: ord(x),list(a))

        needloader=0
        for c in avd:
            if chr(c) in shcode:
                needloader=1
                break
        if not needloader:
            return shcode
        for i in range(64,256)+range(1,64):
            ok=1
            for c in avd:
                if chr(c^i) in shcode:
                    ok=0
                    break
            if ok:
                key=i
                break
        if not ok:
            raise Exception("xor loader: no suitable xor key found.")

        shcode = "".join(map(lambda x: chr(ord(x)^key), shcode))
        length = len(shcode)
        if length < 0x100:
            ld = ("\xeb\x0e\x90\x5e\x31\xc9\xb1"+chr(length)+"\x80\x36"+
                  chr(key)+"\x46\xe2\xfa\xeb\x05\xe8\xee\xff\xff\xff")
        else:
            if length & 0xff == 0:
                length += 1
            ld = ("\xeb\x0f\x5e\x31\xc9\x66\xb9"+
                  chr(length&0xff)+chr(length>>8)+
                  "\x80\x36"+chr(key)+
                  "\x46\xe2\xfa\xeb\x05\xe8\xec\xff\xff\xff")
        ok=1
        for c in avd:
            if chr(c) in ld:
                ok=0
                break
        if not ok:
            raise Exception("xor loader: no suitable xor loader found")
        return ld+shcode

def xorEncode(shcode, avoid="\x00"):
    return x86XorEncode(shcode, avoid)

def x86StackRelocEncode(shcode,smart=1):
        loader = ("\x58"+                     # pop    %eax
                  "\xe8\x00\x00\x00\x00"+     # call   +0
                  "\x5b"+                     # pop    %ebx
                  "\x50"+                     # push   %eax
                  "\x83\xc3\xfa")             # add    $0xfffffffa,%ebx
        if smart != "0":
            loader += (
                  "\x89\xd8"+                 # mov    %ebx,%eax
                  "\x31\xe0"+                 # xor    %esp,%eax
                  "\xc1\xe8\x10"+             # shr    $0x10,%eax
                  "\x85\xc0"+                 # test   %eax,%eax
                  "\x75\x02")                 # jne    +2
        loader += "\x89\xdc"                  # mov    %ebx,%esp
        return loader+shcode

def stackRelocEncode(shcode, smart=1):
    return x86StackRelocEncode(shcode, smart)

def x86CompressEncode(shcode, histo='5',length='2'):
    loader = "\xeb\x38\x5e\x46\xfc\xad\x89\xc1\x89\xf7\x01\xcf\x31\xc0\xac\xa8\x80\x78\x05\xaa\xe2\xf8\xeb\x27\x3d\xff\x00\x00\x00\x75\x03\xac\xe2\xf1\x51\x56\x89\xc1\x24\x1f\x89\xfe\x29\xc6\x80\xe1\x7f\xc0\xe9\x05\xf3\xa4\x5e\x59\xe2\xd6\xeb\x05\xe8\xc3\xff\xff\xff\xe9" # compress.nasm r44
    comp = ""
    histo = int(histo,0)
    length = int(length,0)
    if histo != 5 or length != 2:
        print "Compress: only works for histo and length default values"
    print "Compress: histo=%i length=%i" % (histo, length)
    i = 0
    while i < len(shcode):
        c = shcode[i]
        if ord(c)&0x80:
            c = "\xff"+c
        j = min(2**length-1, i, len(shcode)-i+1)
        while j > 0:
            p = shcode[:i].rfind(shcode[i:i+j])
            if p >= 0 and p >= i-2**histo:
                print "Compress: found @%i %i %r in %r" % (i,p-i, shcode[i:i+j],shcode[max(0,i-2**histo):i])
                c = chr(0x80|(j<<histo)|(i-p))
                i += j-1
                break
            j -= 1
        comp += c
        i += 1
    comp = loader+struct.pack("I",len(comp))+comp

    print "Compress: [%i bytes] ==(C)==> [%i bytes]" % (len(shcode), len(comp))
    return comp

def compressEncode(shcode, histo='5', length='2'):
    return x86CompressEncode(shcode, histo, length)

"""
End of Shellforge extracted functions
"""
