# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (C) 2011 David Martínez Moreno <ender@debian.org>

I am providing code in this repository to you under an open source license.
Because this is a personal repository, the license you receive to my code
is from me and not my employer (Facebook).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import lib.globals as glob

class CIngumaModule:
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma module.
    This class is deprecated, all the new additions should be done to temporary
    class CIngumaNewModule. """

    target = ''
    ports = []
    sport = 1025
    closed = {}
    opened = {}
    mac = {}
    services = {}
    waitTime = 0
    randomizeWaitTime = False
    timeout = 1
    iface = "eth0"
    results = {}
    dict = None
    interactive = True

    # The following are used ONLY for exploits (shellcode)
    command = ""
    listenPort = 4444
    ostype = 1
    payload = "bindshell"

    def __init__(self):
        """ Constructor. """
        pass

    def help(self):
        """ Method called when 'help <module> is executed from the command
        line."""
        pass

    def run(self):
        """ Method called when the module is invoked.
        If it returns False, execution is stopped there.
        If it returns True, then printSummary() is called after run().
        """
        pass

    def show_help(self):
        """ Method called when the module is interactive and 'help' is executed
        from the command line. """
        pass

    # Legacy methods follow.

    def addToDict(self, element, value):
        """ It's used to add data to the knowledge base to be used, i.e., by
        other modules """
        if value == None:
            return

        if self.dict is not None:
            if self.dict.has_key(element):

                for x in self.dict[element]:
                    if x == value:
                        return

                self.dict[element] += [value]
            else:
                self.dict[element] = [value]

    def getPasswordList(self):
        fname = self.dict["base_path"]
        if fname != "" :
            fname += os.sep + "data" + os.sep + "dict"
        else:
            fname = "data" + os.sep + "dict"

        f = file(fname, "r")
        return f.readlines()

    def printSummary(self):
        """ Method called when run() has returned True.  It's used for showing
        a summary of the execution to the user. """
        pass

class CIngumaNewModule:
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma module.
    This class will supersede CIngumaModule in the future. """

    target = ''
    timeout = 1
    dict = None
    module_type = None

    # Legacy properties follow.

    #ports = []
    #sport = 1025
    #closed = {}
    #opened = {}
    #mac = {}
    #services = {}
    #waitTime = 0
    #randomizeWaitTime = False
    #iface = "eth0"
    #results = {}
    #interactive = True

    def __init__(self):
        """ Constructor. """
        pass

    def add_data_to_kb(self, element, value):
        """ Method used to add data to the current knowledge base. """
        if value == None:
            return

        if self.dict is not None:
            if self.dict.has_key(element):

                for x in self.dict[element]:
                    if x == value:
                        return

                self.dict[element] += [value]
            else:
                self.dict[element] = [value]

    def help(self):
        """Method called when 'help <module> is executed from the command
        line."""
        self.gom.echo("Module has no help information.")

    def print_summary(self):
        """ Method called when run() has returned True.  It's used for showing
        a summary of the execution to the user. """
        pass

    def run(self):
        """ Method called when the module is invoked.
        If it returns False, execution is stopped there.
        If it returns True, then print_summary() is called after run().
        """
        pass

    def help_interactive(self):
        """ Method called when the module is interactive and 'help' is executed
        from the command line. """
        pass

    # Legacy methods follow.

    def addToDict(self, element, value):
        """ Legacy method for adding data to the current KB.  Superseded by
        add_data_to_kb(). """
        self.add_data_to_kb(element, value)

    def printSummary(self):
        """ Method called when run() has returned True.  It's used for showing
        a summary of the execution to the user. Superseded by
        print_summary(). """
        self.print_summary()

    def show_help(self):
        """ Method called when the module is interactive and 'help' is executed
        from the command line. Superseded by help_interactive()."""
        self.help_interactive()

class CIngumaBruteModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma brute-force module. """

    module_type = 'brute'

    def get_password_list(self, base_path):
        """Gets a password list distributed with Inguma"""
        """FIXME: Get the base_path instead from the global or a parameter, from glob.base_path."""

        fname = base_path
        if fname != "" :
            fname += os.sep + "data" + os.sep + "dict"
        else:
            fname = "data" + os.sep + "dict"

        f = file(fname, "r")
        return f.readlines()

class CIngumaDiscoverModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma discover module. """

    module_type = 'discover'

class CIngumaExploitModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma exploit module. """

    module_type = 'exploit'

    # Legacy properties follow.
    # The following are used ONLY for exploits (shellcode).
    #command = ""
    #listenPort = 4444
    #ostype = 1
    #payload = "bindshell"

class CIngumaFuzzerModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma fuzzer module. """

class CIngumaGatherModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma gather module. """

    module_type = 'gather'

class CIngumaRCEModule(CIngumaNewModule):
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma RCE module. """

    module_type = 'rce'
