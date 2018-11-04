# -*- coding: utf-8 -*-
#
#       Inguma Penetration Testing Toolkit
#       Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es
#       Copyright (c) 2011 David Martínez Moreno <ender@debian.org>
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

""" This library has core functions used in Inguma that don't fit anywhere
else. """

import os
import sys

import lib.globals as glob
import lib.ui.cli.core as clicore

try:
    import scapy.all as scapy
    from scapy.modules.nmap import *
    bHasScapy = True
except:
    bHasScapy = False

def int2hex(integer):
    """ Convert an integer to hex """

    string = str(hex(integer))
    string = string.replace("0x", "")

    if len(string) == 1:
        string = "0" + string

    return eval("'\\x" + str(string) + "'")

def str2uni(data):
    """ Convert a python string to unicode. NOT to a python unicode object """
    buf = ""

    for char in data:
        buf += char + "\x00"

    return buf

def regexp2pyre(regexp):
    """ Convert a Perl regular expression to a Python-compatible regular
    expression """
    buf = regexp

    # Remove starting slash
    if buf.startswith("/"):
        buf = buf[1:]

    idx = len(buf)
    i = 0
    while 1:
        #
        # Remove ending slash plush modifiers, i.e.: /<regexp>/si
        #
        if buf[idx-i:idx-i+1] == "/":
            buf = buf[:idx-i]
            break

        i += 1

    return buf

def is_ip_addr4(data):
    """ Verification function for IPv4 addresses """
    x = data.split("/")

    if len(x) == 1:
        x = data.split(".")
    else:
        x = x[0].split(".")

    if len(x) == 4:
        for y in x:
            if not y.isalpha():
                try:
                    if int(y) > 256:
                        return False
                except:
                    return False
        return True
    return False

def getMacVendor(mac):
    """ Extract the card vendor from a MAC address """
    try:
        path = conf.nmap_base.replace('os-fingerprints', 'mac-prefixes')
        mac = mac.replace(":", "")

        f = file(path, "r")

        for line in f:
            if line.startswith("#"):
                pass # Ignore, just a comment
            elif line.replace(" ", "") == "":
                pass # Ignore, blank line
            else:
                prefix = line[0:6]
                vendor = line[7:]

                if mac.lower().startswith(prefix.lower()):
                    return vendor.replace("\r", "").replace("\n", "")

        return "Unknown"
    except:
        return "Unknown"# + str(sys.exc_info()[1])

def getProtocolName(proto):
    try:
        for x in scapy.conf.protocols.keys():
            if scapy.conf.protocols[x] == proto:
                return x
    except:
        pass

    return proto

def check_args():
    '''Checks arguments in the command line to trigger special options.'''

    for arg in sys.argv:
        if arg.lower() == "-d" or arg.lower() == "--debug":
            glob.debug = True
        elif arg.lower() == "-w":
            glob.http_server = True
        elif arg.lower() == "-h" or arg.lower() == "--help":
            clicore.usage(glob.gom)
            sys.exit(0)

    return True

def check_distorm_lib(path):
    """Returns True if the distorm library exists at the supplied path"""

    return os.path.isfile(path + 'libdistorm64.so')

def create_profile_dir():
    """ Tries to create ~/.inguma in the user's homedir. """

    inguma_homedir = get_profile_file_path('')

    try:
        if not os.path.exists(inguma_homedir):
            os.mkdir(inguma_homedir, 0700)
        if not os.path.exists(inguma_homedir + 'data'):
            os.mkdir(inguma_homedir + 'data', 0700)
        return True
    except:
        print "Cannot create " + inguma_homedir + ' or one of its subdirectories.'
        return False

def get_profile_file_path(item):
    """ This function returns the proper file path for loading/saving personal
    data in user's homedir. """

    return os.path.expanduser(os.path.join('~', '.inguma', item))
