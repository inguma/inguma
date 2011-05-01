
import envi
import envi.bits as e_bits

#TODO
# f0 0f c7 4d 00 75 f0 5d 5b - this is NOT right in disasm

import copy
import struct

# Gank in our bundled libdisassemble
import envi.disassemblers.libdisassemble.opcode86 as opcode86

all_tables = opcode86.tables86

"""
Use the "universalized" envi opcodes with libdisassemble
and an x86 emulator.
"""

# Eflags bit masks
EFLAGS_CF = 1 << 0
EFLAGS_PF = 1 << 2
EFLAGS_AF = 1 << 4
EFLAGS_ZF = 1 << 6
EFLAGS_SF = 1 << 7
EFLAGS_TF = 1 << 8
EFLAGS_IF = 1 << 9
EFLAGS_DF = 1 << 10
EFLAGS_OF = 1 << 11

# The indexes for the list of segments in the emulator
SEG_CS = 0
SEG_DS = 1
SEG_ES = 2
SEG_FS = 3
SEG_GS = 4
SEG_SS = 5

# Our instruction prefix masks
INSTR_PREFIX=      0x0001
PREFIX_LOCK =      0x0002
PREFIX_REPNZ=      0x0004
PREFIX_REPZ =      0x0008
PREFIX_REP  =      0x0010
PREFIX_REP_SIMD=   0x0020
PREFIX_OP_SIZE=    0x0040
PREFIX_ADDR_SIZE=  0x0080
PREFIX_SIMD=       0x0100
PREFIX_CS  =       0x0200
PREFIX_SS  =       0x0400
PREFIX_DS  =       0x0800
PREFIX_ES  =       0x1000
PREFIX_FS  =       0x2000
PREFIX_GS  =       0x4000
PREFIX_REG_MASK=   0x8000

# Printable prefix names
prefix_names = [
    (PREFIX_LOCK, "lock"),
    (PREFIX_REPNZ, "repnz"),
    (PREFIX_REP, "rep"),
    (PREFIX_CS, "cs"),
    (PREFIX_SS, "ss"),
    (PREFIX_DS, "ds"),
    (PREFIX_ES, "es"),
    (PREFIX_FS, "fs"),
    (PREFIX_GS, "gs"),
]


prefix_table = {
    0xF0 : PREFIX_LOCK ,
    0xF2: PREFIX_REPNZ,
    0xF3: PREFIX_REP,
    0x2E: PREFIX_CS,
    0x36: PREFIX_SS,
    0x3E: PREFIX_DS,
    0x26: PREFIX_ES,
    0x64: PREFIX_FS,
    0x65: PREFIX_GS,
    0x66: PREFIX_OP_SIZE,
    0x67: PREFIX_ADDR_SIZE,
    0:    0
}
# The scale byte index into this for multiplier imm
scale_lookup = (1, 2, 4, 8)

# A set of instructions that are considered privileged (mark with IF_PRIV)
priv_lookup = {
    "int":True,
    "in":True,
    "out":True,
    "insb":True,
    "outsb":True,
    "insd":True,
    "outsd":True,
    "vmcall":True,
    "vmlaunch":True,
    "vmresume":True,
    "vmxoff":True,
    "vmread":True,
    "vmwrite":True,
    "rsm":True,
    "lar":True,
    "lsl":True,
    "clts":True,
    "invd":True,
    "wbinvd":True,
    "wrmsr":True,
    "rdmsr":True,
    "sysexit":True,
    "lgdt":True,
    "lidt":True,
    "lmsw":True,
    "monitor":True,
    "mwait":True,
    "vmclear":True,
    "vmptrld":True,
    "vmptrst":True,
    "vmxon":True,
}

def parse_sib(bytes, offset, mod):
    """
    Return a tuple of (size, scale, index, base, imm)
    """
    byte = ord(bytes[offset])
    scale = (byte >> 6) & 0x3
    index = (byte >> 3) & 0x7
    base  = byte & 0x7
    imm = None

    size = 1

    # Special SIB case with no index reg
    if index == 4:
        index = None

    # Special SIB case with possible immediate
    if base == 5:
        if mod == 0: # [ imm32 + index * scale ]
            base = None
            imm = e_bits.parsebytes(bytes, offset+size, 4, sign=False)
            size += 4
        # FIXME is there special stuff needed here?
        elif mod == 1:
            pass
            #raise Exception("OMG MOD 1")
        elif mod == 2:
            pass
            #raise Exception("OMG MOD 2")

    return (size, scale, index, base, imm)

# Parse modrm as though addr mode might not be just a reg
def extended_parse_modrm(bytes, offset, opersize):
    """
    Return a tuple of (size, Operand)
    """
    mod,reg,rm = parse_modrm(ord(bytes[offset]))

    size = 1

    if mod == 3: # Easy one, just a reg
        if opersize == 1: rm += opcode86.REG_BYTE_OFFSET
        elif opersize == 2: rm += opcode86.REG_WORD_OFFSET
        return (size, envi.Operand(envi.OM_REGISTER, opersize, reg=rm))

    elif mod == 0:
        # means we are [reg] unless rm == 4 (SIB) or rm == 5 ([imm32])
        if rm == 5:
            #NOTE: 32 bit mode specific
            imm = e_bits.parsebytes(bytes, offset + size, 4)
            size += 4
            return(size, envi.Operand(envi.OM_IMMMEM, opersize, imm=imm))

        elif rm == 4:
            disp = None
            sibsize, scale, index, base, imm = parse_sib(bytes, offset+size, mod)
            size += sibsize
            oper = envi.Operand(envi.OM_SIBMEM, opersize, reg=base, indexreg=index, imm=imm, scale=scale_lookup[scale], disp=disp)
            return (size, oper)

        else:
            return(size, envi.Operand(envi.OM_REGMEM, opersize, reg=rm))

    elif mod == 1:
        # mod 1 means we are [ reg + disp8 ] (unless rm == 4 which means sib + disp8)
        if rm == 4:
            sibsize, scale, index, base, imm = parse_sib(bytes, offset+size, mod)
            size += sibsize
            disp = e_bits.parsebytes(bytes, offset+size, 1, sign=True)
            size += 1
            oper = envi.Operand(envi.OM_SIBMEM, opersize, reg=base, indexreg=index, scale=scale_lookup[scale], disp=disp)
            return (size,oper)
        else:
            x = e_bits.signed(ord(bytes[offset+size]), 1)
            size += 1
            return(size, envi.Operand(envi.OM_REGMEM, opersize, reg=rm, disp=x))

    elif mod == 2:
        # Means we are [ reg + disp32 ] (unless rm == 4  which means SIB + disp32)
        if rm == 4:
            sibsize, scale, index, base, imm = parse_sib(bytes,offset+size,mod)
            size += sibsize
            disp = e_bits.parsebytes(bytes, offset + size, 4, sign=True)
            size += 4
            oper = envi.Operand(envi.OM_SIBMEM, opersize, reg=base, indexreg=index, scale = scale_lookup[scale], imm=imm, disp=disp)
            return (size, oper)

        else:
            #FIXME 32 bit mode specific
            disp = e_bits.parsebytes(bytes, offset+size, 4, sign=True)
            size += 4
            return(size, envi.Operand(envi.OM_REGMEM, opersize, reg=rm, disp=disp))

    else:
        raise Exception("How does mod == %d" % mod)
            
def parse_modrm(byte):
    # Pass in a string with an offset for speed rather than a new string
    mod = (byte >> 6) & 0x3
    reg = (byte >> 3) & 0x7
    rm = byte & 0x7
    #print "MOD/RM",hex(byte),mod,reg,rm
    return (mod,reg,rm)

