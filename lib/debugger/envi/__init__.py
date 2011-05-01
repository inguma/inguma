
"""
The Envi framework allows architecutre abstraction through
the use of the ArchitectureModule, Opcode, Operand, and
Emulator objects.
"""

OM_MEMMASK = 0x80

# Operand Modes
OM_IMMEDIATE    = 0x1 #  imm
OM_REGISTER     = 0x2 #  reg
# Begin "Deref" operands.
# Any of these may also specify a "disp" displacement
OM_IMMMEM       = 0x84 #  [ imm + disp]
OM_REGMEM       = 0x85 #  [ reg + disp ]
OM_SIBMEM       = 0x86 #  [ reg/imm + indexreg * scale + disp]

# Instruciton flags
IF_NOFALL = 1 # Set if this instruction does *not* fall through
IF_PRIV   = 2 # Set if this is a "privileged mode" instruction

import envi.bits as e_bits

class ArchitectureModule:
    """
    An architecture module implementes methods to deal
    with the creation of envi objects for the specified
    architecture.
    """
    def __init__(self, archname, maxinst=32):
        self.archname = archname
        self.maxinst = maxinst # What is the maximum length of an instruction

    def makeOpcode(self, bytes, offset=0):
        raise ArchNotImplemented("makeOpcode")

    def reprOpcode(self, op, va=None, names=None):
        raise ArchNotImplemented("reprOpcode")

    def reprOperand(self, op, operindex, va=None, names=None):
        raise ArchNotImplemented("reprOperand")

    def getEmulator(self):
        raise ArchNotImplemented("getEmulator")

    def getRegisterCount(self):
        """
        Return the number of registers your architecture will
        require emulaton for.
        """
        raise ArchNotImplemented("getProgramCounterIndex")

    def getProgramCounterIndex(self):
        raise ArchNotImplemented("getProgramCounterIndex")

    def getStackCounterIndex(self):
        raise ArchNotImplemented("getStackCounterIndex")

    def getFrameCounterIndex(self):
        """
        Return the register index used for the "frame" register
        (ie ebp on x86).  Or None if there is none on this arch.
        """
        raise ArchNotImplemented("getStackCounterIndex")

    def getRegisterName(self, index):
        raise ArchNotImplemented("getRegisterName")

    def getPrefixName(self, prefixes):
        raise ArchNotImplemented("getPrefixName")

    def spoilsReg(self, opcode, regindex):
        """
        Return True of the given instruction changes the value of 
        of the specified register index.
        """
        raise ArchNotImplemented("spoilsReg")

    def getBranches(self, op, va):
        """
        Return a list of the possible next program counter values
        following the opcode (assuming that it lives at
        the specified virtual address).
        """
        raise ArchNotImplemented()

    def getPointerSize(self):
        """
        Get the size of a pointer in memory on this architecture.
        """
        raise ArchNotImplemented("getPointerSize")

    def getStackDelta(self, op):
        """
        If the given opcode instruction changes the value of the
        stack pointer, return the delta from that opcode...
        """
        raise ArchNotImplemented("getStackDelta")

    def isCall(self, opcode):
        """
        Return True if the given opcode object is a "call" type
        branching instruction
        """
        raise ArchNotImplemented("isCall")

    def isBranch(self, opcode):
        """
        Return True if the given opcode object is a branching instruction
        """
        raise ArchNotImplemented("isBranch")

    def pointerString(self, va):
        """
        Return a string representation for a pointer on this arch
        """
        raise ArchNotImplemented("pointerString")

class EnviException(Exception):
    pass

class InvalidInstruction(EnviException):
    """
    Raised by opcode parsers when the specified
    bytes do not represent a valid opcode
    """
    pass

class SegmentationViolation(EnviException):
    """
    Raised by an Emulator extension when you
    bad-touch memory. (Likely from memobj).
    """
    def __init__(self, va, msg=None):
        if msg == None:
            msg = "Bad Memory Access: %s" % hex(va)
        EnviException.__init__(self, msg)
        self.va = va

