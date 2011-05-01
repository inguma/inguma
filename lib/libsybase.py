#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

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
import sys
import socket
import libfuzz

from core import int2hex

VERSION = "0.1.1"

MAX_HOST_SIZE = 30
MAX_USER_SIZE = 30
MAX_PASS_SIZE = 255
MAX_ENCODING_SIZE = 30

magicNumber = "37876"
magicNumber2 = "512"

def makeSqlServerPacket(hostname = "", username = "sa", password = "test", encoding = "iso_1",
                                                    appName = "example1", ip_address = "192.168.1.14", language = "english", dbname = "master"):

    packet = '\x02\x00\x02\x00\x00\x00\x00\x00' # Packet header 
    packet += hostname + "\x00"*(MAX_HOST_SIZE - len(hostname)) + int2hex(len(hostname))
    packet += username + "\x00"*(MAX_USER_SIZE - len(username)) + int2hex(len(username))
    packet += dbname + "\x00"*(MAX_USER_SIZE - len(dbname)) + int2hex(len(password))
    packet += magicNumber + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(magicNumber))
    packet += "\x03\x01\x06\n\t\x01\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00"
    packet += appName + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(appName))
    packet += ip_address + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(ip_address))
    packet += password + "\x00"*(MAX_PASS_SIZE - len(password)) + int2hex(len(password))
    packet += "\x04\x02\x00\x00DB-Library\n\x00\x00\x00\x00\x00\r\x11"
    packet += language + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01\x00"
    packet += "L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    packet += encoding + "\x00"*(MAX_ENCODING_SIZE - len(encoding)) + int2hex(len(encoding)) + "\x01"
    packet += magicNumber2 + "\x00\x00\x00" + int2hex(len(magicNumber2)) + "\x00\x00\x00\x00\x00\x00\x00\x00"
    
    return packet

class CSybaseLib:

    hostname = "prueba"
    username = "test"
    password = "testing"
    dbname = "master"
    encoding = "iso_1"
    appName = "example1"
    ip_address = "255.255.255.255"
    language = "english"

    def __init__(self):
        pass

    def getLoginPacket(self):
        self.dbname = self.password
        packet = '\x02\x00\x02\x00\x00\x00\x00\x00' # Packet header 
        packet += self.hostname + "\x00"*(MAX_HOST_SIZE - len(self.hostname)) + int2hex(len(self.hostname))
        packet += self.username + "\x00"*(MAX_USER_SIZE - len(self.username)) + int2hex(len(self.username))
        packet += self.dbname + "\x00"*(MAX_USER_SIZE - len(self.dbname)) + int2hex(len(self.dbname))
        packet += magicNumber + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(magicNumber))
        packet += "\x03\x01\x06\n\t\x01\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00"
        packet += self.appName + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(self.appName))
        packet += self.ip_address + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + int2hex(len(self.ip_address))
        packet += self.password + "\x00"*(MAX_PASS_SIZE - len(self.password)) + int2hex(len(self.password))
        packet += "\x04\x02\x00\x00DB-Library\n\x00\x00\x00\x00\x00\r\x11"
        packet += self.language + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01\x00"
        packet += "L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        packet += self.encoding + "\x00"*(MAX_ENCODING_SIZE - len(self.encoding)) + int2hex(len(self.encoding)) + "\x01"
        packet += magicNumber2 + "\x00\x00\x00" + int2hex(len(magicNumber2)) + "\x00\x00\x00\x00\x00\x00\x00\x00"

        return packet

def main():
    objSybase = CSybaseLib()
    objSybase.hostname = "clard.des.airtel.es"
    objSybase.username = "fase1c_1"
    objSybase.password = "diciembre"
    objSybase.ip_address = "10.0.0.1"

    packet = objSybase.getLoginPacket()
    print "Data to send",repr(packet)

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((objSybase.hostname, 10000))
    s.send(packet)
    data = s.recv(1024)
    print "Data received",repr(data)

def prueba():
    objSybase = CSybaseLib()
    objSybase.hostname = "192.168.1.11"
    objSybase.username = "test"
    objSybase.password = "testing"
    objSybase.dbname = "users"
    objSybase.ip_address = "192.168.1.11"

    packet = objSybase.getLoginPacket()
    print "Data to send",repr(packet)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((objSybase.hostname, 5000))
    s.send(packet)
    data = s.recv(1024)
    print "Data received",repr(data)

def fuzz():

    properties = ["encoding", "appName", "ip_address", "language"]

    socket.setdefaulttimeout(0.5)

    for prop in properties:
        for i in libfuzz.sizes:
            for str in libfuzz.strings:
                print "[+] Fuzzing property %s - string %s - size %d" % (prop, str, i)
                objSybase = CSybaseLib()
                objSybase.username = "test"
                objSybase.password = "testing"
                exec("objSybase." + prop + " = str*i")
                packet = objSybase.getLoginPacket()
                #print "Data to send",repr(packet)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("192.168.1.11", 5000))
                s.send(packet)
                try:
                    data = s.recv(1024)
                    print "Data received",repr(data)
                except:
                    print "***Error:", sys.exc_info()[1]

if __name__ == "__main__":
    fuzz()
