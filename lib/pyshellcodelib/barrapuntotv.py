#!/usr/bin/python

from pyshellcodelib import PyEgg

a = PyEgg("linux")
gen = a.generator

# Ejecutamos setuid(0)
a.buf += gen.xorEax()
a.buf += gen.xorEbx()
a.buf += gen.call("setuid")

# Saltamos los NOPs que generamos a continuacion
a.buf += gen.jmpTo(3)
# La generacion NOPs es aleatoria tal y como usted podria esperar
a.buf += gen.nop(2)

# Ahora simplemente salimos devolviendo 0
a.buf += gen.xorEax()
a.buf += gen.call("exit")
a.alphaEncode()

sc = a.getShellcode()

print "#include <stdio.h>"
print
print 'char *sc="%s";' % sc
print
print "int main(void) {"
print "\t((void(*)())sc)();"
print "}"
print

