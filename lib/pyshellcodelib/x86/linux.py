#!/usr/bin/python

import struct
import binascii
import linuxsyscalls as syscalls

from base import *

class CBaseShellcode(CBaseStub):
    
    localSyscalls = syscalls
