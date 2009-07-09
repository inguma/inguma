#!/usr/bin/python

import re

FUNCTION_PROLOG= ["push%ebp", "mov%esp,%ebp"]
FUNCTION_END = ["leave", "ret"]
GET_SPACE_FOR_VARS = "sub"
ARG_REGISTER = "(%esp)"
VAR_REGISTER = "(%ebp)"
VAR_START = 4
ARG_START = 8

STACK_ARGUMENTS = {}
GLOBAL_RODATA = None

class CVariableFinder:
    def clean(self, buf):
        return buf.replace(" ", "").replace("\r", "").replace("\n", "")
    
    def checkCondition(self, code, what):
        code = map(self.clean, code)
    
        if len(code) == len(what):
            if code == what:
                return True
        else:
            if len(what) <= len(code):
                return code[len(code)-len(what):] == what
    
        return False
    
    def getVariableSpace(self, code):
        strRe = "sub\s+\$0x(\w+),\%esp"
        x = re.compile(strRe, re.IGNORECASE)
        ret = x.search(code)
    
        if ret:
            return int(ret.groups()[0], 16)
    
    def checkVar(self, code, flow):
        strRe = "0x(\w+)\(\%ebp\)"
        x = re.compile(strRe, re.IGNORECASE)
        ret = x.search(code)
    
        if ret:
            arg = ret.groups()[0]
            var = int("0x" + arg, 16)
    
            if len(str(ret.groups()[0])) == 8:
                value = 0xffffffff - var + 1
                #print "### Variable size %d" % (value)
                #print code
                mdict = {"0x" + arg:value}
                
                if not mdict in flow.vars:
                    flow.vars.append(mdict)
            else:
                iArg = (var/8)
                #print "### Print local argument number %d" % iArg
                #print code
                flow.localArgs.append({"0x"+ str(arg):iArg})

    def checkArg(self, code, flow):
        global STACK_ARGUMENTS
    
        strRe = ".*0x(\w+)\(\%esp\)"
        x = re.compile(strRe, re.IGNORECASE)
        ret = x.match(code)
        
        if ret:
            arg = int(ret.groups()[0], 16) / ARG_START
            iArg = arg + 2
            #print "### Argument number %d" % (arg+2)
            #print code
            STACK_ARGUMENTS.update({arg+2:"code"})
            flow.args.append({"0x" + str(arg):iArg})
        else:
            #print "### Argument number 1"
            #print code
            flow.args.append({"0x8":1})
            STACK_ARGUMENTS.update({1:"code"})
            
    
    def checkConstant(self, code, flow):
        global GLOBAL_RODATA
        
        startAddr = GLOBAL_RODATA.address
        endAddr = startAddr + len(GLOBAL_RODATA.data)
    
        strRe = "\$(0x[a-f0-9]+)"
        x = re.compile(strRe, re.IGNORECASE)
        ret = x.search(code)
        
        if ret:
            address = int(ret.groups()[0], 16)
    
            if address >= startAddr and address <= endAddr:
                constValue = self.getConstantValue(GLOBAL_RODATA.data, startAddr, address)
                #print "### -> Found constant at .rodata+%s" % address, code
                #print "### -> Value: %s" % constValue
                flow.consts.append({address:constValue})
    
    def getConstantValue(self, data, startAddr, address):
        pos = int(address) - int(startAddr)
        ret = data[pos:data.find("\x00", pos)]
        return ret
    
    def analyzeInstruction(self, code, flow):
        
        if code.find(VAR_REGISTER) > -1 or True:
            self.checkVar(code, flow)
    
        if code.find(ARG_REGISTER) > -1:
            self.checkArg(code, flow)
        
        self.checkConstant(code, flow)


