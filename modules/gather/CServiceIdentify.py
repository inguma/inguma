#!/usr/bin/python

##      CServiceIdentify.py
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
NOTE: It works but it *SUCKS*. Should be added support for signatures.
"""
import re
import os
import sys
import time
import socket

from impacket import smb

from lib.libtns import *
from lib.module import CIngumaModule

name = "identify"
brief_description = "Identify services using discovered ports"
type = "gather"

class CServiceIdentify(CIngumaModule):
    verbose = False

    def help(self):
        print "target = <target host or network>"
        print
        print "Optional:"
        print "port = <target port>"
        print
        print "Note: If port is equal to 0 you need to execute a portscanner prior to identify services."

    def tryVmware(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(4096)

            if data.lower().find("vmware authentication daemon version") > -1:
                self.addToDict(self.target + "_services", str(port) + "/vmware")
                return "VMWare Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryStonegate(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(4096)
            
            stoneRe = re.compile("(StoneGate firewall|SG login:)", re.IGNORECASE)

            if stoneRe.match(data) > -1:
                self.addToDict(self.target + "_services", str(port) + "/stonegate")
                return "Stonegate Firewall"
            else:
                return False
        except:
            s.close()
            return False

    def tryCitrix(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(64)
            
            citrixRe = re.compile(".*ICA.*", re.IGNORECASE)

            if citrixRe.match(data) > -1:
                self.addToDict(self.target + "_services", str(port) + "/citrix")
                return "Citrix Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryPcAnywhere(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send("ST")
            data = s.recv(1024)

            if data.find("ST") > -1:
                self.addToDict(self.target + "_services", str(port) + "/pcanywhere")
                return "PC Anywhere"
            else:
                return False
        except:
            s.close()
            return False

    def tryVncServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)

            if data.find("RFB 00") == 0:
                self.addToDict(self.target + "_services", str(port) + "/vnc")
                return "VNC Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryHttpTimesTen(self, port):
        try:
            buf  = "GET /hello\r\n\r\n"
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send(buf)
            data = s.recv(1024)

            if data.find("HTTP/1.0 400 msg=Bad%20Request&rc=%") > -1:
                self.addToDict(self.target + "_services", str(port) + "/timesten")
                return "Oracle TimesTen Web Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryRdp(self, port):
        try:
            buf  = "\x03\x00\x00\x29\x24\xe0\x00\x00\x00\x00\x00Cookie: mstshash=theusername\x0d\x0a"
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send(buf)
            data = s.recv(1024)

            if data == "\x03\x00\x00\x0b\x06\xd0\x00\x00\x124\x00":
                self.addToDict(self.target + "_services", str(port) + "/rdp")
                return "Remote Desktop Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryLdap(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send("\r\n"*3)
            data = s.recv(1024)
            if data.lower().find("1.3.6.1.4.1.1466.20036") > -1:
                self.addToDict(self.target + "_services", str(port) + "/ldaps")
                return "SSL LDAP Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryLdaps(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            ssl_sock = socket.ssl(s)
            ssl_sock.write("\r\n"*3)
            data = ssl_sock.read(1024)
            del ssl_sock
            if data.lower().find("1.3.6.1.4.1.1466.20036") > -1:
                self.addToDict(self.target + "_services", str(port) + "/ldap")
                return "LDAP Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryOrmiServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            pkt  = "\r\n\r\n\r\n"
            s.sendall(pkt)
            data = s.recv(1024)
            s.close()

            if data.lower().find("illegal ormi request") > -1:
                self.addToDict(self.target + "_services", str(port) + "/ormi")
                
                if self.verbose:
                    self.gom.echo( "Response: %s" % repr(data) )

                return "Oracle RMI (OC4J ORMI)"
            else:
                return False
        except:
            return False

    def tryOcfs2Service(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            pkt  = "\xfa\x57\x00\x00\x00\x00\x00\x00"
            pkt += "\x00\x00\x00\x00\x00\x00\x00\x00"
            pkt += "\x00\x00\x00\x00\x00\x00\x00\x00"
            s.sendall(pkt)
            data = s.recv(1024)
            s.close()

            if data[0:2] == "\xfa\x58":
                self.addToDict(self.target + "_services", str(port) + "/ocfs2")
                return "OCFS2"
            else:
                return False
        except:
            return False

    def tryHttpServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send("GET / HTTP/1.1" + os.linesep + "HOST:localhost" + os.linesep + "CONNECTION:close" + os.linesep * 3)
            data = s.recv(1024)
            s.close()

            if data.lower().find("http/") == 0:
                self.addToDict(self.target + "_services", str(port) + "/http")
                pos = data.lower().find("server:")

                if self.verbose:
                    self.gom.echo( "Response: %s" % repr(data) )

                if pos > -1:
                    data = data[pos+len("server:"):]
                    data = data[:data.find("\n")]
                    return data
                else:
                    # Is this correct?
                    if data.lower().find("x-cache") > -1 or data.lower().find("miss from") > -1:
                        return "Proxy Server"
                    else:
                        return "HTTP Server"
            else:
                return False
        except:
            s.close()
            
            try:
                import urllib
                a = urllib.urlopen("http://" + self.target + ":" + str(self.port))
                self.addToDict(self.target + "_services", str(port) + "/http")

                if a.headers.has_key("server"):
                    return a.headers["server"]

                return "HTTP Server"
            except:
                pass

            return False

    def tryRtspServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.send("OPTIONS * RTSP/1.0\r\n\r\n")
            data = s.recv(1024)
            s.close()

            if data.lower().find("rtsp/") == 0:
                self.addToDict(self.target + "_services", str(port) + "/rtsp")
                pos = data.lower().find("server:")

                if self.verbose:
                    self.gom.echo( "Response: %s" % repr(data) )

                if pos > -1:
                    data = data[pos+len("server:"):]
                    data = data[:data.find("\n")]
                    return data
                else:
                    # Is this correct?
                    if data.lower().find("x-cache") > -1 or data.lower().find("miss from") > -1:
                        return "RTSP Proxy Server"
                    else:
                        return "RTSP Server"
            else:
                return False
        except:
            s.close()
            return False

    def tryHttpsServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            
            ssl_sock = socket.ssl(s)
            #print "Server:", ssl_sock.server()
            #print "Issuer:", ssl_sock.issuer()

            ssl_sock.write("GET / HTTP/1.0\n\n\n")
            data = ssl_sock.read(1024)
            del ssl_sock
            s.close()

            if data.lower().find("http/") == 0:
                self.addToDict(self.target + "_services", str(port) + "/https")
                pos = data.lower().find("server:")

                if self.verbose:
                    self.gom.echo( "Response: %s" % repr(data) )

                if pos > -1:
                    data = data[pos+len("server:"):]
                    data = data[:data.find("\n")]
                    return data
                else:
                    return "HTTP-SSL Server"
            else:
                return False
        except:
            return False

    def tryTelnetServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)
            s.close()

            if data.lower().find("server") > -1:
                self.addToDict(self.target + "_services", str(port) + "/telnet")
                tmp = data[:data.find("\n")]
                tmp = data[4:]
                
                if tmp.lower().find("ready") > -1:
                    tmp = tmp[:tmp.lower().find("ready")]

                return tmp
            else:
                if port == "23":
                    self.addToDict(self.target + "_services", str(port) + "/telnet")
                    return "Telnet Server"
                else:
                    return False
        except:
            s.close()
            return False

    def tryFtpServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)
            s.close()

            if data.lower().find("ftp") > -1:
                tmp = data[:data.find("\n")]
                tmp = data[4:]
                
                if tmp.lower().find("ready") > -1:
                    tmp = tmp[:tmp.lower().find("ready")]

                if len(tmp) > 0:
                    # Is really an FTP server?
                    self.addToDict(self.target + "_services", str(port) + "/ftp")

                return tmp
            else:
                return False
        except:
            s.close()
            return False

    def trySshServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)
            s.close()

            if data.lower().find("ssh")>-1:
                tmp = data[:data.find("\n")]
                tmp = data[4:]

                if len(tmp) > 0:
                    # Is really an SSH server?
                    self.addToDict(self.target + "_services", str(port) + "/ssh")

                return tmp
            else:
                return False
        except:
            s.close()
            return False

    def tryTnsServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))

            tns = TNS()
            TNSCONN = TNSCONNECT()
            vsnreq = TNSCONN.getVersionCommand()
            tns.sendConnectRequest(s,vsnreq)
            tns.recvTNSPkt(s)

            if (tns.packet_type == tns.TNS_TYPE_ACCEPT):
                ver_info = tns.recvAcceptData(s,TNS.tns_data)
                vsnnum = tns.getVSNNUM(ver_info)
                versionora = tns.assignVersion(vsnnum)

            if tns.packet_type == tns.TNS_TYPE_ACCEPT:
                data = "Oracle TNS Listener v" + str(tns.assignVersion(versionora)) + " (" + hex(int(vsnnum)) + ")"
            else:
                data = "Oracle TNS Listener (!???) v"+ str(tns.assignVersion(versionora)) + " (" + hex(int(vsnnum)) + ")"

            self.addToDict(self.target + "_services", str(port) + "/tns")
            return data
            data = s.recv(1024)
            s.close()

        except:
            s.close()
            return False

    def trySmbServer(self, port):
        try:
            if port not in ["135", "139", "445"]:
                return False

            self.smb = smb.SMB("*SMBSERVER", self.target, port)
            self.addToDict(self.target + "_services", str(port) + "/smb")

            try:
                self.smb.login("", "")
                data = "SMB Server " + self.smb.get_server_name() + "-" + self.smb.get_server_os() + "/" +  self.smb.get_server_lanman()
                return data
            except:
                return "SMB Server"
        except:
            s.close()
            return False

    def tryLpdServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.sendall("\x03printer\n")
            data = s.recv(1024)
            s.close()

            if data.lower().find("lpd") > -1:
                self.addToDict(self.target + "_services", str(port) + "/lpd")
                if data.find(":") > -1:
                    data = split(data, ":")
                    return data[0]
                else:
                    return "LPD"

            else:
                return False
        except:
            s.close()
            return False

    def tryJetDirect(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            s.sendall("@PJL INFO ID\n")
            data = s.recv(1024)
            s.close()

            if data.lower().find("@pjl info id") > -1:
                self.addToDict(self.target + "_services", str(port) + "/jetdirect")
                if data.find("\n") > -1:
                    data = split(data, "\n")
                    return data[1].replace("\n", "").replace("\r", "").replace('"', '')
                else:
                    return "JET Direct"

            else:
                return False
        except:
            s.close()
            return False

    def trySmtpServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)

            if data.lower().find("220 ") == 0:
                self.addToDict(self.target + "_services", str(port) + "/smtp")
                return data[4:]
            else:
                return False
        except:
            s.close()
            return False

    def tryMySQLServer(self, port):
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, int(port)))
            data = s.recv(1024)
            
            if data.lower().find("mysql") > -1:
                self.addToDict(self.target + "_services", str(port) + "/mysql")
                return "MySQL"
            else:
                return False
        except:
            s.close()
            return False

    def tryDefaultServices(self, port):
        if port == "22":
            data = self.trySshServer(port)
            if data:
                return data
            # Some arcaic unix system's default services
            """
            Port 512/exec is open
            Port 2049/nfs is open
            Port 514/shell is open
            Port 515/printer is open
            Port 513/login is open
            Port 37/time is open
            Port 79/finger is open
            """
        elif port == "11":
            data = "systat"
            self.addToDict(self.target + "_services", "11/systat")
            return data
        elif port == "15":
            data = "netstat"
            self.addToDict(self.target + "_services", "11/netstat")
            return data
        elif port == "37":
            data = "time"
            self.addToDict(self.target + "_services", "37/time")
            return data
        elif port == "79":
            data = "finger"
            self.addToDict(self.target + "_services", "79/finger")
            return data
        elif port == "25":
            data = self.trySmtpServer(port)
            if data:
                return data
        elif port == "9100":
            data = self.tryJetDirect(port)
            if data:
                return data
        elif port == "389":
            data = self.tryLdap(port)
            if data:
                return data
        elif port in ["80", "81", "8080", "8081", "8000", "8001", "8002"] or str(port).startswith("80"):
            data = self.tryHttpServer(port)
            if data:
                return data
        elif port == "443":
            data = self.tryHttpsServer(port)
            if data:
                return data
        elif port == "515":
            data = self.tryLpdServer(port)
            if data:
                return data
        elif port == "21":
            data = self.tryFtpServer(port)
            if data:
                return data
        elif port == "23":
            data = self.tryTelnetServer(port)
            if data:
                return data
        elif port == "1521":
            data = self.tryTnsServer(port)
            if data:
                return data
        elif port in ("135", "139", "445"):
            data = self.trySmbServer(port)
            if data:
                return data
        elif port == "1723":
            data = "PPTP"
            self.addToDict(self.target + "_services", str(port) + "/pptp")
            return data
        elif port == "6000":
            data = "X11 Window System"
            self.addToDict(self.target + "_services", str(port) + "/x11")
            return data
        elif port == "24800":
            data = "Synergy"
            self.addToDict(self.target + "_services", str(port) + "/synergy")
            return data
        elif port == "5520":
            data = self.tryOrmiServer(port)
            if data:
                return data
        elif port == "7777":
            data = self.tryOcfs2Service(port)
            if data:
                return data 

            data = self.tryHttpServer(port)
            if data:
                return data

            data = self.tryHttpsServer(port)
            if data:
                return data
        elif port == "3306":
            data = self.tryMySQLServer(port)
            if data:
                return data
        elif port in ["17000", "17002"]:
            data = self.tryHttpTimesTen(port)
            if data:
                return data
        elif port == "1494":
            data = self.tryCitrix(port)
            if data:
                return data
        else:
            return False

    def identifyService(self, port):
        port = str(port)

        data = self.tryDefaultServices(port)
        if data:
            return data

        bTried = False
        bContinue = True

        for method in dir(self):
            if method.find("try") == 0 and method != "tryDefaultServices":
                try:
                    val = eval("self." + method + "(port)")
                    bTried = True
                    bContinue = True
                    if val:
                        return val
                    else:
                        time.sleep(self.waitTime)
                except:
                    if str(sys.exc_info()[1][0]) == "10061":
                        if bTried and bContinue:
                            self.gom.echo( "[!] Warning! I can't connect with the server after previous sucessfull communications." )
                            self.gom.echo( "[!] Waiting for a while ..." )
                            time.sleep(5)
                            bContinue = False
                            continue
                        else:
                            self.gom.echo( "[!] Can't connect with target at specified port. " +  sys.exc_info()[1] )
                            return False

        try:
            data = socket.getservbyport(port)
        except:
            data = "Unknown"

        return data

    def run(self):
        if self.dict.has_key(self.target + "_tcp_ports"):
            mList = self.dict[self.target + "_tcp_ports"]
            for service in mList:
                srv = self.identifyService(service).strip()
                self.gom.echo( "Port " + str(service) + ": " + srv )
                self.addToDict(self.target + '_' + str(service) + '-info', srv)
        else:
            if self.port == 0:
                self.gom.echo( "No ports detected with a portscanner and the value of port is 0." )
                return False
            else:
                srv = self.identifyService(self.port).strip()
                self.gom.echo( "Port " + str(self.port) + ": " + srv )
                self.addToDict(self.target + '_' + str(service) + '-info', srv)
                print srv

        return True
