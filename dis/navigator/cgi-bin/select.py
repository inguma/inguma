#!/usr/bin/python

import os
import sys

from config import *
from libutils import *

def mainLogic():
	htmlData = "Select binary to analyze:<br/><br/>"
	print htmlData
	
	print "<div align='center'>"
	print "<table border='0' cellpadding='0' cellspacing='0'>"
	for mfile in os.listdir(DATABASES_PATH):
		if mfile.endswith(".sqlite"):
			print "<tr><td><a href='/cgi-bin/analyze.py?database=%s'>%s</a></td></tr>" % (mfile, mfile)
	print "</table>"
	print "</div>"
	print "<br/>"
	print "Or <a href='/upload.html'>upload a new binary to analyze.</a>"

def main():
	printHeader()
	printBodyHeader()
	
	# Specific CGI's logic
	mainLogic()
	
	printBodyFooter()

if __name__ == "__main__":
	main()

