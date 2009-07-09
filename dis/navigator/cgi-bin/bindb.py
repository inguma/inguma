#!/usr/bin/python

import os
import sys
import cgi
import sqlite3

from config import *
from libutils import *
from libgraph import createTree

SYNTAX_ATT   = 0
SYNTAX_INTEL = 1

class CBinDb():
	
	db = None
	dbFile = None
	selectedFunction = ""
	syntax = SYNTAX_ATT
	
	def openDatabase(self, dbFile):
		try:
			db = sqlite3.connect(DATABASES_PATH + dbFile)
			db.text_factory = str
			self.db = db
			self.dbFile = dbFile
			
			self.checkSyntax()
			
		except:
			printHeader()
			dieError("Can't open database: %s" % str(sys.exc_info()[1]))
		
		return self.db
	
	def checkSyntax(self):
		sql = "select format from database_format"
		c = self.db.cursor()
		try:
			c.execute(sql)
		except:
			return
		
		for row in c.fetchall():
			if row[0] == 'IDAPRO':
				self.syntax = SYNTAX_INTEL
		
		c.close()

	def drawSelectFunction(self, selected=""):
		sql = "select * from functions"
		c = self.db.cursor()
		c.execute(sql)

		htmlData = "<select name='function' id='idFunction' onchange='javascript:changeFunction();'>"
		i = 0
		for row in c:
			
			if not row[0].startswith('0'):
				val = hex(int(row[0]))
			else:
				val = row[0]
				
			if selected == "":
				selected = row[1]
			
			if row[1] == selected:
				self.selectedFunction = selected
				htmlData += "<option value='%s' selected>%s - %s</option>" % (row[1], row[1], val)
			else:
				htmlData += "<option value='%s'>%s - %s</option>" % (row[1], row[1], val)
	
		htmlData += "</select>"
		c.close()
	
		return htmlData

	def addressExists(self, addr):
		funcName = None
		c = self.db.cursor()
		
		if self.syntax == SYNTAX_ATT:
			sql = "select function from function_lines where address = ?"
		else:
			sql = "select function from function_lines where function = ?"

		c.execute(sql, (addr, ))

		for row in c.fetchall():
			funcName = row[0]
		
		c.close()
		return funcName

	def getNameByAddress(self, addr):
		return self.addressExists(addr)

	def getLink(self, arg):
		if not arg.startswith("<"):
			if self.syntax == SYNTAX_ATT:
				func = self.addressExists(arg)
			else:
				func = arg[arg.find(":")+1:]
				
			if func:
				return "<a href='/cgi-bin/analyze.py?database=%s&function=%s#%s'>%s</a>" % (self.dbFile, func, cgi.escape(arg), cgi.escape(arg))
			else:
				return "<a href='/cgi-bin/analyze.py?database=%s&function=%s#%s'>%s</a>" % (self.dbFile, self.selectedFunction, cgi.escape(arg), cgi.escape(arg))

		return cgi.escape(arg)

	def getXrefLink(self, arg):
		
		if self.syntax == SYNTAX_ATT:
			if not arg.startswith("<"):
				func = self.addressExists(arg)
	
				if func:
					return "<a href='/cgi-bin/xrefs.py?database=%s&function=%s#%s'><img src='/img/xref.png' alt='XREF'/></a>" % (self.dbFile, func, cgi.escape(arg))
				else:
					return "<a href='/cgi-bin/xrefs.py?database=%s&function=%s#%s'><img src='/img/xref.png' alt='XREF'/></a>" % (self.dbFile, cgi.escape(arg), cgi.escape(arg))

		return False

	def getXref(self, line):
		instructions = line.split(" ")
		theInstruction = instructions[0]
		
		for arg in instructions[1:]:
			if arg == "":
				continue
			elif self.syntax != SYNTAX_ATT:
				if arg in ["dword", "offset", "short"]:
					continue
			if instructions[0] == "call" or instructions[0].startswith("j"):
				return self.getXrefLink(arg)
			
		return False
	
	def formatAsm(self, line):
		instructions = line.split(" ")
		theInstruction = instructions[0]
		code = '<font color="blue">%s</font>' % instructions[0]
		for arg in instructions[1:]:
			if arg == "":
				code += "&nbsp;"
			elif instructions[0] == "call" or instructions[0].startswith("j"):
				code += self.getLink(arg) + "&nbsp;"
			else:
				code += cgi.escape(arg) + "&nbsp;"
		return code
	
	def printProcedure(self, proc):
		
		if proc == "" or proc is None:
			proc = self.selectedFunction
		
		sql = "SELECT * FROM FUNCTION_LINES WHERE FUNCTION = ?"
		c = self.db.cursor()
		c.execute(sql, (proc, ))
		i = 0
		previousBreak = False
		row = False
		xref = None

		for row in c.fetchall():
			i += 1
				
			if i == 1:
				print "<tr><td><a name='%s'/>%s</td><td colspan='2'><b>proc %s</b></td>" % (row[0], cgi.escape(row[0]), proc)
			
			if previousBreak:
				print "<tr><td><a name='%s'/>%s</td><td colspan='2'>%s:</td>" % (row[0], cgi.escape(row[0]), cgi.escape(row[1]))
				previousBreak = False

			if row[4]:
				val = "<div id='idComment_" + row[0] + "'><font color='olive'>;%s</font></div>" % cgi.escape(row[4])
			else:
				val = "<div id='idComment_" + row[0] + "'></div>"
			print """<tr><td><a name='%s' ondblclick="javascript:addComment('%s', '%s');"/>%s</td>
					 <td>%s%s</td><td>%s</td>""" % (row[0], self.dbFile, cgi.escape(row[0]), row[0], "&nbsp;"*4, self.formatAsm(row[3]), val)
			
			if previousBreak:
				previousBreak = False

			instruction = row[3].split(" ")[0]
			if instruction.startswith("j") or instruction.find("call") > -1:
				xref = self.getXref(row[3])
				
				if xref:
					print "<td>%s</td>" % xref
			
			print "</tr>"

			if instruction.startswith("j"):
				print "<tr><td colspan='3'><font color='olive'>;" + "-"*80 + "</font></td></tr>"
				previousBreak = True
	
		if row:
			print "<tr><td><a name='%s'/>%s</td><td colspan='2'><b>end %s</b></td><tr>" % (row[0], cgi.escape(row[0]), proc)
		c.close()

	def drawGraph(self, function):
		
		outputFile = RELATIVE_LOCATION + self.dbFile[:self.dbFile.find(".")] + "/" + function + ".png"
		
		if not os.path.exists("./" + outputFile) or True:
			buf = createTree(self.db, function)
			path = DATABASES_PATH + self.dbFile[:self.dbFile.find(".")] + "/"
			
			try:
				os.mkdir(path)
			except:
				pass # Ignore the possible exception
			
			dotFile = path + function + ".dot"
			f = file(dotFile, "w")
			f.write(buf)
			f.close()
			
			os.system("dot -Tpng %s > %s" % (dotFile, dotFile.replace(".dot", ".png")))

		print getImageJavascript()
		#print """<img id='idImage' src='%s' alt='%s' width='100%%' onclick='javascript:toggleShowHide("divImage", "idImage")'/>""" % (outputFile, function)
		#print """<img id='divImage' style='display:none;visibility:hidden' src='%s' alt='%s'
		#		  onclick='javascript:toggleShowHide("idImage", "divImage")' />""" % (outputFile, function)
		#print """</a>"""
		print """<iframe id='idImage' src="%s" width="100%%" height="100%%"></iframe>""" % (outputFile)
		print """<script>adjustMe('idImage');</script>"""

	def drawCC(self, function):
		buf = createTree(self.db, function, False)
		print "<table width='100%%'><tr><td>Number of edges: <b>%d</b></td></tr>" % len(buf.connections)
		print "<tr><td>Number of nodes: <b>%d</b></td></tr>" % len(buf.edges)
		print "<tr><td>Cyclomatic Complexity: <b>%d</b></td>" % (len(buf.connections) - len(buf.edges) + 2)
		print "</table>"

	def getFunctionLink(self, function):
		return "<a href='/cgi-bin/analyze.py?database=%s&function=%s'>%s</a>" % (self.dbFile, function, function)
	
	def getLinkForAddress(self, address, function):
		return "<a href='/cgi-bin/analyze.py?database=%s&function=%s#%s'>%s</a>" % (self.dbFile, function, address, address)

	def getXrefs(self, function):
		sql = """ select * from function_lines where code like '%<' || ? || '>%' or code like '%<' || ? || '+%>' """
		c = self.db.cursor()
		c.execute(sql, (function, function ))
		
		print "<table border='0'>"
		print "<tr><td colspan='3'>Cross references for '%s':</td></tr>" % cgi.escape(function)
		print "<tr><td colspan='3'><hr/></td></tr>"
		
		rows = 0
		for row in c.fetchall():
			rows += 1
			if row[4]:
				val = "<font color='olive'>;%s</font>" % cgi.escape(row[4])
			else:
				val = ""
			print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (self.getLinkForAddress(row[0], row[2]), self.getFunctionLink(row[2]), self.formatAsm(row[3]), val)
		
		if rows == 0:
			print "<tr><td colspan='3'>"
			showWarning('No XRef found by the normal way! Searching the pattern with a like expressions.')
			print "</td></tr>"
			print "<tr><td colspan='3'><hr></td></tr>"
			
			sql = """ select * from function_lines where code like '%' || ? || '%'"""
			c = self.db.cursor()
			c.execute(sql, (function, ))
			
			print "<table border='0'>"
			rows = 0
			for row in c.fetchall():
				rows += 1
				if row[4]:
					val = "<font color='olive'>;%s</font>" % cgi.escape(row[4])
				else:
					val = ""
				print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % (self.getLinkForAddress(row[0], row[2]), self.getFunctionLink(row[2]), self.formatAsm(row[3]), val)
		print "</table>"
		c.close()

	def addComment(self, address, comment):
		sql = """ UPDATE FUNCTION_LINES SET DESCRIPTION = ? WHERE ADDRESS = ? """
		c = self.db.cursor()
		c.execute(sql, (comment, address))
		self.db.commit()
		c.close()
		
		return True

