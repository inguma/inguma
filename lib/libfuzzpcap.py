#!/usr/bin/python

import os
import sys
import time
import socket

from lib import libfuzz

from scapy.all import *

"""

Interesting to debug with GDB ;)

handle SIGPIPE ignore noprint pass
handle SIGCONT ignore noprint pass
disp /s $eax
disp /s $ebx
disp /s $ecx
disp /s $edx
disp /s $edi
disp /s $esi
disp /s $ebp
disp /s $esp
disp /i $pc
c
"""

class CReplayFuzzer:

    target = ""
    port = 0
    replayList = []

    msocket = None

    # For fuzzing stuff
    currentIndex = -1
    startPacket = 0
    timeout = 0.3
    verbose = False
    linesize = 139
    sleepTime = 3
    waitResponse = True

    dontWaitFor = []
    restartCommand = ""
    restartWait = 0

    pocsDir = ""
    foundPocs = 0

    lastPacket = ""

    def __init__(self, target, port, replayList):
        self.target = target
        
        if not str(port).isdigit():
            self.port = socket.getservbyname(port)
        else:
            self.port = int(port)

        self.replayList = replayList

    def savePoc(self):
        self.foundPocs += 1
        idx = -1
        pocFile = self.pocsDir + "/poc" + str(time.time()) + ".py"
        f = file(pocFile, "w")
        
        buf = ""
        for pkt in self.replayList:
            idx += 1
            
            if idx == self.currentIndex:
                break
            else:
                f.writelines("buf%d=%s\n" % (idx, repr(pkt)))

        f.writelines("\n")
        f.writelines("#The last sent packet:\n")
        f.writelines("crashBuf=%s\n\n" % repr(self.lastPacket))
        f.close()
        
        print "Proof of concept %s saved." % pocFile
        
        if self.foundPocs > 100:
            print "Hey brotha, we found more than 100 POC(s)!"
            raw_input("Continue? Ctrl+C to stop...")

    def showHappyMessage(self):
        print "The target appears to be down! Hurra!"
        print
        print "Last sent packet (after %d expected packets)" % (self.currentIndex)
        print "-"*self.linesize
        print "buf=%s" % repr(self.lastPacket)
        print "-"*self.linesize
        print
        print "Happy haunting!"
        print
        
        if self.restartCommand == "":
            # Interactive fuzzing session
            ret = raw_input("Continue fuzzing? (y/n) ")
            if ret.lower() not in ["y", "yes"]:
                sys.exit(0)
            else:
                self.connectSocket()
        else:
            
            print "Saving proof of concept ... "
            self.savePoc()
            
            print "Restarting target ... "
            print "Waiting for a while (%d) ... " % self.restartWait
            time.sleep(self.restartWait)
            os.system(self.restartCommand + "&")
            time.sleep(self.restartWait)
            print "Done! Continuing with fuzzing now ..."

    def connectSocket(self):
        socket.setdefaulttimeout(self.timeout)
        
        if self.msocket != None:
            try:
                self.msocket.close()
            except:
                pass

        self.msocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.msocket.connect((self.target, self.port))
        except KeyboardInterrupt:
            print "Aborted."
            sys.exit(0)
        except:
            print "[+] Cannot connect to target!!!"
            self.showHappyMessage()

    def sendReceivePacket(self, pkt, cannotFail = False):
        try:
            if self.msocket == None:
                self.connectSocket()

            self.msocket.sendall(pkt)
            res = False

            if self.currentIndex not in self.dontWaitFor:
                if cannotFail:
                    res = self.msocket.recv(4096)
                elif self.waitResponse:
                    res = self.msocket.recv(4096)
            else:
                print "[!] Ignoring response specified packet %d" % self.currentIndex

            return res
        except socket.timeout:
            if cannotFail:
                print "***Timeout while sending AS IS packet... Host appears to be 'in the limb' or debugging is in progress"
                self.showHappyMessage()

        except KeyboardInterrupt:
            print "Aborted."
            sys.exit(0)
        except:
            print "***Error:", sys.exc_info()[1]
            self.connectSocket()
            return False

    def replay(self):
        for pkt in self.replayList:
            print "Sending pkt to %s:%s:" % (self.target, str(self.port))
            print repr(pkt)
            buf = self.sendReceivePacket(pkt)

            if buf:
                print "Response:"
                print repr(buf)

    def fuzzCallback(self, fuzzyPacket, index):
        try:
            print
            print "Total of %d POC(s) generated" % self.foundPocs
            print
            idx = -1
            self.msocket = None

            for pkt in self.replayList:
                idx += 1
                if idx == self.currentIndex:
                    break

                if self.verbose:
                    print "Sending packet as is:"
                    print repr(pkt)

                ret = self.sendReceivePacket(pkt, True)

                if ret and self.verbose:
                    print "Response to as is packet:"
                    print repr(ret)
                    #raw_input()
                else:
                    print "As is packet %d OK" % idx

            print "Sending fuzzy packet (Current packet %d - Current index %d) ..." % (self.currentIndex, index)
            
            if self.verbose:
                print repr(fuzzyPacket)
            else:
                print repr(fuzzyPacket)[0:self.linesize]

            self.lastPacket = fuzzyPacket
            ret = self.sendReceivePacket(fuzzyPacket)

            if ret and self.verbose:
                print "Response to fuzz:"
                print repr(ret)
            elif ret != "" and ret != None:
                print "Response to fuzz:"
                print repr(ret)[0:self.linesize]
        except KeyboardInterrupt:
            print "Aborted."
            sys.exit(0)
        except:
            print "***Error:", sys.exc_info()[1]

    def fuzz(self):
        self.currentIndex = -1
        for pkt in self.replayList:
            self.currentIndex += 1
            
            if self.currentIndex < self.startPacket:
                continue

            libfuzz.fuzzCallback(self.fuzzCallback, pkt, 0, 0, 0, False) # Fast mode
            libfuzz.fuzzCallback(self.fuzzCallback, pkt, 0, 0, 1, False) # Fast mode
        
        print
        print "Fuzzing done!"
        
        if self.foundPocs > 0:
            print
            print "A total of %d POC(s) were saved in directory %s" % (self.foundPocs, self.pocsDir)
            print
        else:
            print 
            print "No luck my friend :( Life sucks..."
            print