class ArchNotImplemented(EnviException):
    """
    Raised by various Envi components when the architecture
    does not implement that envi component.
    """
    pass

class EmuException(EnviException):
    """
    A parent for all emulation exceptions so catching
    them can be easy.
    """
    def __init__(self, emu, msg=None):
        EnviException.__init__(self, msg)
        self.va = emu.getRegister(emu.pcindex)

class UnsupportedInstruction(EmuException):
    """
    Raised by emulators when the given instruction
    is not implemented by the emulator.
    """
    def __init__(self, emu, op):
        EmuException.__init__(self, emu)
        self.op = op

class DivideByZero(EmuException):
    """
    Raised by an Emulator when a divide/mod has
    a 0 divisor...
    """

class BreakpointHit(EmuException):
    """
    Raised by an emulator when you execute a breakpoint instruction
    """

class PDEUndefinedFlag(EmuException):
    """
    This exception is raised when a conditional operation is dependant on
    a flag state that is unknown.
    """

class PDEException(EmuException):
    """
    This exception is used in partially defined emulation to signal where
    execution flow becomes un-known due to undefined values.  This is considered
    un-recoverable.
    """

class UnknownCallingConvention(EmuException):
    """
    Raised when the getCallArgs() or setReturnValue() methods
    are given an unknown calling convention type.
    """

class Operand:
    def __init__(self, mode, tsize, reg=None, indexreg=None, imm=None, disp=None, scale=None):
        self.tsize = tsize
        self.mode = mode
        self.reg = reg
        self.indexreg = indexreg
        self.imm = imm
        self.disp = disp
        self.scale = scale

    def __ne__(self, op):
        return not op == self

    def __eq__(self, oper):
        if not isinstance(oper, Operand):
            return False
        if self.mode != oper.mode:
            return False
        if self.tsize != oper.tsize:
            return False
        if self.reg != oper.reg:
            return False
        if self.indexreg != oper.indexreg:
            return False
        if self.imm != oper.imm:
            return False
        if self.disp != oper.disp:
            return False
        if self.scale != oper.scale:
            return False
        return True

    def __repr__(self):

        if self.mode == OM_IMMEDIATE:
            return hex(self.imm)

        elif self.mode == OM_REGISTER:
            return "reg%d" % self.reg

        elif self.mode == OM_IMMMEM:
            return "[0x%.8x]" % self.imm

        elif self.mode == OM_REGMEM:
            if self.disp != None:
                return "[reg%d + %d]" % (self.reg, self.disp)
            else:
                return "[reg%d]" % self.reg

        elif self.mode == OM_SIBMEM:
            s = ""
            if self.imm != None:
                s += "0x%.8x " % self.imm
            if self.reg != None:
                s += "reg%d " % self.reg
            if self.indexreg != None:
                s += "+ reg%d " % self.indexreg
                if self.scale != None:
                    s += "* %d " % self.scale
            if self.disp != None:
                s += "+ %d" % self.disp
            return "[%s]" % s

class Opcode:
    """
    A universal representation for an opcode
    """
    def __init__(self, opcode, mnem, prefixes, size, operands, iflags=0):
        """
        constructor for the basic Envi Opcode object.  Arguments as follows:

        opcode - An architecture specific numerical value for the opcode
        mnem   - A humon readable mnemonic for the opcode
        prefixes - a bitmask of architecture specific instruction prefixes
        size - The size of the opcode in bytes
        operands - A list of Operand objects for this opcode
        iflags -   A list of Envi (architecture independant) instruction flags (see IF_FOO)
        """
        self.opcode = opcode
        self.mnem = mnem
        self.prefixes = prefixes
        self.size = size
        self.opers = operands
        self.repr = None
        self.iflags = iflags

    def copy(self):
        """
        Create a copy of this opcode object with as little object instantiation
        as possible.
        """
        opers = []
        for o in self.opers:
            opers.append(Operand(o.mode, o.tsize, o.reg, o.indexreg, o.imm, o.disp))
        return Opcode(self.opcode, self.mnem, self.prefixes, self.size, opers, self.iflags)

    def makeRepr(self):
        x = [self.mnem,]
        for o in self.opers:
            x.append(repr(o))
        return " ".join(x)

    def __ne__(self, op):
        return not op == self

    def __eq__(self, op):
        if not isinstance(op, Opcode):
            return False
        if self.opcode != op.opcode:
            return False
        if self.mnem != op.mnem:
            return False
        if self.size != op.size:
            return False
        if self.iflags != op.iflags:
            return False
        if len(self.opers) != len(op.opers):
            return False
        for i in range(len(self.opers)):
            if self.opers[i] != op.opers[i]:
                return False
        return True

    def __hash__(self):
        return int(hash(self.mnem) ^ (self.size << 4))

    def __repr__(self):
        if self.repr == None:
            self.repr = self.makeRepr()
        return self.repr

    def __len__(self):
        return int(self.size)

