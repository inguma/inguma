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

class CJump():
    address = ""
    value = False

    def __init__(self, addr, value):
        self.address = addr
        self.value = value

class CControlFlowDiagram:

    edges = {}
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
    pprint.pprint(edges)
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
    
    # First, create the shapes
    for shape in flow.edges:
        buf += "\n"
        
        lines = ""
        for line in flow.edges[shape]:
            if lines == "":
                lines = "%s\l" % line
            else:
                lines += "%s\l" % line

        buf += ' %s [shape=box, label = "%s"]\n' % (shape, lines)
        #print shape, flow.edges[shape]

    # Next, add the connections between shapes
    for connection in flow.connections:
        for element in connection:
            color = getValueColor(connection[element].value)
            buf += "%s -> %s [style = bold, color=%s]\n" % (element, connection[element].address, color)

    buf += "}"
    f = file("%s.dot" % function, "w")
    f.writelines(buf)
    f.close()

    g = pydot.graph_from_dot_data(buf)
    g.write_jpeg("%s.jpg" % function, prog="dot")
    os.system("konqueror %s.jpg" % function)

def createTree(database, function, to=None):
    f = file(database, "r")

    #
    # The database you will load will be in the following format
    #
    # 1) Raw data found in the .rodata section
    # 2) The whole program in Python structures
    #
    rodata, obj = pickle.load(f)

    # Create a new control flow object
    flow = CControlFlowDiagram()

    #
    # Iterate over all procedures to get the XRefs
    #
    for proc in obj:
        if proc.name.lower() != function.lower():
            continue
        
        for line in proc.lines:
            instructions = line.code.split(" ")
            if instructions[0].find("j") == 0:
                flow.addXRef(getJumpAddress(line.code))

    #
    # Iterate over all procedures in the program (List object)
    #
    for proc in obj:

        if proc.name.lower() != function.lower():
            continue

        mlines = []
        oldAddr = None
        bConnectNext = False
        prevInstruction = ""
        #
        # Iterate over all lines in the procedure
        #
        for line in proc.lines:
            #print line.address + "\t" + line.code
            if flow.currentAddress == None:
                flow.addNewEdge(line.address)

            # Current Instruction (Assume is x86)
            instructions = line.code.split(" ")

            if bConnectNext:
                bConnectNext = False
                flow.addNewEdge(line.address)
                flow.addConnection(oldAddr, CJump(line.address, False))

            if line.address in flow.connectedRegions:
                oldAddr = flow.currentAddress
                flow.addNewEdge(line.address)
                
                if bConnect:
                    flow.addConnection(oldAddr, CJump(line.address, True))

            if line.address in flow.xrefs:
                oldAddr = flow.currentAddress
                flow.addNewEdge(line.address)

                if prevInstruction not in ["jmp", "ret"]:
                    flow.addConnection(oldAddr, CJump(line.address, False))

            flow.addToCurrentEdge(line.address + "\t" + line.code)

            if instructions[0].find("j") == 0:
                oldAddr = flow.currentAddress
                flow.addConnection(oldAddr, CJump(getJumpAddress(line.code), True))

                if instructions[0] not in ["jmp", "ret"]:
                    bConnectNext = True
                else:
                    oldAddr = None

            prevInstruction = instructions[0]

    flow.closeCurrentEdge()
    generateGraph(flow, function)

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
        createTree(sys.argv[1], sys.argv[2])

