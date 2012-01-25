##      XXX.py
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

from lib.module import CIngumaGatherModule

name = "example"
brief_description = "An example module"
type = "gather" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

class CExampleModule(CIngumaGatherModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

    def help(self):
        """ This is the entry point for info <module> """
        self.gom.echo("target = <target host or network>")
        self.gom.echo("port = <target port>")
        self.gom.echo("timeout = <timeout>")

    def run(self):
        """ This is the main entry point of the module """
        self.gom.echo("Honexek ez dau ezebe eitten, aldatu zeozer ein daian ostixe!")
        return False
