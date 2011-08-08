##      CBluetooth.py
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

try:
    import bluetooth
except:
    print "Module bluetooth (pybluez) not found."

from lib.module import CIngumaDiscoverModule

name = "bluetooth"
brief_description = "A simple bluetooth scanner"
type = "discover"

globals = ['mode', ]

class CBluetooth(CIngumaDiscoverModule):
    """ Module for Bluetooth operations. """

    # Default values
    mode = 'discover'
    target = 'all'

    def help(self):
        """ This is the entry point for info <module> """
        self.gom.echo("mode = <discover|gather>")
        self.gom.echo("       <discover: search for bluetooth devices>")
        self.gom.echo("       <gather: gather services of specified device (target)>")
        self.gom.echo("target = <all|localhost|address>")
        self.gom.echo("         <all: gather services of all devices available>")
        self.gom.echo("         <localhost: scan localhost services>")
        self.gom.echo("         <address: scan specified addres>")

    def run(self):
        """ This is the main entry point of the module """

        if self.mode=='discover':
            self.gom.echo("Searching Bluetooth devices...")
            nearby_devices = bluetooth.discover_devices(lookup_names = True)
            self.gom.echo("found " + str(len(nearby_devices)) + " devices")
            for name, addr in nearby_devices:
                self.gom.echo(str(addr) + " " + str(name))
                self.addToDict("blue_hosts", addr)
                self.addToDict(addr + "_addr", name)
            return False

        elif self.mode=='gather':
            self.target = None
            services = bluetooth.find_service(address=self.target)
            if len(services) > 0:
                self.gom.echo("found " + str(len(services)) + " services on " + str(self.target))
                self.gom.echo("")
            else:
                self.gom.echo("no services found")
            
            for svc in services:
                self.gom.echo("Service Name: " +  str(svc["name"]))
                self.gom.echo("    Host:        " + str(svc["host"]))
                self.gom.echo("    Description: " + str(svc["description"]))
                self.gom.echo("    Provided By: " + str(svc["provider"]))
                self.gom.echo("    Protocol:    " + str(svc["protocol"]))
                self.gom.echo("    channel/PSM: " + str(svc["port"]))
                self.gom.echo("    str(svc classes:  " + str(svc["service-classes"]))
                self.gom.echo("    profiles:     " + str(svc["profiles"]))
                self.gom.echo("    service id:   " + str(svc["service-id"]))
                self.gom.echo()
            return False

        else:
            self.gom.echo("Mode " + str(self.mode) + " not valid.")
            return False
