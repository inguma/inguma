#!/usr/bin/python

"""
Module xmlrpc for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

"""
NOTE: Should be enhanced with an XMLRPC fuzzer
"""

import sys
import xmlrpclib
from lib.libexploit import CIngumaModule

name = "xmlrpc"
brief_description = "Interact with an XMLRPC server"
type = "gather"

class CXmlRpc(CIngumaModule):
    target = ""
    port = 8000
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    dict = None
    url = None
    interactive = True

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"

    def showHelp(self):
        print 
        print "Inguma's XMLRPC Interface Help"
        print "------------------------------"
        print
        print "ls                       List server methods using introspection"
        print "help                     Show this help"
        print "url                      Specify an url to use (do not generate)"
        print "call <data>              Call remote server procedure"
        print "exit                     Exit from xmlrpc interface"
        print 

    def extractApi(self, url):
    
        server = xmlrpclib.Server(url)
    
        data = "API for server running at " + url
        print data
        print "-"*len(data)
        print

        try:
            for method in server.system.listMethods():
                print ""
                print "Method: <object>." + method + "()"
                print "Signatures: " 
                i = 0
    
                try:
                    for signature in server.system.methodSignature(method):
                        i += 1
                        if len(signature) > 0 and type(signature) is list:
                            print str(i) + ": " + str(signature)
                        else:
                            print str(i) + ": " + str(server.system.methodSignature(method))
                            break
                except:
                    print "Error (no introspection?)"
    
                print ""
                print "Description: "
                print ""
                print server.system.methodHelp(method)
        except:
            print "Error.", sys.exc_info()[1]

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
            print ret
        except:
            print "Error:", sys.exc_info()[1]
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
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "ls":
                self.listMethods()
            elif words[0].lower() == "call" and len(words)>1:
                self.callServer(words[1:])
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() == "url" and len(words) > 1:
                self.url = words[1]
            elif words[0].lower() in ["exit", "quit"]:
                break
            else:
                print "Unknow option or command '%s'" % res

    def run(self):
        if self.port == 0 or self.port == "":
            self.port = 80

        if self.interactive:
            self.runLoop()
        else:
            self.listMethods()

        return True

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
