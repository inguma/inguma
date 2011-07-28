#!/usr/bin/python

import os
import sys
import time
import urllib
import socket
import thread
import pexpect
import StringIO

verbose = False

separators = [" ", ".", "/", "&", "=", "?", ":", "\r", "\n", "\x00", "@", "-", "*" , "\\", "(", ")", "[", "]", "!", "|",
		"#", "$",  "<", ">", ";", "%"]
ignorechars = [" ", "<", ">", '"', "\r", "\n", "?", "&", "=", "%"]

lastError = ""

lineMode = False
sslMode = False
urlMode = False

numthreads = 0
maxthreads = 1

health = True
lastPacket = None
startCommand = None
webMode = False

def getRegisterValue(c, register, format = "/s"):
    c.sendline("x %s %s" % (format, register))
    c.expect("(gdb)")
    
    c.readline()
    return c.readline().strip("\r\n")

    print "Current instruction:", instruction

def gdbRun(cmdline, run = True):
    c = pexpect.spawn ('gdb ' + cmdline)
    c.expect ('(gdb)')

    time.sleep(1)

    if run:
        c.sendline('r')
    else:
        c.sendline('c')
    c.timeout = 30000
    #c.interact()
    ret = c.expect('Program received signal ')

    msg = c.readline()
    msg2 = c.readline()
    print msg.strip("\r").strip("\n")
    print msg2.strip("\r").strip("\n")
    
    c.sendline("i r")
    c.expect("(gdb)")
    
    c.readline()
    eax = c.readline().strip("\r\n")
    ecx = c.readline().strip("\r\n")
    edx = c.readline().strip("\r\n")
    ebx = c.readline().strip("\r\n")
    esp = c.readline().strip("\r\n")
    ebp = c.readline().strip("\r\n")
    esi = c.readline().strip("\r\n")
    edi = c.readline().strip("\r\n")
    eip = c.readline().strip("\r\n")

    print eax
    print ecx
    print edx
    print ebx
    print esp
    print ebp
    print esi
    print edi
    print eip
    print
    
    instruction = getRegisterValue(c, "$pc", "/i")
    print "Current instruction:", instruction
    print

    strEax = getRegisterValue(c, "$eax")
    strEcx = getRegisterValue(c, "$ecx")
    strEdx = getRegisterValue(c, "$edx")
    strEbx = getRegisterValue(c, "$ebx")
    strEsp = getRegisterValue(c, "$esp")
    strEbp = getRegisterValue(c, "$ebp")
    strEsi = getRegisterValue(c, "$esi")
    strEdi = getRegisterValue(c, "$edi")
    strEip = getRegisterValue(c, "$eip")
    
    print "EAX", strEax
    print "ECX", strEcx
    print "EDX", strEdx
    print "EBX", strEbx
    print "ESP", strEsp
    print "EBP", strEbp
    print "ESI", strEsi
    print "EDI", strEdi
    print "EIP", strEip

def tokenizePacket(pkt):

    ret = []
    tmp = ""

    for x in pkt:
        if x in separators:
            if tmp != "":
                ret.append(tmp)
            ret.append(x)
            tmp = ""
        else:
            tmp += x

    if tmp != "":
        ret.append(tmp)

    return ret

def token2str(tkn):
    x = ""

    for a in tkn:
        x += str(a)

    return x

def sendssl(pkt, host, port):

    global verbose
    global lastError
    global lineMode
    global sslMode
    global numthreads
    global webMode

    numthreads += 1
    verbose = True

    try:
        socket.setdefaulttimeout(3000)
        ssl_sock = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if verbose:
            print "Connecting to %s:%d" % (host, int(port))
        else:
            if verbose:
                sys.stdout.write(".")
                sys.stdout.flush()

        s.connect((host, int(port)))
        ssl_sock = socket.ssl(s)

        if verbose or webMode:
            print "Request (size %d):" % (len(pkt))
            
            if not webMode:
                print repr(pkt[0:1024])
                print 

        if not lineMode:
            ssl_sock.send(pkt)
            res = ssl_sock.recv(128)

            if verbose:
                if not webmode:
                    print "Response:"
                    print repr(res)
                else:
                    if res.find("500") > -1:
                        print "***Interesting response"
                        print repr(res)
        else:
            for line in StringIO.StringIO(pkt):
                ssl_sock.send(line)
                res = ssl_sock.recv(128)

                if verbose:
                    print "Response:"
                    print repr(res)
    except:
        if lastError != str(sys.exc_info()[1]):
            if verbose:
                print "Exception:"
                lastError = str(sys.exc_info()[1])
                print lastError

        if sys.exc_info()[1][0] == 111:
            print "*** Found a bug?"
            print "Waiting for a while...."
            
            if maxthreads == 1:
                time.sleep(1)

                try:
                    raw_input("Continue (Ctrl+C or Enter)?")
                except:
                    print "Ok. Aborted."
                    sys.exit(0)

    numthreads -= 1
    del ssl_sock
    s.close()

    if os.getenv("WAIT_TIME") is not None:
        time.sleep(float(os.getenv("WAIT_TIME")))

