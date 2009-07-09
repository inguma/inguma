#!/usr/bin/python

"""
FTP Fuzzing Tool

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

import os
import sys
import time
import socket

from module.fuzz.data import CFuzzingData

class CFuzzer:

    username = "anonymous"
    password = "test"
    target = None
    port = 21

    fuzzUsername = False
    fuzzPassword = False

    waitTime = 0.1
    debugLevel = 0
    timeout = 50

    binary = False
    strings = True
    numbers = False

    commands = {}

    socket = None
    path = "ftp" + os.sep

    data = CFuzzingData()

    def __init__(self, target = None, port = None, path = None):

        if target:
            self.target = target
        
        if port:
            self.port = int(port)
        
        if path:
            self.readDict(path)
        else:
            self.readDict()

    def readDict(self, path = None):
    
        if not path:
            f = open(self.path + "commands", "r")
        else:
            f = open(self.path + "commands", "r")
        i = 0

        while 1:
            i += 1
            line = f.readline()

            if not line:
                break

            line = line.strip("\r")
            line = line.strip("\n")

            self.commands[i] = line
        
        f.close()

    def debugPrint(self, mdata):
        if self.debugLevel > 0:
            print mdata

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.target, self.port))
        socket.setdefaulttimeout(self.timeout)

    def checkHost(self):
        try:
            self.socket = None
            self.connect()
            self.login()
            
            return False
        except:
            return True

    def login(self):
        if self.socket is None:
        
            try:
                self.connect()
            except:
                return self.checkHost()

        s = self.socket
        mdata = s.recv(1024)

        self.debugPrint("BANNER " + mdata)
        self.debugPrint("Logging in ... ")
        self.debugPrint("USER " + self.username)
        s.send("USER " + self.username + "\r\n")

        res = s.recv(1024)
        self.debugPrint(res)

        self.debugPrint("PASS " + self.password)
        s.send("PASS " + self.password + "\r\n")
        res = s.recv(1024)
        self.debugPrint("Received " + res)

    def runTest(self, cmd, testData, size):
        try:
            mdata = ""
            if self.socket is None:
                self.login()

            s  = self.socket

            try:
                isnum = True
                aux = float(testData)
            except:
                isnum = False

            if not isnum:
                toSend = cmd + self.data.getStringWithSize(testData, size)
            else:
                toSend = cmd + testData

            s.send(toSend + "\r\n")

            mdata = s.recv(1024)
            self.debugPrint(mdata)
            if mdata.find("530") > -1:
                self.checkHost()
            return False
        except:
            print
            print sys.exc_info()[1]
            return self.checkHost()

    def run(self):
        
        commandList = {}
        objData = self.data

        if self.strings:
            commandList.update(objData.strings)

        if self.binary:
            commandList.update(objData.binary)

        if self.numbers:
            commandList.update(objData.numbers)
        
        for cmd in self.commands:
        
            if cmd == 1 and self.fuzzUsername == False:
                continue
            elif cmd == 2 and self.fuzzPassword == False:
                self.login()
                continue

            sys.stdout.write("\b"*256 + "Fuzzing command " + str(cmd) +": " + repr(self.commands[cmd]) + " "*30)
            sys.stdout.flush()

            try:
                if cmd > 3:
                    self.connect()
            except:
                print "Error connecting to server:",sys.exc_info()[1]
                return

            for test in commandList:
                for size in objData.sizes:
                    time.sleep(self.waitTime)
                    #print " Size",objData.sizes[size]," bytes"
                    sys.stdout.write("\b"  * 256 + "Fuzzing cmd " + self.commands[cmd] + "Data " + commandList[test]  + ". Size " + str(objData.sizes[size]) + " bytes" + " "*30)
                    sys.stdout.flush()

                    if self.runTest(self.commands[cmd], commandList[test], objData.sizes[size]):
                        print
                        print "Service crashed with packet",self.commands[cmd], commandList[test], objData.sizes[size]
                        return
            
            print

        print "Fuzzing session finished with no luck :("

def main():

    objFuzzer = CFuzzer("192.168.1.14", 21)
    objFuzzer.debugLevel = 0
    objFuzzer.timeout = 1
    objFuzzer.binary = False
    objFuzzer.strings = True
    objFuzzer.numbers = False
    objFuzzer.username = "test"
    objFuzzer.password = "test"
    objFuzzer.run()

if __name__ == "__main__":
    main()
