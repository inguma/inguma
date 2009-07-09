#!/usr/bin/python

import cgi
import sys

from config import *
from bindb import CBinDb
from libutils import *

def addComment(dbFile, address, comment):
	binDb = CBinDb()
	binDb.openDatabase(dbFile)
	binDb.addComment(address, comment)
	function = binDb.getNameByAddress(address)

	print "Content-type: text/html"
	print
	print "Comment added"
	#print "<html><body>"
	#print "<meta http-equiv='refresh' content='0;URL=/cgi-bin/analyze.py?database=" + cgi.escape(dbFile) + "&function=" + cgi.escape(function) + "#" + address + ">"
	#print "</body></html>"

def mainLogic():
	
	# Check parameters
	form = cgi.FieldStorage()
	
	if not form.has_key("database"):
		dieError("No database selected!")
	else:
		try:
			databaseFile = form.getvalue("database")
			databaseFile = cleanFile(databaseFile)
			
			f = file(DATABASES_PATH + databaseFile, "r")
			f.close()
		except:
			dieError("Database doesn't exsits!")

	if form.has_key("address"):
		address = form.getvalue("address")
	else:
		dieError("No address specified")

	if form.has_key("comment"):
		comment = form.getvalue("comment")
	else:
		dieError("No comment specified")

	addComment(databaseFile, address, comment)

def main():
	# Specific CGI's logic
	mainLogic()

if __name__ == "__main__":
	main()
