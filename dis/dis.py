#!/usr/bin/python

"""
OpenDis asm beautifier
A part of the Inguma project.

Copyright (c) 2007,2008 Joxean Koret, joxeankoret [at] yahoo.es

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
$Log: dis.py,v $
Revision 1.9  2008/05/27 19:55:23  joxean
Added support for global variables.
Enhanced the output format.
Minor fixes.

Revision 1.8  2007/11/18 11:35:52  joxean
Added support to save the internal cPickle format database to a file

Revision 1.7  2007/09/07 15:24:13  joxean
Correct support for sparc.

Revision 1.6  2007/09/06 20:41:29  joxean
Small change to the version number.

Revision 1.5  2007/09/06 20:40:03  joxean
Initial support for sparc processors.

Revision 1.4  2007/09/05 16:13:43  joxean
Support for AVR binaries

Revision 1.2  2007/09/05 15:19:59  joxean
Initial revision

"""
import re
import os
import sys
import copy
import string

sys.path.append(".")

import asmcallbacks

from asmconsts import *
from asmclasses import *

PROGRAM_SHORT_NAME = "OpenDis"
PROGRAM_NAME = "C Disassembler & Future Decompiler ;)"
VERSION = "$Id: dis.py,v 1.9 2008/05/27 19:55:23 joxean Exp joxean $"

SECTION_TEXT_START = "section .text:"
SECTION_TEXT_END = "section ."

binaryFile = None
pascalHack = False
mainHack = False
exactRodataPos = True
uninteresting = False

callList = []
globalSymbols = {}
usedGlobalSymbols = {}

NM = "nm"
OBJDUMP = "objdump"
SAVE_FILE = None
SQLDB = False

def generateNmFile(bin):

    global NM
    global globalSymbols

    os.putenv("LANG", "C")
    cmd = "%s -B -l -p %s" % (NM, bin)
    mSymbolList = os.popen(cmd).readlines()

    ret = {}

    for symbol in mSymbolList:
        symbol = symbol.strip("\r").strip("\n")

        tmp = CSymbol()
        x = symbol.split("\t")

        if len(x) > 1:
            tmp.filename = x[1]

        x = symbol.split(" ")

        if len(x) == 3:
            if x[0].isalnum:
                tmp.address = eval('0x' + x[0])
            else:
                print "*** Internal error reading the symbol address"
                print x
                sys.exit(-1)

            tmp.symbolType = x[1]
            tmp.name = x[2].split("\t")[0]
        elif len(x) == 11:
            tmp.symbolType = x[9]
            tmp.name = x[10].split("\t")[0]
        elif x == ['']:
            continue
        else:
            print "*** Internal error reading symbol list!"
            print x
            sys.exit(-1)

        globalSymbols[x[0]] = tmp.name
        ret[tmp.name] = tmp
        del tmp

    return ret

def isStriped(line):

    if line.find(">") == -1:
        return True

def generateObjdumpFile(bin, calls = False):

    global pascalHack
    global callList
    global uninteresting
    global OBJDUMP
    global CURRENT_CPU
    global FUNCTION_START

    os.putenv("LANG", "C")
    cmd = "%s --prefix-addresses -d %s" % (OBJDUMP, bin)
    disassembled_data = os.popen(cmd).readlines()

    started = False
    lines = []
    i = 0
    lastFunc = ""

    for line in disassembled_data:
        i += 1
        line = line.strip("\r").strip("\n")

        if calls:
            x = splitData(line)

            if x:
                for ins in INTERESTING_INSTRUCTIONS[CURRENT_CPU]:
                    if x.code.replace(" ", "").replace("\t", "").find(ins) > -1:
                        callList.append(x)
                        break

        if line.find(SECTION_TEXT_START) > -1:
            started = True
            continue
        elif line.find(SECTION_TEXT_END) > -1 and started:
            break
        else:
            if not started:
                continue

        x = splitData(line)

        if pascalHack:
            if lastFunc != x.function and lastFunc.lower() == "pascalmain":
                break
        
        if mainHack:
            if lastFunc != x.function and lastFunc.lower() == "main":
                break

        if x.function == ".text":
            data = x.code.replace(" ", "").replace("\t", "")

            if data == FUNCTION_START[CURRENT_CPU][0]:
                if len(disassembled_data) > i:
                    if disassembled_data[i].strip("\r").strip("\n").replace("\t", "").replace(" ", "").find(FUNCTION_START[CURRENT_CPU][1]) > -1:   
                        x.function = "loc_" + x.address.replace("0x", "")
                        lastFunc = x.function
                        bDone = True
                    else:
                        x.function = lastFunc
                else:
                    x.function = lastFunc
            else:
                x.function = lastFunc

        if not uninteresting:
            if x.function not in IGNORE_FUNCTIONS:
                lines.append(x)
        else:
            lines.append(x)

        lastFunc = x.function

    return lines

