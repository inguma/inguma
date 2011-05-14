#!/usr/bin/env python

#       ginguma.py
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

import sys, os

# go with GTK, but first check about DISPLAY environment variable
if sys.platform != "win32":
    display = os.getenv("DISPLAY")
    if display is None or display.strip() is "":
        print "The DISPLAY environment variable is not set!  Do you have graphical capabilities?"
        sys.exit(1)
import lib.ui.main
# lib.ui.main.main(profile)
lib.ui.main.main()
