#!/usr/bin/python

import os
import cgi
import sys
import popen2
import tempfile

from config import *
from libutils import *

def runDis(thefile, afile):
    outputfile = cleanFile(afile)
    cmdLine = DIS_PATH + " -sdb=" + DATABASES_PATH + outputfile + ".sqlite " + thefile
    os.system(cmdLine)

def createDatabase(item):
    num, thefile = tempfile.mkstemp()
    f = file(thefile, "wb")
    f.write(item.file.read())
    f.close()
    
    runDis(thefile, item.filename)

def printUploadForm(item):
    print "<table><tr>"
    print "<td>Binary: <b>%s</b> uploaded. Analyzing it now!</td>" % cgi.escape(item.filename)
    print "</tr><tr>"
    print "<td>"
    createDatabase(item)
    print "</td>"
    print "</tr></table>"
    print "<b>Database created.</b><a href='/cgi-bin/select.py'>Continue</a>"

def mainLogic():
    form = cgi.FieldStorage()
    
    if form.has_key("file"):
        item = form["file"]
    else:
        printHeader()
        dieError("No file uploaded!")
    
    if not item.file or item.filename == "" or not item.filename:
        printHeader()
        dieError("Empty file given")

    printHeader()
    printBodyHeader()
    printUploadForm(item)
    printBodyFooter()

def main():
    # Specific CGI's logic
    mainLogic()

if __name__ == "__main__":
    main()

