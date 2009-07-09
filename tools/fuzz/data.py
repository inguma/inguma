#!/usr/bin/python

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

