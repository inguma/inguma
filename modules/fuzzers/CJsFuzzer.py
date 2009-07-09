#!/usr/bin/python

"""
Module JavaScript object fuzzer for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""

import sys

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from lib.libexploit import CIngumaModule

name = "jsfuzz"
brief_description = "A Javascript object's fuzzer"
type = "fuzzer"

class JsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = file("modules/fuzz/web/fuzz.html", "r").read()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.wfile.write(data)

        return

class CJsFuzzer(CIngumaModule):

    def help(self):
        print "port    = <port>"
        print "timeout = <timeout>"

    def run(self):
    
        if self.port == 0 or self.port is None:
            self.port = 10000

        try:
            print "[+] Listening at http://*:%d/" % self.port
            server = HTTPServer(("", self.port), JsHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()

        return False

    def printSummary(self):
        pass
