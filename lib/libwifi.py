from scapy.all import *

unique = []

def sniffBeacon(p):
     if p.haslayer(Dot11Beacon):
          if unique.count(p.addr2) == 0:
           unique.append(p.addr2)
           print p.sprintf("%Dot11.addr2%[%Dot11Elt.info%|%Dot11Beacon.cap%]")

def sniffNonBeacon(p):
     if not p.haslayer(Dot11Beacon):
          if unique.count(p.addr2) == 0:
               unique.append(p.addr2)
               print p.sprintf("[%Dot11.addr1%][%Dot11.addr2%][%Dot11Elt.info%]")
               print p.summary()

def sniffMAC(p):
     if p.haslayer(Dot11):
          mac = p.sprintf("[%Dot11.addr1%)|(%Dot11.addr2%)|(%Dot11.addr3%)]")
          if unique.count(mac) == 0:
               unique.append(mac)
               print mac

def sniffarpip(p):
     if p.haslayer(IP):
          ip = p.sprintf("IP - [%IP.src%)|(%IP.dst%)]")
          if unique.count(ip) == 0:
               unique.append(ip)
               print ip
     elif p.haslayer(ARP):
          arp = p.sprintf("ARP - [%ARP.hwsrc%)|(%ARP.psrc%)]-[%ARP.hwdst%)|(%ARP.pdst%)]")
          if unique.count(arp) == 0:
               unique.append(arp)
               print arp
