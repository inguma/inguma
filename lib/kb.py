# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2012 David Martínez Moreno <ender@debian.org>

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

""" This library has functions for accessing the KB. """

import lib.globals as glob

class KnowledgeBase:
    """Main class for a generic Knowledge Base."""

    def __init__(self):
        """Init method"""

        self._kb = {}
        self.set_defaults()

        self.default_filename = 'data.kb'

    def reset(self):
        """Clears the KB and resets it with a fresh set of default values."""
        self._kb.clear()
        self.set_defaults()

    def format_json(self):
        """Returns the KB in JSON format."""

        import json

        return json.dumps(self._kb)

    def format_text(self):
        """Returns the KB in a suitable plain text format."""

        kb = self.get()
        output = ''
        for x in kb:
            if type(kb[x]) == str or type(kb[x]) == int or type(kb[x]) == float or type(kb[x]) == bool:
                output += "%s -> %s\n" % (x, kb[x])
            else:
                output += str(x) + ":\n"
                data = kb[x]

                for y in data:
                    output += "  %s\n" % y

        return output

    def get(self):
        """Generic getter.  Right now it just gives you a dictionary."""
        return self._kb

    def load(self, filename=''):
        """Loads a new KB into the global space"""
        # FIXME: This version of the function is just for console.  Pretty
        # lame, I know, but I brought it from inguma.py.  We'll have to extend
        # it in some way for ginguma before using this class there.

        import pickle
        import sys

        if not filename:
            filename = self.default_filename

        try:
            input = open(filename, 'r')
            # Update has to be careful, as we have references to this object
            # in the globals module.
            self._kb.clear()
            self._kb.update(pickle.load(input))

            if not glob.target:
                if self._kb.has_key('target'):
                    glob.gom.echo('Setting target (%s)' % self._kb['target'])
                    glob.target = self._kb['target']

            input.close()
        except:
            # FIXME: Only for console!!
            print 'Error loading knowledge base:', sys.exc_info()[1]

    def save(self, filename=''):
        """Saves a KB to disk"""

        import pickle
        import sys

        if not filename:
            filename = self.default_filename

        try:
            if glob.target:
                self._kb['target'] = glob.target

            output = open(filename, 'wb')
            pickle.dump(self._kb, output)
            output.close()
        except:
            # FIXME: Only for console!!
            print "Error saving knowledge base:", sys.exc_info()[1]

    def set_defaults(self):
        """Sets a list of default values in the KB."""

        import os
        import sys

        self._kb['target'] = ''
        self._kb['targets'] = []
        self._kb['port'] = ''
        self._kb['covert'] = 0
        self._kb['timeout'] = 5
        self._kb['user'] = ''
        self._kb['password'] = ''
        self._kb['waittime'] = ''
        self._kb['services'] = []
        self._kb['hosts'] = []
        self._kb['wizard'] = []
        self._kb['base_path'] = os.path.dirname(sys.argv[0])
        self._kb['dict'] = self._kb['base_path'] + 'data' + os.sep + 'dict'
        self._kb['ports'] = glob.ports

