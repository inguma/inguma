#!/usr/bin/python

##      CWinSpDetect.py
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
NOTE: If the module works the Administrator's password is blank.
"""

import os
from lib.module import CIngumaModule

try:
    if os.name == "nt":
        import _winreg
except:
    self.gom.echo( "No Winreg support." )

name = "winspdetect"
brief_description = "Detect service pack using remote registry (LAME)"
type = "gather"

class CWinSpDetect(CIngumaModule):

    waitTime = 0
    timeout = 1
    exploitType = 1
    wizard = False
    services = {}
    results = {}
    string = ""
    interactive = True

    def help(self):
        print "target = <target host or network>"

    def run(self):
        if os.name != "nt":
            self.gom.echo( "Only supported under Win32 platforms" )
            return False

        self.results = {}
        host = _winreg.ConnectRegistry(self.target, _winreg.HKEY_LOCAL_MACHINE)
        key = _winreg.OpenKey(host, "Software\\Microsoft\\Windows NT\\CurrentVersion\\")
        os_name, sp_ver =  _winreg.QueryValueEx(key, "ProductName")[0],_winreg.QueryValueEx(key,"CSDVersion")[0]
        self.string = os_name + " " + sp_ver

        return True

    def printSummary(self):
        self.gom.echo( self.string )


if __name__ == "__main__":

    objSp = CSpDetect()
    objSp.target = "127.0.0.1"
    objSp.run()
    objSp.printSummary()
