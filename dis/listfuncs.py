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

    showLabel = False
    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:
        print proc.address, "\t", proc.name

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

