#       dependencyCheck.py
#
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
#       Based on code from w3af by Andres Riancho (w3af.sourceforge.net)
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

from __future__ import print_function
import os, sys, platform


def gtkui_dependency_check(config):
    '''
    This function verifies that the dependencies that are needed by the GTK user interface are met.
    '''

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    print('Checking:')
    print('\tGTK UI dependencies...', end='')

    # Check Gtk
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        assert Gtk.get_major_version(), Gtk.get_minor_version() >= (3, 14)
        print(OKGREEN + "\tOK" + ENDC)
    except:
        print(FAIL + "D'oh!" + ENDC)
        msg = 'You have to install GTK and GObject versions >=3.14 to be able to run the GTK user interface.\n'
        msg += '    - On Debian-based distributions: apt-get install python-gi gir1.2-gtk-3.0\n'
        msg += '    - On Mac: read the Installation instructions in the README'
        print(msg)
        sys.exit(1)

    # Check Scapy
    try:
        print("\tScapy...", end='')
        import scapy.all as scapy
        print(OKGREEN + "\t\tOK" + ENDC)
    except:
        print(FAIL + "\tD'oh!" + ENDC)
        print(WARNING + "No scapy found" + ENDC)
        sys.exit(1)

    # Check Network
    try:
        print("\tNetwork connectivity...", end='')
        for net, mask, gw, iface, addr, metric in scapy.read_routes():
            if iface == scapy.conf.iface and gw != '0.0.0.0':
                pass
        if gw:
            print(OKGREEN + "\tOK" + ENDC)
        else:
            raise Exception("D'Oh!")
    except:
        print(FAIL + "\tD'oh!" + ENDC)
        print(WARNING + "No network connectivity found" + ENDC)
        sys.exit(1)

    # Check GtkSource
    try:
        print("\tGtkSource...", end='')
        gi.require_version('GtkSource', '3.0')
        from gi.repository import GtkSource
        print(OKGREEN + "\tOK" + ENDC)
        # Having GtkSource enables Bokken and hell breaks loose.
        print(WARNING + "GtkSource found but force-disabled, module and exploits editors will be disabled" + ENDC)
        config.HAS_SOURCEVIEW = False
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "GtkSource not found, module and exploits editors will be disabled" + ENDC)
        config.HAS_SOURCEVIEW = False

    # Check Vte
    try:
        print("\tVTE Terminal...", end='')
        gi.require_version('Vte', '2.91')
        from gi.repository import Vte
        print(OKGREEN + "\tOK" + ENDC)
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "VTE Terminal not found, Sniffer, Scapy, and terminals will be disabled" + ENDC)
        config.HAS_VTE = False

    # Check Impacket
    try:
        print("\tImpacket library...", end='')
        import impacket
        print(OKGREEN + "\tOK" + ENDC)
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "Impacket library not found, some modules will not work" + ENDC)

    # Check PySNMP
    try:
        print("\tPySNMP library...", end='')
        import pysnmp
        print(OKGREEN + "\tOK" + ENDC)
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "PySNMP library not found, some modules will not work" + ENDC)

    # Check GeoIP
    try:
        print("\tGeoIP library...", end='')
        import GeoIP
        print(OKGREEN + "\tOK" + ENDC)
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "GeoIP library not found, some modules will not work" + ENDC)
        config.HAS_GEOIP = False

    # Check Nmap
    try:
        print("\t" + config.NMAP_PATH + "...", end='')
        if os.path.exists(config.NMAP_PATH):
            print(OKGREEN + "\tOK" + ENDC)
        else:
            raise
    except:
        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "Nmap not found on: " + config.NMAP_PATH + ", so some features will be disabled" + ENDC)
        config.HAS_NMAP = False

    # Check Graphviz
    print("\tGraphviz binaries...", end='')
    if os.environ.has_key('PATH'):
        for path in os.environ['PATH'].split(os.pathsep):
            progs = __find_executables(path)

            if progs is not None :
                print(OKGREEN + "\tOK" + ENDC)
                return

        print(WARNING + "\tD'oh!" + ENDC)
        print(WARNING + "Graphviz binaries not found, this software is necessary to run the GUI" + ENDC)
        sys.exit(1)


def __find_executables(path):
    # Code borrowed from pydot
    # http://code.google.com/p/pydot/
    # Thanks to Ero Carrera

    """Used by find_graphviz

    path - single directory as a string

    If any of the executables are found, it will return a dictionary
    containing the program names as keys and their paths as values.

    Otherwise returns None
    """

    success = False
    if platform.system() != 'Windows':
        progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': '', 'sfdp': ''}
    else:
        progs = {'dot.exe': '', 'twopi.exe': '', 'neato.exe': '', 'circo.exe': '', 'fdp.exe': '', 'sfdp.exe': ''}

    was_quoted = False
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
        was_quoted =  True

    if os.path.isdir(path) :

        for prg in progs.iterkeys():

            if progs[prg]:
                continue

            if os.path.exists( os.path.join(path, prg) ):

                if was_quoted:
                    progs[prg] = '"' + os.path.join(path, prg) + '"'
                else:
                    progs[prg] = os.path.join(path, prg)

                success = True

    if success:
        return progs

    else:
        return None