def ameth_a(bytes, offset, tsize, flags):
    imm = e_bits.parsebytes(bytes, offset, tsize)
    seg = e_bits.parsebytes(bytes, offset+tsize, 2)
    # THIS BEING GHETTORIGGED ONLY EFFECTS callf jmpf
    #print "FIXME: envi.intel.ameth_a skipping seg prefix %d" % seg
    return (tsize+2, envi.Operand(envi.OM_IMMEDIATE, tsize, imm=imm))

def ameth_e(bytes, offset, tsize, flags):
    size, oper = extended_parse_modrm(bytes, offset, tsize)
    return (size, oper)

def ameth_n(bytes, offset, tsize, flags):
    size, oper = extended_parse_modrm(bytes, offset, tsize)
    if oper.reg != None: oper.reg += opcode86.REG_MMX_OFFSET
    if oper.indexreg != None: oper.indexreg += opcode86.REG_MMX_OFFSET
    return (size, oper)

def ameth_w(bytes, offset, tsize, flags):
    size, oper = extended_parse_modrm(bytes, offset, tsize)
    if oper.reg != None: oper.reg += opcode86.REG_SIMD_OFFSET
    if oper.indexreg != None: oper.indexreg += opcode86.REG_SIMD_OFFSET
    return (size, oper)

def ameth_i(bytes, offset, tsize, flags):
    imm = e_bits.parsebytes(bytes, offset, tsize)
    return (tsize, envi.Operand(envi.OM_IMMEDIATE, tsize, imm=imm))

def ameth_j(bytes, offset, tsize, flags):
    imm = e_bits.parsebytes(bytes, offset, tsize, sign=True)
    return (tsize, envi.Operand(envi.OM_IMMEDIATE, tsize, imm=imm))

def ameth_o(bytes, offset, tsize, flags):
    #FIXME 32 bit mode specific (in naive 16 or native 64 it would change
    imm = e_bits.parsebytes(bytes, offset, 4, sign=False)
    return (4, envi.Operand(envi.OM_IMMMEM, tsize, imm=imm))

