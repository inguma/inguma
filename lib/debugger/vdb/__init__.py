import os
import sys
import code
import signal
import string
import traceback

from ConfigParser import *

from cmd import *
from struct import *
from getopt import getopt
from UserDict import *
from threading import *

import vtrace
import vtrace.util as v_util
import vtrace.notifiers as v_notif

import vdb
import vdb.formatters as fmt
import vdb.extensions as v_ext

import envi

import vstruct

vdb.basepath = vdb.__path__[0] + "/"

class VdbLookup(UserDict):
    def __init__(self, initdict={}):
        UserDict.__init__(self)
        for key,val in initdict.items():
            self.__setitem__(self, key, value)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        UserDict.__setitem__(self, item, key)

class ScriptThread(Thread):
    def __init__(self, cobj, locals):
        Thread.__init__(self)
        self.setDaemon(True)
        self.cobj = cobj
        self.locals = locals

    def run(self):
        try:
            exec(self.cobj, self.locals)
        except Exception, e:
            print "Script Error: ",e

class CliExtMeth:
    """
    This is used to work around the difference
    between functions and bound methods for extended
    command modules
    """
    def __init__(self, vdb, func):
        self.vdb = vdb
        self.func = func
        self.__doc__ = func.__doc__

    def __call__(self, line):
        return self.func(self.vdb, line)

