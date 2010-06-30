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

import sys

def gtkui_dependency_check():
    '''
    This function verifies that the dependencies that are needed by the GTK user interface are met.
    '''

    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    print 'Checking:'
    print '\tGTK UI dependencies...',

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
        msg += '    - On Debian based distributions: apt-get install python-gtk2\n'
        msg += '    - On Mac: sudo port install py25-gtk'        
        print msg
        sys.exit( 1 )

    try:
        print "\tScapy...",
        import scapy.all as scapy
        print OKGREEN + "\t\tOK" + ENDC
    except:
        print FAIL + "\tD'oh!" + ENDC
        print WARNING + "No scapy found" + ENDC
        sys.exit( 1 )

    try:
        print "\tNetwork conectivity...",
        net,msk,gw,iface,addr = scapy.read_routes()
        if gw:
            print OKGREEN + "\tOK" + ENDC
        else:
            raise "D'Oh!"
    except:
        print FAIL + "\tD'oh!" + ENDC
        print WARNING + "No network conectivity found" + ENDC
        sys.exit( 1 )

    try:
        print "\tGtkSourceView2...",
        import gtksourceview2 as gtksourceview
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "GtkSourceView2 not found, module and exploits editors will be disabled" + ENDC

    try:
        print "\tVTE Terminal...",
        import vte
        print OKGREEN + "\tOK" + ENDC
    except:
        print WARNING + "\tD'oh!" + ENDC
        print WARNING + "VTE Terminal not found, Sniffer, Scapy, and terminals will be disabled" + ENDC
