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

import os
import gtk

def askDialog():
    msg = ("Autosaved KB found. Load it?")
    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
    opt = dlg.run()
    dlg.destroy()

    if opt == gtk.RESPONSE_YES:
        return True
    else:
        return False

def createDir():
    path = os.path.expanduser('~')
    os.mkdir(path + '/.inguma')

def checkKB():
    path = os.path.expanduser('~')
    if os.path.exists(path + '/.inguma/autosaved.kb'):
        return True
    else:
        return False

def checkDir():
    path = os.path.expanduser('~')
    if os.path.exists(path + '/.inguma/'):
        return True
    else:
        createDir()
        return True

def removeKB():
    path = os.path.expanduser('~')
    os.remove(path + '/.inguma/autosaved.kb')

def getKbPath():
    path = os.path.expanduser('~') + '/.inguma/autosaved.kb'
    return path
