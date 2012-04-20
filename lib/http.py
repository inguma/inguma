# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2011-2012 David Martínez Moreno <ender@debian.org>

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

import threading
import web

class IngumaHttpServer(threading.Thread):

    def __init__(self, port=4545):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        urls = (
                '/', 'RestIndex',
                '/kb(|/.*)', 'RestKB',
               )

        self.http = web.application(urls, globals())
        web.httpserver.runsimple(self.http.wsgifunc(), ('0.0.0.0', self.port))
        #self.http = HTTPServer(('', self.port), HttpHandler)
        #self.http.serve_forever()

    def terminate(self):
        raise KeyboardInterrupt
        #self.http.shutdown()

class RestIndex:

    def GET(self, path):
        return "Inguma"

class RestKB:

    def GET(self, path):
        #raise web.forbidden()
        response = """
        """
        return response