class Emulator:
    """
    The Emulator class is mostly "Abstract" in the java
    Interface sense.  The emulator should be able to
    be extended for the architecutures which are included
    in the envi framework.  You *must* give the constructor
    an instance of your architecture abstraction module.

    (NOTE: Most users will just use an arch mod and call getEmulator())

    The intention is for "light weight" emulation to be
    implemented mostly for user-space emulation of 
    protected mode execution.

    Additionally, the envi Emulator is capable of "partially defined
    emulation" which is triggered by any registers or memory reads having
    the value None (not 0).  In these cases, special exceptions may be used
    to manage execution flow and determine whatever is possible from the 
    PDE process that reversers typically do in their heads.
    """
    def __init__(self, archmod, regarray=None, segs=None, memobj=None):
        self.arch = archmod
        self.pcindex = archmod.getProgramCounterIndex()
        self.spindex = archmod.getStackCounterIndex()
        self.rcount  = archmod.getRegisterCount()
        if regarray == None:
            regarray = []
            for i in range(self.rcount):
                regarray.append(0)

        if segs == None:
            segs = [(0,0xffffffff),]

        self.segments = segs

        # Set up some regs and masks
        self.regs = regarray

        # Save off the memory object
        self.setMemoryObject(memobj)

        self.call_convs = {}

        # Automagically setup an instruction mnemonic handler dict
        # by finding all methods starting with i_ and assume they
        # implement an instruction by mnemonic
        # FIXME THIS *MUST* GET FASTER FOR UTIL FUNCS!
        # POSSIBLY DECLARE IN ADVANCE?
        self.op_methods = {}
        for name in dir(self):
            if name.startswith("i_"):
                self.op_methods[name[2:]] = getattr(self, name)

    def setStackCounter(self, value):
        return self.setRegister(self.spindex, value)

    def getStackCounter(self):
        return self.getRegister(self.spindex)

    def setProgramCounter(self, value):
        return self.setRegister(self.pcindex, value)

    def getProgramCounter(self):
        return self.getRegister(self.pcindex)

    def getSegmentInfo(self, op):
        idx = self.getSegmentIndex(op)
        return self.segments[idx]

    def getSegmentIndex(self, op):
        """
        The *default* segmentation is none (most arch's will over-ride).
        This method may be implemented to return a segment index based on either
        emulator state or properties of the particular instruction in question.
        """
        return 0

    def setSegmentInfo(self, idx, base, size):
        self.segments[idx] = (base,size)

    def setMemoryObject(self, memobj):
        """
        Give the emulator a memory object to use for reads and writes.
        A memory object must implement the methods from the base MemoryObject.
        """
        self.memobj = memobj

    def getMemoryObject(self):
        return self.memobj

    def executeOpcode(self, opobj):
        """
        This is the core method for the 
        """
        raise ArchNotImplemented()

    def getRegister(self, regindex):
        """
        Given the architecture specific register index,
        return the current value.
        """
        return self.regs[regindex]

    def setRegister(self, regindex, value):
        """
        Set the value of the architecuture specific register
        by index.
        """
        # We assume a default "pointer length" width.  If you are
        # dealing with registers other than that, you will need
        # to over-ride this method to use them (see IntelModule for example)
        width = self.arch.getPointerSize()
        value = e_bits.unsigned(value, width)
        self.regs[regindex] = value

    def makeOpcode(self, pc):
        """
        This is the core method for the 
        """
        raise ArchNotImplemented()

    def run(self, stepcount=None):
        """
        Run the emulator until "something" happens.
        (breakpoint, segv, syscall, etc...)
        """
        if stepcount != None:
            for i in xrange(stepcount):
                self.stepi()
        else:
            while True:
                self.stepi()

    def stepi(self):
        pc = self.getProgramCounter()
        op = self.makeOpcode(pc)
        self.executeOpcode(op)

    def readMemory(self, va, size):
        """
        Read memory bytes in the emulated environment.
        For partially-defined emulation, this may return None when
        the state is unknown.
        """
        return self.memobj.readMemory(va, size)

    def writeMemory(self, va, bytes):
        """
        Write memory in the emulation Environment
        """
        return self.memobj.writeMemory(va, bytes)

    def getOperValue(self, op, idx):
        """
        Return the value for the operand at index idx for
        the given opcode reading memory and register states if necissary.

        In partially-defined emulation, this may return None
        """
        oper = op.opers[idx]
        if oper.mode == OM_IMMEDIATE:
            return oper.imm

        if oper.mode == OM_REGISTER:
            return self.getRegister(oper.reg)

        val = self.getOperAddress(op, idx)
        return self.readMemValue(val, oper.tsize)

    def getOperAddress(self, op, idx):
        """
        Return the address that an operand which deref's memory
        would read from on getOperValue().
        """

        oper = op.opers[idx]

        if oper.mode == OM_IMMMEM:
            base,size = self.getSegmentInfo(op)
            return e_bits.unsigned(base + oper.imm, oper.tsize)

        if oper.mode == OM_REGMEM:

            val = self.getRegister(oper.reg)
            if val == None:
                return None

            base,size = self.getSegmentInfo(op)
            val += base

            if oper.disp != None:
                val += oper.disp

            return e_bits.unsigned(val, oper.tsize)

        if oper.mode == OM_SIBMEM:
            addr = 0
            if oper.reg != None:
                basereg = self.getRegister(oper.reg)
                if basereg == None:
                    return None
                addr += basereg

            if oper.imm != None:
                addr += oper.imm

            if oper.indexreg != None:
                index = self.getRegister(oper.indexreg)
                if index == None:
                    return None
                if oper.scale != None:
                    index *= oper.scale
                addr += index

            if oper.disp != None:
                addr += oper.disp

            base,size = self.getSegmentInfo(op)
            return e_bits.unsigned(addr + base, oper.tsize)

        raise Exception("getOperAddress() on wrong type!")

    def setOperValue(self, op, idx, value):
        """
        Set the value of the target operand at index idx from
        opcode op.
        (obviously OM_IMMEDIATE *cannot* be set)
        """
        oper = op.opers[idx]

        value = e_bits.unsigned(value, oper.tsize)

        if oper.mode == OM_IMMEDIATE:
            raise InvalidInstruction()

        if oper.mode == OM_REGISTER:
            return self.setRegister(oper.reg, value)

        if oper.mode == OM_IMMMEM:
            base,size = self.getSegmentInfo(op)
            return self.writeMemValue(base + oper.imm, value, oper.tsize)

        if oper.mode == OM_REGMEM:
            reg = self.getRegister(oper.reg)

            base,size = self.getSegmentInfo(op)
            reg += base

            if oper.disp != None:
                reg += oper.disp
            return self.writeMemValue(reg, value, oper.tsize)

        if oper.mode == OM_SIBMEM:
            base,size = self.getSegmentInfo(op)
            addr = base

            if oper.reg != None:
                addr += self.getRegister(oper.reg)

            if oper.imm != None:
                addr += oper.imm

            if oper.indexreg != None:
                index = self.getRegister(oper.indexreg)
                if oper.scale != None:
                    index *= oper.scale
                addr += index

            if oper.disp != None:
                addr += oper.disp

            return self.writeMemValue(addr, value, oper.tsize)

    def addCallingConvention(self, name, obj):
        self.call_convs[name] = obj

    def hasCallingConvention(self, name):
        if self.call_convs.get(name) != None:
            return True
        return False

    def getCallArgs(self, count, cc):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to get stack/reg/whatever args.

        Usage: getCallArgs(3, "stdcall") -> (0, 32, 0xf00)
        """
        c = self.call_convs.get(cc, None)
        if c == None:
            raise UnknownCallingConvention(cc)

        return c.getCallArgs(self, count)

    def setReturnValue(self, value, cc, ccinfo=None):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to set a function return value. (this should also take
        care of any argument cleanup or other return time tasks
        for the calling convention)
        """
        c = self.call_convs.get(cc, None)
        if c == None:
            raise UnknownCallingConvention(cc)

        return c.setReturnValue(self, value, ccinfo)

