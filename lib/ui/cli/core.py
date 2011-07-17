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