def test():
    g = pydot.graph_from_dot_data("""digraph G {
// rankdir=LR
node [fontname=Courier];
       4288512 [shape=box, label = "0x00417000 90                              nop \l0x00417001 90                              nop \l0x00417002 90                              nop \l0x00417003 90                              nop \l0x00417004 90                              nop \l0x00417005 90                              nop \l0x00417006 90                              nop \l0x00417007 90                              nop \l0x00417008 EB15                            jmp 0x17\l0x0041701f E8E6FFFFFF                      call 0xffffffeb\l0x0041700a B98BE61341                      mov ecx,0x4113e68b\l0x0041700f 81F139E61341                    xor ecx,0x4113e639\l0x00417015 5E                              pop esi\l"]
       4288534 [shape=box, label = "0x00417016 807431FF17                      xor byte [ecx+esi-0x1],0x17\l"]
       4288539 [shape=box, label = "0x0041701b E2F9                            loop 0xfffffffb\l"]
       4288541 [shape=box, label = "0x0041701d EB05                            jmp 0x7\l0x00417024 33DB                            xor ebx,ebx\l0x00417026 648B4330                        mov eax,fs:[ebx+0x30]\l0x0041702a 8B400C                          mov eax,[eax+0xc]\l0x0041702d 8B701C                          mov esi,[eax+0x1c]\l0x00417030 AD                              lodsd \l0x00417031 8B7808                          mov edi,[eax+0x8]\l0x00417034 E845000000                      call 0x4a\l0x0041707e 5E                              pop esi\l0x0041707f 6833320000                      push dword 0x3233\l0x00417084 687773325F                      push dword 0x5f327377\l0x00417089 54                              push esp\l0x0041708a BA926E0484                      mov edx,0x84046e92\l0x0041708f FFD6                            call esi\l"]
       4288569 [shape=box, label = "0x00417039 53                              push ebx\l"]
       4288570 [shape=box, label = "0x0041703a 56                              push esi\l0x0041703b 8B5F3C                          mov ebx,[edi+0x3c]\l0x0041703e 8B5C3B78                        mov ebx,[ebx+edi+0x78]\l0x00417042 03DF                            add ebx,edi\l0x00417044 53                              push ebx\l0x00417045 8B5B20                          mov ebx,[ebx+0x20]\l0x00417048 03DF                            add ebx,edi\l0x0041704a 53                              push ebx\l"]
       4288587 [shape=box, label = "0x0041704b 83C304                          add ebx,0x4\l"]
       4288590 [shape=box, label = "0x0041704e 8B33                            mov esi,[ebx]\l0x00417050 03F7                            add esi,edi\l0x00417052 33C9                            xor ecx,ecx\l"]
       4288596 [shape=box, label = "0x00417054 AC                              lodsb \l"]
       4288597 [shape=box, label = "0x00417055 32C8                            xor cl,al\l0x00417057 C1C105                          rol ecx,0x5\l0x0041705a 84C0                            test al,al\l"]
       4288604 [shape=box, label = "0x0041705c 75F6                            jnz 0xfffffff8\l"]
       4288606 [shape=box, label = "0x0041705e 2BCA                            sub ecx,edx\l"]
       4288608 [shape=box, label = "0x00417060 75E9                            jnz 0xffffffeb\l"]
       4288610 [shape=box, label = "0x00417062 58                              pop eax\l0x00417063 2BD8                            sub ebx,eax\l0x00417065 D1EB                            shr ebx,0x1\l0x00417067 5E                              pop esi\l0x00417068 035E24                          add ebx,[esi+0x24]\l0x0041706b 03DF                            add ebx,edi\l0x0041706d 668B0B                          mov cx,[ebx]\l0x00417070 8B5E1C                          mov ebx,[esi+0x1c]\l0x00417073 03DF                            add ebx,edi\l0x00417075 8B048B                          mov eax,[ebx+ecx*4]\l0x00417078 03C7                            add eax,edi\l0x0041707a 5E                              pop esi\l0x0041707b 5B                              pop ebx\l"]
       4288636 [shape=box, label = "0x0041707c FFE0                            jmp eax\l"]
       2088770935 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c801d77 LoadLibraryA\l"]
       4288657 [shape=box, label = "0x00417091 8BF8                            mov edi,eax\l0x00417093 81EC00020000                    sub esp,0x200\l0x00417099 8BEC                            mov ebp,esp\l0x0041709b 53                              push ebx\l0x0041709c 6A01                            push byte 0x1\l0x0041709e 6A02                            push byte 0x2\l0x004170a0 BA83538300                      mov edx,0x835383\l0x004170a5 FFD6                            call esi\l"]
       1906391953 [shape=box, style=filled, color=".7 .3 1.0", label = "0x71a13b91 socket\l"]
       4288679 [shape=box, label = "0x004170a7 53                              push ebx\l0x004170a8 53                              push ebx\l0x004170a9 683E2FD9FE                      push dword 0xfed92f3e\l0x004170ae 6802003C19                      push dword 0x193c0002\l0x004170b3 8BD4                            mov edx,esp\l0x004170b5 8BD8                            mov ebx,eax\l0x004170b7 6A10                            push byte 0x10\l0x004170b9 52                              push edx\l0x004170ba 53                              push ebx\l0x004170bb BA6330605A                      mov edx,0x5a603063\l0x004170c0 FFD6                            call esi\l"]
       1906393194 [shape=box, style=filled, color=".7 .3 1.0", label = "0x71a1406a connect\l"]
       4288706 [shape=box, label = "0x004170c2 50                              push eax\l0x004170c3 B402                            mov ah,0x2\l0x004170c5 50                              push eax\l0x004170c6 55                              push ebp\l0x004170c7 53                              push ebx\l0x004170c8 BA005860E2                      mov edx,0xe2605800\l0x004170cd FFD6                            call esi\l"]
       1906401626 [shape=box, style=filled, color=".7 .3 1.0", label = "0x71a1615a recv\l"]
       4288719 [shape=box, label = "0x004170cf BFACAC0685                      mov edi,0x8506acac\l0x004170d4 FFE5                            jmp ebp\l0x0012fc90 83EC20                          sub esp,0x20\l0x0012fc93 8BEC                            mov ebp,esp\l0x0012fc95 895D04                          mov [ebp+0x4],ebx\l0x0012fc98 897D00                          mov [ebp+0x0],edi\l0x0012fc9b 81EC00020000                    sub esp,0x200\l0x0012fca1 896514                          mov [ebp+0x14],esp\l0x0012fca4 33DB                            xor ebx,ebx\l0x0012fca6 648B4330                        mov eax,fs:[ebx+0x30]\l0x0012fcaa 8B400C                          mov eax,[eax+0xc]\l0x0012fcad 8B701C                          mov esi,[eax+0x1c]\l0x0012fcb0 AD                              lodsd \l0x0012fcb1 8B7808                          mov edi,[eax+0x8]\l0x0012fcb4 897D08                          mov [ebp+0x8],edi\l0x0012fcb7 E845000000                      call 0x4a\l0x0012fd01 5E                              pop esi\l0x0012fd02 6833320000                      push dword 0x3233\l0x0012fd07 687773325F                      push dword 0x5f327377\l0x0012fd0c 54                              push esp\l0x0012fd0d BA926E0484                      mov edx,0x84046e92\l0x0012fd12 FFD6                            call esi\l"]
       1244348 [shape=box, label = "0x0012fcbc 53                              push ebx\l"]
       1244349 [shape=box, label = "0x0012fcbd 56                              push esi\l0x0012fcbe 8B5F3C                          mov ebx,[edi+0x3c]\l0x0012fcc1 8B5C3B78                        mov ebx,[ebx+edi+0x78]\l0x0012fcc5 03DF                            add ebx,edi\l0x0012fcc7 53                              push ebx\l0x0012fcc8 8B5B20                          mov ebx,[ebx+0x20]\l0x0012fccb 03DF                            add ebx,edi\l0x0012fccd 53                              push ebx\l"]
       1244366 [shape=box, label = "0x0012fcce 83C304                          add ebx,0x4\l"]
       1244369 [shape=box, label = "0x0012fcd1 8B33                            mov esi,[ebx]\l0x0012fcd3 03F7                            add esi,edi\l0x0012fcd5 33C9                            xor ecx,ecx\l"]
       1244375 [shape=box, label = "0x0012fcd7 AC                              lodsb \l"]
       1244376 [shape=box, label = "0x0012fcd8 32C8                            xor cl,al\l0x0012fcda C1C105                          rol ecx,0x5\l0x0012fcdd 84C0                            test al,al\l"]
       1244383 [shape=box, label = "0x0012fcdf 75F6                            jnz 0xfffffff8\l"]
       1244385 [shape=box, label = "0x0012fce1 2BCA                            sub ecx,edx\l"]
       1244387 [shape=box, label = "0x0012fce3 75E9                            jnz 0xffffffeb\l"]
       1244389 [shape=box, label = "0x0012fce5 58                              pop eax\l0x0012fce6 2BD8                            sub ebx,eax\l0x0012fce8 D1EB                            shr ebx,0x1\l0x0012fcea 5E                              pop esi\l0x0012fceb 035E24                          add ebx,[esi+0x24]\l0x0012fcee 03DF                            add ebx,edi\l0x0012fcf0 668B0B                          mov cx,[ebx]\l0x0012fcf3 8B5E1C                          mov ebx,[esi+0x1c]\l0x0012fcf6 03DF                            add ebx,edi\l0x0012fcf8 8B048B                          mov eax,[ebx+ecx*4]\l0x0012fcfb 03C7                            add eax,edi\l0x0012fcfd 5E                              pop esi\l0x0012fcfe 5B                              pop ebx\l"]
       1244415 [shape=box, label = "0x0012fcff FFE0                            jmp eax\l"]
       1244436 [shape=box, label = "0x0012fd14 89450C                          mov [ebp+0xc],eax\l0x0012fd17 8BF8                            mov edi,eax\l0x0012fd19 53                              push ebx\l0x0012fd1a 6A04                            push byte 0x4\l0x0012fd1c 55                              push ebp\l0x0012fd1d FF7504                          push dword [ebp+0x4]\l0x0012fd20 BA009066E0                      mov edx,0xe0669000\l0x0012fd25 FFD6                            call esi\l"]
       1906393738 [shape=box, style=filled, color=".7 .3 1.0", label = "0x71a1428a send\l"]
       1244455 [shape=box, label = "0x0012fd27 83F804                          cmp eax,0x4\l0x0012fd2a 0F85C5000000                    jnz 0xcb\l0x0012fd30 8B7D08                          mov edi,[ebp+0x8]\l0x0012fd33 E80D000000                      call 0x12\l0x0012fd45 8F4518                          pop dword [ebp+0x18]\l0x0012fd48 53                              push ebx\l0x0012fd49 6A02                            push byte 0x2\l0x0012fd4b 6A01                            push byte 0x1\l0x0012fd4d 53                              push ebx\l0x0012fd4e 53                              push ebx\l0x0012fd4f 68000000C0                      push dword 0xc0000000\l0x0012fd54 FF7518                          push dword [ebp+0x18]\l0x0012fd57 BA3DD36B5C                      mov edx,0x5c6bd33d\l0x0012fd5c FFD6                            call esi\l"]
       2088770084 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c801a24 CreateFileA\l"]
       1244510 [shape=box, label = "0x0012fd5e 89451C                          mov [ebp+0x1c],eax\l0x0012fd61 40                              inc eax\l0x0012fd62 0F848D000000                    jz 0x93\l"]
       1244520 [shape=box, label = "0x0012fd68 8B7D0C                          mov edi,[ebp+0xc]\l"]
       1244523 [shape=box, label = "0x0012fd6b 33C0                            xor eax,eax\l0x0012fd6d 50                              push eax\l0x0012fd6e B402                            mov ah,0x2\l0x0012fd70 50                              push eax\l0x0012fd71 FF7514                          push dword [ebp+0x14]\l0x0012fd74 FF7504                          push dword [ebp+0x4]\l0x0012fd77 BA005860E2                      mov edx,0xe2605800\l0x0012fd7c FFD6                            call esi\l"]
       1244542 [shape=box, label = "0x0012fd7e 8B7D08                          mov edi,[ebp+0x8]\l0x0012fd81 85C0                            test eax,eax\l"]
       1244547 [shape=box, label = "0x0012fd83 741E                            jz 0x20\l"]
       1244549 [shape=box, label = "0x0012fd85 8BC8                            mov ecx,eax\l0x0012fd87 41                              inc ecx\l0x0012fd88 7457                            jz 0x59\l0x0012fd8a 53                              push ebx\l0x0012fd8b 8D4D10                          lea ecx,[ebp+0x10]\l0x0012fd8e 51                              push ecx\l0x0012fd8f 50                              push eax\l0x0012fd90 FF7514                          push dword [ebp+0x14]\l0x0012fd93 FF751C                          push dword [ebp+0x1c]\l0x0012fd96 BAB9BEF5CB                      mov edx,0xcbf5beb9\l0x0012fd9b FFD6                            call esi\l"]
       2088832391 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c810d87 WriteFile\l"]
       1244573 [shape=box, label = "0x0012fd9d 85C0                            test eax,eax\l0x0012fd9f 7440                            jz 0x42\l0x0012fda1 EBC5                            jmp 0xffffffc7\l"]
       1244579 [shape=box, label = "0x0012fda3 FF751C                          push dword [ebp+0x1c]\l0x0012fda6 BA5C93C59D                      mov edx,0x9dc5935c\l0x0012fdab FFD6                            call esi\l"]
       2088803143 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c809b47 CloseHandle\l"]
       1244589 [shape=box, label = "0x0012fdad 6A44                            push byte 0x44\l0x0012fdaf 58                              pop eax\l0x0012fdb0 2BE0                            sub esp,eax\l0x0012fdb2 8BFC                            mov edi,esp\l0x0012fdb4 8BD7                            mov edx,edi\l0x0012fdb6 AB                              stosd \l0x0012fdb7 33C0                            xor eax,eax\l0x0012fdb9 6A10                            push byte 0x10\l0x0012fdbb 59                              pop ecx\l"]
       1244604 [shape=box, label = "0x0012fdbc AB                              stosd \l"]
       1244605 [shape=box, label = "0x0012fdbd E2FD                            loop 0xffffffff\l"]
       1244607 [shape=box, label = "0x0012fdbf 8B7D08                          mov edi,[ebp+0x8]\l0x0012fdc2 52                              push edx\l0x0012fdc3 52                              push edx\l0x0012fdc4 50                              push eax\l0x0012fdc5 50                              push eax\l0x0012fdc6 50                              push eax\l0x0012fdc7 50                              push eax\l0x0012fdc8 50                              push eax\l0x0012fdc9 50                              push eax\l0x0012fdca 50                              push eax\l0x0012fdcb FF7518                          push dword [ebp+0x18]\l0x0012fdce BA2CF19426                      mov edx,0x2694f12c\l0x0012fdd3 FFD6                            call esi\l"]
       2088772455 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c802367 CreateProcessA\l"]
       1244629 [shape=box, label = "0x0012fdd5 58                              pop eax\l0x0012fdd6 FEC7                            inc bh\l0x0012fdd8 53                              push ebx\l0x0012fdd9 50                              push eax\l0x0012fdda BA01D634DE                      mov edx,0xde34d601\l0x0012fddf FFD6                            call esi\l"]
       2088772896 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c802520 WaitForSingleObject\l"]
       1244641 [shape=box, label = "0x0012fde1 FF751C                          push dword [ebp+0x1c]\l0x0012fde4 BA5C93C59D                      mov edx,0x9dc5935c\l0x0012fde9 FFD6                            call esi\l"]
       1244651 [shape=box, label = "0x0012fdeb FF7518                          push dword [ebp+0x18]\l0x0012fdee BA3D53CF27                      mov edx,0x27cf533d\l0x0012fdf3 FFD6                            call esi\l"]
       2088967851 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c831eab DeleteFileA\l"]
       1244661 [shape=box, label = "0x0012fdf5 8B7D0C                          mov edi,[ebp+0xc]\l0x0012fdf8 FF7504                          push dword [ebp+0x4]\l0x0012fdfb BA85563107                      mov edx,0x7315685\l0x0012fe00 FFD6                            call esi\l"]
       1906415161 [shape=box, style=filled, color=".7 .3 1.0", label = "0x71a19639 closesocket\l"]
       1244674 [shape=box, label = "0x0012fe02 8B7D08                          mov edi,[ebp+0x8]\l0x0012fe05 BABA460CC1                      mov edx,0xc10c46ba\l0x0012fe0a FFD6                            call esi\l"]
       2088812632 [shape=box, style=filled, color=".7 .3 1.0", label = "0x7c80c058 ExitThread\l"]
       4288512 -> 4288534 [style = bold ]
       4288534 -> 4288539 [style = bold, color=red ]
       4288539 -> 4288534 [style = dashed, color=red ]
       4288539 -> 4288541 [style = bold ]
       4288541 -> 4288569 [style = bold ]
       4288569 -> 4288570 [style = bold, color=orange ]
       4288570 -> 4288587 [style = bold, color=orange ]
       4288587 -> 4288590 [style = bold, color=red ]
       4288590 -> 4288596 [style = bold, color=red ]
       4288596 -> 4288597 [style = bold, color=red ]
       4288597 -> 4288604 [style = bold, color=red ]
       4288604 -> 4288596 [style = dashed, color=red ]
       4288604 -> 4288606 [style = bold, color=red ]
       4288606 -> 4288608 [style = bold, color=red ]
       4288608 -> 4288587 [style = dashed, color=red ]
       4288608 -> 4288610 [style = bold, color=orange ]
       4288610 -> 4288636 [style = bold, color=orange ]
       4288636 -> 2088770935 [style = bold ]
       4288636 -> 1906391953 [style = bold ]
       4288636 -> 1906393194 [style = bold ]
       4288636 -> 1906401626 [style = bold ]
       2088770935 -> 4288657 [style = bold ]
       2088770935 -> 1244436 [style = bold ]
       4288657 -> 4288569 [style = bold ]
       1906391953 -> 4288679 [style = bold ]
       4288679 -> 4288569 [style = bold ]
       1906393194 -> 4288706 [style = bold ]
       4288706 -> 4288569 [style = bold ]
       1906401626 -> 4288719 [style = bold ]
       1906401626 -> 1244542 [style = bold, color=red ]
       4288719 -> 1244348 [style = bold ]
       1244348 -> 1244349 [style = bold, color=red ]
       1244349 -> 1244366 [style = bold, color=red ]
       1244366 -> 1244369 [style = bold, color=red ]
       1244369 -> 1244375 [style = bold, color=red ]
       1244375 -> 1244376 [style = bold, color=red ]
       1244376 -> 1244383 [style = bold, color=red ]
       1244383 -> 1244375 [style = dashed, color=red ]
       1244383 -> 1244385 [style = bold, color=red ]
       1244385 -> 1244387 [style = bold, color=red ]
       1244387 -> 1244366 [style = dashed, color=red ]
       1244387 -> 1244389 [style = bold, color=red ]
       1244389 -> 1244415 [style = bold, color=red ]
       1244415 -> 2088770935 [style = bold ]
       1244415 -> 1906393738 [style = bold ]
       1244415 -> 2088770084 [style = bold ]
       1244415 -> 1906401626 [style = bold, color=red ]
       1244415 -> 2088832391 [style = bold, color=red ]
       1244415 -> 2088803143 [style = bold, color=orange ]
       1244415 -> 2088772455 [style = bold ]
       1244415 -> 2088772896 [style = bold ]
       1244415 -> 2088967851 [style = bold ]
       1244415 -> 1906415161 [style = bold ]
       1244415 -> 2088812632 [style = bold ]
       1244436 -> 1244348 [style = bold ]
       1906393738 -> 1244455 [style = bold ]
       1244455 -> 1244348 [style = bold ]
       2088770084 -> 1244510 [style = bold ]
       1244510 -> 1244520 [style = bold ]
       1244520 -> 1244523 [style = bold, color=red ]
       1244523 -> 1244348 [style = bold, color=red ]
       1244542 -> 1244547 [style = bold, color=red ]
       1244547 -> 1244549 [style = bold, color=red ]
       1244547 -> 1244579 [style = dashed ]
       1244549 -> 1244348 [style = bold, color=red ]
       2088832391 -> 1244573 [style = bold, color=red ]
       1244573 -> 1244520 [style = bold, color=red ]
       1244579 -> 1244348 [style = bold ]
       2088803143 -> 1244589 [style = bold ]
       2088803143 -> 1244651 [style = bold ]
       1244589 -> 1244604 [style = bold ]
       1244604 -> 1244605 [style = bold, color=orange ]
       1244605 -> 1244604 [style = dashed, color=orange ]
       1244605 -> 1244607 [style = bold ]
       1244607 -> 1244348 [style = bold ]
       2088772455 -> 1244629 [style = bold ]
       1244629 -> 1244348 [style = bold ]
       2088772896 -> 1244641 [style = bold ]
       1244641 -> 1244348 [style = bold ]
       1244651 -> 1244348 [style = bold ]
       2088967851 -> 1244661 [style = bold ]
       1244661 -> 1244348 [style = bold ]
       1906415161 -> 1244674 [style = bold ]
       1244674 -> 1244348 [style = bold ]
}
""")
    g.write_jpeg("test.jpg", prog="dot")
    os.system("konqueror test.jpg")

if __name__ == "__main__":
    main()
    #test()