def readRodataSection(bin):
    global OBJDUMP

    os.putenv("LANG", "C")
    cmd = "%s -s %s" % (OBJDUMP, bin)
    disassembled_data = os.popen(cmd).readlines()

    buf = []
    bStart = False

    for line in disassembled_data:
        line = line.replace("\r", "").replace("\n", "")
        
        if line.lower().find("contents of section .rodata") == 0 and bStart == False:
            bStart = True
        else:
            if bStart and line.lower().find("contents of section") == 0:
                break
            elif bStart:
                buf.append(line)

    return rodata2hex(buf)

def rodata2hex(lines):
    
    i = -1
    address = ""
    data = ""

    for line in lines:
        i += 1

        line = line.strip()
        line = line[:line.find("  ")]
        
        res = line.split(" ")

        for x in res:
            if x == res[0]:

                if address == "":
                    x = eval("0x" + x)
                    address = x
            else:
                data += x

    data = data.replace(" ", "")
    objRodata = Rodata(address, str2hex(data))

    return objRodata

def str2hex(arg):

    i = 0
    buf = ""

    while 1:
        x = arg[i:i+2]
        if x.strip(" ") == "" or len(x.strip(" ")) == 1:
            return ""

        try:
            buf += eval("'\\x" + x + "'")
        except:
            print "*** internal error str2hex(%s)" % repr(x)
            print sys.exc_info()[1]
            sys.exit(0)

        i += 2
        
        if i == len(arg):
            break

    return buf

def splitData(asm):
    
    asm = asm.strip(" ")
    address = asm[0:asm.find(" ")]

    pos = asm.find("<")
    end = asm.find(">")

    function = asm[pos+1:end]
    pos = function.find("+")
    functionPos = function

    if pos == -1:
        pos = function.find("-")

    if pos > -1:
        function = function[:pos]

    if not isStriped(asm):
        code = asm[end+2:]
    else:
        code = asm[asm.find(" "):].strip(" ")
        function = ".text"
        functionPos = address

    objLine = CLine()
    objLine.address = address
    objLine.code = code
    objLine.function = function
    objLine.label = functionPos

    return objLine

def searchGlobalVar(code, vars):

    global globalSymbols
    global usedGlobalSymbols

    x = re.compile("(0x[a-f0-9]{2,8})", re.IGNORECASE)
    res = x.findall(code)
    
    if res:
        realAddress = res[0]
        address = res[0].lstrip("0x")

        if len(address) == 7:
            address = "0" + address

        if globalSymbols.has_key(address):
            theGlobal = globalSymbols[address]
            if not usedGlobalSymbols.has_key(address):
                usedGlobalSymbols[address] = theGlobal

            code = code.replace(realAddress, theGlobal)

            objLine = CLine()
            objLine.code = code
            objLine.description = "Global symbol %s at %s" % (theGlobal, str(realAddress))

            return objLine

def searchVar(code, vars):

    global exactRodataPos

    x = re.compile("(0x[a-f0-9]{2,8})", re.IGNORECASE)
    res = x.findall(code)

    if res:
        address = eval(res[0])
    else:
        return

    if address > vars.address and address < len(vars.data)+vars.address or True:

        buf = ""
        index = address-vars.address

        if not exactRodataPos:
            buf = vars.data[index::-1]
            index -= buf.find("\x00")-1
    
            buf = ""

        for c in vars.data[index:]:
            if c != "\x00":
                buf += c
            else:
                return buf
    else:
        return address