class CallingConvention:
    """
    Implement calling conventions for your arch.
    """
    def setReturnValue(self, emu, value, ccinfo=None):
        pass

    def getCallArgs(self, emu, count):
        pass

class MemoryObject:
    def __init__(self, maps=None, pagesize=4096):
        """
        Take a set of memory maps (va, perms, bytes) and put them in
        a sparse space finder. You may specify your own page-size to optimize
        the search for an architecture.
        """
        self.pagesize = pagesize
        self.mask = (0-pagesize) & 0xffffffff
        self.maplookup = {}
        if maps != None:
            for va,perms,bytes in maps:
                self.addMemoryMap(va, perms, bytes)

    def addMemoryMap(self, va, perms, bytes):
        x = [va, perms, bytes] # Asign to a list cause we need to write to it
        base = va & self.mask
        maxva = va + len(bytes)
        while base < maxva:
            self.maplookup[base] = x
            base += self.pagesize

    def getMemoryMap(self, va):
        """
        Get the va,perms,bytes list for this map
        """
        return self.maplookup.get(va & self.mask)

    #FIXME make extendable maps for things like the stack
    def checkMemory(self, va, perms=0):
        map = self.maplookup.get(va & self.mask)
        if map == None:
            return False
        if (perms & map[1]) != perms:
            return False
        return True

    def readMemory(self, va, size):
        map = self.maplookup.get(va & self.mask)
        if map == None:
            raise SegmentationViolation(va)
        if not map[1] & 4: #FIXME make permission bits
            raise SegmentationViolation(va)
        offset = va - map[0]
        return map[2][offset:offset+size]

    def writeMemory(self, va, bytes):
        map = self.maplookup.get(va & self.mask)
        if map == None:
            raise SegmentationViolation(va)
        if not map[1] & 2: #FIXME make permission bits
            raise SegmentationViolation(va)
        offset = va - map[0]
        map[2] = map[2][:offset] + bytes + map[2][offset+len(bytes):]

class MemoryTracker:
    """
    A utility that will track memory access and let everything be valid
    memory for reading and writing.
    """
    def __init__(self):
        self.bytes = {}
        self.reads = []
        self.writes = []

    def readMemory(self, va, size):
        #FIXME make this unique so it can be tracked
        #FIXME make this return anything he's written already
        self.reads.append((va, size))
        return "A"*size

    def writeMemory(self, va, bytes):
        self.writes.append((va, bytes))
        self.bytes[va] = bytes
        
class FakeMemory:
    def checkMemory(self, va, perms=0):
        return True
    def readMemory(self, va, size):
        return "A"*size
    def writeMemory(self, va, bytes):
        pass

def getArchModule(name):
    """
    return an Envi architecture module instance for the following
    architecture name.
    
    Current architectures include:

    i386 - Intel i386
    """
    if name in ["i386","i486","i586","i686"]:
        import envi.intel as e_intel
        return e_intel.IntelModule()
    else:
        raise ArchNotImplemented(name)

