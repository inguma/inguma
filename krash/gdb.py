#!/usr/bin/env python

"""
GDB Python wrapper v0.1
Copyright (c) 2007, 2008 Joxean Koret

License GPLv2
"""

import os
import sys
import time
import pexpect

def getRegisterValue(c, register, format = "/s"):
    """ Get the value of one register in the format specified by 'format' """
    c.sendline("x %s %s" % (format, register))
    c.expect("(gdb)")

    # Ignore the blank line
    c.readline()
    # Return the value
    return c.readline().strip("\r\n")

    print "Current instruction:", instruction

def gdbTrace(pid, funcs):
    # Execute GDB passing the command line we construct
    c = pexpect.spawn ('gdb attach %d' % int(pid))

    # Wait for the (gdb) prompt
    c.expect ('(gdb)')

    # Wait a bit
    time.sleep(1)
    
    for func in funcs:
        c.sendline("b %s" % func)
    #c.sendline("b kqlsrcsql")
    
    try:
        while 1:
            c.expect("Breakpoint .*")
            
            print
            # Get the data stored at the register's addresses
            strEax = getRegisterValue(c, "$eax")
            strEcx = getRegisterValue(c, "$ecx")
            strEdx = getRegisterValue(c, "$edx")
            strEbx = getRegisterValue(c, "$ebx")
            strEsp = getRegisterValue(c, "$esp")
            strEbp = getRegisterValue(c, "$ebp")
            strEsi = getRegisterValue(c, "$esi")
            strEdi = getRegisterValue(c, "$edi")
            strEip = getRegisterValue(c, "$eip")

            # Print the string value of these
            print "EAX", strEax
            print "ECX", strEcx
            print "EDX", strEdx
            print "EBX", strEbx
            print "ESP", strEsp
            print "EBP", strEbp
            print "ESI", strEsi
            print "EDI", strEdi
            print "EIP", strEip
    
            c.sendline("cont") # Continue
    except KeyboardInterrupt:
        c.interact()

def gdbRun(cmdline, run = True):
    print "Running:", 'gdb ' + cmdline

    # Execute GDB passing the command line we construct
    c = pexpect.spawn ('gdb ' + cmdline)
    # Wait for the (gdb) prompt
    c.expect ('(gdb)')

    # Wait a bit
    time.sleep(1)

    # Should we execute the program?
    if run:
        c.sendline('r')
    else:
        # Or are we attached and we must [c]ontinue execution?
        c.sendline('c')
        print "Continuing..."

    # Set a very high timeout
    c.timeout = 300000
    
    # Uncomment the following line to see what occurs, only for debugging
    #c.interact()
    
    # Wait for a signal...
    ret = c.expect('Program received signal ')
    print "Program crashes, inspecting it ... "

    # The first lines are the prompt and uninteresting messages
    msg = c.readline()
    msg2 = c.readline()
    print msg.strip("\r").strip("\n")
    print msg2.strip("\r").strip("\n")

    # Get register's values
    c.sendline("i r")
    # Wait for the prompt
    c.expect("(gdb)")
    
    # Ignore the line as is a blank line
    c.readline()
    
    # Read register's values
    eax = c.readline().strip("\r\n")
    ecx = c.readline().strip("\r\n")
    edx = c.readline().strip("\r\n")
    ebx = c.readline().strip("\r\n")
    esp = c.readline().strip("\r\n")
    ebp = c.readline().strip("\r\n")
    esi = c.readline().strip("\r\n")
    edi = c.readline().strip("\r\n")
    eip = c.readline().strip("\r\n")

    # Print these
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

    # Get the current instruction (AT&T syntax)
    # For Intel syntax, run first set disassembly-flavour intel
    instruction = getRegisterValue(c, "$pc", "/i")
    print "Current instruction:", instruction
    print

    # Get the data stored at the register's addresses
    strEax = getRegisterValue(c, "$eax")
    strEcx = getRegisterValue(c, "$ecx")
    strEdx = getRegisterValue(c, "$edx")
    strEbx = getRegisterValue(c, "$ebx")
    strEsp = getRegisterValue(c, "$esp")
    strEbp = getRegisterValue(c, "$ebp")
    strEsi = getRegisterValue(c, "$esi")
    strEdi = getRegisterValue(c, "$edi")
    strEip = getRegisterValue(c, "$eip")

    # Print the string value of these
    print "EAX", strEax
    print "ECX", strEcx
    print "EDX", strEdx
    print "EBX", strEbx
    print "ESP", strEsp
    print "EBP", strEbp
    print "ESI", strEsi
    print "EDI", strEdi
    print "EIP", strEip

if __name__ == "__main__":
    # Did we receive a pid?
    if len(sys.argv) == 2:
        #gdbRun("attach " + sys.argv[1], False)
        gdbTrace(sys.argv[1], ["strcpy", "strcat"])
    else:
        # Show usage
        print "Usage: %s <pid>" % sys.argv[0]


