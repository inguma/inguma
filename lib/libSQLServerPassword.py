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
import hashlib

from core import str2uni

class CSQLServerPassword:

    data = ""
    _header = ""
    _key = ""
    _password = ""
    _upperPassword = ""
    
    def __init__(self, data = None):

        if data:
            self.data = data

            if len(self.data) != 94:
                raise Exception("Invalid password hash size")

            if self.data[0:2].lower() != "0x":
                raise Exception("Invalid password hash")

            self._header   = int(self.data[2:6])
            self._key      = int(self.data[6:8])
            self._password = self.data[8:40]
            self._upperPassword = self.data[40:]

    def printSummary(self):
        print "Header           : ", hex(self._header)
        print "Key              : ", self._key
        print "Password         : ", self._password
        print "Password (Upper) : ", self._upperPassword

    def encrypt(self, passwd):
        # Convert the password to an unicode string
        mPasswd = str2uni(passwd)
        # Append the random stuff (the key)
        mPasswd += str(self._key)
        # Get the first hash (normal)
        baseHash = hashlib.sha1(mPasswd).hexdigest().upper()
        # Get the upper case hash
        upperHash = hashlib.sha1(mPasswd.upper()).hexdigest().upper()

        # Generate the password
        buf  = "0x"
        buf += str(self._header)
        buf += str(self._key)
        buf += baseHash
        buf += upperHash

        return buf

if __name__ == "__main__":
    passwd = "0x01008444930543174C59CC918D34B6A12C9CC9EF99C4769F819B43174C59CC918D34B6A12C9CC9EF99C4769F819B"
    objSQLServer = CSQLServerPassword(passwd)
    print objSQLServer.encrypt("sa")
