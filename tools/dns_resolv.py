#!/usr/bin/python

from scapy import *

def resolve(host):
    dns = DNS(rd=1,qd=DNSQR(qname=host))
    response = sr1(IP(dst='192.168.1.1')/UDP()/dns);
    if response.haslayer(DNS):
        answer = response.getlayer(DNS).an
        answer.show()
