#!/usr/bin/python

##      CDebugger.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

from lib.libexploit import CIngumaModule

name = "debugger"
brief_description = "Userland Debugger"
type = "rce" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

globals = ["gui",  "verbose"]

class CDebugger(CIngumaModule):

    gui = False
    verbose = False

    def help(self):
        """ This is the entry point for info <module> """
        print "verbose = <True/False>"
        print "gui = <True/False>"

    def run(self):
        
        import sys
        sys.path.append('lib/debugger/')        

        import lib.debugger.vdb
        import lib.debugger.vtrace
        import lib.debugger.cobra
        import sys
        import getopt
        import traceback
        
        # Parse options

        if self.verbose == True:
            lib.debugger.vtrace.verbose = True
            lib.debugger.cobra.verbose = True
    
        trace = lib.debugger.vtrace.getTrace()
        db = lib.debugger.vdb.Vdb(trace)

        if self.gui == True:
            import lib.debugger.vdb.gui
            lib.debugger.vdb.gui.domain(db)
        else:
            cli = lib.debugger.vdb.VdbCli(db)

            # Run the staff
    
            while True:
                try:
                    cli.cmdloop()
        
                except KeyboardInterrupt:
                    trace = db.getTrace()
                    if trace:
                        trace.sendBreak()
                    break
            
                except SystemExit:
                    break
        
                except:
                    traceback.print_exc()
        
                return False

    def printSummary(self):
        pass
