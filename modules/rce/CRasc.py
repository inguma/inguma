#!/usr/bin/python
"""
Module Radare Shellcodes for Inguma
Copyright (c) 2008 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

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
