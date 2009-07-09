#!/usr/bin/python

import os
import sys
import cgi

from bindb import *
from config import *
from libutils import *

def drawGui(dbFile, funcName = ""):
	
	binDb = CBinDb()
	binDb.openDatabase(dbFile)
	print "<form name='fmAnalyze' action='/cgi-bin/analyze.py'>"
	print "<input type='hidden' name='database' value='%s'/>" % dbFile
	print "<table border='0'>"
	print "<tr><td colspan='2'>Function: %s" % binDb.drawSelectFunction(funcName)
	print "<td align='right'>"
	print "		<a href='/'><img src='/img/home.png' alt='Home'></a>"
	print "		<input type='image' src='/img/analyze.png' name='action' value='analyze' alt='Analyze'>"
	print "		<input type='image' src='/img/graph.png' name='action' value='graph' alt='Graph'>"
	print "		<input type='image' src='/img/cc.png' name='action' value='Cyclomatic Complexity' alt='Cyclomatic Complexity'>"
	print "		<a href='/cgi-bin/xrefs.py?database=%s&function=%s'><img src='/img/xref.png' height='32' width='32' alt='Cross References'></a>" % (dbFile, binDb.selectedFunction)
	print "</td></tr>"
	print "<tr><td colspan='4'><hr/></td></tr>"
	print "<tr><td colspan='3'><iframe src='' id='idStatus' height='0' width='0' style='display:none;visibility:hidden'></iframe></td></tr>"
	binDb.printProcedure(funcName)
	print "</table>"
	print "</form>"

def drawGraph(dbFile, funcName):
	binDb = CBinDb()
	binDb.openDatabase(dbFile)
	print "<form name='fmAnalyze' action='/cgi-bin/analyze.py'>"
	print "<input type='hidden' name='database' value='%s'/>" % dbFile
	print "<table border='0'>"
	print "<tr><td colspan='3'>Function: %s &nbsp;" % binDb.drawSelectFunction(funcName)
	print "		<a href='/'><img src='/img/home.png' alt='Home'></a>"
	print "		<input type='image' src='/img/analyze.png' name='action' value='analyze'>"
	print "		<input type='image' src='/img/graph.png' name='action' value='graph'>"
	print "		<input type='image' src='/img/cc.png' name='action' value='Cyclomatic Complexity'>"
	print "		<a href='/cgi-bin/xrefs.py?database=%s&function=%s'><img src='/img/xref.png' height='32' width='32' alt='Cross References'></a>" % (dbFile, binDb.selectedFunction)
	print "</td></tr>"

	print "<td>"
	binDb.drawGraph(funcName)
	print "</td></tr>"
	print "</table>"
	print "</form>"
	
def drawCC(dbFile, funcName):
	binDb = CBinDb()
	binDb.openDatabase(dbFile)
	print "<form name='fmAnalyze' action='/cgi-bin/analyze.py'>"
	print "<input type='hidden' name='database' value='%s'/>" % dbFile
	print "<table border='0'>"
	print "<tr><td colspan='3'>Function: %s &nbsp;" % binDb.drawSelectFunction(funcName)
	print "		<a href='/'><img src='/img/home.png' alt='Home'></a>"
	print "		<input type='image' src='/img/analyze.png' name='action' value='analyze'>"
	print "		<input type='image' src='/img/graph.png' name='action' value='graph'>"
	print "		<input type='image' src='/img/cc.png' name='action' value='Cyclomatic Complexity'>"
	print "		<a href='/cgi-bin/xrefs.py?database=%s&function=%s'><img src='/img/xref.png' height='32' width='32' alt='Cross References'></a>" % (dbFile, binDb.selectedFunction)
	print "</td></tr><tr><td colspan='3'><hr/></td></tr>"
	print "<tr><td>"
	binDb.drawCC(funcName)
	print "</td></tr><tr><td colspan='3'><hr/></td></tr>"
	print "</table>"
	print "</form>"

def mainLogic():
	
	# Check parameters
	form = cgi.FieldStorage()
	
	if not form.has_key("database"):
		print "Content-type:text/html"
		print
		dieError("No database selected!")
	else:
		try:
			databaseFile = form.getvalue("database")
			databaseFile = cleanFile(databaseFile)
			
			f = file(DATABASES_PATH + databaseFile, "r")
			f.close()
		except:
			print "Content-type:text/html"
			print
			dieError("Database doesn't exsits!")

	if form.has_key("function"):
		function = form.getvalue("function")
	else:
		function = ""

	if form.has_key("action"):
		action = form.getvalue("action")
	else:
		action = "analyze"

	if action == "analyze":
		printHeader()
		printBodyHeader()
		drawGui(databaseFile, function)
		printBodyFooter()
	elif action == "graph":
		printHeader()
		printBodyHeader()
		drawGraph(databaseFile, function)
		printBodyFooter()
	elif action == "Cyclomatic Complexity":
		printHeader()
		printBodyHeader()
		drawCC(databaseFile, function)
		printBodyFooter()
	else:
		print "Content-type: text/html"
		print
		dieError("Invalid action %s" % cgi.escape(action))

def main():
	# Specific CGI's logic
	mainLogic()

if __name__ == "__main__":
	main()
