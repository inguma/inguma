#!/usr/bin/python

##      CSmbGold.py
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

import sys
import time
import string
from impacket import smb
from lib.module import CIngumaModule

name = "smbgold"
brief_description = "Search for 'gold' in shared SMB directories"
type = "gather"

INTERESTING = ["pass", "priv", "conf", "secr", ".mdb", "id_dsa", "id_rsa"]

class CSmbGold(CIngumaModule):

    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    interactive = True

    def help(self):
        print "target = <target host or network>"
        print
        print "Optional:"
        print "user = <username>"
        print "password = <password>"

    def info(self):
        if not self.smb:
            self.gom.echo( "Open a connection first." )

        domain = self.smb.get_server_domain()
        lanman = self.smb.get_server_lanman()
        serverName = self.smb.get_server_name()
        serverOs = self.smb.get_server_os()
        serverTime = self.smb.get_server_time()
        sessionKey = self.smb.get_session_key()
        loginRequired = self.smb.is_login_required()

        self.gom.echo( "Current connection information" )
        self.gom.echo( "------------------------------" )
        self.gom.echo( "" )
        self.gom.echo( "Domain name      :" + domain )
        self.gom.echo( "Lanman           :" + lanman )
        self.gom.echo( "Server name      :" + serverName )
        self.gom.echo( "Operative System :" + serverOs )
        self.gom.echo( "Server Time      :" + serverTime )
        self.gom.echo( "Session Key      :" + sessionKey )
        self.gom.echo( "" )
        self.gom.echo( "Is login required?" + loginRequired )

        data = {}
        data["domain"] = domain
        data["lanman"] = lanman
        data["server_name"] = serverName
        data["os"] = serverOs
        data["time"] = (time.time(), serverTime)
        data["key"] = sessionKey
        data["login_required"] = loginRequired

        self.addToDict(self.target + "_os", serverOs)
        self.addToDict(self.target + "_smb", data)

    def run(self):
        # Open the connection
        self.smb = smb.SMB("*SMBSERVER", self.target, self.port)

        if self.user != "" and self.user is not None:
            self.smb.login(self.user, self.password)
        else:
            if self.smb.is_login_required():
                self.gom.echo( "Valid credentials *ARE* required for target %s" % self.target )
                self.gom.echo( 'Use the following syntax prior to rerun the module:\r\n\r\nuser="username"\r\npassword="password"\r\n' )
                self.gom.echo( "" )
                return False
            else:
                self.smb.login("", "")

        try:
            self.info()
            self.gom.echo( "" )
        except:
            self.gom.echo( "[!]" + sys.exc_info()[1] )
            self.gom.echo( "You will need a valid account :(" )

        self.searchGold()

        return True

    def scanDir(self, shareName, dir):
        pwd = "/" + dir + "/*"

        for f in self.smb.list_path(shareName, pwd):
            name = f.get_longname()
            if name == "." or name == "..":
                continue
            else:
                for x in INTERESTING:
                    if name.lower().find(x) > -1:
                        self.gom.echo( "  --> Found" + name )
                        self.addToDict("share_gold_" + shareName, dir + "/" + name)
                
                if f.is_directory():
                    self.scanDir(shareName, dir + "/" + f.get_longname())
                else:
                    continue

    def scanShare(self, shareName):
        self.gom.echo( "Scanning share %s..." % shareName )
        self.gom.echo( "" )
        self.tid = self.smb.tree_connect(shareName)
        pwd = "/"
        for f in self.smb.list_path(shareName, pwd):
            name = f.get_longname()

            if name == "." or name == "..":
                continue
            else:
                for x in INTERESTING:
                    if name.lower().find(x) > -1:
                        self.gom.echo( "  --> Found" + name )
                        self.addToDict("share_gold_" + shareName, name)
                
                if f.is_directory():
                    self.scanDir(shareName, f.get_longname())
                else:
                    continue

        self.gom.echo( "" )

    def searchGold(self):
        self.gom.echo( "List of remote shares" )
        self.gom.echo( "---------------------" )
        self.gom.echo( "" )
        try:
            list = self.smb.list_shared()
        except:
            self.gom.echo( "Error:" + sys.exc_info()[1] )
            self.gom.echo( "Invalid credentials?" )
            return False

        for share in list:
            if share.get_type() == 0 and not share.get_name().endswith("$"):
                self.gom.echo( "Name:" + share.get_name() )
                self.gom.echo( "Comment:" + share.get_comment() )
                self.gom.echo( "Type:" + share.get_type() )
                self.gom.echo( "" )
                self.scanShare(share.get_name())
