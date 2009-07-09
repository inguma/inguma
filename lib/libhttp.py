#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import sys
import urllib2
import exceptions

from urlparse import urlparse
from HTMLParser import HTMLParser

# BEGIN
# The following piece of code was found at:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/267197
# BEGIN

class HTTPRealmFinderHandler(urllib2.HTTPBasicAuthHandler):
    realm = ""

    def http_error_401(self, req, fp, code, msg, headers):
        realm_string = headers['www-authenticate']
        
        q1 = realm_string.find('"')
        q2 = realm_string.find('"', q1+1)
        realm = realm_string[q1+1:q2]
        
        self.realm = realm

class HTTPRealmFinder:
    def __init__(self, url):
        self.url = url
        scheme, domain, path, x1, x2, x3 = urlparse(url)

        handler = HTTPRealmFinderHandler()
        handler.add_password(None, domain, 'test', 'test')
        self.handler = handler

        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    def ping(self, url):
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            pass

    def get(self):
        self.ping(self.url)
        try:
            realm = self.handler.realm
        except AttributeError:
            realm = None
        
        return realm

    def prt(self):
        print self.get()

# END
# The following piece of code was found at:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/267197
# END

class IngumaHttpException(exceptions.Exception):

    msg = ""

    def __init__(self):
        return
    
    def __str__(self):
        return self.msg

class CIngumaHttp:

    url = None

    def __init__(self, aurl = None):
        self.url = aurl

    def buildUrl(self, target, port = 80, ssl = False, url = None):

        if url:
            self.url = url
        else:
            url = self.url

        if port == 0:
            port = 80

        if url == None:
            x = IngumaHttpException()
            x.msg = "No url specified"
            raise x

        if not url.startswith("/"):
            return url

        if ssl:
            tmp = "https://"
        else:
            tmp = "http://"

        tmp += target + ":" + str(port) + url
        self.url = tmp

        return self.url

    def open(self, webuser=None, webpass=None):

        if not self.url:
            x = IngumaHttpException()
            x.msg = "No url specified"
            raise x
        
        url = self.url

        if webuser:
            scheme, domain, path, x1, x2, x3 = urlparse(url)
            realm = ""

            finder = HTTPRealmFinder(url)
            realm = finder.get()

            handler = urllib2.HTTPBasicAuthHandler()
            handler.add_password(realm, url, webuser, webpass)

            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)

        return urllib2.urlopen(url)

class CIngumaHTMLParser(HTMLParser):

    ignoreIt = False

    def handle_starttag(self, tag, attrs):
        if str.upper(tag) == "SCRIPT":
            self.ignoreIt = True

    def handle_endtag(self, tag):
        if str.upper(tag) == "SCRIPT":
            self.ignoreIt = False

    def handle_data(self, data):
        if self.ignoreIt:
            return

        if len(data) > 1:

            if data[0:1] == '\r' or data[0:1] == '\n':
                data = data[1:]

            print str(data)