def ameth_g(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    if tsize == 1: reg += opcode86.REG_BYTE_OFFSET
    elif tsize == 2: reg += opcode86.REG_WORD_OFFSET
    return (0, envi.Operand(envi.OM_REGISTER, tsize, reg=reg))

def ameth_c(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return (1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_CTRL_OFFSET))

def ameth_d(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return (1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_DEBUG_OFFSET))

def ameth_p(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return (1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_MMX_OFFSET))

def ameth_s(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return (1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_SEG_OFFSET))

def ameth_u(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return(1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_TEST_OFFSET))

def ameth_v(bytes, offset, tsize, flags):
    mod,reg,rm = parse_modrm(ord(bytes[offset]))
    return(1, envi.Operand(envi.OM_REGISTER, tsize, reg = reg + opcode86.REG_SIMD_OFFSET))

def ameth_x(bytes, offset, tsize, flags):
    #FIXME this needs the DS over-ride, but is only for outsb which we don't support
    return (0, envi.Operand(envi.OM_REGMEM, tsize, reg=REG_ESI))

def ameth_y(bytes, offset, tsize, flags):
    #FIXME this needs the ES over-ride, but is only for insb which we don't support
    return (0, envi.Operand(envi.OM_REGMEM, tsize, reg=REG_EDI))

# This will make function lookups nice and quick
addr_methods = [ None for x in range(22) ]
addr_methods[opcode86.ADDRMETH_A>>16] = ameth_a
addr_methods[opcode86.ADDRMETH_C>>16] = ameth_c
addr_methods[opcode86.ADDRMETH_D>>16] = ameth_d
addr_methods[opcode86.ADDRMETH_E>>16] = ameth_e
addr_methods[opcode86.ADDRMETH_M>>16] = ameth_e
addr_methods[opcode86.ADDRMETH_N>>16] = ameth_n
addr_methods[opcode86.ADDRMETH_Q>>16] = ameth_n
addr_methods[opcode86.ADDRMETH_R>>16] = ameth_e
addr_methods[opcode86.ADDRMETH_W>>16] = ameth_w
addr_methods[opcode86.ADDRMETH_I>>16] = ameth_i
addr_methods[opcode86.ADDRMETH_J>>16] = ameth_j
addr_methods[opcode86.ADDRMETH_O>>16] = ameth_o
addr_methods[opcode86.ADDRMETH_G>>16] = ameth_g
addr_methods[opcode86.ADDRMETH_P>>16] = ameth_p
addr_methods[opcode86.ADDRMETH_S>>16] = ameth_s
addr_methods[opcode86.ADDRMETH_U>>16] = ameth_u
addr_methods[opcode86.ADDRMETH_V>>16] = ameth_v
addr_methods[opcode86.ADDRMETH_X>>16] = ameth_x
addr_methods[opcode86.ADDRMETH_Y>>16] = ameth_y


#FIXME maybe just use the list in opcode86?
reg_names = [
"eax","ecx","edx","ebx","esp","ebp","esi","edi",
"ax","cx","dx","bx","sp","bp","si","di",
"al","cl","dl","bl","ah","ch","dh","bh",
"mm0","mm1","mm2","mm3","mm4","mm5","mm6","mm7",
"xmm0","xmm1","xmm2","xmm3","xmm4","xmm5","xmm6","xmm7",
"dr0","dr1","dr2","dr3","dr4","dr5","dr6","dr7",
"cr0","cr1","cr2","cr3","cr4","cr5","cr6","cr7",
"tr0","tr1","tr2","tr3","tr4","tr5","tr6","tr7",
"es","cs","ss","ds","fs","gs","INVALID","INVALID1",
"st(0)","st(1)","st(2)","st(3)","st(4)","st(5)","st(6)","st(7)",
"eflags","fpctrl","fpstatus","fptag","eip","ip"]

# These are used by the emulator to support
# partial register asignment
reg_setters = [ None for k in reg_names ]
reg_getters = [ None for k in reg_names ]


def set_bytereg(emu, id, val):
    val = val & 0xff
    realidx = id - opcode86.REG_BYTE_OFFSET
    if realidx < 4:
        curval = emu.getRegister(realidx)
        emu.setRegister(realidx, (curval & 0xffffff00) | (val & 0xff))
    else:
        realidx = realidx % 4
        curval = emu.getRegister(realidx)
        emu.setRegister(realidx, (curval & 0xffff00ff) | (val&0xff) << 8)


def set_shortreg(emu, id, val):
    val = val & 0xffff
    realidx = id - opcode86.REG_WORD_OFFSET
    curval = emu.getRegister(realidx)
    emu.setRegister(realidx, (curval & 0xffff0000) | val)

def get_bytereg(emu, id):
    realidx = id - opcode86.REG_BYTE_OFFSET
    if realidx < 4:
        return emu.getRegister(realidx) & 0xff
    else:
        realidx = realidx % 4
        return (emu.getRegister(realidx) >> 8) & 0xff

def get_shortreg(emu, id):
    realidx = id - opcode86.REG_WORD_OFFSET
    return emu.getRegister(realidx) & 0xffff

# Over-ride the entries for short/byte register addressing
reg_getters[opcode86.REG_BYTE_OFFSET:opcode86.REG_BYTE_OFFSET+8] = [ get_bytereg for i in range(8) ]
reg_setters[opcode86.REG_BYTE_OFFSET:opcode86.REG_BYTE_OFFSET+8] = [ set_bytereg for i in range(8) ]
reg_getters[opcode86.REG_WORD_OFFSET:opcode86.REG_WORD_OFFSET+8] = [ get_shortreg for i in range(8) ]
reg_setters[opcode86.REG_WORD_OFFSET:opcode86.REG_WORD_OFFSET+8] = [ set_shortreg for i in range(8) ]

# Use and extend the intel values
REG_EAX = 0
REG_ECX = 1
REG_EDX = 2
REG_EBX = 3
REG_ESP = 4
REG_EBP = 5
REG_ESI = 6
REG_EDI = 7

REG_AX = 0 + opcode86.REG_WORD_OFFSET
REG_CX = 1 + opcode86.REG_WORD_OFFSET
REG_DX = 2 + opcode86.REG_WORD_OFFSET
REG_BX = 3 + opcode86.REG_WORD_OFFSET
REG_SP = 4 + opcode86.REG_WORD_OFFSET
REG_BP = 5 + opcode86.REG_WORD_OFFSET
REG_SI = 6 + opcode86.REG_WORD_OFFSET
REG_DI = 7 + opcode86.REG_WORD_OFFSET

REG_AL = 0 + opcode86.REG_BYTE_OFFSET
REG_CL = 1 + opcode86.REG_BYTE_OFFSET
REG_DL = 2 + opcode86.REG_BYTE_OFFSET
REG_BL = 3 + opcode86.REG_BYTE_OFFSET

# These are extensions
REG_EIP = opcode86.REG_EIP_INDEX
REG_FLAGS = opcode86.REG_FLAGS_INDEX

def shiftMask(val, size):
    if size == 1:
        return (val & 0x1f) % 9
    elif size == 2:
        return (val & 0x1f) % 17
    elif size == 4:
        return val & 0x1f
    elif size == 8:
        return val & 0x3f
    else:
        raise Exception("shiftMask is broke in envi/intel.py")

nofall_types = [
    opcode86.INS_RET,
    opcode86.INS_BRANCH,
]
branch_types = [
    opcode86.INS_CALL,
    opcode86.INS_CALLCC,
    opcode86.INS_BRANCH,
    opcode86.INS_BRANCHCC,
]
call_types = [
    opcode86.INS_CALL,
    opcode86.INS_CALLCC,
]

operand_range = (2,3,4)

sizenames = (None, "BYTE ","WORD ",None,"DWORD ")

class IntelModule(envi.ArchitectureModule):
    def __init__(self):
        envi.ArchitectureModule.__init__(self, "Intel x86")

    def isCall(self, op):
        if op.opcode in call_types:
            return True
        return False

    def getPointerSize(self):
        return 4

    def isBranch(self, op):
        return op.opcode in branch_types

    def pointerString(self, va):
        return "0x%.8x" % va

    def reprOperand(self, op, operindex, va=None, names=None):
        o = op.opers[operindex]
        if o.mode == envi.OM_IMMEDIATE:
            if self.isBranch(op):
                if va != None:
                    targ = va + o.imm + len(op)
                    #FIXME optimize
                    tname = "0x%.8x" % targ
                    if names:
                        tname = names.get(targ, tname)
                    return tname
                else:
                    return "%d" % o.imm
            elif o.tsize == 4:
                return "0x%.8x" % o.imm
            else:
                return "%d" % o.imm

        elif o.mode == envi.OM_REGISTER:
            return reg_names[o.reg]

        # If we reach here, we're doing a deref.
        sizestr = ""
        if o.tsize == 1:
            sizestr = "byte "

        if o.mode == envi.OM_IMMMEM:
            return "%s[0x%.8x]" % (sizestr,o.imm)
        elif o.mode == envi.OM_REGMEM:
            if o.disp != None:
                return "%s[%s %s]" % (sizestr,reg_names[o.reg], self.prdisp(o))
            else:
                return "%s[%s]" % (sizestr,reg_names[o.reg])

        elif o.mode == envi.OM_SIBMEM:
            s = ["%s[" % sizestr,]
            if o.reg != None:
                s.append(reg_names[o.reg])
            if o.imm != None:
                s.append("0x%.8x" % o.imm)
            if o.indexreg != None:
                s.append(" + %s" % reg_names[o.indexreg])
                if o.scale != None:
                    s.append(" * %d" % o.scale)
            if o.disp != None:
                s.append(self.prdisp(o))
            s.append("]")
            return "".join(s)

    def reprOpcode(self, op, va=None, names=None):
        """
        Return an architecture specific string representation.
        if you specify a VA, it will assume that va as opcode
        location (for relative calculations).  You may also
        specify a "names" dictionary which will be used to
        look up "friendly" names for mem-deref immediates.
        """
        ret = []
        #FIXME Get our prefixes
        if op.prefixes:
            ret.append(self.getPrefixName(op.prefixes))
        ret.append(op.mnem)
        for i in range(len(op.opers)):
            ret.append(self.reprOperand(op, i, va, names))
        return " ".join(ret)

    def prdisp(self, o):
        # Just a displacement print helper
        dabs = abs(o.disp)
        if dabs > 4096:
            if o.disp < 0:
                return "- 0x%.8x" % dabs
            else:
                return "+ 0x%.8x" % dabs
        else:
            if o.disp < 0:
                return "- %d" % dabs
            else:
                return "+ %d" % dabs
                
    def makeOpcode(self, bytes, offset=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        #FIXME make this take a BytesDef
        # Stuff for opcode parsing
        tabdesc = all_tables[0] # A tuple (optable, shiftbits, mask byte, sub, max)
        startoff = offset # Use startoff as a size knob if needed

        # Stuff we'll be putting in the opcode object
        optype = None # This gets set if we successfully decode below
        mnem = None 
        operands = []
        prefixes = 0
        iflags = 0

        while True:
            obyte = ord(bytes[offset])
            #print "OBYTE",hex(obyte)
            if (obyte > tabdesc[4]):
                #print "Jumping To Overflow Table:", tabdesc[5]
                tabdesc = all_tables[tabdesc[5]]

            tabidx = ((obyte - tabdesc[3]) >> tabdesc[1]) & tabdesc[2]
            #print "TABIDX",tabidx
            opdesc = tabdesc[0][tabidx]

            # Check for and eat up prefixes...
            if opdesc[1] == opcode86.INSTR_PREFIX:
                if ord(bytes[offset+1]) == 0x0f: # on 66 0f we have a new table to jump to
                    tabdesc = all_tables[opdesc[0]]
                    offset += 2 # one for the 66 and the other for the 0F
                    #startoff += 1 # Fake out the extra opcode byte
                    continue
                else:
                    prefixes |= prefix_table[obyte]
                    offset += 1
                # Reset our table use and continue
                tabdesc = all_tables[0] # A tuple (optable, shiftbits, mask byte, sub, max)
                continue

            # Hunt down multi-byte opcodes
            if opdesc[0] != 0: # If we have a sub-table specified, use it.
                #print "Multi-Byte Next Hop For",hex(obyte),opdesc[0]
                tabdesc = all_tables[opdesc[0]]
                offset += 1
                continue

            # We are now on the final table...
            #print repr(opdesc)
            mnem = opdesc[6]
            optype = opdesc[1]
            if tabdesc[2] == 0xff:
                offset += 1 # For our final opcode byte
            break

        if optype == 0:
            #print tabidx
            #print opdesc
            #print "OPTTYPE 0"
            raise envi.InvalidInstruction()

        operoffset = 0
        # Begin parsing operands based off address method
        for i in operand_range:

            oper = None # Set this if we end up with an operand
            osize = 0

            # Pull out the operand description from the table
            operflags = opdesc[i]
            opertype = operflags & opcode86.OPTYPE_MASK
            addrtype = operflags & opcode86.ADDRMETH_MASK

            sizelist = opcode86.OPERSIZE.get(opertype, None)
            if sizelist == None:
                tsize = self.getPointerSize()
            else:
                # We only support 32 bit native mode right now
                tsize = sizelist[1]

            #FIXME this is broken I think for floating 64 and 128 stuff...
            if prefixes & PREFIX_OP_SIZE and tsize > 2:
                tsize = 2

            #print hex(opertype),hex(addrtype)

            # If addrtype is zero, we have operands embedded in the opcode
            if addrtype == 0:

                if operflags & opcode86.OP_REG:
                    osize = 0
                    oper = envi.Operand(envi.OM_REGISTER, tsize, reg=opdesc[5+i])

                elif operflags & opcode86.OP_IMM:
                    osize = 0
                    oper = envi.Operand(envi.OM_IMMEDIATE, tsize, imm=opdesc[5+i])

            else:
                ameth = addr_methods[addrtype >> 16]
                if ameth == None:
                    raise Exception("Implemented Addressing Method 0x%.8x" % addrtype)

                # NOTE: Depending on your addrmethod you may get beginning of operands, or offset
                try:
                    if addrtype == opcode86.ADDRMETH_I or addrtype == opcode86.ADDRMETH_J:
                        osize, oper = ameth(bytes, offset+operoffset, tsize, operflags)
                    else:
                        osize, oper = ameth(bytes, offset, tsize, operflags)
                except struct.error, e:
                    # Catch struct unpack errors due to insufficient data length
                    raise envi.InvalidInstruction()

            if oper != None: operands.append(oper)
            operoffset += osize

        # Make global note of instructions who
        # do *not* fall through...
        if optype in nofall_types:
            iflags |= envi.IF_NOFALL

        if priv_lookup.get(mnem, False):
            iflags |= envi.IF_PRIV

        ret = envi.Opcode(optype, mnem, prefixes, (offset-startoff)+operoffset, operands, iflags)

        return ret

    def getEmulator(self):
        return IntelEmulator()

    def getRegisterCount(self):
        return len(reg_names)

    def getProgramCounterIndex(self):
        return REG_EIP

    def getStackCounterIndex(self):
        return REG_ESP

    def getFrameCounterIndex(self):
        return REG_EBP

    def getRegisterName(self, regidx):
        return reg_names[regidx]

    def getPrefixName(self, prefix):
        """
        """
        ret = []
        for byte,name in prefix_names:
            if prefix & byte:
                ret.append(name)
        return "".join(ret)
        
    def getBranches(self, op, va, emu=None):
        """
        Return the discernable branches for the instruction.
        (with the assumption that it is located at va).
        If an optional emulator object is passed in, use the
        emulator (getOperValue()) to attempt to detect the
        target location for the branch in the emulation env.

        NOTE: This does *not* return a "branch" to the next
              instruction. Users should check IF_NOFALL.
        """
        ret = []

        if op.opcode in branch_types:

            if op.opers[0].mode == envi.OM_IMMEDIATE:
                ret.append(va + op.size + op.opers[0].imm)

            elif emu != None:
                # If we have an emulator, lets see if it can figgure
                # it out...
                ret.append(emu.getOperValue(op, 0))

        return ret

class IntelCall(envi.CallingConvention):

    def setReturnValue(self, emu, value, ccinfo):
        """
        For intel returns, ccinfo is the number of stack args
        to cleanup in addition to the eip.
        """
        if ccinfo == None:
            ccinfo = 0
        esp = emu.getRegister(REG_ESP)
        eip = struct.unpack("<L", emu.readMemory(esp, 4))[0]
        esp += 4 # For the saved eip
        esp += (4 * ccinfo) # Cleanup saved args

        emu.setRegister(REG_ESP, esp)
        emu.setRegister(REG_EAX, value)
        emu.setProgramCounter(eip)

class StdCall(IntelCall):

    def getCallArgs(self, emu, count):
        esp = emu.getRegister(REG_ESP)
        #FIXME 64bit
        esp += 4 # For the saved eip
        return struct.unpack("<%dL" % count, emu.readMemory(esp, 4*count))

class Cdecl(envi.CallingConvention):

    def getCallArgs(self, emu, count):
        esp = emu.getRegister(REG_ESP)
        #FIXME 64bit
        esp += 4 # For the saved eip
        return struct.unpack("<%dL" % count, emu.readMemory(esp, 4*count))

    def setReturnValue(self, emu, value, ccinfo):
        esp = emu.getRegister(REG_ESP)
        eip = struct.unpack("<L", emu.readMemory(esp, 4))[0]
        esp += 4 # For the saved eip

        emu.setRegister(REG_ESP, esp)
        emu.setRegister(REG_EAX, value)
        emu.setProgramCounter(eip)

class ThisCall(envi.CallingConvention):

    #FIXME do something about emulated argc vs our arg count...
    def getCallArgs(self, emu, count):
        #ret = [emu.getRegister(REG_ECX),]
        esp = emu.getRegister(REG_ESP)
        #FIXME 64bit
        esp += 4 # For the saved eip
        #count -= 1
        #if count > 0:
            #ret.extend(struct.unpack("<%dL" % count, emu.readMemory(esp, 4*count)))
        #return ret
        return struct.unpack("<%dL" % count, emu.readMemory(esp, 4*count))

    def setReturnValue(self, emu, value, ccinfo):
        """
        """
        if ccinfo == None:
            ccinfo = 0
        # Our first arg (if any) is in a reg
        esp = emu.getRegister(REG_ESP)
        eip = struct.unpack("<L", emu.readMemory(esp, 4))[0]
        esp += 4 # For the saved eip
        esp += (4 * ccinfo) # Cleanup saved args
        emu.setRegister(REG_ESP, esp)
        emu.setRegister(REG_EAX, value)
        emu.setProgramCounter(eip)

# Pre-make these and use the same instances for speed
stdcall = StdCall()
thiscall = ThisCall()
cdecl = Cdecl()

class IntelEmulator(envi.Emulator):

    def __init__(self, regarray=None):
        seglist = [ (0,0xffffffff) for i in range(6) ]
        envi.Emulator.__init__(self, IntelModule(), regarray=regarray, segs=seglist)
        self.fp_exceptions = []
        global reg_setters
        global reg_getters
        self.reg_setters = reg_setters
        self.reg_getters = reg_getters
        self.addCallingConvention("stdcall", stdcall)
        self.addCallingConvention("thiscall", thiscall)
        self.addCallingConvention("cdecl", cdecl)

    def getSegmentIndex(self, op):
        # FIXME make this not suck.  Right now it only checks for
        # segmen over-ride prefixes and returns DS otherwise
        if op.prefixes & PREFIX_ES:
            return SEG_ES
        elif op.prefixes & PREFIX_CS:
            return SEG_CS
        elif op.prefixes & PREFIX_SS:
            return SEG_SS
        elif op.prefixes & PREFIX_DS:
            return SEG_DS
        elif op.prefixes & PREFIX_FS:
            return SEG_FS
        elif op.prefixes & PREFIX_GS:
            return SEG_GS
        return SEG_DS

    def getRegister(self, index):
        #NOTE: These are here to allow partial reg assignment
        getter = self.reg_getters[index]
        if getter == None:
            return envi.Emulator.getRegister(self, index)
        return getter(self, index)

    def setRegister(self, index, val):
        #NOTE: These are here to allow partial reg assignment
        # NOTE: We're enforcing a 32 bit unsigned &. Maybe core should do it?
        setter = self.reg_setters[index]
        if setter == None:
            return envi.Emulator.setRegister(self, index, val & 0xffffffff)
        return setter(self, index, val)

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(REG_FLAGS)
        # On PDE, assume we're setting enough flags...
        if flags ==  None:
            flags = 0

        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_FLAGS)
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    def readMemValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        #FIXME change this (and all uses of it) to passing in format...
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length")
        if size == 1:
            return struct.unpack("B", bytes)[0]
        elif size == 2:
            return struct.unpack("<H", bytes)[0]
        elif size == 4:
            return struct.unpack("<L", bytes)[0]
        elif size == 8:
            return struct.unpack("<Q", bytes)[0]

    def writeMemValue(self, addr, value, size):
        #FIXME change this (and all uses of it) to passing in format...
        if size == 1:
            bytes = struct.pack("B",value & 0xff)
        elif size == 2:
            bytes = struct.pack("<H",value & 0xffff)
        elif size == 4:
            bytes = struct.pack("<L", value & 0xffffffff)
        elif size == 8:
            bytes = struct.pack("<Q", value & 0xffffffffffffffff)
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack("b", bytes)[0]
        elif size == 2:
            return struct.unpack("<h", bytes)[0]
        elif size == 4:
            return struct.unpack("<l", bytes)[0]

    def makeOpcode(self, pc):
        bytes = self.readMemory(pc, 32)
        return self.arch.makeOpcode(bytes)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)
        if op.prefixes & PREFIX_REP:
            x = self.doRepPrefix(meth, op)
        else:
            x = meth(op)
        if x != None:
            self.setProgramCounter(x)
        else:
            pc = self.getProgramCounter()
            pc += op.size
            self.setProgramCounter(pc)

    def doPush(self, val):
        esp = self.getRegister(REG_ESP)
        esp -= 4
        self.writeMemValue(esp, val, 4)
        self.setRegister(REG_ESP, esp)

    def doPop(self):
        esp = self.getRegister(REG_ESP)
        val = self.readMemValue(esp, 4)
        self.setRegister(REG_ESP, esp+4)
        return val

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        if src == None or dst == None:
            self.undefFlags()
            return None

        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necissary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        return self.intSubBase(src, dst, ssize, dsize)

    def intSubBase(self, src, dst, ssize, dsize):

        usrc = e_bits.unsigned(src, ssize)
        udst = e_bits.unsigned(dst, dsize)

        ssrc = e_bits.signed(src, ssize)
        sdst = e_bits.signed(dst, dsize)

        ures = udst - usrc
        sres = sdst - ssrc

        #print "dsize/ssize: %d %d" % (dsize, ssize)
        #print "unsigned: %d %d %d" % (usrc, udst, ures)
        #print "signed: %d %d %d" % (ssrc, sdst, sres)

        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(usrc, udst))
        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ures, dsize))
        self.setFlag(EFLAGS_ZF, not sres)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ures))

        return ures

    def logicalAnd(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        # PDE
        if dst == None or src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        # sign-extend an immediate if needed
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        # Make sure everybody's on the same bit page.
        dst = e_bits.unsigned(dst, dsize)
        src = e_bits.unsigned(src, ssize)

        res = src & dst

        self.setFlag(EFLAGS_AF, 0) # AF is undefined, but it seems like it is zeroed
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        return res

    def doRepPrefix(self, meth, op):
        #FIXME check for opcode family valid to rep
        ret = None
        ecx = self.getRegister(REG_ECX)
        while ecx != 0:
            ret = meth(op)
            ecx -= 1
        self.setRegister(REG_ECX, 0)
        return ret

    def doRepzPrefix(self, meth, op):
        pass

    # Beginning of Instruction methods
    def i_adc(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        cf = 0
        if self.getFlag(EFLAGS_CF):
            cf = 1

        dstsize = op.opers[0].tsize
        srcsize = op.opers[1].tsize

        if (op.opers[1].mode == envi.OM_IMMEDIATE and
            srcsize < dstsize):
            src = e_bits.sign_extend(src, srcsize, dstsize)
            srcsize = dstsize

        #FIXME perhaps unify the add/adc flags/arith code
        res = dst + src + cf

        tsize = op.opers[0].tsize

        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(res, tsize))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, tsize))
        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(res, tsize))

        self.setOperValue(op, 0, res)

    def i_add(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        #FIXME PDE and flags
        if dst == None or src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        if dsize > ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        udst = e_bits.unsigned(dst, dsize)
        usrc = e_bits.unsigned(src, ssize)
        sdst = e_bits.signed(dst, dsize)
        ssrc = e_bits.signed(src, ssize)

        ures = udst + usrc
        sres = sdst + ssrc

        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ures))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
        self.setFlag(EFLAGS_ZF, not ures)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ures, dsize))
        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))

        self.setOperValue(op, 0, ures)

    def i_and(self, op):
        #FIXME 24 and 25 opcodes should *not* get sign-extended.
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)

    def i_bswap(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        self.setOperValue(op, 0, e_bits.byteswap(val, tsize))

    def i_call(self, op):
        eip = self.getRegister(REG_EIP)
        saved = eip + op.size
        self.doPush(saved)

        val = self.getOperValue(op, 0)
        if val == None:
            raise envi.PDEException(self, "Unknown Call Target")

        if op.opers[0].mode == envi.OM_IMMEDIATE: # relative
            return saved + val
        else: # absolute indirect
            return val

    def i_clc(self, op):
        self.setFlag(EFLAGS_CF, 0)

    def i_cld(self, op):
        self.setFlag(EFLAGS_DF, 0)

    def i_cmp(self, op):
        self.integerSubtraction(op)

    def i_cmpxchg(self, op):
        tsize = op.opers[0].tsize
        if tsize == 4:
            areg = REG_EAX
        elif tsize == 1:
            areg = REG_AL
        else:
            areg = REG_AX

        aval = self.getRegister(areg)
        tval = self.getOperValue(op, 0)
        vval = self.getOperValue(op, 1)

        #FIXME eflags... is this supposed to be a real cmp?
        if aval == tval:
            self.setFlag(EFLAGS_ZF, True)
            self.setOperValue(op, 0, vval)
        else:
            self.setFlag(EFLAGS_ZF, False)
            self.setRegister(areg, tval)

    def twoRegCompound(self, topreg, botreg, size):
        """
        Build a compound value where the value of the top reg is shifted and
        or'd with the value of the bot reg ( assuming they are size
        bytes in length).  The return is size * 2 wide (and unsigned).
        """
        top = e_bits.unsigned(self.getRegister(topreg), size)
        bot = e_bits.unsigned(self.getRegister(botreg), size)

        return ((top << (size *8)) | bot)

    def regsFromCompound(self, val, size):
        top = e_bits.unsigned(val >> (size * 8), size)
        bot = e_bits.unsigned(val, size)
        return (top, bot)

    def i_cmpxch8b(self, op):
        #FIXME 66 prefix?
        size = 4
        dsize = 8
        if op.prefixes & PREFIX_OP_SIZE:
            size = 2
            dsize = 4

        bignum = self.twoRegCompound(REG_EDX, REG_EAX, size)
        testnum = self.getOperValue(op, 0)
        if bignum == testnum:
            self.setFlag(EFLAGS_ZF, 1)
            resval = self.twoRegCompound(REG_ECX, REG_EBX, size)
            self.setOperValue(op, 0, resval)
        else:
            self.setFlag(EFLAGS_ZF, 0)
            edx,eax = self.regsFromCompound(testnum, dsize)
            self.setRegister(REG_EDX, edx)
            self.setRegister(REG_EAX, eax)

    def i_cdq(self, op):
        return self.i_cwd(op)

    def i_cwd(self, op):
        """also i_cdq"""
        #FIXME handle 16 bit variant
        eax = self.getRegister(REG_EAX)
        #PDE
        if eax == None:
            self.setRegister(REG_EDX, None)
            return

        if e_bits.is_signed(eax, 4):
            self.setRegister(REG_EDX, 0xffffffff)
        else:
            self.setRegister(REG_EDX, 0)

    def i_dec(self, op):
        val = self.getOperValue(op, 0)
        if val == None:
            self.undefFlags()
            return
        val -= 1
        self.setOperValue(op, 0, val)
        #FIXME change over to integer subtraction

        self.setFlag(EFLAGS_OF, 0) #FIXME OF
        self.setFlag(EFLAGS_SF, e_bits.is_signed(val, op.opers[0].tsize))
        self.setFlag(EFLAGS_ZF, not val)
        self.setFlag(EFLAGS_AF, 0) #FIXME AF...
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(val))

    def i_div(self, op):
        #FIXME this is probably broke
        oper = op.opers[0]
        val = self.getOperValue(op, 0)
        if val == 0: raise envi.DivideByZero(self)
        if oper.tsize == 1:
            ax = self.getRegister(REG_AX)
            quot = ax / val
            rem  = ax % val
            if quot > 255:
                #FIXME stuff
                print "FIXME: division exception"
            self.setRegister(REG_EAX, (quot << 8) + rem)

        elif oper.tsize == 4:
            #FIXME 16 bit over-ride
            eax = self.getRegister(REG_EAX)
            edx = self.getRegister(REG_EDX)
            tot = (edx << 32) + eax
            quot = tot / val
            rem = tot % val

            if quot > 0xffffffff:
                print "FIXME: division exception"

            self.setRegister(REG_EAX, quot)
            self.setRegister(REG_EDX, rem)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_enter(self, op):
        locsize = self.getOperValue(op, 0)
        depth = self.getOperValue(op, 1)
        if depth != 0:
            raise envi.UnsupportedInstruction(self, op)

        esp = self.getRegister(REG_ESP)
        ebp = self.getRegister(REG_EBP)

        esp -= 4 # Room for the base pointer

        self.writeMemValue(esp, ebp, 4)
        self.setRegister(REG_EBP, esp)
        esp -= locsize
        self.setRegister(REG_ESP, esp)

    def i_idiv(self, op):
        #FIXME this needs emulation testing!
        tsize = op.opers[0].tsize
        if tsize == 1:
            ax = self.getRegister(REG_AX)
            ax = e_bits.signed(ax, 2)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 1)
            if d == 0: raise envi.DivideByZero(self)
            q = ax / d
            r = ax % d
            res = ((r & 0xff) << 8) | (q & 0xff)
            self.setRegister(REG_AX, res)

        elif tsize == 2:
            val = self.twoRegCompound(REG_DX, REG_AX, 2)
            val = e_bits.signed(val, 4)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 2)
            if d == 0: raise envi.DivideByZero(self)
            q = val / d
            r = val % d

            self.setRegister(REG_AX, q)
            self.setRegister(REG_DX, r)

        elif tsize == 4:
            val = self.twoRegCompound(REG_EDX, REG_EAX, 4)
            val = e_bits.signed(val, 8)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 4)
            if d == 0: raise envi.DivideByZero(self)
            q = val / d
            r = val % d

            self.setRegister(REG_EAX, q)
            self.setRegister(REG_EDX, r)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_imul(self, op):
        #FIXME eflags
        # FIXME imul bugs
        ocount = len(op.opers)
        if ocount == 2:
            dst = self.getOperValue(op, 0)
            src = self.getOperValue(op, 1)
            dsize = op.opers[0].tsize
            ssize = op.opers[1].tsize

            if dsize > ssize:
                src = e_bits.sign_extend(src, ssize, dsize)
                ssize = dsize

            res = dst * src

            sof = e_bits.is_unsigned_carry(res, dsize)
            self.setFlag(EFLAGS_CF, sof)
            self.setFlag(EFLAGS_OF, sof)

            self.setOperValue(op, 0, res)

        elif ocount == 3:
            dst = self.getOperValue(op, 0)
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)

            dsize = op.opers[0].tsize
            ssize1 = op.opers[1].tsize
            ssize2 = op.opers[2].tsize

            if dsize > ssize2: # Only the last operand may be shorter imm
                src2 = e_bits.sign_extend(src2, ssize2, dsize)
                ssize2 = dsize

            res = src1 * src2

            sof = e_bits.is_unsigned_carry(res, dsize)
            self.setFlag(EFLAGS_CF, sof)
            self.setFlag(EFLAGS_OF, sof)

            self.setOperValue(op, 0, res)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_in(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_inc(self, op):
        size = op.opers[0].tsize
        val = self.getOperValue(op, 0)

        sval = e_bits.signed(val, size)
        sval += 1

        self.setOperValue(op, 0, sval)

        # Another arithmetic op where doing signed and unsigned is easier ;)

        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sval, size))
        self.setFlag(EFLAGS_SF, e_bits.is_signed(sval, size))
        self.setFlag(EFLAGS_ZF, not sval)
        self.setFlag(EFLAGS_AF, (sval & 0xf == 0))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(sval))

    def i_int(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_int3(self, op):
        raise envi.BreakpointHit(self)

    def relJump(self, op):
        eip = self.getRegister(REG_EIP)
        eip += op.size
        eip += self.getOperValue(op, 0)
        return eip

    def i_ja(self, op):
        if (self.getFlag(EFLAGS_CF) == 0 and
            self.getFlag(EFLAGS_ZF) == 0):
            return self.relJump(op)

    def i_jae(self, op):
        if self.getFlag(EFLAGS_CF) == 0:
            return self.relJump(op)

    def i_jb(self, op):
        if self.getFlag(EFLAGS_CF) == 0:
            return self.relJump(op)

    def i_jbe(self, op):
        if (self.getFlag(EFLAGS_CF) or
            self.getFlag(EFLAGS_ZF)):
            return self.relJump(op)

    def i_jc(self, op):
        if self.getFlag(EFLAGS_CF):
            return self.relJump(op)

    def i_jnc(self, op):
        if not self.getFlag(EFLAGS_CF):
            return self.relJump(op)

    def i_jno(self, op):
        if not self.getFlag(EFLAGS_OF):
            return self.relJump(op)

    def i_jns(self, op):
        if not self.getFlag(EFLAGS_SF):
            return self.relJump(op)

    def i_jo(self, op):
        if self.getFlag(EFLAGS_OF):
            return self.relJump(op)

    def i_jpe(self, op):
        if self.getFlag(EFLAGS_PF):
            return self.relJump(op)

    def i_jecxz(self, op):
        if self.getRegister(REG_ECX) == 0:
            return self.relJump(op)

    def i_je(self, op):
        if self.getFlag(EFLAGS_ZF):
            return self.relJump(op)

    def i_jnz(self, op):
        if self.getFlag(EFLAGS_ZF) == 0:
            return self.relJump(op)

    def i_jg(self, op):
        if (self.getFlag(EFLAGS_ZF) == 0 and
            self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF)):
            return self.relJump(op)

    def i_jge(self, op):
        if self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF):
            return self.relJump(op)

    def i_jz(self, op):
        if self.getFlag(EFLAGS_ZF):
            return self.relJump(op)

    def i_jnl(self, op):
        if self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF):
            return self.relJump(op)

    def i_jl(self, op):
        if self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF):
            return self.relJump(op)

    def i_jle(self, op):
        if self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF):
            return self.relJump(op)
        if self.getFlag(EFLAGS_ZF):
            return self.relJump(op)

    def i_js(self, op):
        if self.getFlag(EFLAGS_SF):
            return self.relJump(op)

    def i_lea(self, op):
        base = self.getOperAddress(op, 1)
        self.setOperValue(op, 0, base)

    def decCounter(self):
        """
        A helper to decrement and return the counter
        """
        ecx = self.getRegister(REG_ECX)
        ecx -= 1
        self.setRegister(REG_ECX, ecx)
        return ecx

    def i_loop(self, op):
        if self.decCounter() != 0:
            return self.relJump(op)

    def i_loope(self, op):
        if (self.decCounter() != 0 and
            self.getFlag(EFLAGS_ZF)):
            return self.relJump(op)

    def i_loopne(self, op):
        if (self.decCounter() != 0 and
            not self.getFlag(EFLAGS_ZF)):
            return self.relJump(op)

    def i_leave(self, op):
        ebp = self.getRegister(REG_EBP)
        self.setRegister(REG_ESP, ebp)
        self.setRegister(REG_EBP, self.doPop())

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    def i_movsb(self, op):
        esi = self.getRegister(REG_ESI)
        edi = self.getRegister(REG_EDI)
        bytes = self.readMemory(esi, 1)
        self.writeMemory(edi, bytes)
        if self.getFlag(EFLAGS_DF):
            self.setRegister(REG_ESI, esi-1)
            self.setRegister(REG_EDI, edi-1)
        else:
            self.setRegister(REG_ESI, esi+1)
            self.setRegister(REG_EDI, edi+1)

    def i_movsd(self, op):
        esi = self.getRegister(REG_ESI)
        edi = self.getRegister(REG_EDI)
        bytes = self.readMemory(esi, 4)
        self.writeMemory(edi, bytes)
        if self.getFlag(EFLAGS_DF):
            self.setRegister(REG_ESI, esi-4)
            self.setRegister(REG_EDI, edi-4)
        else:
            self.setRegister(REG_ESI, esi+4)
            self.setRegister(REG_EDI, edi+4)

    def i_movsx(self, op):
        #FIXME prefix / 64 bit handling in all these
        osize = op.opers[1].tsize
        nsize = op.opers[0].tsize
        val = self.getOperValue(op, 1)
        val = e_bits.sign_extend(val, osize, nsize)
        self.setOperValue(op, 0, val)

    def i_movzx(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    def i_mul(self, op):
        #FIXME make sure these work right
        tsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        if tsize == 4:
            a = self.getRegister(REG_EAX)
        elif tsize == 2:
            a = self.getRegister(REG_AX)
        elif tsize == 1:
            a = self.getRegister(REG_Al)

        res = a * val

        if tsize == 1:
            self.setRegister(REG_AX, res)
        elif tsize == 2:
            dx,ax = self.regsFromCompound(res, tsize)
            self.setRegister(REG_AX, ax)
            self.setRegister(REG_DX, dx)
        else:
            edx,eax = self.regsFromCompound(res, tsize)
            self.setRegister(REG_EAX, eax)
            self.setRegister(REG_EDX, edx)

        # If the high order stuff was used, set CF/OF
        if res >> (tsize * 8):
            self.setFlag(EFLAGS_CF, True)
            self.setFlag(EFLAGS_OF, True)
        else:
            self.setFlag(EFLAGS_CF, False)
            self.setFlag(EFLAGS_OF, False)

    def i_neg(self, op):
        tsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        res = 0 - val
        self.setOperValue(op, 0, res)

        self.setFlag(EFLAGS_CF, val != 0)
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, tsize))
        #FIXME how does neg cause/not cause a carry?
        self.setFlag(EFLAGS_AF, 0) # FIXME EFLAGS_AF

    def i_nop(self, op):
        pass

    def i_not(self, op):
        val = self.getOperValue(op, 0)
        val ^= e_bits.u_maxes[op.opers[0].tsize]
        self.setOperValue(op, 0, val)

    def i_or(self, op):
        dst = self.getOperValue(op, 0)
        dsize = op.opers[0].tsize
        src = self.getOperValue(op, 1)
        ssize = op.opers[1].tsize

        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        res = dst | src

        self.setOperValue(op, 0, res)

        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))

    def i_pop(self, op):
        val = self.doPop()
        self.setOperValue(op, 0, val)

    def i_popad(self, op):
        #FIXME 16 bit?
        self.setRegister(REG_EDI, self.doPop())
        self.setRegister(REG_ESI, self.doPop())
        self.setRegister(REG_EBP, self.doPop())
        self.doPop() # skip one
        self.setRegister(REG_EBX, self.doPop())
        self.setRegister(REG_EDX, self.doPop())
        self.setRegister(REG_ECX, self.doPop())
        self.setRegister(REG_EAX, self.doPop())

    def i_popfd(self, op):
        eflags = self.doPop()
        self.setRegister(REG_FLAGS, eflags)

    def i_push(self, op):
        val = self.getOperValue(op, 0)
        if op.opers[0].mode == envi.OM_IMMEDIATE:
            val = e_bits.sign_extend(val, op.opers[0].tsize, 4) #FIXME 64bit
        self.doPush(val)

    def i_pushad(self, op):
        tmp = self.getRegister(REG_ESP)
        self.doPush(self.getRegister(REG_EAX))
        self.doPush(self.getRegister(REG_ECX))
        self.doPush(self.getRegister(REG_EDX))
        self.doPush(self.getRegister(REG_EBX))
        self.doPush(tmp)
        self.doPush(self.getRegister(REG_EBP))
        self.doPush(self.getRegister(REG_ESI))
        self.doPush(self.getRegister(REG_EDI))

    def i_pushfd(self, op):
        eflags = self.getRegister(REG_FLAGS)
        self.doPush(eflags)

    def i_jmp(self, op):
        val = self.getOperValue(op, 0)
        if op.opers[0].mode == envi.OM_IMMEDIATE:
            return self.relJump(op)
        else:
            return val

    def i_rcl(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # Put that carry bit up there.
        if self.getFlag(EFLAGS_CF):
            dst = dst | (1 << (8 * dsize))

        # Add one to account for carry
        x = ((8*dsize) - src) + 1

        res = (dst << src) | (dst >> x)
        cf = (res >> (8*dsize)) & 1
        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        if src == 1:
            m1 = e_bits.msb(res, dsize)
            m2 = e_bits.msb(res << 1, dsize)
            self.setFlag(EFLAGS_OF, m1 ^ m2)

        self.setOperValue(op, 0, res)

    def i_rcr(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f
        # Put that carry bit up there.
        if self.getFlag(EFLAGS_CF):
            dst = dst | (1 << (8 * dsize))

        # Add one to account for carry
        x = ((8*dsize) - src) + 1

        res = (dst >> src) | (dst << x)
        cf = (res >> (8*dsize)) & 1
        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        if src == 1:
            m1 = e_bits.msb(res, dsize)
            m2 = e_bits.msb(res << 1, dsize)
            self.setFlag(EFLAGS_OF, m1 ^ m2)

        self.setOperValue(op, 0, res)

    def i_rol(self, op):
        dstSize = op.opers[0].tsize
        count = self.getOperValue(op, 1)
        tempCount = shiftMask(count, dstSize)

        if tempCount > 0: # Yeah, i know...weird. See the intel manual
            while tempCount:
                val = self.getOperValue(op, 0)
                tempCf = e_bits.msb(val, dstSize)
                self.setOperValue(op, 0, (val * 2) + tempCf)
                tempCount -= 1
            val = self.getOperValue(op, 0)
            self.setFlag(EFLAGS_CF, e_bits.lsb(val))
            if count == 1:
                val = self.getOperValue(op, 0)
                cf = self.getFlag(EFLAGS_CF)
                self.setFlag(EFLAGS_OF, e_bits.msb(val, dstSize) ^ cf)
            else:
                self.setFlag(EFLAGS_OF, False)
        
    def i_ror(self, op):
        dstSize = op.opers[0].tsize
        count = self.getOperValue(op, 1)
        tempCount = shiftMask(count, dstSize)

        if tempCount > 0: # Yeah, i know...weird. See the intel manual
            while tempCount:
                val = self.getOperValue(op, 0)
                tempCf = e_bits.lsb(val)
                self.setOperValue(op, 0, (val / 2) + (tempCf * (2 ** dstSize)))
                tempCount -= 1
            val = self.getOperValue(op, 0)
            self.setFlag(EFLAGS_CF, e_bits.msb(val, dstSize))
            if count == 1:
                val = self.getOperValue(op, 0)
                cf = self.getFlag(EFLAGS_CF)
                # FIXME: This may be broke...the manual is kinda flaky here
                self.setFlag(EFLAGS_OF, e_bits.msb(val, dstSize) ^ (e_bits.msb(val, dstSize) - 1))
            else:
                self.setFlag(EFLAGS_OF, False)

    def i_ret(self, op):
        ret = self.doPop()
        if len(op.opers):
            esp = self.getRegister(REG_ESP)
            ival = self.getOperValue(op, 0)
            self.setRegister(REG_ESP, esp+ival)
        return ret

    def i_shl(self, op):
        return self.i_sal(op)

    def i_sal(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        res = dst << src
        cf = (res >> 8*dsize) & 1

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, not e_bits.msb(res, dsize) == cf)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_sar(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        signed = e_bits.msb(dst, dsize)

        res = dst >> src
        cf = (dst >> (src-1)) & 1

        # If it was signed, we need to fill in all those bits we
        # shifted off with ones.
        if signed:
            x = (8*dsize) - src
            umax = e_bits.u_maxes[dsize]
            res |= (umax >> x) << x

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, False)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_shr(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        res = dst >> src
        cf = (dst >> (src-1)) & 1

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, False)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_scasb(self, op):
        al = self.getRegister(REG_AL)
        edi = self.getRegister(REG_EDI)
        base,size = self.segments[SEG_ES]
        memval = ord(self.readMemory(base+edi, 1))
        self.intSubBase(al, memval, 1, 1)
        if self.getFlag(EFLAGS_DF):
            edi -= 1
        else:
            edi += 1
        self.setRegister(REG_EDI, edi)

    def i_scasd(self, op):
        #FIXME probably need to handle oper prefix by hand here...
        eax = self.getRegister(REG_EAX)
        edi = self.getRegister(REG_EDI)
        base,size = self.segments[SEG_ES]
        memval = struct.unpack("<L",self.readMemory(base+edi, 4))[0]
        self.intSubBase(eax, memval, 4, 4)
        if self.getFlag(EFLAGS_DF):
            edi -= 4
        else:
            edi += 4
        self.setRegister(REG_EDI, edi)

    def i_stosb(self, op):
        al = self.getRegister(REG_AL)
        edi = self.getRegister(REG_EDI)
        base,size = self.segments[SEG_ES]
        self.writeMemory(base+edi, chr(al))
        if self.getFlag(EFLAGS_DF):
            edi -= 1
        else:
            edi += 1
        self.setRegister(REG_EDI, edi)

    def i_stosd(self, op):
        al = self.getRegister(REG_AL)
        edi = self.getRegister(REG_EDI)
        base,size = self.segments[SEG_ES]
        self.writeMemory(base+edi, struct.pack("<L", eax))
        if self.getFlag(EFLAGS_DF):
            edi -= 4
        else:
            edi += 4
        self.setRegister(REG_EDI, edi)

    def i_setnz(self, op):
        if not self.getFlag(EFLAGS_ZF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)
        
    def i_setz(self, op):
        if self.getFlag(EFLAGS_ZF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_setge(self, op):
        if self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_setg(self, op):
        if (self.getFlag(EFLAGS_ZF) == 0 and
                self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF)):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_seto(self, op):
        if self.getFlag(EFLAGS_OF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_setl(self, op):
        if self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_setle(self, op):
        if (self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF) or
                self.getFlag(EFLAGS_ZF)):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_sets(self, op):
        if self.getFlag(EFLAGS_SF):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)
        
    def i_sbb(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        # Much like "integer subtraction" but we need
        # too add in the carry flag
        if src == None or dst == None:
            self.undefFlags()
            return None

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        src += self.getFlag(EFLAGS_CF)
        res = self.intSubBase(src, dst, ssize, dsize)
        self.setOperValue(op, 0, res)

    # FIXME scas stuff goes here
    # FIXME conditional byte set goes here
    def i_stc(self, op):
        self.setFlag(EFLAGS_CF, True)

    def i_std(self, op):
        self.setFlag(EFLAGS_DF, True)

    def i_sti(self, op):
        self.setFlag(EFLAGS_IF, True)

    # FIXME stos variants go here
    def i_stosd(self, op):
        eax = self.getRegister(REG_EAX)
        edi = self.getRegister(REG_EDI)
        # FIXME shouldn't have to do this directly
        # FIXME this needs a 32/16 bit mode check
        base,size = self.segments[SEG_ES]
        self.writeMemValue(base+edi, eax, 4)
        # FIXME edi inc must be by oper len
        self.setRegister(REG_EDI, edi+4)

    def i_sub(self, op):
        x = self.integerSubtraction(op)
        if x != None:
            self.setOperValue(op, 0, x)

    def i_test(self, op):
        self.logicalAnd(op)

    def i_wait(self, op):
        if len(self.fp_exceptions) > 0:
            raise Exception("WAIT DOESN'T KNOW WHAT TO DO")

    def i_xadd(self, op):
        val1 = self.getOperValue(op, 0)
        val2 = self.getOperValue(op, 1)
        temp = val1 + val2
        self.setOperValue(op, 1, val1)
        self.setOperValue(op, 0, temp)

    def i_xchg(self, op):
        temp = self.getOperValue(op, 0)
        self.setOperValue(op, 0, self.getOperValue(op, 1))
        self.setOperValue(op, 1, temp)

    def i_xor(self, op):
        # NOTE: This is pre-emptive for partially defined emulation
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        if op.opers[0] == op.opers[1]:
            ret = 0
        else:
            dst = self.getOperValue(op, 0)
            src = self.getOperValue(op, 1)
            if dsize != ssize:
                src = e_bits.sign_extend(src, ssize, dsize)
                ssize = dsize
            ret = src ^ dst

        self.setOperValue(op, 0, ret)

        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ret, dsize))
        self.setFlag(EFLAGS_ZF, not ret)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ret))
        self.setFlag(EFLAGS_AF, False) # Undefined but actually cleared on amd64 X2

class IntelUtilEmulator(IntelEmulator):
    """
    This type of emulator is used to calculate sp deltas
    and determine if registers are used or not.
    """
    def __init__(self):
        IntelEmulator.__init__(self)
        self.regs = [ 0x41414140+(4*i) for i in range(self.rcount) ]
        self.setMemoryObject(envi.FakeMemory())

    def snapshot(self):
        """
        NOTE: we can only use snapshot/restore where the memobj
        is OK to deepcopy...  use carefully...
        """
        return (list(self.regs),
                copy.deepcopy(self.memobj))

    def restore(self, stuff):
        self.regs    = list(stuff[0])
        self.memobj  = copy.deepcopy(stuff[1])

    def doRepPrefix(self, meth, op):
        # Fake out the rep prefix (cause ecx == 0x41414141 ;) )
        return meth(op)

