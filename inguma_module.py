"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

"""
NOTE: Why have I this in a separated module???
"""

import sys
import lib.globals as glob

def runModule(vars, module, dict, om=None):
    objModule = eval("module."+module.__name__ +"()")
    objModule.dict = dict
    objModule.gom = om

    for x in vars:
        if not x.startswith("_") and type(vars[x]) is not type(sys) and str(x) not in ['showHelp']:
            try:
                exec("objModule." + x + " = vars[x]")
            except:
                print "ERROR", sys.exc_info()[1]

    if objModule.run():
        objModule.print_summary()

        if glob.isGui == True:
            objModule.gom.uicore.getDot(False)
            objModule.gom.update_graph()
            #objModule.gom.map.set_dotcode( dict['dotcode'] )

            objModule.gom.kbwin.update_targets_tree()
            #objModule.gom.map.set_filter('twopi')
            #objModule.gom.map.zoom_to_fit()
        return dict

def runGatherModule(vars, module, dict, om=None):
    return runModule(vars, module, dict, om)