def appearsToBeGlobalVariable(disLine):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return False

    if disLine.code.find("0x") > 0:
        return True

    return False

def appearsToBeVariable(disLine):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return False

    if not disLine.code.find("$") > -1:
        return False
    
    if disLine.code.find("0x") > disLine.code.find("$"):
        if disLine.code.find(",") >= disLine.code.find("0x")+2:
            return True
        elif disLine.code.find("(") >= disLine.code.find("0x")+2:
            return True
        else:
            for c in disLine.code[disLine.code.find("0x")+2:]:
                if c not in string.hexdigits and c not in ["\r", "\n", " "]:
                    return False

            return True

    return False

def checkBinFile(bin):

    try:
        f = file(bin, "r")
        f.close()
    except:
        print "*** Error opening file %s" % bin
        print sys.exc_info()[1]
        sys.exit(1)

def isArgument(code):

    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return

    x = re.compile("[^\$]0x[a-f0-9]{1,4}\(\%e[b|s]p\)")
    res = x.findall(code)

    return res

def isLocalVar(code):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return

    x = re.compile("[^\$]0x[a-f0-9]{4,8}\(\%e[b|s]p\)")
    res = x.findall(code)

    return res

def getVar(code, expr):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return

    tmp = expr[0]

    if tmp[0] in [",", " ", "*"]:
        tmp = tmp[1:]
        expr[0] = tmp

    decimal = eval(tmp[:tmp.find("(")])
    #decimal = (0xffffffff - decimal + 1)/4
    decimal = (0xffffffff - decimal + 1)
    #arg = "local_var_" + tmp[:tmp.find("(")].replace("ffff", "")#str(decimal)
    arg = "local_var_" + str(decimal/4)
    return arg

def replaceVar(code, expr):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return

    tmp = expr[0]

    if tmp[0] in [",", " "]:
        tmp = tmp[1:]
        expr[0] = tmp

    arg = getVar(code, expr)
    tmp = code.replace(expr[0], arg)

    return tmp

def replaceArgument(code, expr, ismain = False):
    global CURRENT_CPU

    if CURRENT_CPU != "x86":
        return code

    tmp = expr[0]

    if tmp[0] in [",", " ", "*"]:
        tmp = tmp[1:]
        expr[0] = tmp

    decimal = eval(tmp[:tmp.find("(")])
    arg = str(decimal/4-1)

    # FIX: It needs a lot of work
    if tmp.find("esp"):
        arg = str(decimal/4)
        arg = "func_argument_" + arg
        # Ignore at the moment
    else:
        arg = str(decimal/4-1)
        arg = "local_arg_" + arg
    
    if ismain:
        if arg == "func_argument_2" and expr[0].find("ebp") > -1:
            arg = "argc"
        elif arg == "func_argument_3" and expr[0].find("ebp") > -1:
            arg = "argv"
        else:
            pass # at the moment just ignore
            return code
    else:
        return code

    tmp = code.replace(expr[0], arg)

    return tmp

def readProgram(rodata, asm, report = False, showVariables = True, showArguments = True):

    # Procedure's list
    procList = []

    # Single procedure
    proc = CProc()
    proc.lines = []

    for line in asm:
        line.code = line.code.strip(" ")

        if proc.name:
            if proc.name != line.function:
                procList.append(proc)
                del proc

                proc = CProc()
                proc.address = line.address
                proc.name = line.function
                proc.lines = []
        else:
            if not proc.address:
                proc.address = line.address

            proc.name = line.function

        if appearsToBeVariable(line):
            ret = searchVar(line.code, rodata)

            if ret:
                if ret == 0xffffffff:
                    ret = -1

                line.description = ret

        if showArguments:
            ret = isArgument(line.code)
    
            if ret:
                line.code = replaceArgument(line.code, ret, line.function == "main")

        if showVariables:
            ret = isLocalVar(line.code)
            if ret:
                line.code = replaceVar(line.code, ret)

        if appearsToBeGlobalVariable(line):
            res = searchGlobalVar(line.code, rodata)

            if res:
                line.code = res.code
                
                if line.description is None or line.description == "":
                    line.description = res.description
                else:
                    line.description = line.description + " " + res.description

        proc.lines.append(line)

    procList.append(proc)
    
    prog = CProgram()
    prog.procs = procList
    prog.calls = callList

    return procList

