#!/usr/bin/python

import struct
import binascii
import macosxsyscalls as syscalls

from base import *

class CBaseShellcode(CBaseStub):
    
    localSyscalls = syscalls
