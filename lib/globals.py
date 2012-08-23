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

----------------------------------------------------------------------

Global configuration object for Inguma.  It replaces all the 'global'
usage that has become a nightmare in the code."""

version = '0.5-dev'
commands = {}
debug = False
http_server = False
isGui = False
ports = []
listeners = {}

discovers = []
gathers = []
rces = []
fuzzers = []
brutes = []
classes = []
others = []
exploits = []
target=''

GLOBAL_VARIABLES = """
global target; global targets; global port; global covert; global timeout; global waittime;
global otherTargets; global services; global wizard; global user_data; global user;
global password; global domain; global payload; global ostype; global command;
global listenPort; global ignore_host;
"""
