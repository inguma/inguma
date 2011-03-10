#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit

Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

"""
NOTE: Should be rewritten from scratch!!!
"""

import sys
import pprint

baseVars = ["target", "otherTargets", "services", "port", "covert", 
                    "timeout", "waittime", "wizard", "user", "password"]

def generateReport(data, host=''):

    DATA = ''
 
    if data.has_key("hosts") and host == '':
        for host in data["hosts"]:
            title = "Report for host %s" % host
            print title
            DATA += title + '\n'
            print "-"*len(title)
            DATA += "-"*len(title) + '\n'
            print
            DATA += '\n'

            for x in data:
                if x.startswith(host + "_"):
                    field = str(x[len(host)+1:]).upper()

                    if type(data[x][0]) is dict:
                        print str(field) + ":"
                        DATA += str(field) + ":\n"

                        for y in data[x][0]:
                            print "\t", str(y).upper() +':', data[x][0][y]
                            DATA += "\t", str(y).upper() +':\n', data[x][0][y] + '\n' 
                    else:
                        if len(data[x]) == 1:
                            print field + ':\t', data[x][0]
                            DATA += field + ':\t' + str(data[x][0]) + '\n'
                        else :
                            print field + ':'
                            DATA += field + ':\n'
                            for element in data[x]:
                                print "\t" + str(element)
                                DATA += "\t" + str(element) + '\n'
            print
            DATA += '\n'
    else:
        title = "Report for host %s" % host
        print title
        DATA += title + '\n'
        print "-"*len(title)
        DATA += "-"*len(title) + '\n'
        print
        DATA += '\n'

        for x in data:
            if x.startswith(host + "_"):
                field = str(x[len(host)+1:]).upper()

                if type(data[x][0]) is dict:
                    print str(field) + ":"
                    DATA += str(field) + ":\n"

                    for y in data[x][0]:
                        print "\t", str(y).upper() +':', data[x][0][y]
                        DATA += "\t", str(y).upper() +':\n', data[x][0][y] + '\n' 
                else:
                    if len(data[x]) == 1:
                        print field + ':\t', data[x][0]
                        DATA += field + ':\t' + str(data[x][0]) + '\n'
                    else :
                        print field + ':'
                        DATA += field + ':\n'
                        for element in data[x]:
                            print "\t" + str(element)
                            DATA += "\t" + str(element) + '\n'
        print
        DATA += '\n'

    return DATA
