#!/usr/bin/python

##      CJsFuzzer.py
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

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from lib.module import CIngumaModule

name = "jsfuzz"
brief_description = "A Javascript object's fuzzer"
type = "fuzzer"

class JsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = file("tools/fuzz/web/fuzz.html", "r").read()

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
