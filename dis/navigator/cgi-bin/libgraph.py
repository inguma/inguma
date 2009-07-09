#!/usr/bin/python

import os
import sys
import pydot
import pprint

class CJump():
    address = ""
    value = False

    def __init__(self, addr, value):
        self.address = addr
        self.value = value

class CControlFlowDiagram:

    edges = {}
    procedureName = ""
    startAddress = None
    endAddress = None
    currentAddress = None
    currentEdge = []
    connections = []
    connectedRegions = []
    xrefs = []

    def __init__(self):
        pass

    def addNewEdge(self, address):
        if self.currentEdge != []:
            self.edges[self.currentAddress] = self.currentEdge
            
        self.currentEdge = []
        self.currentAddress = address

    def addNewConnectedEdge(self, address, connect):
        self.addNewEdge(address)

    def addToCurrentEdge(self, line):
        self.currentEdge.append(line)

    def addConnection(self, fromAddress, toAddress):
        self.connections.append({fromAddress:toAddress})
        self.connectedRegions.append(toAddress)

    def closeCurrentEdge(self):
        self.edges[self.currentAddress] = self.currentEdge
        self.currentAddress = None
    
    def addXRef(self, address):
        self.xrefs.append(address)

def renderGraph(edges):
    #return
    g=pydot.graph_from_edges(edges) 
    g.write_jpeg('test.jpg', prog='dot')
    os.system("konqueror test.jpg")

def getJumpAddress(instruction):
    data = instruction.split(" ")
    for element in data[1:]:
        if element == "":
            continue
        else:
            return element

def getValueColor(value):
    if value:
        return "green"
    else:
        return "red"

def generateGraph(flow, function):
    """
    import pprint
    pprint.pprint(flow.connections)
    return
    """
    buf = "digraph G { node [fontname=Courier]; "
    colorize = False
    times = 0

    # First, create the shapes
    for shape in flow.edges:
        buf += "\n"
        times += 1
        
        lines = ""
        for line in flow.edges[shape]:
            if lines == "":
                lines = "%s\l" % line
            else:
                lines += "%s\l" % line
                
        #if len(flow.edges) == times:
        #    colorize = True
                
        if shape == flow.startAddress:
            buf += ' "%s" [shape=box, color = blue, label = ";;; Entry point ;;;\l\l%s"]\n' % (shape, lines.replace('"', "'"))
        #elif colorize:
        #    buf += ' "%s" [shape=box, color = red, label = "%s"]\n' % (shape, lines.replace('"', "'"))
        #    colorize = False
        else:
            buf += ' "%s" [shape=box, label = "%s"]\n' % (shape, lines.replace('"', "'"))

    # Next, add the connections between shapes
    for connection in flow.connections:
        for element in connection:
            color = getValueColor(connection[element].value)
            buf += '"%s" -> "%s" [style = bold, color=%s]\n' % (element, connection[element].address, color)

    buf += "}"

    return buf

def createTree(db, function, generate=True):
    # Create a new control flow object
    flow = CControlFlowDiagram()

    c = db.cursor()
    c.execute("SELECT * FROM FUNCTION_LINES WHERE FUNCTION = ? ", (function, ))
    
    for row in c.fetchall():
        line = row[3]
        instructions = line.split(" ")
        if instructions[0].find("j") == 0:
            flow.addXRef(getJumpAddress(line))
    c.close()

    # Re-read the procedure's lines
    c.execute("SELECT * FROM FUNCTION_LINES WHERE FUNCTION = ? ", (function, ))

    mlines = []
    oldAddr = None
    bConnectNext = False
    prevInstruction = ""
    times = 0
    
    for row in c.fetchall():
        times += 1
        
        if times == 1:
            flow.startAddress = row[0]
            flow.procedureName = row[1]
            
        line = row[3]
        
        if row[4] != None and row[4] != "" and row[4] != '\x03': # Hack!
            line = line + "\t; " + repr(row[4].replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
        
        if flow.currentAddress == None:
            flow.addNewEdge(row[0])

        # Current Instruction (Assume is x86)
        instructions = line.split(" ")

        if bConnectNext:
            bConnectNext = False
            flow.addNewEdge(row[0])
            flow.addConnection(oldAddr, CJump(row[0], False))

        if row[0] in flow.connectedRegions:
            oldAddr = flow.currentAddress
            flow.addNewEdge(row[0])
            
            if bConnect:
                flow.addConnection(oldAddr, CJump(row[0], True))

        if row[0] in flow.xrefs:
            oldAddr = flow.currentAddress
            flow.addNewEdge(row[0])

            if prevInstruction not in ["jmp", "ret"]:
                flow.addConnection(oldAddr, CJump(row[0], False))

        flow.addToCurrentEdge(row[0] + "\t" + line)

        if instructions[0].find("j") == 0:
            oldAddr = flow.currentAddress
            flow.addConnection(oldAddr, CJump(getJumpAddress(line), True))

            if instructions[0] not in ["jmp", "ret"]:
                bConnectNext = True
            else:
                oldAddr = None

        prevInstruction = instructions[0]

    flow.endAddress = row[0]
    flow.closeCurrentEdge()
    
    if generate:
        return generateGraph(flow, function)
    else:
        return flow

