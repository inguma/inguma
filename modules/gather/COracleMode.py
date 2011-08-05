#!/usr/bin/python

##      COracleMode.py
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
import urllib

from lib.module import CIngumaModule
from lib.libhttp import CIngumaHTMLParser, CIngumaHttp
from lib.libvulnoas import getVulnerableDad

try:
    import cx_Oracle
    oracleSupport = True
except:
    print sys.exc_info()[1]
    oracleSupport = False

name = "oratool"
brief_description = "Oracle wrapper for all related stuff"
type = "gather"

globals = ["dad", "method", "ssl", "injectionPoint"]

class COracleMode(CIngumaModule):

    sid = "orcl"
    dad = None
    method = None
    user = "test"
    password = "test"
    console = False

    colSize = 15
    connection = None

    baseUrl = None
    ssl = False

    injectionPoint = ""

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print "sid = <sid name>"
        print "user = <database's username>"
        print "password = <user's password>"
        print "dad = <dad>"
        print "method = <PL/SQL gateway bypass method>"
        print
        print 'Use dad="?" to autoresolve DAD'

    def show_help(self):
        print
        print "Inguma's Oracle mode help"
        print "-------------------------"
        print
        print "help | h | ?                 Show this help"
        print "exit | quit | ..             Exit from oracle mode"
        print "sql                          Opens an interactive SQL terminal"
        print "sid=<sid>                    Specify the database's SID"
        print "dad=<dad>                    Specify the server's DAD name"
        print "user=<user>                  Specify the user to use"
        print "password=<password>          Specify the password to use"
        print "print <var>                  Print the value of one variable"
        print "set colsize <size>           Set the result's column size"
        print
        print "Any other typed expression will be evaled as a python expression"
        print

    def connect(self):
        if self.dad == None:
            link    = "%s/%s@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%d)))"
            link += "(CONNECT_DATA=(SERVICE_NAME=%s)))"
            link    = link % (self.user, self.password, self.target, int(self.port), self.sid)

            self.connection = cx_Oracle.connect(link)
            self.connection.rollback()
            self.connection.commit()

    def funnySQLCommand(self, sql):
        objHttp = CIngumaHttp("")
        objParser = CIngumaHTMLParser()
        
        self.baseUrl = objHttp.buildUrl(self.target, self.port, self.ssl, "")
        
        if self.injectionPoint == "":
            self.baseUrl = objHttp.buildUrl(self.target, self.port, self.ssl, self.baseUrl + self.dad + self.method + ".cellsprint?p_thequery=" + urllib.quote(sql))
        else:
            self.baseUrl = objHttp.buildUrl(self.target, self.port, self.ssl, self.baseUrl + self.dad + self.injectionPoint.replace("XXX", urllib.quote(sql)))

        res = objHttp.open()
        objParser.feed(res.read())
        objParser.close()

    def runSQLCommand(self, sql, pprint=True, *params):

        """ Are we using a DAD? """
        if self.dad != None:
            self.funnySQLCommand(sql)
            return

        MAGIC_SIZE = self.colSize
        cur = self.connection.cursor()
        cur.execute(sql, *params)

        if sql.lower().find("select") > -1:
            buf = ""
            for col in cur.description:
                buf += col[0].ljust(MAGIC_SIZE) + " "*4

            print buf
            print "-" * len(buf)

            for row in cur.fetchall():
                buf = ""
                for col in row:
                    buf += str(col).ljust(MAGIC_SIZE) + " "*4
                print buf
            print
            print "Total of",cur.rowcount, "row(s) selected."
        else:
            print "Statement executed."

    def sqlLoop(self):
        import lib.ui.cli.core as CLIcore

        self.connect()
        buf = ""
        i = 1
        prompt = 'oratool/sql'

        print "Type ';' or '/' in a single line to run a command. Exit to quit."

        while 1:
            res = CLIcore.unified_input_prompt(self, prompt)
            if res == None:
                break

            tmp = buf + res

            if res.lower().startswith("set colsize"):
                x = res.split(" ")
                self.colSize = int(x[len(x)-1])
                continue
            elif res in [";", "r", "/"]:
                if buf == "":
                    print "No data in buffer"
                    continue

                prompt = "oratool/sql"
                i = 1
                self.runSQLCommand(buf, True)
                buf = ""
            elif res.endswith(";") and tmp[0:5].upper() not in ["BEGIN", "DECLA"]:
                buf += res[:len(res)-1] + "\n"
                prompt = "oratool/sql"
                self.runSQLCommand(buf, True)
                buf = ""
            else:
                buf += res + "\n"
                i += 1
                prompt = " %d   " % i

    def showExploits(self):
        pass

    def runOracleModeLoop(self):
        import lib.ui.cli.core as CLIcore

        dad = self.dad
        sid = self.sid
        port = self.port
        target = self.target
        user = self.user
        password = self.password

        while 1:
            res = CLIcore.unified_input_prompt(self, 'oratool')
            if res == None:
                break

            self.dad = dad
            self.sid = sid
            self.target = target
            self.port = port
            self.user = user
            self.password = password

            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "sql":
                self.sqlLoop()
            elif words[0].lower() == "show" and words[1].lower() == "exploits":
                self.showExploits()
            else:
                try:
                    exec(res)
                except:
                    print "Error:",sys.exc_info()[1]

        return True

    def run(self):
        if not oracleSupport and self.dad == None:
            print "No support for cx_Oracle. Please, install it first."
            return False

        if self.console:
            self.sqlLoop()
        else:
            self.runOracleModeLoop()

        return True
