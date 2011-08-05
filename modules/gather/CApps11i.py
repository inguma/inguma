#!/usr/bin/python

##      CApps11i.py
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
NOTE: Sucks but works. It may fail if the server is behind a Web Cache.
"""

import socket
import time
from lib.module import CIngumaModule

name = "apps11i"
brief_description = "Get information from Oracle E-Business Suite 11i"
type = "gather"

class CApps11i(CIngumaModule):

    __internal_results = ""
    dadName = None
    timeAt = {}
    version = None
    sid = None
    schemaName = None
    _buffer = None
    aolVersion = None
    webAgent = None
    databaseHost = None
    databasePort = None
    loginFormPath = None
    prodComnPath = None
    results = {}
    exploitType = 1
    timeout = 5

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "timeout = <timeout>"
        print "dad = <DAD name>"
        print
        print "If the DAD is not specified it will be guessed."

    def getDAD(self):
        socket.setdefaulttimeout(self.timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target, self.port))

        request = "GET /pls/ HTTP/1.0\r\n\r\n"
        s.sendall(request)
        banner = s.recv(4096)
        pos = banner.find("Location: ")
        
        if pos > -1:
            startPos = banner.find("/pls/")
            endPos = banner.find("/", startPos+6)

            self.dadName = banner[startPos+5:endPos]
        else:
            banner = None
            self.dadName = None

        self.addToDict(self.target + "_dad", self.dadName)
        return(self.dadName)

    def getField(self, data, field):
        startPos = data.find(field)
        
        if startPos == -1:
            return None
        
        startPos = data.find('">', startPos+len(field) + 1)

        if startPos == -1:
            return None
        
        endPos = data.find("</", startPos+3)
        
        if endPos == -1:
            return None

        return(data[startPos+2:endPos])

    def getSysdate(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        mDate = self.getField(banner, "SYSDATE")
        self.timeAt[time.time()] = mDate
        self.addToDict(self.target + "_sysdate", mDate)

        return(mDate)

    def getDatabaseVersion(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        self.version = self.getField(banner, "DATABASE_VERSION")
        self.addToDict(self.target + "_database_version", self.version)
        return(self.version)

    def getDatabaseSid(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        self.sid = self.getField(banner, "DATABASE_ID")
        self.addToDict(self.target + "_database_id", self.sid)
        return(self.sid)
    
    def getSchemaName(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        self.schemaName = self.getField(banner, "SCHEMA_NAME")
        self.addToDict(self.target + "_schema_name", self.schemaName)
        return(self.schemaName)
    
    def getAOLVersion(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        self.aolVersion = self.getField(banner, "AOL_VERSION")
        self.addToDict(self.target + "_aol_version", self.aolVersion)
        return(self.aolVersion)

    def getAppsWebAgent(self):
        if self.dadName is None:
            self.getDAD()
        
        if self._buffer is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target, self.port))
    
            request = "GET /pls/" + self.dadName + "/fnd_web.ping HTTP/1.0\r\n\r\n"
            s.sendall(request)
            banner = s.recv(1024)
            self._buffer = banner
            
            if banner.find("403 Forbidden") > 0: 
                return None
        else:
            banner = self._buffer

        self.webAgent = self.getField(banner, "APPS_WEB_AGENT")
        self.addToDict(self.target + "_apps_web_agent", self.webAgent)
        return(self.webAgent)
    
    def getInternalHostnamePort(self, informationJsp):

        magicStr  = "java.lang.NullPointerException: Host ["
        magicStr2 = "and/or Port ["

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target, self.port))

        request = "GET /OA_HTML/" + informationJsp + " HTTP/1.0\r\n\r\n"
        s.sendall(request)
        line = ""
        banner = ""

        while 1:
            line = s.recv(4096)
            banner += line

            if not line:
                break

        if banner.find("403 Forbidden") > 0: 
            return None

        startPos = banner.find(magicStr)

        if startPos == -1:
            return None
        else:
            startPos = startPos + len(magicStr)
        
        endPos = banner.find("]", startPos+1)

        if endPos == -1:
            return None

        self.databaseHost = banner[startPos:endPos]
        
        startPos = banner.find(magicStr2)
        
        if startPos == -1:
            return None
        else:
            startPos = startPos + len(magicStr2)
        
        endPos = banner.find("]", startPos+1)
        self.databasePort = banner[startPos:endPos]
        
        self.addToDict(self.target + "_internal_db_host", self.databaseHost)
        self.addToDict(self.target + "_internal_db_host", self.databasePort)

    def getInternalData(self):
        self.getInternalHostnamePort("bispmfer.jsp?dbc=a1")
        
        if self.databaseHost is None:
            self.getInternalHostnamePort("bispcust.jsp?dbc=test")

    def getLoginFormPath(self):
        magicStr = 'value="module=/'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target, self.port))

        request = "GET /dev60cgi/f60cgi HTTP/1.0\r\n\r\n"
        s.sendall(request)
    
        line = ""
        banner = ""

        while 1:
            line = s.recv(1024)
            banner += line

            if not line:
                break

        if banner.find("403 Forbidden") > 0: 
            return None

        startPos = banner.find(magicStr)

        if startPos == -1:
            return None
        else:
            startPos = startPos + len(magicStr)
        
        endPos = banner.find(" fndnam=", startPos+1)

        if endPos == -1:
            return None

        self.loginForm = banner[startPos-1:endPos]
        self.addToDict(self.target + "_login_form", self.loginForm)
        return(self.loginForm)

    def getProdComnPath(self):
        magicStr = 'javax.servlet.ServletException: java.io.FileNotFoundException: /'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target, self.port))

        try:
            request = "GET /OA_HTML/.jsp HTTP/1.0\r\n\r\n"
            s.sendall(request)
    
            line = ""
            banner = ""
    
            while 1:
                line = s.recv(1024)
                banner += line
    
                if not line:
                    break
    
            if banner.find("403 Forbidden") > 0: 
                return None
            
            startPos = banner.find(magicStr)
            
            if startPos == -1:
                return None
            else:
                startPos = startPos + len(magicStr)
            
            endPos = banner.find(".jsp", startPos+1)
    
            if endPos == -1:
                return None
    
            self.prodComnPath = banner[startPos-1:endPos]
            self.addToDict(self.target + "_prod_comn_path", self.prodComnPath)
        except:
            self.prodComnPath = None

        return(self.prodComnPath)
    
    def run(self):
        if self.port == 0:
            self.port = 80

        self.getInternalData()
        mAgent = self.getAppsWebAgent()
        mDad = self.getDAD()

        data = "DAD Name         : " + str(mDad) + "\n"
        data += "Sysdate          : " + str(self.getSysdate()) + "\n"
        data += "Database Version : " + str(self.getDatabaseVersion()) + "\n"
        data += "Database Sid     : " + str(self.getDatabaseSid()) + "\n"
        data += "Schema           : " + str(self.getSchemaName()) + "\n"
        data += "AOL Version      : " + str(self.getAOLVersion()) + "\n"
        data += "Apps Web Agent   : " + str(mAgent) + "\n"
        data += "Internal DB Host : " + str(self.databaseHost) + "\n"
        data += "Internal DB Port : " + str(self.databasePort) + "\n"
        data += "Login Form Path  : " + str(self.getLoginFormPath()) + "\n"
        data += "Prod. Comn. Path : " + str(self.getProdComnPath()) + "\n"
        self.__internal_results = data

        return True
    
    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Oracle E-Business Suite 11i Information" )
        self.echo.gom( "---------------------------------------" )
        self.gom.echo( "" )
        self.echo.gom( self.__internal_results )
        self.gom.echo( "" )

if __name__ == "__main__":

    import sys

    objApps = CApps11i()
    #objApps.target = "vis11510ext5.solutionbeacon.net"
    #objApps.target = "vis11510.solutionbeacon.net"
    #objApps.target = "becd.feriadebilbao.com"

    if len(sys.argv) > 1:
        objApps.target = sys.argv[1]
    else:
        objApps.target = "becd.feriadebilbao.com"

    if len(sys.argv) > 2:
        objApps.port = int(sys.argv[2])
    else:
        objApps.port = 8000

    objApps.getInternalData()

    print "DAD Name         : ", objApps.getDAD()
    print "Sysdate          : ", objApps.getSysdate()
    print "Database Version : ", objApps.getDatabaseVersion()
    print "Database Sid     : ", objApps.getDatabaseSid()
    print "Schema           : ", objApps.getSchemaName()
    print "AOL Version      : ", objApps.getAOLVersion()
    print "Apps Web Agent   : ", objApps.getAppsWebAgent()
    print "Internal DB Host : ", objApps.databaseHost
    print "Internal DB Port : ", objApps.databasePort
    print "Login Form Path  : ", objApps.getLoginFormPath()
    print "Prod. Comn. Path : ", objApps.getProdComnPath()


