#!/usr/bin/python

"""
Example usage of the ASM Classes library and OpenDis framework
A part of the Inguma Project
"""

import os
import sys
import pydot
import pprint
import pickle
import asmclasses

global rodata
global obj

rodata = obj = None

def renderGraph(edges):
    pprint.pprint(edges)
    #return
    g=pydot.graph_from_edges(edges) 
    g.write_jpeg('test.jpg', prog='dot')
    os.system("display test.jpg")

def searchXRefs(database, functions, level=1, endlevel=3):

    global rodata
    global obj

    f = file(database, "r")

    if obj == None:
        #
        # The database you will load will be in the following format
        #
        # 1) Raw data found in the .rodata section
        # 2) The whole program in Python structures
        #
        rodata, obj = pickle.load(f)

    edges = []
    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:
        if proc.name not in functions:
            continue

        if level > 1 and proc.name.lower() == functions[0]:
            continue

        print "Checking proc.name %s" % proc.name
        mlines = []

        #
        # Iterate over all lines in the procedure
        #
        for line in proc.lines:
            # Current Instruction (Assume is x86)
            instructions = line.code.split(" ")
            
            #if instructions[0].find("j") == 0 or instructions[0] == "call":
            if instructions[0] == "call":
                edges.append(mlines)
                pos = line.code.find("<")+1
                func = line.code[pos:line.code.find(">")]
                
                pos = func.find("+")
                if pos > -1:
                    func = func[:pos]
                
                pos = func.find("@")
                if pos > -1:
                    func = func[:pos]

                mlines = [func]
                functions.append(func)
                print "Added function %s" % func
                edges.append([proc.name, func])

    print "Level is %d and max level is %d" % (level, endlevel)
    if level <= endlevel:
        print "Level is %d and max level is %d" % (level, endlevel)
        level = level + 1
        return searchXRefs(database, functions, level, endlevel)
    else:
        return edges

def printProgram(database, function, level=3):
    ret = searchXRefs(database, [function], level=1, endlevel=int(level))
    
    edges = []
    for row in ret:
        if len(row) == 2:
            edges.append(row)

    print "Size is %d" % len(edges)
    raw_input("Continue? ")
    renderGraph(edges)

def usage():
    print "Example OpenDis framework's API usage"
    print
    print "Usage:", sys.argv[0], "<opendis format database> <function> <level>"
    print

def main():
    if len(sys.argv) < 4:
        usage()
        sys.exit(0)
    else:
        printProgram(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()

