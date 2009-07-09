#!/usr/bin/python

"""
Example usage of the ASM Classes library and OpenDis framework
A part of the Inguma Project
"""

import sys
import pickle
import asmclasses

import x86ops as CurrentCpu

def printProgram(database, function, fromto=0):

    f = file(database, "r")

    #
    # The database you will load will be in the following format
    #
    # 1) Raw data found in the .rodata section
    # 2) The whole program in Python structures
    #
    rodata, obj = pickle.load(f)
    CurrentCpu.GLOBAL_RODATA = rodata
    cpu = CurrentCpu.CVariableFinder()

    functionProlog = False

    flow = asmclasses.CProcTree()

    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:
        if proc.name.lower() != function.lower():
            continue

        i = 0
        block = []
        tested = 0
        #
        # Iterate over all lines in the procedure
        #
        for line in proc.lines:
            i += 1
            # Current Instruction (Assume is x86)
            instructions = line.code.split(" ")
            #print line.code
            block.append(line.code)
            
            if functionProlog:
                if tested == 1:
                    tested = 0
                    functionProlog = False
                else:
                    tested = 1

            if i == len(CurrentCpu.FUNCTION_PROLOG):
                if cpu.checkCondition(block, CurrentCpu.FUNCTION_PROLOG):
                    functionProlog = True
                    #print "### FUNCTION PROLOG ###"

            if instructions[0].find("j") == 0 or instructions[0].find("call") > -1:
                block = []
                functionProlog = False
                
                if instructions[0].find("call") > -1:
                    #print "CALL", instructions[len(instructions)-1], CurrentCpu.STACK_ARGUMENTS
                    CurrentCpu.STACK_ARGUMENTS = {}
                #print
            else:
                cpu.analyzeInstruction(line.code, flow)
            
            if functionProlog:
                if instructions[0] == CurrentCpu.GET_SPACE_FOR_VARS:
                    space = cpu.getVariableSpace(line.code)
                    #print "### Space reserved %s ###" % space
                    #print "### So number of locals appears to be %d ###" % (int(space) / 8)
                    flow.localVariables = int(space) / 8

        if len(block) >= len(CurrentCpu.FUNCTION_END):
            if cpu.checkCondition(block, CurrentCpu.FUNCTION_END):
                #print "### FUNCTION END ###"
                pass

        print "Expected number of local variables + local parameters", flow.localVariables
        print "Foreign arguments",flow.args
        print "Local arguments", flow.localArgs
        print "Local vars", flow.vars

def usage():
    print "Example OpenDis framework's API usage"
    print
    print "Usage:", sys.argv[0], "<opendis format database> <function>"
    print

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)
    else:
        printProgram(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()

