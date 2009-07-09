#!/usr/bin/python

class CDisassembledLine:

    address = None
    function = None
    code = None
    functionPos = None

    def __init__(self, theaddress, thefunction, thecode, thefunctionPos):
        self.address = theaddress
        self.function = thefunction
        self.code = thecode
        self.functionPos = thefunctionPos

class Rodata:

    address = None
    data = None

    def __init__(self, theaddress, thedata):
        self.data = thedata
        self.address = theaddress

class AsmLine:
    address = None
    code = None
    data = None

#################
### The new fashion  ###
#################

VAR_TYPE_GLOBAL = 0
VAR_TYPE_LOCAL = 0

class CRodata:
    address = None
    data = None

class CVar:
    varType = VAR_TYPE_LOCAL
    address = None
    name = None
    value = None

class CVars:
    vars = []

class CLine:
    address = None
    code = None
    label = None
    description = None

class CLines:
    lines = []

class CParam:
    address = None
    name = None

class CParams:
    params = []

class CProc:
    name = None
    address = None
    lines = []
    vars = []
    params = []

    startAddress = None
    endAddress = None

class CProcs:
    procs = None

class CProgram:
    vars = None # Only globals
    rodata = None
    procs = None

class CCall:
    address = None
    code = None
    function = None
    label = None

class CSymbol:

    address = None
    symbolType = None
    name = None
    filename = None

#################
### End new fashion  ###
#################

class CNode:
    # Condition
    condition = []
    # Raw code
    code = None
    # Execution flow
    nodes = []

class CProcTree:
    # Space reserved for locals
    localVariables = None
    # Variables found
    vars = []
    # Arguments found
    args = []
    # Local arguments found
    localArgs = []
    # Constants found
    consts = []
    # Execution flow
    nodes = []



    
    
    
    
    
    
    
    
    
    
    
    
    