def isBranchCallJumpCode(instruction):

    global CURRENT_CPU
    global JUMP_INSTRUCTIONS

    i = 0
    for c in instruction:
        if not c.isalnum():
            instruction = instruction[:i]
        i += 1

    return instruction in JUMP_INSTRUCTIONS[CURRENT_CPU]

def isCallInstruction(instruction):
    
    global CURRENT_CPU
    
    if CURRENT_CPU == "x86":
        return instruction == "call"
    elif CURRENT_CPU == "avr":
        return instruction == "rcall" or instruction == "icall"

def printProgram(procList, pseudo = False, showReport = True, symbols = {}):

    global binaryFile
    global callList
    global CURRENT_CPU
    global usedGlobalSymbols

    prevInstruction = ""
    hits = 0
    lastBlockLines = []
    lastBlock = ""
    repbuf = ""

    print ";"
    print "; File generated by %s - %s" % (PROGRAM_SHORT_NAME, PROGRAM_NAME)
    print "; %s" % VERSION
    print "; Disassembly code for '%s'" %  binaryFile
    print ";"
    print

    showCpuWarnings(CURRENT_CPU) # If any

    if len(usedGlobalSymbols) > 0:
        for address in usedGlobalSymbols:
            x = str(usedGlobalSymbols[address])
            x = x.ljust(32) + " db; Address 0x%s" 
            print x % address
        print

    for x in procList:

        if symbols.has_key(x.name):
            if symbols[x.name].filename:
                print ";"
                print "; Source -> %s " % symbols[x.name].filename
                print ";"

        if len(x.lines) == 0:
            continue

        print "sub %s:" % x.name
	print 

	index = 0

        for line in x.lines:
	    index += 1
            if line.code in IGNORE_INSTRUCTIONS[CURRENT_CPU]:
                continue

            if pseudo:
                ret = asmcallbacks.codeCallback(None, line.code, None, None)
                if ret:
                    if line.description:
                        line.description = str(line.description) + ", PCODE: %s" % ret
                    else:
                        line.description = "PCODE: %s" % ret

            if lastBlockLines == []:
                print "    %s:" % line.label

            if line.description:
                buf = "\t0x%s: %s\t\t;%s" % (line.address, line.code.ljust(30), repr(line.description))
            else:
                buf = "\t0x%s: %s" % (line.address, line.code.ljust(30))
            print buf

            lastBlockLines.append(line)
            lastBlock += buf + os.linesep

            instruction = line.code.split(" ")[0].strip(" ")

            if instruction == "":
                instruction = " "

            if isBranchCallJumpCode(instruction):
                if isCallInstruction(instruction):
                    for x in WARNING_CALLS:
                        if line.code.find(x) > -1:
                            hits += 1
                            if showReport:
                                repbuf += os.linesep +  " %d) Usage of %s in function %s:%s%s" % (hits, x, line.function, os.linesep, os.linesep)
                                repbuf += lastBlock
                                repbuf += os.linesep*2

                                res = asmcallbacks.warningCallback(lastBlockLines, line.code, x, prevInstruction)

                                if res:
                                    repbuf += " Analysis: %s" % res
                                    repbuf += os.linesep*2
                                    
                                    print "\t; Analysis: %s" % res

                            print "\t; CHECK: Usage of %s (Hit %d)" % (x, hits)

                lastBlock = ""
                lastBlockLines = []
                print
            elif line.code.replace(" ", "") == "sub%eax,%esp" and len(lastBlockLines) > 1:
                ins = lastBlockLines[len(lastBlockLines)-2]
                
                if ins.code.find("shl") > -1 and ins.code.find("%eax") > -1:
                    print
                    print "    ;"
                    print "    ; Start: Programmers code starts here?"
                    print "    ;"
                    print "    %s:" % line.label

            prevInstruction = buf

        print "end sub;"
        print 

    if callList != []:
        print ";"
        print "; Interesting jmps/calls in '%s'" % binaryFile
        print ";"
        
        for x in callList:
            if x.address.find("00") > -1:
                print ";\t" + x.code + "; 0x" + x.address + " <" + x.label + "> - Appears to be unusable"
            else:
                print ";\t" + x.code + "; 0x" + x.address + " <" + x.label + "> "
        print

    if showReport:
        print ";"
        print "; Report of presumable error prone blocks"
        print ";"
        print "; " + repbuf.replace(os.linesep, os.linesep + ";")
        print "; Total of %d hit(s). Happy hunting!" % hits
        print

