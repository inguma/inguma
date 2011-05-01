#!/usr/bin/python

import os
import sys
import time
import socket

from lib import libfuzz

from scapy.all import *
from fuzzpcap import *

def main(pcapFile, dest, destPort):
    
    replayList = []
    
    pktList = rdpcap(pcapFile)
    
    for pkt in pktList:
        tcpPkt = pkt[TCP]
        flags = tcpPkt.sprintf("%flags%")
        dst = pkt.sprintf("%IP.dst%")
        dstPort = tcpPkt.sprintf("%TCP.dport%")

        if flags == "PA" and dst == dest and dstPort == destPort:
            # Get the packet's data
            pktBuf = str(tcpPkt[Raw])
            replayList.append(pktBuf)

    replayer = CReplayFuzzer(dest, destPort, replayList)
    replayer.verbose = True
    replayer.timeout = 0.3
    replayer.waitResponse = False
    replayer.startPacket = 1
    replayer.dontWaitFor = xrange(0, 1024)
    """replayer.restartCommand = "sudo su - informix -c '/tmp/start.sh'"
    replayer.restartWait = 15
    replayer.pocsDir = "/home/joxean/proyectos/tool/informix"""
    replayer.replay()
    replayer.fuzz()

if __name__ == "__main__":
    
    if len(sys.argv) < 4:
        #main("/tmp/ifx/ifx.dump", "192.168.1.11", "sqlexec")
        main("/tmp/syb/sybase.dump", "192.168.1.11", "5000")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