class VdbCli(Cmd,v_notif.Notifier):

    """
    The command object used by the VDB command line interface
    """

    def __init__(self, myvdb, stdin=sys.stdin, stdout=sys.stdout):
        Cmd.__init__(self, stdin=stdin, stdout=stdout)
        v_notif.Notifier.__init__(self)
        self.vdb = myvdb
        self.prompt = "vdb > "
        self.banner = "Welcome To VDB!\n"
        self.vcmds = {}
        self.vdb.registerNotifier(vtrace.NOTIFY_ALL, self)

    def do_config(self, line):
        """
        Show or edit a vdb config option from the command line

        Usage: config [-S section] [option=value]
        """
        argv = v_util.splitargs(line)
        secname = None
        try:
            opts,args = getopt(argv, "S:")
            for opt,optarg in opts:
                if opt == "-S":
                    secname = optarg

        except Exception, e:
            print e
            return self.do_help("config")

        if len(args) > 1:
            return self.do_help("config")

        if len(args) == 0:
            if secname != None:
                secs = [secname,]
            else:
                secs = self.vdb.config.sections()

            for secname in secs:
                self.vdb.vprint("")
                self.vdb.vprint("[%s]" % secname)
                for oname in self.vdb.config.options(secname):
                    val = self.vdb.config.get(secname, oname)
                    self.vdb.vprint("%s=%s" % (oname, val))

        else:
            if secname == None:
                secname = ""
            key,val = args[0].split("=",1)
            self.vdb.config.set(secname, key, val)
            self.vdb.vprint("[%s] %s = %s" % (secname,key,val))

        #import vwidget.config as vw_config
        #x = vw_config.ConfigDialog(self.vdb.config)
        #x.show()

    def do_alias(self, line):
        """
        Add an alias to the command line interpreter's aliases dictionary

        Usage: alias <alias_word> rest of the alias command
        To delete an alias:
        Usage: alias <alias_word>
        """
        if len(line):
            row = line.split(None, 1)
            if len(row) == 1:
                self.vdb.delConfig("Aliases",row[0])
            else:
                self.vdb.setConfig("Aliases",row[0],row[1])

        self.vdb.vprint("Current Aliases:\n")
        for a,v in self.vdb.getConfigSection("Aliases").items():
            self.vdb.vprint("%s -> %s" % (a,v))
        self.vdb.vprint("")
        return

    def get_names(self):
        ret = []
        ret.extend(Cmd.get_names(self))
        ret.extend(self.vdb.extcmds.keys())
        return ret

    def __getattr__(self, name):
        func = self.vdb.extcmds.get(name, None)
        if func == None:
            raise AttributeError
        return CliExtMeth(self.vdb, func)

    def precmd(self, line):
        for k,v in self.vdb.getConfigSection("Aliases").items():
            if line.startswith(k):
                line = line.replace(k, v)
        return line

    def onecmd(self, line):
        try:
            Cmd.onecmd(self, line)
        except SystemExit:
            raise
        except Exception, msg:
            #traceback.print_exc()
            self.vdb.vprint("ERROR: %s" % msg)

    def do_vstruct(self, line):
        """
        List the available structure modules and optionally
        structure definitions from a particular module in the
        current vstruct.

        Usage: vstruct [modname]
        """
        if len(line) == 0:
            self.vdb.vprint("\nVStruct Modules:")
            plist = vstruct.getModuleNames()
        else:
            self.vdb.vprint("\nKnown Structures:")
            plist = vstruct.getStructNames(line)

        for n in plist:
            self.vdb.vprint(n)
        self.vdb.vprint("\n")

    def do_dis(self, line):
        """
        Print out the opcodes for a given address expression

        Usage: dis <address expression>
        """
        if len(line) == 0:
            return self.do_help("dis")
        t = self.vdb.getTrace()
        t.requireAttached()
        addr = t.parseExpression(line)
        mem = t.readMemory(addr, 256)
        offset = 0
        count = 0
        self.vdb.vprint("Dissassembly:")
        while offset < 255 and count < 20:
            va = addr + offset
            op = self.vdb.arch.makeOpcode(mem[offset:])
            self.vdb.vprint("0x%.8x: %s" % (va,self.vdb.arch.reprOpcode(op, va=va)))
            offset += len(op)
            count += 1

    def do_maps(self, line):
        """
        Display all the current memory maps.

        Usage: maps
        """
        t = self.vdb.getTrace()
        self.vdb.vprint("[ address ] [ size ] [ perms ] [ File ]")
        for addr,size,perm,fname in t.getMaps():
            self.vdb.vprint("0x%.8x\t%d\t%s\t%s" % (addr,size,perm,fname))

    def do_memdump(self, line):
        """
        Dump process memory out to a file.

        Usage: memdump <addr_expression> <size_expression> <filename>
        """
        if len(line) == 0:
            return self.do_help("memdump")

        argv = v_util.splitargs(line)
        if len(argv) != 3:
            return self.do_help("memdump")

        t = self.vdb.getTrace()
        addr = t.parseExpression(argv[0])
        size = t.parseExpression(argv[1])

        mem = t.readMemory(addr, size)
        file(argv[2], "wb").write(mem)
        
    def do_mem(self, line):
        """
        Show some memory (with optional formatting and size)

        Usage: mem [-F <formatter>] <addr expression> [size]

        NOTE: use -F ? for a list of the formatters
        """
        fmtname = "Bytes"

        if len(line) == 0:
            return self.do_help("mem")

        argv = v_util.splitargs(line)
        try:
            opts,args = getopt(argv, "F:")
        except:
            return self.do_help("mem")

        for opt,optarg in opts:
            if opt == "-F":
                fmtname = optarg
                if fmtname == "?":
                    self.vdb.vprint("Registered Formatters:")
                    for name in self.vdb.getFormatNames():
                        self.vdb.vprint(name)
                    return

        t = self.vdb.getTrace()
        size = 256
        addr = t.parseExpression(args[0])
        if len(args) == 2:
            size = int(args[1], 0)

        bytes = t.readMemory(addr, size)
        abuf,dbuf,cbuf = self.vdb.doFormat(fmtname, addr, bytes)
        alines = abuf.split("\n")
        dlines = dbuf.split("\n")
        clines = cbuf.split("\n")
        for i in xrange(len(alines)):
            self.vdb.vprint("%s  %s  %s" % (alines[i],dlines[i],clines[i]))

    def do_python(self, line):
        """
        Start an interactive python interpreter with the following
        objects mapped into the namespace:
        vtrace - The Vtrace Module
        vdb    - The Vdb Module
        db     - The debugger instance
        trace  - The current tracer

        Usage: python
        """
        local = {"vtrace":vtrace,
                  "vdb":vdb,
                  "db":self.vdb,
                  "trace":self.vdb.getTrace()}
        code.interact(local=local)

    def do_struct(self, args):
        """
        Break out a strcuture from memory.  You may use the command
        "vstruct" to show the known structures in vstruct.

        Usage: struct <StructName> <vtrace expression>
        """
        try:
            clsname, vexpr = v_util.splitargs(args)
        except:
            return self.do_help("struct")

        t = self.vdb.getTrace()

        addr = t.parseExpression(vexpr)
        s = t.getStruct(clsname, addr)
        self.vdb.vprint(repr(s))

    def notify(self, event, trace):
        """
        Some CLI notifiers for printing out debugger events.
        """

        pid = trace.getPid()

        if event == vtrace.NOTIFY_ATTACH:
            self.vdb.vprint("Attached to : %d" % pid)

        elif event == vtrace.NOTIFY_CONTINUE:
            pass
            #self.vdb.vprint("PID %d continuing" % pid

        elif event == vtrace.NOTIFY_DETACH:
            self.vdb.vprint("Detached from %d" % pid)

        elif event == vtrace.NOTIFY_SIGNAL:
            win32 = trace.getMeta("Win32Event", None)
            if win32:
                code = win32.get("ExceptionCode", 0)
                addr = win32.get("ExceptionAddress")
                chance = 2
                if win32.get("FirstChance", False):
                    chance = 1
                self.vdb.vprint("Win32 Exception: 0x%.8x at 0x%.8x (%d chance)" % (code, addr, chance))
            else:
                self.vdb.vprint("Process Recieved Signal %d" % trace.getMeta("PendingSignal"))

        elif event == vtrace.NOTIFY_BREAK:
            pc = trace.getProgramCounter()
            bp = trace.breakpoints.get(pc, None)
            if bp:
                self.vdb.vprint("Hit Break: %s" % repr(bp))

        elif event == vtrace.NOTIFY_EXIT:
            self.vdb.vprint("PID %d exited: %d" % (pid,trace.getMeta("ExitCode")))

        elif event == vtrace.NOTIFY_LOAD_LIBRARY:
            self.vdb.vprint("Loading Binary: %s" % trace.getMeta("LatestLibrary",None))

        elif event == vtrace.NOTIFY_CREATE_THREAD:
            self.vdb.vprint("New Thread: %d" % trace.getMeta("ThreadId"))

        elif event == vtrace.NOTIFY_EXIT_THREAD:
            self.vdb.vprint("Exit Thread: %d" % trace.getMeta("ThreadId"))

        elif event == vtrace.NOTIFY_DEBUG_PRINT:
            s = "<unknown>"
            win32 = trace.getMeta("Win32Event", None)
            if win32:
                s = win32.get("DebugString", "<unknown>")
            self.vdb.vprint("DEBUG PRINT: %s" % s)

    def do_writemem(self, args):
        """
        Over-write some memory in the target address space.
        Usage: writemem <addr expression> <py string>
        NOTE: do NOT have any whitspace in addr-expression until I get off
        my ass a write a good parser
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        addr,buf = args.split(None, 1)
        addr = t.parseExpression(addr)
        buf = eval(buf)
        t.writeMemory(addr, buf)

    def do_signal(self, args):
        """
        Show or set the current pending signal (this is ONLY relavent on POSIX signaling
        systems).

        Usage: signal [newsigno]
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        cursig = t.getMeta("PendingSignal", 0)
        self.vdb.vprint("Current signal: %d" % cursig)
        if args:
            newsig = int(args)
            t.setMeta("PendingSignal", newsig)
            self.vdb.vprint("New signal: %d" % newsig)

    def do_snapshot(self, line):
        """
        Take a process snapshot of the current (stopped) trace and
        save it to the specified file.

        Usage: snapshot <filename>
        """
        if len(line) == 0:
            return self.do_help("snapshot")
        alist = v_util.splitargs(line)
        if len(alist) != 1:
            return self.do_help("snapshot")

        t = self.vdb.getTrace()
        t.requireAttached()
        print "Taking Snapshot"
        snap = t.takeSnapshot()
        print "Saving To File"
        snap.saveToFile(alist[0])
        print "Done"

    def do_script(self, text):
        """
        Execute a vscript file.

        The vscript file is arbitrary python code which is run with
        the trace, vdb, vtrace, and optional arguments mapped in as locals.

        Usage: script <scriptfile> [...script args...]
        """
        args = text.split()
        if len(args) == 0:
            return self.do_help("script")
        filename = ""
        for i in range(len(args)):
            filename = string.join(args[:i+1])
            if os.path.exists(filename):
                args = args[i+1:]
                break

        self.vdb.script(filename, args)

    def do_ignore(self, args):
        """
        Add the specified signal id (exception id for windows) to the ignored
        signals list for the current trace.  This will make the smallest possible
        performance impact for that particular signal but will also not alert
        you that it has occured.

        Usage: ignore [[-d] <sigcode>]
        """
        #FIXME make a good arg parser
        t = self.vdb.getTrace()
        alist = v_util.splitargs(args)
        if len(alist) == 1:
            sigid = int(args, 0)
            self.vdb.vprint("ADDING 0x%.8x to the ignores list" % sigid)
            t.addIgnoreSignal(sigid)
        elif len(alist) == 2 and alist[0] == "-d":
            sigid = int(alist[1], 0)
            t.delIgnoreSignal(sigid)
        else:
            ilist = t.getMeta("IgnoredSignals")
            self.vdb.vprint("Currently Ignored Signals/Exceptions:")
            for x in ilist:
                self.vdb.vprint("0x%.8x" % x)

    def do_exec(self, string):
        """
        Execute a program with the given command line and
        attach to it.
        Usage: exec </some/where and some args>
        """
        t = self.vdb.newTrace()
        t.execute(string)

    def do_threads(self, line):
        """
        List the current threads in the target process or select
        the current thread context for the target tracer.
        Usage: thread [thread id]
        """
        t = self.vdb.getTrace()
        t.requireAttached()

        if len(line) > 0:
            thrid = int(line, 0)
            t.selectThread(thrid)

        self.vdb.vprint("Current Threads:")
        self.vdb.vprint("(thrid -> thrinfo)")
        tid = t.getMeta("ThreadId")
        for key,val in t.getThreads().items():
            a = " "
            if key == tid:
                a = "*"
            self.vdb.vprint("%s%s -> 0x%.8x" % (a, key, val))

    def do_mode(self, args):
        """
        Set modes in the tracers...
        mode Foo=True/False
        """
        t = self.vdb.getTrace()
        if args:
            mode,val = args.split("=")
            newmode = eval(val)
            self.vdb.setMode(mode, newmode)
        else:
            for key,val in t.modes.items():
                self.vdb.vprint("%s -> %d" % (key,val))

    def do_regs(self, args):
        """
        Show *all* the current registers.
        FIXME: This needs some prettifying

        Usage: regs
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        regs = t.getRegisters()
        rnames = regs.keys()
        rnames.sort()
        for r in rnames:
            self.vdb.vprint("%s 0x%.8x" % (r, regs[r]))

    def do_stepi(self, args):
        """
        Single step the target tracer.
        Usage: stepi [count expression]
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        if len(args):
            count = t.parseExpression(args)
        else:
            count = 1

        for i in xrange(count):
            t.stepi()

    def do_go(self, line):
        """
        Continue the target tracer.
        -I go icount linear instructions forward (step over style)
        -U go *out* of fcount frames (step out style)
        <until addr> go until explicit address

        Usage: go [-U <fcount> | -I <icount> | <until addr expression>]
        """
        until = None
        icount = None
        fcount = None

        t = self.vdb.getTrace()
        t.requireAttached()
        argv = v_util.splitargs(line)
        try:
            opts,args = getopt(argv, "U:I:")
        except:
            return self.do_help("go")

        for opt,optarg in opts:
            if opt == "-U":
                if len(optarg) == 0: return self.do_help("go")
                fcount = t.parseExpression(optarg)
            elif opt == "-I":
                if len(optarg) == 0: return self.do_help("go")
                icount = t.parseExpression(optarg)

        if icount != None:
            addr = t.getProgramCounter()
            for i in xrange(icount):
                addr += len(self.vdb.arch.makeOpcode(t.readMemory(addr, 16)))
            until = addr
        elif fcount != None:
            until = t.getStackTrace()[fcount][0]
        elif len(args):
            until = t.parseExpression(args[0])

        if not until:
            self.vdb.vprint("Running Tracer (use 'break' to stop it)")
        t.run(until=until)

    def do_server(self, port):
        """
        Start a vtrace server on the local box
        optionally specify the port

        Usage: server [port]
        """
        if port:
            vtrace.port = int(port)

        vtrace.startVtraceServer()

    def do_syms(self, args):
        """
        List symbols and by file.

        Usage: syms [filename]

        With no arguments, syms will self.vdb.vprint(the possible
        libraries with symbol resolvers.  Specify a library
        to see all the symbols for it.
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        if len(args) == 0:
            self.vdb.vprint("Current Library Symbol Resolvers:")
            for libname in t.getNormalizedLibNames():
                self.vdb.vprint("  %s" % libname)
        else:
            self.vdb.vprint("Symbols From %s:" % args)
            for sym in t.getSymsForFile(args):
                self.vdb.vprint("0x%.8x %s" % (sym.value, repr(sym)))

    def do_call(self, string):
        """
        Allows a C-like syntax for calling functions inside
        the target process (from his context).
        Example: call printf("yermom %d", 10)
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        ind = string.index("(")
        if ind == -1:
            raise Exception('ERROR - call wants c-style syntax: ie call printf("yermom")')
        funcaddr = t.parseExpression(string[:ind])

        try:
            args = eval(string[ind:])
        except:
            raise Exception('ERROR - call wants c-style syntax: ie call printf("yermom")')

        self.vdb.vprint("calling %s -> 0x%.8x" % (string[:ind], funcaddr))
        t.call(funcaddr, args)

    def do_bestname(self, args):
        """
        Return the "best name" string for an address.

        Usage: bestname <vtrace expression>
        """
        if len(args) == 0:
            return self.do_help("bestname")
        t = self.vdb.getTrace()
        addr = t.parseExpression(args)
        self.vdb.vprint(self.vdb.bestName(addr))

    def do_EOF(self, string):
        self.vdb.vprint("No.. this is NOT a python interpreter... use quit ;)")

    def do_quit(self,args):
        """
        Quit VDB
        """
        t = self.vdb.getTrace()
        if t.isAttached():
            self.vdb.vprint("Detaching...")
            t.detach()
        self.vdb.vprint("Exiting...")
        sys.exit(0)

    def do_detach(self, args):
        """
        Detach from the current tracer
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        t.detach()

    def do_attach(self, args):
        """
        Attach to a process by PID
        usage: attach <pid>
        """
        pid = int(args)
        self.vdb.vprint("Attaching to ",pid)
        self.vdb.newTrace().attach(pid)

    def emptyline(self):
        self.do_help("")

    def do_sections(self, args):
        self.vdb.vprint("TEMPORARILY BROKEN WHILE I REDO THE BINARY PARSERS")

    def do_bt(self, line):
        """
        Show a stack backtrace for the currently selected thread.

        Usage: bt
        """
        self.vdb.vprint("[   PC   ] [ Frame  ] [ Location ]")
        t = self.vdb.getTrace()
        for frame in t.getStackTrace():
            self.vdb.vprint("0x%.8x 0x%.8x %s" % (frame[0],frame[1],self.vdb.bestName(frame[0])))

    def do_lm(self, args):
        """
        Show the loaded libraries and their base addresses.

        Usage: lm
        """
        t = self.vdb.getTrace()
        bases = t.getMeta("LibraryBases")
        self.vdb.vprint("Loaded Libraries:")
        names = t.getNormalizedLibNames()
        names.sort()
        for libname in names:
            base = bases.get(libname, -1)
            self.vdb.vprint("0x%.8x - %s" % (base, libname))

    def do_bpedit(self, line):
        """
        Manipulcate the python code that will be run for a given
        breakpoint by ID.  (Also the way to view the code).

        Usage: bpedit <id> [optionally new code]
        """
        argv = v_util.splitargs(line)
        if len(argv) == 0:
            return self.do_help("bpedit")
        t = self.vdb.getTrace()
        bpid = int(argv[0])

        if len(argv) == 2:
            t.setBreakpointCode(bpid, argv[1])

        pystr = t.getBreakpointCode(bpid)
        self.vdb.vprint("[%d] Breakpoint code: %s" % (bpid,pystr))

    def do_bp(self, line):
        """
        Show, add,  and enable/disable breakpoints
        USAGE: bp [-d <addr>] [-a <addr>] [-o <addr>] [[-c pycode] <address> ...]
        -C - Clear All Breakpoints
        -c "py code" - Set the breakpoint code to the given python string
        -d <id> - Disable Breakpoint
        -e <id> - Enable Breakpoint
        -r <id> - Remove Breakpoint
        -o <addr> - Create a OneTimeBreak
        -L <libname> - Add bp's to all functions in <libname>
        <address>... - Create Breakpoint

        NOTE: -c adds python code to the breakpoint.  The python code will
            be run with the following objects mapped into it's namespace
            automagically:
                vtrace  - the vtrace package
                trace   - the tracer
                bp      - the breakpoint object
        """
        argv = v_util.splitargs(line)
        opts,args = getopt(argv, "e:d:o:r:L:Cc:")
        t = self.vdb.getTrace()
        pycode = None

        for opt,optarg in opts:
            if "-e" in opt:
                t.setBreakpointEnabled(eval(optarg), True)

            if "-c" in opt:
                pycode = optarg
                test = compile(pycode, "test","exec")

            elif "-r" in opt:
                t.removeBreakpoint(eval(optarg))

            elif "-C" in opt:
                for bp in t.getBreakpoints():
                    t.removeBreakpoint(bp.id)

            elif "-d" in opt:
                t.setBreakpointEnabled(eval(optarg), False)

            elif "-o" in opt:
                t.addBreakpoint(vtrace.OneTimeBreak(None, expression=optarg))

            elif "-L" in opt:
                for sym in t.getSymsForFile(optarg):
                    if sym.stype != vtrace.SYM_FUNCTION:
                        continue
                    try:
                        bp = vtrace.Breakpoint(None, expression="%s.%s" % (optarg,str(sym)))
                        bp.setBreakpointCode(pycode)
                        t.addBreakpoint(bp)
                        self.vdb.vprint("Added: %s" % str(sym))
                    except Exception, msg:
                        self.vdb.vprint("WARNING: %s" % str(msg))

        for arg in args:
            bp = vtrace.Breakpoint(None, expression=arg)
            bp.setBreakpointCode(pycode)
            t.addBreakpoint(bp)

        self.vdb.vprint(" [ Breakpoints ]")
        for bp in t.getBreakpoints():
            self.vdb.vprint("%s enabled: %s" % (bp, bp.isEnabled()))

    def do_fds(self, args):
        """
        Show all the open Handles/FileDescriptors for the target process.
        The "typecode" shown in []'s is the vtrace typecode for that kind of
        fd/handle.

        Usage: fds
        """
        t = self.vdb.getTrace()
        t.requireAttached()
        for id,fdtype,fname in t.getFds():
            self.vdb.vprint("0x%.8x [%d] %s" % (id,fdtype,fname))

    def do_ps(self, args):
        """
        Show the current process list.

        Usage: ps
        """
        trace = self.vdb.getTrace()
        self.vdb.vprint("[Pid]\t[ Name ]")
        for ps in trace.ps():
            self.vdb.vprint("%s\t%s" % (ps[0],ps[1]))

    def do_break(self, args):
        """
        Send the break signal to the target tracer to stop
        it's execution.

        Usage: break
        """
        self.vdb.getTrace().sendBreak()

    def do_meta(self, string):
        """
        Show the metadata for the current trace
        """
        self.vdb.vprint(repr(self.vdb.getTrace().metadata))

class Vdb(v_notif.Notifier, v_util.TraceManager):

    """
    A VDB object is a debugger object which may be used to embed full
    debugger like functionality into a python application.  The
    Vdb object implements many useful utilities and may in most cases
    be treated like a vtrace tracer object due to __getattr__ overrides.
    """

    def __init__(self, trace=None):
        v_notif.Notifier.__init__(self)
        v_util.TraceManager.__init__(self)

        self.stdout = sys.stdout
        self.stderr = sys.stderr

        if trace == None:
            trace = vtrace.getTrace()

        arch = trace.getMeta("Architecture")
        self.arch = envi.getArchModule(arch)

        self.setMode("NonBlocking", True)

        self.manageTrace(trace)
        self.registerNotifier(vtrace.NOTIFY_ALL, self)

        if vtrace.verbose:
            self.registerNotifier(vtrace.NOTIFY_ALL, vtrace.VerboseNotifier())

        self.config = ConfigParser()
        # FIXME search pwd/home/lib/something/
        vdbhome = None
        configs = [os.path.join(vdb.basepath,"configs","vdb.conf"),]
        if sys.platform == "win32":
            homepath = os.getenv("HOMEPATH")
            homedrive = os.getenv("HOMEDRIVE")
            if homedrive != None and homepath != None:
                vdbhome = os.path.join(homedrive,homepath,".vdb")
        else:
            home = os.getenv("HOME")
            if home != None:
                vdbhome = os.path.join(home, ".vdb")

        # The first run...
        if vdbhome != None:
            if not os.path.exists(vdbhome):
                os.mkdir(vdbhome)
                os.mkdir(os.path.join(vdbhome,"modules"))
                cfg = file(configs[0], "r").read()
                file(os.path.join(vdbhome,"vdb.conf"), "w").write(cfg)

            configs.append(os.path.join(vdbhome, "vdb.conf"))

        self.config.read(configs)

        self.formatters = {}
        self.breaktypes = {}
        self.formatnames = []
        self.extcmds = {}

        self.setupSignalLookups()

        self.registerBreaktype("Breakpoint", vtrace.Breakpoint)
        self.registerBreaktype("One Time Break", vtrace.OneTimeBreak)
        self.registerBreaktype("Tracker Breakpoint", vtrace.TrackerBreak)

        fmt.setupFormatters(self)
        self.loadExtensions(trace)
        if vdbhome != None:
            self.loadModules(vdbhome)

    def vprint(self, msg, addnl=True):
        if addnl:
            msg += "\n"
        self.stdout.write(msg)

    def verror(self, msg, addnl=True):
        if addnl:
            msg += "\n"
        self.stderr.write(msg)

    def loadExtensions(self, trace):
        """
        Load up any extensions which are relevant for the current tracer's
        platform/arch/etc...
        """
        v_ext.loadExtensions(self, trace)

    def registerCmdExtension(self, func):
        self.extcmds["do_%s" % func.__name__] = func

    def initFromTrace(self, trace):
        """
        Do the necissary work to initialize vdb from a new tracer.
        """
        pass

    def getTrace(self):
        return self.trace

    def newTrace(self):
        """
        Generate a new trace for this vdb instance.  This fixes many of
        the new attach/exec data munging issues because tracer re-use is
        *very* sketchy...
        """
        oldtrace = self.getTrace()
        if oldtrace.isRunning():
            oldtrace.sendBreak()
        if oldtrace.isAttached():
            oldtrace.detach()

        self.trace = vtrace.getTrace()
        self.manageTrace(self.trace)
        return self.trace

    def notify(self, event, trace):
        # We don't really *need* this yet, but lets keep it around
        pass

    def loadModules(self, vdbdir):
        """
        Modules placed in HOME/.vdb/modules will be loaded
        run with a reference to the vdb instance on load.
        """
        mdir = os.path.join(vdbdir, "modules")
        self.vprint("Loading VDB Modules: ")
        for name in os.listdir(mdir):
            if not name.endswith(".py"):
                continue
            try:
                self.script(os.path.join(mdir,name))
                self.vprint(name+" ")
            except Exception,msg:
                self.verror("ERROR: %s: %s" % (name,msg))
        self.vprint("... Complete")

    def delConfig(self, section, option):
        """
        Delete a config option (use with extreeme caution).
        """
        self.config.remove_option(section, option)

    def setConfig(self, section, option, value):
        """
        Set a vdb config option.
        """
        self.config.set(section, option, value)

    def getConfigSection(self, section):
        """
        Get a python dictionary of a whole section of the config.
        """
        ret = {}
        for opt in self.config.options(section):
            ret[opt] = self.config.get(section,opt)
        return ret

    def getConfig(self, section, option, default):
        """
        Get a config option from a section as a string.
        """
        if not self.config.has_option(section, option):
            return default
        return self.config.get(section,option)

    def getConfigInt(self, section, option, default):
        """
        Get a config option from a section as an int
        """
        if not self.config.has_option(section, option):
            return default
        return self.config.getint(section,option)

    def getConfigBool(self, section, option, default):
        """
        Get a config option from a section as a boolean
        """
        if not self.config.has_option(section, option):
            return default
        return self.config.getbool(section,option)

    def registerBreaktype(self, name, cls):
        """
        Register a breakpoint type for use in the breakpoint
        management window.  cls specifies the class, whose constructor
        *must* take address and expression just like the base Breakpoint
        (ie. Breakpoint(<address>, expression=<expression>)).
        """
        self.breaktypes[name] = cls

    def getBreakTypes(self):
        """
        Return the list of the currently register
        breakpoint types
        """
        return self.breaktypes.keys()

    def constructBreakpoint(self, typename, expression, enabled=True):
        """
        Construct a breakpoint of the type associated with the given
        typename and for the address in "expression" and return it
        """
        cls = self.breaktypes.get(typename, None)
        if not cls:
            raise Expression("Unknown Breakpoint Type: %s" % typename)
        bp = cls(None, expression=expression)
        bp.setEnabled(enabled)
        return bp

    def vmemProtFormat(self, mask):
        """
        Return a printable repr for the protections specified
        in mask
        """
        plist = ['-','-','-','-']
        if mask & vtrace.MM_SHARED:
            plist[0] = 's'
        if mask & vtrace.MM_READ:
            plist[1] = 'r'
        if mask & vtrace.MM_WRITE:
            plist[2] = 'w'
        if mask & vtrace.MM_EXEC:
            plist[3] = 'x'

        return string.join(plist,"")

    def registerFormatter(self, name, formater):
        """
        A "formatter"
        """
        self.formatnames.append(name)
        self.formatters[name] = formater

    def getFormatNames(self):
        return self.formatnames

    def doFormat(self, name, address, memory):
        formater = self.formatters.get(name,None)
        if not formater:
            raise Exception("ERROR - Invalid formater: %s" % name)
        return formater.format(address,memory)

    def setupSignalLookups(self):
        self.siglookup = VdbLookup()

        self.siglookup[0] = "None"

        for name in dir(signal):
            if name[:3] == "SIG" and "_" not in name:
                self.siglookup[name] = eval("signal.%s"%name)
        
    def getSignal(self, sig):
        """
        If given an int, return the name, for a name, return the int ;)
        """
        return self.siglookup.get(sig,None)

    def parseExpression(self, exprstr):
        return self.trace.parseExpression(exprstr)

    def bestName(self, address):
        """
        Return a string representing the best known name for
        the given address
        """
        if not address:
            return "NULL"

        match = self.trace.getSymByAddr(address)
        if match != None:
            if long(match) == address:
                return repr(match)
            else:
                return "%s+%d" % (repr(match), address - long(match))

        map = self.trace.getMap(address)
        if map:
            return map[3]

        return "Who knows?!?!!?"

    def script(self, filename, args=[]):
        """
        Execute a vdb script.

        This script has 4 references in it's builtin locals:
        trace - The trace object
        vdb - The vdb instance
        vtrace - The vtrace package
        args - User specified arguments
        """
        text = file(filename).read()
        self.scriptstring(text, filename, args)

    def scriptstring(self, script, filename, args=[]):
        """
        Do the actual compile and execute for the script data
        contained in script which was read from filename.
        """
        local = {"vdb":self, "vtrace":vtrace,"args":args}
        local["trace"] = self.trace
        if self.trace.isAttached() and not self.trace.isRunning():
            local.update(self.trace.getRegisters())
        cobj = compile(script, filename, "exec")
        sthr = ScriptThread(cobj, local)
        sthr.start()

