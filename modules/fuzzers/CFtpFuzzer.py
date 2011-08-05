#!/usr/bin/python

##      CFtpFuzzer.py
#       
#       Copyright 2010 Joxean Koret <joxeankoret@yahoo.es>
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

import sys
import time
import socket

from lib import libfuzz
from lib.libftp import FTP_COMMANDS
from lib.module import CIngumaModule

name = "ftpfuzz"
brief_description = "A simple FTP fuzzer"
type = "fuzzer"

class CFtpFuzzer(CIngumaModule):
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    interactive = True
    user = ""
    password = ""
    ssl = False

    def help(self):
        print "target  = <IP address>"
        print "port    = <port>"
        print "timeout = <timeout>"

    def fuzzCallback(self, data, idx):
        try:
            if self.ssl:
                ssl = True
            else:
                ssl = False
            
            if len(data) < 10:
                return

            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(self.port)))
            print "Banner %s" % s.recv(4096)

            cmd = data.split(" ")[0]
            if cmd.lower() not in ["user", "pass"]:
                print "Logging in..."
                s.send("USER %s\r\n" % self.user)
                print s.recv(1024)
                s.send("PASS %s\r\n" % self.password)
                x = s.recv(4096)
                
                if x.find("230") == -1 and x.find("530") == -1:
                    print "Cannot login. Exiting..."
                    return

                print s.recv(4096)
            else:
                s.close()
                return
            
            print "Sending\n%s" % repr(data)
            s.sendall(data + "\r\n")
            print "Received\n%s" % repr(s.recv(4096))
        
            s.close()
        except:
            print "Exception", sys.exc_info()[1]
            try:
                s.close()
            except:
                pass
        
        if self.waitTime > 0:
            time.sleep(self.waitTime)

    def fuzz(self):
        cmd = ""
        
        if self.interactive:
            try:
                idx = raw_input("Index?: ")
                idx = int(idx) + 2
            except KeyboardInterrupt:
                print "Aborted."
                return
        else:
            idx = 0

        for cmd in FTP_COMMANDS[idx:]:
            print "Fuzzing cmd %s" % cmd
            libfuzz.fuzzCallback(self.fuzzCallback, cmd + " a", 1)

        print
        print "Fuzzing finished. Any luck?"
        print

    def run(self):        
        
        if self.port == "" or self.port == 0:
            self.port = 21
        
        if self.user == "" or self.user == None:
            self.user = "anonymous"
        
        if self.password == "" or self.password == None:
            self.password = "anon@test.com"

        self.fuzz()
        return True