def createBaseTables(db):
    c = db.cursor()
    try:
        c.execute("""
              CREATE TABLE RODATA (START_ADDRESS, RODATA)
              """)
        c.execute("""
              CREATE TABLE FUNCTIONS (ADDRESS, FUNCTION)
              """)
        c.execute("""
              CREATE TABLE FUNCTION_LINES (ADDRESS, LABEL, FUNCTION, CODE, DESCRIPTION)
              """)
        c.execute("""
              CREATE TABLE DATABASE_FORMAT (FORMAT)
              """)
        c.execute(""" INSERT INTO DATABASE_FORMAT VALUES ('OPENDIS') """)
        db.commit()
        c.close()
    except:
        print "Warning! Error creating base tables:", sys.exc_info()[1]

def saveRodataToDatabase(db, rodata):
    c = db.cursor()
    c.execute("INSERT INTO RODATA VALUES (?, ?)", (rodata.address, rodata.data))
    db.commit()
    c.close()

def saveProcToDb(db, proc):
    
    c = db.cursor()
    c.execute("INSERT INTO FUNCTIONS VALUES (?, ?)", (proc.address, proc.name))

    for line in proc.lines:
        c.execute(""" INSERT INTO FUNCTION_LINES VALUES (?, ?, ?, ?, ?) """, (line.address, line.label, proc.name, line.code, line.description) )

    db.commit()
    c.close()

def saveProgramToDatabase(db, program):
    for proc in program:
        saveProcToDb(db, proc)

def saveToDatabase(rodata, program):
    
    global SAVE_FILE
    
    try:
        import sqlite3
    except:
        print "Error import module sqlite3:", sys.exc_info()[1]
        print "Can't save database..."
        return False
    
    try:
        db = sqlite3.connect(SAVE_FILE)
    except:
        print "Error creating database:", sys.exc_info()[1]
        return False

    createBaseTables(db)
    saveRodataToDatabase(db, rodata)
    saveProgramToDatabase(db, program)

def decompile(bin, out, args):

    global pascalHack
    global mainHack
    global uninteresting
    global SAVE_FILE

    checkBinFile(bin)

    pseudo = False
    report = False
    showArguments = False
    showVariables = False
    calls = False
    ignoreRodata = False
    saveData = True

    if "-p" in args:
        pseudo = True

    if "-r" in args:
        report = True
    
    if "-v" in args:
        showVariables = True
    
    if "-a" in args:
        showArguments = True

    if "-ph" in args:
        pascalHack = True
    
    if "-mh" in args:
        mainHack = True
    
    if "-j" in args:
        calls = True

    if "-i" in args:
        ignoreRodata = True

    if "-rh" in args:
        exactRodataPos = True
    
    if "-d" in args:
        uninteresting = True

    sys.stderr.write("Reading symbols ... " + os.linesep)
    symbols = generateNmFile(bin)

    if not ignoreRodata:
        sys.stderr.write("Reading .rodata section ..." + os.linesep)
        rawRoData = readRodataSection(bin)
    else:
        rawRoData = Rodata(0,"")

    sys.stderr.write("Reading .text section ..." + os.linesep)
    rawDisassemble = generateObjdumpFile(bin, calls)

    sys.stderr.write("Reading the whole program ..." + os.linesep)
    program = readProgram(rawRoData, rawDisassemble, report, showVariables, showArguments)

    if SAVE_FILE != None:
        if not SQLDB:
            try:
                import cPickle as pickle
            except:
                try:
                    import pickle as pickle
                except:
                    print "Error:", sys.exc_info()[1]
    
            sys.stderr.write("Writing database to file..." + os.linesep)
            x = (rawRoData, program)
            f = file(SAVE_FILE, "w")
            pickle.dump(x, f)
            f.close()
        else:
            saveToDatabase(rawRoData, program)
        sys.stderr.write("Database saved\n")
        return

    sys.stderr.write("Printing the generated program..." + os.linesep)
    printProgram(program, pseudo, report, symbols)

