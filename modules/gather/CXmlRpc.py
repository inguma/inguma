##      CXmlRpc.py
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
NOTE: Should be enhanced with an XMLRPC fuzzer
"""

import sys
import xmlrpclib
from lib.module import CIngumaGatherModule

name = "xmlrpc"
brief_description = "Interact with an XMLRPC server"
type = "gather"

class CXmlRpc(CIngumaGatherModule):
    port = 8000
    services = {}
    results = {}
    dict = None
    url = None
    interactive = True

    def help(self):
        self.gom.echo("target = <target host or network>")
        self.gom.echo("port = <target port>")

    def help_interactive(self):
        self.gom.echo()
        self.gom.echo("Inguma's XMLRPC Interface Help")
        self.gom.echo("------------------------------")
        self.gom.echo()
        self.gom.echo("ls                       List server methods using introspection")
        self.gom.echo("help                     Show this help")
        self.gom.echo("url                      Specify an url to use (do not generate)")
        self.gom.echo("call <data>              Call remote server procedure")
        self.gom.echo("exit                     Exit from xmlrpc interface")
        self.gom.echo()

    def extractApi(self, url):

        server = xmlrpclib.Server(url)

        data = "API for server running at " + url
        self.gom.echo(data)
        self.gom.echo("-"*len(data))
        self.gom.echo()

        try:
            for method in server.system.listMethods():
                self.gom.echo()
                self.gom.echo("Method: <object>." + method + "()")
                self.gom.echo("Signatures: ")
                i = 0

                try:
                    for signature in server.system.methodSignature(method):
                        i += 1
                        if len(signature) > 0 and type(signature) is list:
                            self.gom.echo(str(i) + ": " + str(signature))
                        else:
                            self.gom.echo(str(i) + ": " + str(server.system.methodSignature(method)))
                            break
                except:
                    self.gom.echo("Error (no introspection?)")

                self.gom.echo()
                self.gom.echo("Description: ")
                self.gom.echo()
                self.gom.echo(server.system.methodHelp(method))
        except:
            self.gom.echo("Error." + sys.exc_info()[1])

    def listMethods(self):
        if not self.url:
            url = "http://" + self.target + ":" + str(self.port)
        else:
            url = self.url

        self.extractApi(url)

    def callServer(self, data):
        buf = ""
        for x in data:
            buf += x + " "

        server = xmlrpclib.Server("http://" + self.target + ":" + str(self.port))
        ret = None

        try:
            ret = eval("server." + buf)
            self.gom.echo(ret)
        except:
            self.gom.echo("Error:", sys.exc_info()[1])
            return None

        return ret

    def runLoop(self):
        while 1:
            try:
                res = raw_input("XMLRPC> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                self.gom.echo("raw_input:", sys.exc_info()[1])

            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "ls":
                self.listMethods()
            elif words[0].lower() == "call" and len(words)>1:
                self.callServer(words[1:])
            elif words[0].lower() == "help":
                self.help_interactive()
            elif words[0].lower() == "url" and len(words) > 1:
                self.url = words[1]
            elif words[0].lower() in ["exit", "quit"]:
                break
            else:
                self.gom.echo("Unknown option or command '%s'" % res)

    def run(self):
        if self.port == 0 or self.port == "":
            self.port = 80

        if self.interactive:
            self.runLoop()
        else:
            self.listMethods()

        return True
