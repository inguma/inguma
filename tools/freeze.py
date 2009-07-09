#!/usr/bin/env python
"""Show a shell command's output in a gtk.TextView without freezing the UI"""

import os, threading, locale

import pygtk
pygtk.require('2.0')
import gtk

encoding = locale.getpreferredencoding()
utf8conv = lambda x : unicode(x, encoding).encode('utf8')

def on_button_clicked(button, buffer, command):
    print "Button clicked!"
    thr = threading.Thread(target= read_output, args=(buffer, command))
    thr.start()
    thr.join()
    print "Thread started!"

def read_output(buffer, command):
    print "Read output!"
    stdin, stdouterr = os.popen4(command)
    for line in stdouterr.readlines():
        buffer.insert(buffer.get_end_iter(), line)
    #print "Output:", stdouterr.read()

sw = gtk.ScrolledWindow()
sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
textview = gtk.TextView()
textbuffer = textview.get_buffer()
sw.add(textview)
win = gtk.Window()
win.resize(300,500)
win.connect('delete-event', gtk.main_quit)
button = gtk.Button(u"Press me!")
command = 'ls -l %s' % os.getcwd()
print command
button.connect("clicked", on_button_clicked, textbuffer, command)
vbox = gtk.VBox()
vbox.pack_start(button, False)
vbox.pack_start(sw)
win.add(vbox)
win.show_all()

gtk.main()
