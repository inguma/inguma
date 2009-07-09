import gtk
from ipython_view import *
import pango

import platform
if platform.system()=="Windows":
        FONT = "Lucida Console 9"
else:
        FONT = "Luxi Mono 10"

W = gtk.Window()
W.set_size_request(750,550)
W.set_resizable(True)
S = gtk.ScrolledWindow()
S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
V = IPythonView()
V.modify_font(pango.FontDescription(FONT))
V.set_wrap_mode(gtk.WRAP_CHAR)
V.show()
S.add(V)
S.show()
W.add(S)
W.show()
W.connect('delete_event',lambda x,y:False)
W.connect('destroy',lambda x:gtk.main_quit())
gtk.main()

"""

Exposing variables to the shell

If you have variables you want to expose in the shell, use the following syntax. Also look at the files in the Accerciser source code for how to synchronise other aspects of your GUI with the actions in the IPython prompt. 

   V.updateNamespace({'myvar': myvar})

"""
