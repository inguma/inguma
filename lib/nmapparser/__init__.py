# Copyright (C) 2007 Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
Convenience wrapper for core nmap xml output parser, use this for playing
with your nmap xml files.
"""

from _nmapxmlparser import parse_nmap_xml

__version__ = '0.2.5'
__author__ = 'Guilherme Polo <gpolo@gmail.com>'

DICTKEYS = "options"

def check_adict(func):
    """Check for expected parameter in func."""

    def _checked(cls, adict):
        """Return func in case it received a dict."""
        if isinstance(adict, dict):
            return func(cls, adict)
    
    return _checked

class _NmapParsed(dict):
    """
    A special dict used to facilitate attribute access and listing
    for parsed nmap xml output.
    """

    def __init__(self, adict=None):
        self._active_attrs = []
        if adict:
            self.set_it(adict)


    @check_adict
    def set_it(self, adict):
        """
        Setup a especial dict for the contents of adict.

        You can access the dict keys as instance attributes, ex:
        adict["nmaprun"] = {"start": something}, you can access "start"
        doing: adict.nmaprun.start. You can also list possible options by
        doing adict.options, for example.
        """
        self.update(adict)

        setattr(self, DICTKEYS, adict.keys())
        for key, value in adict.items():
            if isinstance(value, dict):
                setattr(self, key, _NmapParsed(value))

            elif hasattr(value, "__iter__"):
                setattr(self, key, value)
                for indx, item in enumerate(value):
                    value[indx] = _NmapParsed(item)

            else:
                setattr(self, key, value)

            self._active_attrs.append(key)


    def clear(self):
        """Clear current dict content and other attributes created."""
        while self._active_attrs:
            delattr(self, self._active_attrs.pop())
        dict.clear(self)


class NmapParser(object):
    """
    A wrapper over core nmap xml parser.

    After parsing a xml file you can access its dict keys as instance
    attributes. You can also list the options available by doing
    myinstance.options, where myinstance is a NmapParser instance. If
    myinstance.someoption is a dict, it will contain .options too
    (myinstance.someoption.options), otherwise you iterate over it where
    it's items may be a dict, and if it is, it will contain .options too.
    """

    def __init__(self, *discard_elements):
        """
        discard_elements will be used in every parse you may do, but
        you can change it.
        """
        self.parsed = _NmapParsed()
        self.discard = discard_elements


    def __getattr__(self, attr):
        if self.parsed:
            if attr == DICTKEYS:
                return self.parsed.keys()
            else:
                return getattr(self.parsed, attr)


    def parse(self, xml_file):
        """Nothing to see, move along."""
        self.parsed.set_it(parse_nmap_xml(xml_file, *self.discard))
        return self.parsed


    def _get_discard(self):
        """Returns elements that will be discarded."""
        return self.__discarded


    def _set_discard(self, discard):
        """Set new elements to be discarded."""
        if isinstance(discard, str):
            discard = (discard, )

        self.__discarded = discard


    discard = property(_get_discard, _set_discard,
        doc="Set/Get elements to be discarded. Elements that may be discarded "
        "\nare the keys especified in parse return dict: "
        "\n'nmaprun', 'runstats', 'verbose', 'debugging', 'scaninfo', "
        "\n'taskbegin', 'taskend' and 'host'.")

    parse.__doc__ = parse_nmap_xml.__doc__
