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
import lib.config as config

def debug_print(*args):
    """Prints a debug message on the terminal."""
    # FIXME: This should be a method in the gom object.

    # Print debug messages if debug is activated (run with -d)
    if not config.debug:
        return

    output_string = ""
    for arg in args:
        output_string += str(arg) + " "

    print output_string

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

    from lib.core import get_inguma_version

    gom.echo('Inguma v' + get_inguma_version())
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

