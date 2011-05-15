##      libAutosave.py
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

""" Library containing functions related to KB autosave feature. """

import os
import gtk
from lib.core import get_profile_file_path

_autosave_kb_path = get_profile_file_path('autosaved.kb')

def ask_dialog():
    """ Prompt the use with a GTK dialog for loading the KB. """
    msg = ("Autosaved KB found. Load it?")
    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, 
                            gtk.BUTTONS_YES_NO, msg)
    opt = dlg.run()
    dlg.destroy()

    if opt == gtk.RESPONSE_YES:
        return True
    else:
        return False

def check_kb():
    """ Checks if the KB exists or not. """
    if os.path.exists(_autosave_kb_path):
        return True
    else:
        return False

def remove_kb():
    """ Removes the KB. """
    try:
        os.remove(_autosave_kb_path)
    except:
        pass

def get_kb_path():
    """ Returns the path for the KB. """
    return _autosave_kb_path
