# lib/ui/cli/core.py
# encoding: utf-8

"""
Copyright 2011 David Martínez Moreno <ender@debian.org>

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

----------------------------------------------------------------------

This library offers functions for the CLI version of Inguma.
"""

import sys
import lib.globals as glob

def debug_print(*args):
    """Prints a debug message on the terminal."""
    # FIXME: This should be a method in the gom object.

    # Print debug messages if debug is activated (run with -d)
    if not glob.debug:
        return

    output_string = ""
    for arg in args:
        output_string += str(arg) + " "

    print output_string

def show_exploit_info(cmd):

    for mod in glob.exploits:
        if mod.name == cmd.lower():
            try:
                glob.gom.echo("Information")
                glob.gom.echo("-----------")
                glob.gom.echo()
                glob.gom.echo("Name: " + mod.name)
                glob.gom.echo("Type: " + mod.category)
                glob.gom.echo("Discoverer: " + mod.discoverer)
                glob.gom.echo("Module author: " + mod.author)
                glob.gom.echo("Description: " + mod.brief_description)
                glob.gom.echo("Affected versions:")
                glob.gom.echo()
                for affected in mod.affects:
                    glob.gom.echo("\t" + affected)
                glob.gom.echo()
                glob.gom.echo("Notes:\r\n" + mod.description)
                glob.gom.echo()
                glob.gom.echo("Patch information: " + mod.patch)
                glob.gom.echo()
            except:
                glob.gom.echo("Error getting module's information: " + sys.exc_info()[1])

            return

    for command in glob.commands:
        if command == cmd.lower():
            try:
                module = glob.commands[command]
                if module.__name__.isalnum():
                    obj = eval("module."+module.__name__ +"()")
                    # FIXME: Remove this when all the modules have been converted to glob.gom.
                    obj.gom = glob.gom
                    obj.help()
            except AttributeError:
                glob.gom.echo("Module has no help information.")
            except:
                glob.gom.echo("Internal error: " + str(sys.exc_info()[1]))

            return

    glob.gom.echo("Module does not exist.")

def unified_input_prompt(caller, prompt = ''):
    """
    Helper for common input loops.
    It needs a method show_help() in the caller object.
    Returns the string, or None if the loop should stop.
    """

    default_prompt = 'inguma'
    if prompt:
        prompt = default_prompt + "/" + prompt
    else:
        prompt = default_prompt

    try:
        input = raw_input(prompt + '> ')
    except KeyboardInterrupt:
        print
        input = ""
    except EOFError:
        print
        return None
    except:
        # Uh-oh, what happened?
        print "Internal error:", sys.exc_info()[1]

    if input.lower() in ['help', 'h', '?']:
        caller.show_help()
        input = ""
    elif input.lower() in ['quit', 'exit', '..', 'urten']:
        return None

    return input

def print_banner(gom):
    """Prints the salute banner."""

    gom.echo('Inguma v' + glob.version)
    gom.echo('Copyright (c) 2006-2008 Joxean Koret <joxeankoret@yahoo.es>')
    gom.echo('Copyright (c) 2009-2011 Hugo Teso <hugo.teso@gmail.com>')
    gom.echo()

def usage(gom):
    """Prints help and usage instructions."""

    gom.echo('Usage:', sys.argv[0], ' <flag>')
    gom.echo()
    gom.echo('-d      Show debug information')
    gom.echo('-h      Show this help and exit')
    gom.echo('-w      Run HTTP server on port 4545 (EXPERIMENTAL AND HIGHLY INSECURE!!)')
    gom.echo()

