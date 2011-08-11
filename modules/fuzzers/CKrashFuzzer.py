##      CKrashFuzzer.py
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

from lib.krash import KrashLib
from lib.module import CIngumaFuzzerModule

name = "krash"
brief_description = "Krash, a block-based fuzzer"
type = "fuzzer"

class CKrashFuzzer(CIngumaFuzzerModule):
    """ Block-based fuzzer. """

    def __init__(self):

        self.file = ''
        self.sindex = 0
    
        self.line = False
        self.ssl = False
        self.url = False
        self.health = False
    
        self.wait_time = 0

    def help(self):
        self.gom.echo("target = <target IP>")
        self.gom.echo("port   = <target port>")
        self.gom.echo("file   = <file with packet dump>")
        self.gom.echo("sindex = <start index>")
        self.gom.echo()
        self.gom.echo("Optional flags:")
        self.gom.echo()
        self.gom.echo("line   = <Line mode: True/False>")
        self.gom.echo("         Send one line at a time")
        self.gom.echo("ssl    = <SSL mode: True/False>")
        self.gom.echo("         Send data over an SSL channel")
        self.gom.echo("url    = <URL mode: True/False>")
        self.gom.echo("         Encode arguments as in HTTP requests")
        self.gom.echo("health = <Health mode: True/False>")
        self.gom.echo("         Disable healthy checks to gain speed")

    def run(self):
        self.krash = KrashLib(self.gom)
        if self.file and self.target and self.port:
            self.krash.fuzz(file(self.file, "r").read(), self.target, self.port, self.sindex)
        else:
            self.gom.echo("Target, port and file parameters are mandatory.")
            return False

    def stop(self):
        self.krash.stop = True
