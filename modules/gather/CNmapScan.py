#!/usr/bin/python

##      CNmapScan.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import sys, os, string
import lib.ui.nmapParser as nmapParser
from lib.libexploit import CIngumaModule

name = "nmapscan"
brief_description = "A module for port scanning using Nmap"
type = "gather"

class CNmapScan(CIngumaModule):
    target = ""
    interactive = True

    def help(self):
        print "A module for port scanning using Nmap"

    def showHelp(self):
        print 
        print "Inguma's Nmap Interface Help"
        print "------------------------------"
        print
        print "help                     Show this help"
        print "nmaphelp                 Show Nmap's help"
        print "nmap <options>           Execute Nmap with options specified"
        print "exit                     Exit from nmapscan interface"
        print 

    def HelpNmap(self):
        self.gom.echo( os.popen('nmap --help').read() )

    def runNmap(self,  options):
        os.popen(options + " -oX /tmp/nmapxml.xml")
        nmapxml = open('/tmp/nmapxml.xml')
        
        outputs = nmapParser.parseNmap('/tmp/nmapxml.xml')
        nmapxml.close()
        os.remove('/tmp/nmapxml.xml')
        
        for output in outputs:
            
            # Add a new target, hostname and OS
            self.addToDict( 'targets', output['hostip'] )
            self.gom.echo( "Host IP:\t" + output['hostip'] )
            if 'hostname' in output.keys():
                self.addToDict( output['hostip'] + '_name', output['hostname'] )
                self.gom.echo( "Host Name:\t" + output['hostname'] )
            if 'os' in output.keys():
                self.addToDict( output['hostip'] + '_os', output['os'] )
                self.gom.echo( "Host OS:\t" + output['os'] )
        
            # Add Open ports and services
            self.gom.echo( "Host Ports:" )
            for port in output['ports'].keys():
                if output['ports'][port][0] == 'open':
                    self.gom.echo( "\n\tPort: " + port )
                    self.addToDict(output['hostip'] + "_tcp_ports", port)
                    try:
                        self.addToDict(output['hostip'] + "_" + port + '-info', output['ports'][port][1])
                        self.addToDict(output['hostip'] + "_" + port + '-info', output['ports'][port][2])
                        self.gom.echo( "\tInfo 1: " + output['ports'][port][1] )
                        self.gom.echo( "\tInfo 2: " + output['ports'][port][2] )
                    except:
                        pass
        
            # Add traceroute
            self.gom.echo( "\nTraceroute:" )
            for host in output['hops']:
                self.addToDict( 'hosts', host[0] )
                if host[1] != '':
                    self.addToDict( host[0] + '_name', host[1] )
                    self.gom.echo( "\t" + host[0] + "\t-> " + host[1] )
                else:
                    self.gom.echo( "\t" + host[0] )
                self.addToDict( output['hostip'] + '_trace', host[0] )

    def runLoop(self):
        while 1:
            try:
                res = raw_input("NMAP> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "nmap" and len(words)>1:
                mystring = string.join(words, ' ')
                self.runNmap(mystring)
            elif words[0].lower() == "nmaphelp":
                self.HelpNmap()
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() in ["exit", "quit"]:
                break
            else:
                print "Unknow option or command '%s'" % res

    def run(self):

        self.runLoop()

        return True

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