def send(pkt, host, port):

    global verbose
    global lastError
    global lineMode
    global sslMode
    global numthreads

    numthreads += 1

    #raw_input("Continue?")

    try:
        socket.setdefaulttimeout(0.3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if verbose:
            print "Connecting to %s:%d" % (host, int(port))
        else:
            if verbose:
                sys.stdout.write(".")
                sys.stdout.flush()
        s.connect((host, int(port)))

        if verbose and not lineMode:
            print "Request (size %d):" % (len(pkt))
            print repr(pkt[0:1024])
            print 

        if not lineMode:
            s.send(pkt)
            res = s.recv(128)
            if verbose:
                print "Response:"
                print repr(res)
        else:
            for line in StringIO.StringIO(pkt):
                if verbose:
                    print "Request (size %d):" % (len(line))
                    print repr(line[0:4096])

                res = s.recv(128)
    
                if verbose:
                    print "Response:"
                    print repr(res)
    except:
        if lastError != str(sys.exc_info()[1]):
            if verbose:
                print "Exception:"
                lastError = str(sys.exc_info()[1])
                print lastError

        if sys.exc_info()[1][0] == 111:
            print "*** Found a bug?"
            
            if maxthreads > 1:
                print "Waiting for a while...."
                time.sleep(1)
                try:
                    raw_input("Continue (Ctrl+C or Enter)?")
                except:
                    print "Ok. Aborted."
                    sys.exit(0)

    numthreads -= 1
    s.close()

    if os.getenv("WAIT_TIME") is not None:
        time.sleep(float(os.getenv("WAIT_TIME")))

def checkAlive(host, port, times = 0):

    global lastPacket
    global startCommand

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.close()
    except:
        if times == 0:
            time.sleep(0.1)
            checkAlive(host, port, times = 1)
        else:
            if lastPacket is None:
                print "Host appears to be down..."
                print "Startup it previous to try kr4$h1ng something ;)"
                #sys.exit(0)

            print "HEALTH CHECK: Could not connect to host %s at %d" % (host, int(port))
            print "Host may be dead (Yippie!)"
            print
            print "The last sended packet is the following (truncated at byte 2048):"
            print "~"*80
            print repr(lastPacket)[0:2048]
            print "~"*80
            print
            print "-"*80
            #raise Exception("*** Found a bug?\r\n" + "-"*80)
        
            if startCommand:
                print "[+] Starting up target program ..."
                print "[+] Running: %s " % startCommand
                os.system(startCommand)
                time.sleep(1)
                f = file("/var/TimesTen/tt70/timestend.pid", "r")
                pid = f.read().strip("\r\n")
                print "El PID es %s" % pid
                f.close()
                cmd = "/home/joxean/proyectos/tool/krash/gdb.py %s >> audit.timesten.70.txt&" % pid
                print "Running %s " % cmd
                os.system(cmd)
                print "Waiting GDB to end reading the binary ... "
                time.sleep(3)

def sendwrapper(pkt, host, port):

    global sslMode
    global maxthreads
    global numthreads
    global verbose
    global lastPacket
    global health

    if health:
        checkAlive(host, port)

    if maxthreads > 1 and verbose:
        print "Using %d thread(s) out of a maximun of %d thread(s)" % (numthreads, maxthreads)

    lastPacket = pkt

    while numthreads > maxthreads:
        if verbose:
            print "Waiting for child threads to end..."

        time.sleep(0.1)

    if maxthreads == 1:
        if not sslMode:
            send(pkt, host, port)
        else:
            sendssl(pkt, host, port)
    else:
        if numthreads >= maxthreads:
            time.sleep(0.5)

        if not sslMode:
            thread.start_new_thread(send, (pkt, host, port))
        else:
            thread.start_new_thread(sendssl, (pkt, host, port))

def fuzz(basePacket, host, port, idx):

    global urlMode

    mtokens = tokenizePacket(basePacket)

    # Fuzzing data
    strings = ("A", 
                "%s", "%n", "%x", "%d", 
                "/.", "\\\\", "C:\\", "../", "..\\")

    numbers = (-2, -1, 0, 1, 2147483647, 4294967294, -2147483647, -4294967294)
    sizes   = (1, 4, 100, 500, 2000, 5000, 9000, 10000)

    tokens = mtokens
    j = 0

    for i in range(int(idx), len(mtokens)):
        tokens = tokenizePacket(basePacket)
        tmp = ""

        if tokens[i] in separators:
            if tokens[i] in ignorechars:
                continue

        isVar = False

        if urlMode:
            if tokens[i-1] == "&":
                isVar = True
                continue
            else:
                isVar = False

        x = 0
        for num in numbers:
            x+= 1
            if x < 0:
                continue
                
            if verbose:
                print "Fuzzing var %d:%d" % (i, x)
            tmp = tokens
            tmp[i] = num

            sendwrapper(token2str(tmp), host, port)
            j += 1

        for size in sizes:

            for stmt in strings:
                x += 1
                if x < 0:
                    continue
                
                if verbose:
                    print "Fuzzing var %d:%d:%d" % (i, x, size)
                tmp = tokens
                tmp[i] = stmt*size
                if not isVar:
                    sendwrapper(token2str(tmp), host, port)
                else:
                    sendwrapper(urllib.quote(token2str(tmp)), host, port)

                j += 1

            for char in range(0, 255):
            
                if chr(char) in ["&", "="]:
                    continue
                x += 1
                if x < 0:
                    continue

                if verbose:
                    print "Fuzzing var %d:%d:%d" % (i, x, size)

                tmp = tokens
                tmp[i] = chr(char)*size
                if not isVar:
                    sendwrapper(token2str(tmp), host, port)
                else:
                    sendwrapper(urllib.quote(token2str(tmp)), host, port)
                j += 1

def usage():
    print "Krash Token Fuzzer v0.1"
    print "Copyright (c) 2007 Joxean Koret"
    print
    print "Usage:", sys.argv[0], "<pkt file> <host> <port> <start index> <verbose> [flags]"
    print
    print "Flags:"
    print
    print "-L           Line mode, send one line at a time"
    print "-S           SSL mode, send data over an SSL channel"
    print "-U           URL mode, encode arguments as in HTTP requests"
    print "-H           Disable healthy checks to gain speed"
    print
    print "Environment Variables:"
    print
    print "WAIT_TIME    Sleep the specified time between packets"
    print "USE_THREADS  How many threads the fuzzer will use? Default is '0'"
    print
    print "Example:", sys.argv[0], "audits/web/packet.http 192.168.1.10 6680 0"
    print

def main():
    global verbose
    global lineMode
    global urlMode
    global maxthreads
    global health
    global startCommand
    global webMode

    startCommand = None # "/opt/TimesTen/tt70/startup/tt_tt70 start"
    if len(sys.argv) < 5:
        usage()
        sys.exit(0)
    else:
        if len(sys.argv) == 6:
            if sys.argv[5][0] != "-":
                verbose = True
        else:
            verbose = False

        for arg in sys.argv[6:]:
            if arg.upper() == "-L" or arg.upper() == "--LINE":
                lineMode = True
                print "DEBUG: Will fuzz in line mode"
            elif arg.upper() == "-S" or arg.upper() == "--SSL":
                sslMode = True
                print "DEBUG: Will fuzz in ssl mode"
            elif arg.upper() == "-U" or arg.upper() == "--URL":
                urlMode = True
                print "DEBUG: Will fuzz in url mode"
            elif arg.upper() == "-H" or arg.upper() == "--HEALTH":
                health = False
                print "DEBUG: Healthy checks are disabled"
            elif arg.upper() == "-W" or arg.upper() == "--WEB":
                webMode = True
                print "DEBUG: Webmode enabled"
            else:
                print "Unknown flag %s" % arg
                print
                usage()
                sys.exit(0)

        if os.getenv("USE_THREADS") is not None and os.getenv("USE_THREADS") != "":
            """
            Using it will be very hard to identify the bug which makes crashing the server but,
            anyway, it may be usefull (speed!).
            
            If you want to audit a product using threads you should do the following:
            
                1) Launch the fuzzer with threads (i.e., 256) to see if it crashes
                2) If you found a crash relaunch the fuzzer using a single thread (unset USE_THREADS)

            Using threads I found bugs in ~4 seconds that, in any other case, will took several
            minutes.
            """
            maxthreads = int(os.getenv("USE_THREADS"))
            print "DEBUG: Will use %d thread(s)" % maxthreads

        fuzz(file(sys.argv[1], "r").read(), sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()
