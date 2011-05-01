
import getopt
import vtrace
import vtrace.tools.win32heap as win32heap
import vtrace.util as v_util

def peb(vdb, line):
    """
    Print the PEB

    Usage: peb
    """
    t = vdb.getTrace()
    t.requireAttached()
    pebaddr = t.getMeta("PEB")
    peb = t.getStruct("win32.PEB", pebaddr)
    vdb.vprint(repr(peb))

def regkeys(vdb, line):
    """
    Show all the registry keys the target process currently has open.

    Usage: regkeys
    """
    t = vdb.getTrace()
    t.requireAttached()
    vdb.vprint("\nOpen Registry Keys:\n")
    for fd,ftype,fname in t.getFds():
        if ftype == vtrace.FD_REGKEY:
            vdb.vprint("\t%s" % fname)
    vdb.vprint("")

def einfo(vdb, line):
    """
    Show all the current exception information.
    Usage: einfo
    """
    t = vdb.getTrace()
    exc = t.getMeta("Win32Event", None)
    if exc == None:
        vdb.vprint("No Exception Information Found")
    ecode = exc.get("ExceptionCode", 0)
    eaddr = exc.get("ExceptionAddress",0)
    chance = 2
    if exc.get("FirstChance", False):
        chance = 1
    einfo = exc.get("ExceptionInformation", [])
    #FIXME get extended infoz
    #FIXME unify with cli thing
    vdb.vprint("Win32 Exception 0x%.8x at 0x%.8x (%d chance)" % (ecode, eaddr, chance))
    vdb.vprint("Exception Information: %s" % " ".join([hex(i) for i in einfo]))

def seh(vdb, line):
    """
    Walk and print the SEH chain for the current (or specified) thread.

    Usage: seh [threadid]
    """
    t = vdb.getTrace()
    if len(line) == 0:
        tid = t.getMeta("ThreadId")
    else:
        tid = int(line)
    tinfo = t.getThreads().get(tid, None)
    if tinfo == None:
        vdb.vprint("Unknown Thread Id: %d" % tid)
        return
    teb = t.getStruct("win32.TEB", tinfo)
    addr = long(teb.TIB.ExceptionList)
    vdb.vprint("REG        HANDLER")
    while addr != 0xffffffff:
        #FIXME print out which frame these are in
        er = t.getStruct("win32.EXCEPTION_REGISTRATION", addr)
        vdb.vprint("0x%.8x 0x%.8x" % (addr, er.handler))
        addr = long(er.prev)

def heaps(vdb, line):
    """
    Show Win32 Heap Information.

    Usage: heaps [-F <heapaddr>] [-C <address>] [-L <segmentaddr>]
    -F <heapaddr> print the freelist for the heap
    -C <address>  Find and print the heap chunk containing <address>
    -L <segmentaddr> Print the chunks for the given heap segment
    (no options lists heaps and segments)
    """
    t = vdb.getTrace()
    t.requireAttached()

    argv = v_util.splitargs(line)
    freelist_heap = None
    chunkfind_addr = None
    chunklist_seg = None
    try:
        opts,args = getopt.getopt(argv, "F:C:L:")
    except Exception, e:
        vdb.vprint("Unrecognized Options in: %s" % line)

    for opt,optarg in opts:
        if opt == "-F":
            freelist_heap = t.parseExpression(optarg)
        elif opt == "-C":
            chunkfind_addr = t.parseExpression(optarg)
        elif opt == "-L":
            chunklist_seg = t.parseExpression(optarg)

    if freelist_heap != None:
        print "NOT YET"

    elif chunkfind_addr != None:
        heap,seg,chunk = win32heap.getHeapSegChunk(t, chunkfind_addr)
        vdb.vprint("Address  0x%.8x found in:" % (chunkfind_addr,))
        vdb.vprint("Heap:    0x%.8x" % (heap.address))
        vdb.vprint("Segment: 0x%.8x" % (seg.address))
        vdb.vprint("Chunk:   0x%.8x (%d) FLAGS: %s" % (chunk.address, len(chunk),chunk.reprFlags()))

    elif chunklist_seg != None:

        for heap in win32heap.getHeaps(t):
            for seg in heap.getSegments():
                if chunklist_seg == seg.address:
                    vdb.vprint("Chunks for segment at 0x%.8x (X == in use)" % chunklist_seg)
                    for chunk in seg.getChunks():
                        c = " "
                        if chunk.isBusy():
                            c = "X"
                        vdb.vprint("0x%.8x %s (%d)" % (chunk.address,c,len(chunk)))
                    return

        vdb.vprint("Segment 0x%.8x not found!" % chunklist_seg)

    else:
        vdb.vprint("Heap\t\tSegment")
        for heap in win32heap.getHeaps(t):
            segs = heap.getSegments()
            for s in segs:
                vdb.vprint("0x%.8x\t0x%.8x" % (heap.address, s.address))

# The necissary module extension function
def vdbExtension(vdb, trace):
    vdb.registerCmdExtension(peb)
    vdb.registerCmdExtension(einfo)
    vdb.registerCmdExtension(heaps)
    vdb.registerCmdExtension(regkeys)
    vdb.registerCmdExtension(seh)

