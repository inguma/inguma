#!/usr/bin/python

##      CRasc.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os
import sys
from lib.libexploit import CIngumaModule
from lib.libradare import *

name = "rasc"
brief_description = "A Radare Shellcode Wrapper"
type = "rce"

class CRasc(CIngumaModule):

    format = "C"
    cmd = ""
    host = ""
    port = ""
    shellcode = ""

    def showHelp(self):
        print 
        print "Inguma's Rasc Wrapper"
        print "---------------------"
        print
        print "list                         List Shellcodes"
        print "gen                          Generate selected Shellcode"
        print "help                         Show this help"
        print "exit                         Exit from Rasc"
        print
        print "Shellcode creation Options"
        print "--------------------------"
        print
        print "format                       <C|string|hex|>"
        print "cmd                          Command to execute on execves"
        print "host                         Host to connect"
        print "port                         Port to listen or connect"
        print "shellcode                    Use command 'list'"

    def run(self):
        while 1:
            try:
                res = raw_input("RASC> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "list":
                r = Radare()
                r.rasc_list()
            elif words[0].lower() == "gen":
                r = Radare()
                r.rasc_gen(self.shellcode, self.cmd, self.format, self.port, self.host)
            elif words[0].lower() == "shellcode":
                self.shellcode = words[1]
            elif words[0].lower() == "format":
                self.format = words[1]
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() == "quit" or words[0].lower() == "exit":
                break
            else:
                print "Unknown command or options '" + str(res) + "'"

        return True

    def printSummary(self):
        pass
