#!/usr/bin/python

##      CTnsCmd.py
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

"""
NOTE: Check for bugs!
"""

import sys
import socket

from lib.module import CIngumaModule
from lib.libtns import *

from lib import libfuzz

name = "tnscmd"
brief_description = "Interact with an Oracle TNS Listener"
type = "gather"

class CTnsCmd(CIngumaModule):

    target = "192.168.1.10"
    port = 1521
    sid = ""
    serviceName = ""
    vsnnum = ""
    version = 9
    exploitType = 1

    _lastError = None

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "sid = <sid name>"

    def processVersionResponse(self, res):
        pos = res.find("TNSLSNR")
        end = res.find("@")

        print

        if end > 0:
            print "\t", res[pos:end]
            self.addToDict(self.target + "_tnsversion", res[pos:end])
        else:
            print "\t", res[pos:]
            self.addToDict(self.target + "_tnsversion", res[pos:])

    def run(self):
        print
        return self.tnscmdLoop()

    def processTnsCode(self, code):
        if code == 32:
            print "No error. Command Succesfull."
        elif code == 33:
            print "Bad syntax"
        elif code == 35:
            print "Unknow command"
        else:
            print "Unknow return code"

    def showTnsError(self, res):
        pos = res.find("DESCRIPTION")
        print "TNS Listener returns an error:"
        print
        print "Raw response:"
        print repr(res)
        print
        print "Formated response:"
        formatter = TNSDataFormatter(res[pos-1:])
        print formatter.format()

        tns = TNS()
        errCode = tns.extractErrorcode(res)

        if errCode:
            print "TNS-%s: %s" % (errCode, tns.getTnsError(errCode))

    def getBaseCommand(self):
        if self.version < 10:
            return "(CONNECT_DATA=(COMMAND=%s))"
        else:
            data   = "(CONNECT_DATA=(CID=(PROGRAM=)(HOST=linux)(USER=oracle))(COMMAND=%s)(ARGUMENTS=64)"
            data += "(SERVICE=LISTENER)(VERSION=169869568))"
            return data

    def doVersion(self):
        res = self.runInternalCommand(self.getBaseCommand() % "version", 1)

        if len(res) < 78:
            # Resend the command. It's a >=10g instance.
            res = self.runInternalCommand(self.getBaseCommand() % "version", 2)

        self.processVersionResponse(res)

    def formatResponse(self, res):
        pos = res.find("DESCRIPTION=")
        data = res[pos-1:]
        formatter = TNSDataFormatter(data)
        print formatter.format()

    def doPing(self):
        res = self.runInternalCommand(self.getBaseCommand() % "ping", 1)
        self.formatResponse(res)

    def doServices(self):
        if self.version < 10:
            times = 1
        else:
            times = 2

        res = self.runInternalCommand(self.getBaseCommand() % "services", times)

        if res:
            self.formatResponse(res)

    def doStatus(self):
        if self.version < 10:
            times = 1
        else:
            times = 2

        res = self.runInternalCommand(self.getBaseCommand() % "status", times)

        if res:
            self.formatResponse(res)

    def runRawCommand(self, cmd, times = 1):
        data = self.getBaseCommand() % cmd
        print "Running '" + data + "' ... "
        print

        """
        if self.version < 10:
            times = 1
        else:
            times = 2
        """

        res = self.runInternalCommand(data, times)

    def runInternalCommand(self, theCommand, times = 1):
        try:
            res = ""

            tns = TNSPacket()
            tns.version = self.version
            data = tns.getPacket(theCommand)

            if self.port == "" or str(self.port) == "0":
                self.port = 1521

            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))

            for i in range(1, times+1):
                s.send(data)
                res = s.recv(1024)

                if res.find("ERROR_STACK=") > 0:
                    self.showTnsError(res)
                    return res

            return res

        except:
            print "TNSCMD Error.",sys.exc_info()[1]

    def showCommands(self):
        print "Inguma's TNSCMD Help"
        print "--------------------"
        print
        print "Commands:"
        print "resolve      Resolve database version"
        print "ping         Ping the database"
        print "version      Show version information"
        print "services     Show available services"
        print "status       Show instance's status"
        print "sid          Get the Oracle SID list"
        print "raw          Send a raw command"
        print "cmd          Send one tnslsnr command"
        print "fuzz         Fuzz all tokens from a given NV command string"
        print "help         Show this help"
        print "quit         Exits from tnscmd mode"
        print
        print "Any other typed command will be sended to the TNS Listener."
        print "The following is a list of raw interesting commands:"
        print
        print "'stop', 'reload', 'status', 'spawn' and 'services'"
        print

    def rawCommandLoop(self, mtimes = 1):
        buf = ""
        print "Type '.' in a single line to end raw command."
        print
        while 1:
            res = raw_input()
            
            if res == ".":
                print "Sending '" + buf + "' ..."
                self.runInternalCommand(theCommand=buf, times = mtimes)
                break
            else:
                if buf == "":
                    buf += res
                else:
                    buf += "\n" + res

    def resolveVersion(self):
        res = self.runInternalCommand("(CONNECT_DATA=(COMMAND=ping))")
        tns = TNS()
        vsnnum = tns.getVSNNUM(res)
        version = tns.assignVersion(vsnnum)

        if version:
            self.version = int(tns.assignVersion(vsnnum))
    
            print "Oracle Decimal version    : ", vsnnum
            print "Oracle Hexadecimal version: ", hex(int(vsnnum))
            print "Major Oracle version      : ", self.version
            self.addToDict(self.target + "_tnsvsnnum", vsnnum)
        else:
            print "Couldn't resolve Server Version"

    def fuzzCallback(self, data, idx):
        res = self.runInternalCommand(data)

        if res:
            tns = TNS()
            errCode = tns.extractErrorcode(res)

            if errCode:
            
                if errCode != self._lastError:
                    self.formatResponse(res)
                    print "TNS-%s: %s" % (errCode, tns.getTnsError(errCode))

                self._lastError = errCode

    def fuzz(self):
        try:
            cmd = raw_input("Base NV string: ")
            idx = raw_input("Start index: ")
            var = raw_input("Variable: ")
            
            if idx == "" or not idx:
                idx = 0
            else:
                idx = int(idx)
                
            if var == "" or not var:
                var = 0
            else:
                var = int(var)

        except KeyboardInterrupt:
            print "Aborted."
        except:
            raise

        libfuzz.fuzzCallback(self.fuzzCallback, cmd, idx)

        print
        print "Fuzzing finished. Any luck?"
        print

    def getSIDList(self):
        if self.version < 10:
            times = 1
        else:
            times = 2

        res = self.runInternalCommand(self.getBaseCommand() % "services", times)

        if not res:
            print "*** Internal Error!", sys.exc_info()[1]
            return

        pos = res.find("DESCRIPTION=")
        data = res[pos-1:]

        parser = TNSParser(data)
        values = parser.getValueFor("INSTANCE_NAME")

        banner = "Oracle SID List at %s" % self.target
        print banner
        print "-" * len(banner)
        print
        i = 0
        for value in values:
            i += 1
            print i, value
            self.addToDict(self.target + "_sidlist", value)

    def tryCmd(self):
        try:
            cmd = raw_input("Command to run: ")
        except KeyboardInterrupt:
            print "Aborted."

        res = self.runInternalCommand(self.getBaseCommand() % cmd, 1)
        
        if res:
            self.formatResponse(res)

    def tnscmdLoop(self):
        try:

            self.resolveVersion()

            if self.interactive:
                while 1:
                    data = raw_input("TNSCMD> ")
                    words = data.split(" ")
    
                    if len(words) > 0:
                        cmd = words[0]
                        args = []
    
                        for arg in words[1:]:
                            args += arg
                        
                        if len(args) > 0:
                            try:
                                times = int(args[0])
                            except:
                                print "Invalid number.", sys.exc_info()[1]
                    else:
                        cmd = ""
                        times = 1
    
                    if cmd.lower() == "resolve":
                        self.resolveVersion()
                    elif cmd.lower() == "version":
                        self.doVersion()
                    elif cmd.lower() == "ping":
                        self.doPing()
                    elif cmd.lower() == "services":
                        self.doServices()
                    elif cmd.lower() == "sid":
                        self.getSIDList()
                    elif cmd.lower() == "status":
                        self.doStatus()
                    elif cmd.lower() == "help":
                        self.showCommands()
                    elif cmd.lower() == "quit" or cmd.lower() == "exit":
                        break
                    elif cmd.lower() == "raw":
                        self.rawCommandLoop()
                    elif cmd.lower() == "fuzz":
                        self.fuzz()
                    elif cmd.lower() == "cmd":
                        self.tryCmd()
                    elif cmd == "":
                        pass
                    else:
                        self.runRawCommand(cmd)
            else:
                print
                print "Ping"
                print "----"
                self.doPing()

                print "Version"
                print "-------"
                self.doVersion()

                print
                self.getSIDList()

        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
        except:
            print "TNSCMD Error.", sys.exc_info()[1]
    
        return True
