#!/usr/bin/python

"""
An example usage of the OpenDis Framework
A part of the Inguma Project

The following example compares 2 databases to look for differences between different versions.

Copyright (c) 2007 Joxean Koret
"""

import os
import sys
import pickle
import asmclasses

def compareLines(fixedProc, procOrig, fOrig, fFixed):
    
    i = -1
    for objLine in fixedProc.lines:
        i += 1

        if objLine.code.split(" ")[0] != procOrig.lines[i].code.split(" ")[0]:
            print "Function %s differs at line %d" % (fixedProc.name, i+1)
            writeProcedureToFile(fOrig, procOrig)
            writeProcedureToFile(fFixed, fixedProc)
            break

def log(buf):
    sys.stderr.write(buf + "\n")

def getDatabases(orig, fixed):
    
    # Read the first object database
    f = file(orig, "r")
    rodataOrig, objOrig = pickle.load(f)
    f.close()

    # Read the second object database
    f = file(fixed, "r")
    rodataFixed, objFixed = pickle.load(f)
    f.close()

    return rodataOrig, objOrig, rodataFixed, objFixed

def generatediff(orig, fixed, program=None):

    rodataOrig, objOrig, rodataFixed, objFixed = getDatabases(orig, fixed)

    if len(objOrig) != len(objFixed):
        log("Different number of functions\n")

    fOrig  = file(orig + ".asm", "w")
    fFixed = file(fixed + ".asm", "w")

    for procOrig in objOrig:
        procFixed = searchProc(objFixed, procOrig.name)

        if not procFixed:
            continue
        
        if len(procFixed.lines) != len(procOrig.lines):
            log("Function %s differs (%d, %d)" % (procFixed.name, len(procFixed.lines), len(procOrig.lines)))

            writeProcedureToFile(fOrig, procOrig)
            writeProcedureToFile(fFixed, procFixed)
        else:
            compareLines(procFixed, procOrig, fOrig, fFixed)

    if len(objOrig) != len(objFixed):
        for procFixed in objFixed:
            procOrig = searchProc(objOrig, procFixed.name)
            
            if not procOrig:
                log("Function %s ONLY exists in fixed version" % procFixed.name)
                continue

    print
    
    if program:
        os.system("%s %s.asm %s.asm" % (program, orig, fixed))
    else:
        log("Check the files %s and %s" % (orig + ".asm", fixed + ".asm"))

def writeProcedureToFile(f, proc):
    f.write("0x%s: sub %s\n" % (proc.address, proc.name))
    for line in proc.lines:
        if line.code == "nop": # Assume we're in x86
            continue
        if line.description:
            data = "0x%s:\t%s; %s" % (line.code, line.address, line.description)
        else:
            data= "0x%s:\t%s" % (line.code, line.address)

        f.write(data + "\n")
    f.write("0x%s: end sub; (%s) \n\n" % (proc.address, proc.name))

def cleanCode(base):
    data = base.split(" ")
    
    for x in data:
        tmp = x.split(",")
        for arg in tmp:
            if arg.find("$0x") == 0 and len(arg) > 6:
                base = base.replace(arg, arg[0:len(arg)-2] + "XX")

    return base

def searchProc(obj, name):
    for x in obj:
        if x.name == name:
            return x

def banner():
    print "OpenDis ASM Diff v0.1 - The Inguma Project"
    print "Copyright (c) Joxean Koret 2007, 2008"
    print

def usage():
    print "Usage:", sys.argv[0], " <database 1> <database 2> [program to show differences]"
    print 
    print "Example:"
    print sys.argv[0], "test1.db fixed.db kompare"

def main():
    banner()

    if len(sys.argv) < 3:
        usage()
        sys.exit(0)
    else:
        if len(sys.argv) == 4:
            generatediff(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            generatediff(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