def usage():
    print PROGRAM_SHORT_NAME, "-", PROGRAM_NAME
    print "Copyright (c) 2007 Joxean Koret"
    print
    print VERSION
    print
    print "Usage:"
    print sys.argv[0], "<binary file> [options]"
    print
    print "Options:"
    print " -s\t\tSave the database to -s=file"
    print " -sdb\t\tSave the database to -sdb=database"
    print " -p\t\tGenerate pseudo-code instructions"
    print " -r\t\tGenerate a report of dangerous functions"
    print " -v\t\tSearch for variables"
    print " -a\t\tSearch for arguments"
    print " -j\t\tReport interesting calls (call *%eax, jmp *%ebx, etc..)"
    print " -ph\t\tEnable the Free Pascal hack"
    print " -mh\t\tEnable the 'only code before main' hack"
    print " -i\t\tIgnore .rodata section"
    print " -rh\t\tDon't search afterward for the 0x00 when reading constants"
    print " -d\t\tDecompile all, even uninteresting functions"
    print " -f\t\tDisassemble object file in format -f=<format> (i.e., objdump -b elf32-arm)"
    print " -c\t\tAssume that CPU is of type -c=CPU (i.e., -c=x86)"
    print

def showCpuWarnings(cpu):

    global mainHack

    if cpu.lower() == "avr":
        if not mainHack:
            print "; TIP: For 'avr' usage of -mh (main hack) is recommended\n"

def main():
    global binaryFile
    global OBJDUMP
    global NM
    global CURRENT_CPU
    global SAVE_FILE
    global SQLDB

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    binaryFile = None
    outputFile = None
    args = []

    for arg in sys.argv[1:]:
        if arg[0] == "-": # Is an option
            if len(arg) > 1:
                if arg[1] == "f":
                    OBJDUMP += " -b %s " % arg[3:]
                    NM += " --target=%s " % arg[3:]
                    sys.stderr.write("Format is %s\n" % arg[3:])
                elif arg[1] == "c":
                    cpu = arg[3:].lower()
                    
                    if cpu.lower() in AVAILABLE_CPUS:
                        CURRENT_CPU = cpu
                        sys.stderr.write("Assuming CPU is %s\n" % arg[3:].lower())
                    else:
                        sys.stdout.write("No support for CPU %s\n" % cpu.lower())
                        sys.stdout.write("Oficially supported CPU's are:%s\n" % AVAILABLE_CPUS)
                        sys.stdout.write("\n")
                        sys.stdout.write("Press enter to continue or Ctrl+C to cancel...")
                        print "Using unknown cpu %s" % cpu
                        CURRENT_CPU = "unknown"
                        OBJDUMP += " -b %s " % arg[3:]
                        NM += " --target=%s " % arg[3:]
                elif arg[1:4] == "sdb":
                    SAVE_FILE = arg[5:].lower()
                    SQLDB = True
                elif arg[1] == "s":
                    print arg[1:3]
                    SAVE_FILE = arg[3:].lower()
                else:
                    args.append(arg)
        else:
            if not binaryFile:
                binaryFile = arg
            else:
                outputFile = arg

    if not binaryFile:
        usage()
        sys.exit(0)

    decompile(binaryFile, outputFile, args)

if __name__ == "__main__":
    main()
