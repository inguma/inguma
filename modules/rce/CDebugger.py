#!/usr/bin/python

"""
Module Debugger for Inguma
Copyright (c) 2007 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""

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
