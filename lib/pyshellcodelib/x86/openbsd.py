#!/usr/bin/python

import struct
import binascii
import openbsdsyscalls as syscalls

from base import *

class CBaseShellcode(CBaseStub):
    
    localSyscalls = syscalls
