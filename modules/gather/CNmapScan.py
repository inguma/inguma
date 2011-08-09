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

import os, string
import lib.ui.nmapParser as nmapParser
from lib.module import CIngumaGatherModule

name = "nmapscan"
brief_description = "A module for port scanning using Nmap"
type = "gather"

class CNmapScan(CIngumaGatherModule):
    interactive = True

    def help(self):
        self.gom.echo("A module for port scanning using Nmap")

    def help_nmap(self):
        self.gom.echo(os.popen('nmap --help').read())

    def show_help(self):
        self.gom.echo()
        self.gom.echo("Inguma's Nmap Interface Help")
        self.gom.echo("------------------------------")
        self.gom.echo()
        self.gom.echo("help                     Show this help")
        self.gom.echo("nmaphelp                 Show Nmap's help")
        self.gom.echo("nmap <options>           Execute Nmap with options specified")
        self.gom.echo("exit                     Exit from nmapscan interface")
        self.gom.echo()

    def run(self):
        import lib.ui.cli.core as CLIcore

        while 1:
            res = CLIcore.unified_input_prompt(self, 'nmapscan')
            if res == None:
                break
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "nmap" and len(words)>1:
                mystring = string.join(words, ' ')
                self.run_nmap(mystring)
            elif words[0].lower() == "nmaphelp":
                self.help_nmap()
            else:
                self.gom.echo("Unknown option or command '%s'" % res)

        return True

    def run_nmap(self, options):
        os.popen(options + " -oX /tmp/nmapxml.xml")
        nmapxml = open('/tmp/nmapxml.xml')
        
        outputs = nmapParser.parseNmap('/tmp/nmapxml.xml')
        nmapxml.close()
        os.remove('/tmp/nmapxml.xml')
        
        for output in outputs:
            
            # Add a new target, hostname and OS
            self.add_data_to_kb( 'targets', output['hostip'] )
            self.gom.echo("Host IP:\t" + output['hostip'])
            if 'hostname' in output.keys():
                self.add_data_to_kb( output['hostip'] + '_name', output['hostname'] )
                self.gom.echo("Host Name:\t" + output['hostname'])
            if 'os' in output.keys():
                self.add_data_to_kb( output['hostip'] + '_os', output['os'] )
                self.gom.echo("Host OS:\t" + output['os'])
        
            # Add open ports and services.
            self.gom.echo("Host Ports:")
            for port in output['ports'].keys():
                if output['ports'][port][0] == 'open':
                    self.gom.echo("\n\tPort: " + port)
                    self.add_data_to_kb(output['hostip'] + "_tcp_ports", port)
                    try:
                        self.add_data_to_kb(output['hostip'] + "_" + port + '-info', output['ports'][port][1])
                        self.add_data_to_kb(output['hostip'] + "_" + port + '-info', output['ports'][port][2])
                        self.gom.echo("\tInfo 1: " + output['ports'][port][1])
                        self.gom.echo("\tInfo 2: " + output['ports'][port][2])
                    except:
                        pass
        
            # Add traceroute
            self.gom.echo("\nTraceroute:")
            for host in output['hops']:
                self.add_data_to_kb( 'hosts', host[0] )
                if host[1] != '':
                    self.add_data_to_kb(host[0] + '_name', host[1])
                    self.gom.echo("\t" + host[0] + "\t-> " + host[1])
                else:
                    self.gom.echo("\t" + host[0])
                self.add_data_to_kb(output['hostip'] + '_trace', host[0])
