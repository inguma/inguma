#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
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
NOTE: Subject to change!
"""
import random

wordsToRandomize = ["CREATE ", " OR ", "REPLACE ", "SELECT ", "FROM ", " WHERE ", " IS ", " NOT ", " NULL ",
                                    "PRAGMA ", "AUTONOMOUS_TRANSACTION", "EXECUTE ", "IMMEDIATE ", " FUNCTION ", "PROCEDURE ",
                                    "GRANT ", " TO ", " DBA ", " AUTHID ", " CURRENT_USER "]

def getRandomSpaces(min = 0, max = 50, comments = True):

    tmp = ""
    for i in range(min, max):
        if comments:
            num = random.randint(1, 5)
        else:
            num = random.randint(1, 3)
        
        if num == 1:
            tmp += " "
        elif num == 2:
            tmp += "\t"
        elif num == 3:
            tmp += "\n"
        else:
            tmp += "/*" + getRandomSpaces(comments = False) + "*/"
    
    return tmp

def randomizeSpaces(data):
    
    tmp = data
    for word in wordsToRandomize:
        tmp = tmp.replace(word, getRandomSpaces(0,5) + word + getRandomSpaces(0,5))
    
    return tmp
