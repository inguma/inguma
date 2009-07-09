#!/usr/bin/python

import cgi
import sys

from config import *
from bindb import CBinDb
from libutils import *

def printXrefsTo(dbFile, function):
	binDb = CBinDb()
	binDb.openDatabase(dbFile)
	binDb.getXrefs(function)

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

	if form.has_key("function"):
		function = form.getvalue("function")
	else:
		function = ""

	printHeader()
	printBodyHeader()
	printXrefsTo(databaseFile, function)
	printBodyFooter()

def main():
	# Specific CGI's logic
	mainLogic()

if __name__ == "__main__":
	main()
