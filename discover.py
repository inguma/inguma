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

import sys

from inguma_module import *

def doDiscover(vars):

    targets = ()

    if not vars:
        print "INTERNAL ERROR: No one variable was passed"
        return False
    else:
        target = vars[0]
        port = vars[1]
        covert = vars[2]
        timeout = vars[3]
        waittime = vars[4]
        wizard = vars[5]
        modules = vars[6]

    try:
        if target == "":
            mTarget = raw_input("Target: ")
        else:
            mTarget = target
    
        vars = (mTarget, port, covert, timeout, waittime, wizard)

        print 
        print "Available modules:"
        print

        index = 0
        for x in modules:
            print "\t",index+1,x.name,"  \t",x.brief_description
            index += 1

        print
        res = raw_input("Select module [all]: ")

        try:
            if res.lower() == "all" or res.lower() == "":
                for x in modules:
                    targets += runModule(vars, x)
            else:
                targets += runModule(vars, modules[int(res)-1])
        except KeyboardInterrupt:
            print "Aborted."
        except EOFError:
            print "Aborted."
        except:
            print "Internal error:",sys.exc_info()[1]

        tmp = (mTarget, )
        tmp += cleanTargets(targets)
        ret = cleanTargets(tmp)

        return ret
    except KeyboardInterrupt:
        print "Aborted."
    except EOFError:
        print "Aborted."
    except:
        print "Error from module:",sys.exc_info()[1]
        return

def cleanTargets(targets):

    ret = ()
    
    for x in targets:
        bFound = False
        for y in ret:
            if y == x:
                bFound = True
                break
            else:
                bFound = False
                
        if not bFound:
            ret += (x, )

    return ret
