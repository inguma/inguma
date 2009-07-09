#!/usr/bin/python
"""
Module winspdetect for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

"""
NOTE: If the module works the Administrator's password is blank.
"""

import os
from lib.libexploit import CIngumaModule

try:
    if os.name == "nt":
        import _winreg
except:
    self.gom.echo( "No Winreg support." )

name = "winspdetect"
brief_description = "Detect service pack using remote registry (LAME)"
type = "gather"

class CWinSpDetect(CIngumaModule):

    target = ""
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
