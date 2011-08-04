#!/usr/bin/python

##      CSubdomainer.py
#       
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
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

#
#       Some code used from quickrecon (http://code.google.com/p/quickrecon/)
#

import random
import socket
import pprint
import httplib

from lib.module import CIngumaModule

name = "subdomainer"
brief_description = "Find subdomains for a given domain"
type = "discover"

class CSubdomainer(CIngumaModule):

    exploitType = 0
    results = {}
    wizard = False

    database = [
                "adm", "admin", "admins", "agent", "aix", "alerts", "av", "antivirus", "app", "apps", "appserver",
                "archive", "as400", "auto", "backup", "banking", "bbdd", "bbs", "bea", "beta", "blog", "catalog",
                "cgi", "channel", "channels", "chat", "cisco", "client", "clients", "club", "cluster", "clusters",
                "code", "commerce",    "community", "compaq", "console", "consumer", "contact", "contracts", "corporate",
                "ceo", "cso", "cust", "customer", "data", "bd", "db2", "default", "demo", "design",    "desktop", "dev",
                "develop", "developer", "device", "dial", "digital", "dir",    "directory", "disc", "discovery", "disk",
                "dns", "dns1", "dns2", "dns3", "docs", "documents", "domain", "domains", "dominoweb", "download",
                "downloads", "ecommerce", "e-commerce", "edi", "edu", "education", "email", "enable", "engine",
                "engineer",    "enterprise", "event", "events", "example", "exchange", "extern", "external", "extranet",
                "fax", "field", "finance", "firewall", "forum", "forums", "fsp", "ftp",    "ftp2", "fw", "fw1", "gallery",
                "galleries", "games", "gateway", "gopher", "guest",    "gw", "hello", "helloworld", "help", "helpdesk",
                "helponline", "hp", "ibm", "ibmdb",    "ids", "ILMI", "images", "imap", "imap4", "img", "imgs", "info",
                "intern", "internal", "intranet", "invalid", "iphone", "ipsec", "irc", "ircserver", "jobs", "ldap",
                "link",    "linux", "lists", "listserver", "local", "localhost", "log", "logs", "login", "lotus", "mail",
                "mailboxes", "mailhost", "management", "manage", "manager", "map", "maps", "marketing", "device",
                "media", "member", "members", "messenger", "mngt", "mobile", "monitor", "multimedia", "music", "names",
                "net", "netdata", "netstats", "network", "news", "nms", "nntp", "ns", "ns1", "ns2", "ns3", "ntp",
                "online", "openview", "oracle",    "outlook", "page", "pages", "partner", "partners", "pda", "personal",
                "ph", "pictures", "pix", "pop", "pop3", "portal", "press", "print", "printer", "private", "project",
                "projects", "proxy", "public", "ra", "radio", "raptor", "ras", "read", "register", "remote", "report",
                "reports", "root", "router", "rwhois", "sac", "schedules", "scotty", "search", "secret", "secure",
                "security", "seri", "serv", "serv2", "server", "service", "services", "shop", "shopping", "site", "sms",
                "smtp", "smtphost", "snmp", "snmpd", "snort", "solaris", "solutions", "support", "source", "sql", "ssl",
                "stats", "store", "stream", "streaming", "sun", "support", "switch", "sysback", "system", "tech",
                "terminal", "test", "testing", "testing123", "time", "tivoli", "training", "transfers",    "uddi",
                "update", "upload", "uploads", "video", "vpn", "w1", "w2", "w3", "wais", "wap",    "web", "webdocs",
                "weblib", "weblogic", "webmail", "webserver", "webservices", "websphere", "whois", "wireless", "work",
                "world", "write", "ws", "ws1", "ws2", "ws3", "www1", "www2", "www3", "error", "cpanel", "my"
                    ]
    
    agents = [
                "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                "Opera/9.80 (Windows NT 5.1; U; pl) Presto/2.8.131 Version/11.10",
                "Links (2.3pre1; Linux 2.6.38-8-generic i686; 160x40)",
                "Mozilla/5.0 (X11; Linux i686; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                "Lynx/2.8.8dev.7 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.8.6",
                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24",
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
                "Mozilla/5.0 (compatible; Konqueror/4.6; Linux) KHTML/4.6.0 (like Gecko) SUSE",
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.10) Gecko/20101005 Fedora/3.6.10-1.fc14 Firefox/3.6.10",
                "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
                ]

    def help(self):
        self.gom.echo( "target = <target domain. ej: example.com>" )

    def test_wildcard(self):
        self.gom.echo( "Testing wildcard..." )
        results = []
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        for count in range(3):
            random_charset = random.sample(charset, random.randint(6, 12))
            subdomain = "%s.%s" % ("".join(random_charset), self.target)
            try:
                connection = httplib.HTTPConnection(subdomain)
                connection.putrequest("GET", "/")
                connection.putheader("User-Agent", random.choice( self.agents ))
                connection.endheaders()
                response = connection.getresponse()
                results.append(response.status)
            except:
                pass
    
        if not results:
            #self.gom.echo( "\tFalse" )
            return False
        else:
            #self.gom.echo( "\tTrue" )
            return True
    
    def check_host(self, hostname):
        #self.gom.echo( "\t\tSearching for: " + hostname )
        try:
            ip = socket.gethostbyname(hostname)
            self.results[hostname] = ip
            #self.gom.echo( "OK -> " + ip )
        except:
            #self.gom.echo( "Meeec!" )
            pass
    
    def find_subdomains(self):
        if self.test_wildcard() is True:
            self.gom.echo( "The target domain has a DNS wildcard configuration." )
            return
        else:
            # Internal dictionary
            self.gom.echo( "Searching subdomains..." )
            for item in self.database:
                subdomain = "%s.%s" % (item, self.target)
                self.check_host(subdomain)
    
        if not self.results:
            self.gom.echo( "\tNothing found." )
            return False
        else:
            return True

    def run(self):
        self.results = {}
        self.find_subdomains()

        return True

    def printSummary(self):
        for domain in self.results.keys():
            self.gom.echo( "Domain: %s:\tIP: %s" % (domain, self.results[domain]) )
            #self.gom.echo( "Adding to discovered hosts " + self.results[domain] )
            self.addToDict("targets", self.results[domain])
            self.addToDict(self.results[domain] + "_name", domain)
