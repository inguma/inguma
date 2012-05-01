# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2011 David Martínez Moreno <ender@debian.org>

I am providing code in this repository to you under an open source license.
Because this is a personal repository, the license you receive to my code
is from me and not my employer (Facebook).

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

""" This library has HTTP functions used in the web UI server. """

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading
import lib.globals as glob
import lib.ui.cli.core as uicore

class IngumaHttpServer(threading.Thread):

    def __init__(self, port=4545):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        self.http = HTTPServer(('', self.port), HttpHandler)
        self.http.serve_forever()

    def terminate(self):
        self.http.shutdown()

class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        uicore.debug_print('Request from %s' % self.client_address[0])
        self.send_response(200)
        self.send_header('Content-type:', 'text/html')
        self.end_headers()
        self.wfile.write('<b>You are %s on port %d</b>\n' % self.client_address)
        self.wfile.flush()

    def log_message(self, format, *args):
        if not glob.debug:
            pass
        else:
            BaseHTTPRequestHandler.log_message(self, format, *args)
