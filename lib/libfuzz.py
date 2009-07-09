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

import struct

# Fuzzing data
strings = ("A", "%s", "%n", "%x", "%n", "%d", "\x00A", "ABCD\x00",  "A\x00", "AAAAAAAA\x00",
                "localhost", "127.0.0.1"
                "\\\\", "C:\\", "\\\\?\\PIPE", "/.", "../", "\\\\.\\TEST")
numbers = (-2, -1, 0, 1, 2, 3, 4, 6, 8, 16, 24, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 2147483647, 4294967294)
sizes   = (1, 4, 100, 512, 1024, 2048, 4096, 8192)#, 10000, 16384, 32000, 64000,  128000)

separators = [" ", ".", "/", "&", "=", "?", ":", "\r", "\n", "\x00", "@", "-", "_", "*" , "\\", "(", ")", "[", "]", "!", "|",
		"#", "$", "%", "<", ">", ";"]
ignorechars = [" ", "<", ">", '"', "\r", "\n", "?", "(", ")"]

fastStrings = ("A", "%s", "%n", "%x", "\x00A", "ABCD\x00")

TOKEN_TYPE_TOKEN = 0
TOKEN_TYPE_INJECT = 1
TOKEN_TYPE_APPEND = 0

def tokenizePacket(pkt, mode):
    
    if mode == 0:
        """
        Split a packet into tokens
        """
        ret = []
        tmp = ""
    
        for x in pkt:
            if x in separators:
                if tmp != "":
                    ret.append(tmp)
                ret.append(x)
                tmp = ""
            else:
                tmp += x
    
        if tmp != "":
            ret.append(tmp)
    
        return ret
    elif mode == 1:
        """ Fuzz every character """
        ret = [""]
        for c in pkt:
            ret.append(c)
        ret.append("")
        return ret

def token2str(tkn):
    """ 
    Convert a token list into a Python string
    """

    #x = "".join(tkn) Doesn't work if some element is not an string
    x = ""

    for a in tkn:
        x += str(a)

    return x

def fuzzCallback(func, cmd, idx, var=0, mode=0, fastMode = False):
    """
    Callback to use when writting fuzzers
    """
    mtokens = tokenizePacket(cmd, mode)
    tokens = mtokens
    j = 0

    for i in range(int(idx), len(mtokens)):
        tokens = tokenizePacket(cmd, mode)
        tmp = ""

        if tokens[i] in separators:
            if tokens[i] in ignorechars:
                continue

        x = 0
        for num in numbers:
            x+= 1
            if x < var:
                continue
            
            print "Fuzzing var %d:%d" % (i, x)
            
            tmp = tokens
            tmp[i] = num

            func(token2str(tmp), i)
            j += 1

        for num in numbers:
            x+= 1
            if x < var:
                continue
            
            print "Fuzzing var %d:%d" % (i, x)
            
            tmp = tokens
            tmp[i] = struct.pack("<l", num)

            func(token2str(tmp), i)
            j += 1

        for size in sizes:

            if not fastMode:
                fuzzyList = strings
            else:
                fuzzyList = fastStrings

            for stmt in fuzzyList:
                x += 1
                if x < var:
                    continue
                print "Fuzzing var %d:%d:%d" % (i, x, size)
                tmp = tokens
                tmp[i] = stmt*size
                func(token2str(tmp), i)

                j += 1

            if fastMode:
                continue

            for char in range(0, 255):
                x += 1
                if x < var:
                    continue
                print "Fuzzing var %d:%d:%d" % (i, x, size)
                tmp = tokens
                tmp[i] = chr(char)*size
                func(token2str(tmp), i)
                j += 1
