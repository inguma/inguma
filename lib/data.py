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
NOTE: Subject to be removed as is not being used!
"""
import os
import sys

class CFuzzingData:
    
    strings = {}
    binary = {}
    numbers = {}
    
    sizes = {}

    path = "." + os.sep

    def __init__(self, path="../"):

        self.readStrings()
        self.readBinary()
        self.readNumbers()
        
        self.readSizes()
        self.path = path
        #FIX: It's hardcoded!
        self.path = "/home/joxean/proyectos/oracletool/fuzz/"

    def readStrings(self):
        f = open(self.path + "strings", "r")
        i = 0
        
        while 1:
            i += 1
            line = f.readline()
            line = line.strip("\r")
            line = line.strip("\n\n")
            if not line:
                break

            self.strings[i] = line
        
        f.close()

    def readBinary(self):
        f = open(self.path + "binary", "rb")
        i = 0
        
        while 1:
            i += 1
            line = f.read(4)

            if not line:
                break

            self.binary[i] = line
        
        f.close()

    def readNumbers(self):
        f = open(self.path + "numbers", "r")
        i = 0
        
        while 1:
            i += 1
            line = f.readline()
            line = line.strip("\r")
            line = line.strip("\n\n")

            if not line:
                break

            self.numbers[i] = line
            
        f.close()

    def readSizes(self):
        f = open(self.path + "sizes", "r")
        i = 0

        while 1:
            i += 1
            line = f.readline()
            line = line.strip("\r")
            line = line.strip("\n\n")

            if not line:
                break

            self.sizes[i] = line
            
        f.close()
    
    def getStringWithSize(self, data, size):
        curSize = len(data)
        tmp = data*((int(size) / curSize)+1)
        
        return tmp[0:int(size)]

if __name__ == "__main__":
    objFuzzData = CFuzzingData()
    
    print "Alphabetic tests"
    for x in objFuzzData.strings:
        print "Test",x,":",objFuzzData.strings[x]
    print

    print "Binary tests"
    for x in objFuzzData.binary:
        print "Test",x,":",repr(objFuzzData.binary[x])
    print

    print "Numeric tests"
    for x in objFuzzData.numbers:
        print "Test",x,":",repr(objFuzzData.numbers[x])

    print    
    print "Total tests: " + str(len(objFuzzData.numbers) + 
                                                       len(objFuzzData.strings) + 
                                                       len(objFuzzData.binary))

