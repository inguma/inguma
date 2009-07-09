#!/usr/bin/python

"""
Example usage of the ASM Classes library and OpenDis framework
A part of the Inguma Project
"""

import os
import sys
import pydot
import pickle
import asmclasses

def drawGraph(edges):
    g = pydot.graph_from_edges(edges)
    g.write_jpg("test.jpg", prog="dot")
    os.system("display test.jpg")

def printProgram(database, function, fromto=0):
    f = file(database, "r")

    #
    # The database you will load will be in the following format
    #
    # 1) Raw data found in the .rodata section
    # 2) The whole program in Python structures
    #
    rodata, obj = pickle.load(f)
    fromto = int(fromto)

    edges = []

    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:
        if fromto == 0:
            if proc.name.lower() != function.lower():
                continue
        elif proc.name.lower() == function.lower():
            continue

        mlines = []
        #
        # Iterate over all lines in the procedure
        #
        for line in proc.lines:
            # Current Instruction (Assume is x86)
            instructions = line.code.split(" ")

            if instructions[0].find("j") == 0 or instructions[0].find("call") > -1:
                if fromto == 0:
                    print line.address + ":" + instructions[len(instructions)-1]
                    edges.append([function, line.code])
                elif line.code.find(function.lower()) > -1:
                    print "At %s: %s -> %s" % (line.address, proc.name, instructions[len(instructions)-1])

    drawGraph(edges)

def usage():
    print "Example OpenDis framework's API usage"
    print
    print "Usage:", sys.argv[0], "<opendis format database> <function> <option>"
    print
    print "Option: "
    print " 0               From the function"
    print " 1               To the function"
    print 

def main():
    if len(sys.argv) < 4:
        usage()
        sys.exit(0)
    else:
        printProgram(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()

