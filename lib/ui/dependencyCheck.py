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

import os, sys, platform

def gtkui_dependency_check(config):
    '''
    This function verifies that the dependencies that are needed by the GTK user interface are met.
    '''

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    print 'Checking:'
    print '\tGTK UI dependencies...',

    # Check Gtk
    try:
        import pygtk
        pygtk.require('2.0')
        import gtk, gobject
        assert gtk.gtk_version >= (2, 12)
        assert gtk.pygtk_version >= (2, 12)
        print OKGREEN + "\tOK" + ENDC
    except:
        print FAIL + "D'oh!" + ENDC
        msg = 'You have to install GTK and PyGTK versions >=2.12 to be able to run the GTK user interface.\n'
        msg += '    - On Debian-based distributions: apt-get install python-gtk2\n'
        msg += '    - On Mac: sudo port install py25-gtk'        
        print msg
        sys.exit( 1 )

    # Check Scapy
    try:
        print "\tScapy...",
        import scapy.all as scapy
        print OKGREEN + "\t\tOK" + ENDC
    except:
        print FAIL + "\tD'oh!" + ENDC
        print WARNING + "No scapy found" + ENDC
        sys.exit( 1 )

    # Check Network
    try:
        print "\tNetwork connectivity...",
        for net,msk,gw,iface,addr in scapy.read_routes():
            if iface == scapy.conf.iface and gw != '0.0.0.0':
                pass
        if gw:
            print OKGREEN + "\tOK" + ENDC
        else:
            raise Exception("D'Oh!")
    except:
        print FAIL + "\tD'oh!" + ENDC
        print WARNING + "No network connectivity found" + ENDC
        sys.exit( 1 )

    # Check tkSourceView2
    try:
        print "\tGtkSourceView2...",
        import gtksourceview2 as gtksourceview
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "GtkSourceView2 not found, module and exploits editors will be disabled" + ENDC
        config.HAS_SOURCEVIEW = False

    # Check Vte
    try:
        print "\tVTE Terminal...",
        import vte
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "VTE Terminal not found, Sniffer, Scapy, and terminals will be disabled" + ENDC
        config.HAS_VTE = False

    # Check Impacket
    try:
        print "\tImpacket library...",
        import impacket
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "Impacket library not found, some modules would not work" + ENDC

    # Check PySNMP
    try:
        print "\tPySNMP library...",
        import pysnmp
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "PySNMP library not found, some modules would not work" + ENDC

    # Check GeoIP
    try:
        print "\tGeoIP library...",
        import GeoIP
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "GeoIP library not found, some modules would not work" + ENDC
        config.HAS_GEOIP = False

    # Check Nmap
    try:
        print "\t" + config.NMAP_PATH + "...",
        if os.path.exists(config.NMAP_PATH):
            print OKGREEN + "\tOK" + ENDC
        else:
            raise    
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "Nmap not found on: " + config.NMAP_PATH + " some features will be disabled" + ENDC
        config.HAS_NMAP = False

    # Check Graphviz
    print "\tGraphviz binaries...",
    if os.environ.has_key('PATH'):
        for path in os.environ['PATH'].split(os.pathsep):
            progs = __find_executables(path)

            if progs is not None :
                #print progs
                print OKGREEN + "\tOK" + ENDC
                return

        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "Graphviz binaries not found, this software is necessary to run the GUI" + ENDC
        sys.exit( 1 )

#   Not yey necessary
#    # Check w3af
#    try:
#        print "\t" + config.W3AF_PATH + "...",
#        if os.path.exists(config.W3AF_PATH):
#            print OKGREEN + "\tOK" + ENDC
#        else:
#            raise    
#    except:
#        print WARNING + "\tD'oh!" + ENDC
#        print WARNING + "w3af not found on: " + config.W3AF_PATH + " some features will be disabled" + ENDC
#        config.HAS_W3AF = False

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

            #print prg 
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
