#!/usr/bin/python

"""
Example usage of the ASM Classes library and OpenDis framework
A part of the Inguma Project
"""

import sys
import pickle
import asmclasses

def printProgram(database):
    f = file(database, "r")
    
    #
    # The database you will load will be in the following format
    #
    # 1) Raw data found in the .rodata section
    # 2) The whole program in Python structures
    #
    rodata, obj = pickle.load(f)

    print "Section .rodata: %s" % hex(rodata.address)
    print "-"*80
    print repr(rodata.data)
    print "-"*80
    print 

    showLabel = False
    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:
        print "PROCEDURE", proc.name, "AT 0x" + proc.address

        #
        # Iterate over all lines in the procedure
        #
        for line in proc.lines:
            if showLabel:
                print "  %s:"  % line.label
            if line.description:
                mtype = str(type(line.description)).split("'")[1]
                print "\t", "0x" + line.address.ljust(8) + ":", line.code.ljust(30), ";", mtype.ljust(4) + ":", repr(line.description)
            else:
                print "\t", "0x" + line.address.ljust(8) + ":", line.code.ljust(30)

            # Current Instruction (Assume is x86)
            instructions = line.code.split(" ")

            if instructions[0].find("j") == 0 or instructions[0].find("call") > -1:
                print
                showLabel = True
            else:
                showLabel = False

        print "END PROCEDURE"
        print

def usage():
    print "Example OpenDis framework's API usage"
    print
    print "Usage:", sys.argv[0], "<opendis format database>"
    print

def main():
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)
    else:
        printProgram(sys.argv[1])

if __name__ == "__main__":
    main()

