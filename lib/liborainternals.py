#!/usr/bin/env python

ORACLE_VERSION_8_OR_LOWER = 0
ORACLE_VERSION_9_OR_HIGHER = 1
ORACLE_VERSION_10 = 2
ORACLE_VERSION_11 = 3

LOGIN_AS_SYSDBA_ALLOWED = "\x1f"
LOGIN_AS_SYSDBA_DENIED  = "\x1d"

class COraPwdFile:
	""" Oracle [Remote] Password File Management Object """

	# By default, version 9i or higher
	version = ORACLE_VERSION_9_OR_HIGHER

	# Just for 9i and higher. In Oracle 8 this header doesn't exists.
	header  = "\x00"*5 + "\x02" + "\x00"*2 + "\x02" + "\x00\x00\x00" + "\x5d\x5c\x5b\x5a" + "\x00"*496

	# Common header & data
	strHeader = "ORACLE Remote Password file"
	strHeaderMaxSize = 30
	
	# Just for Oracle v8 or lower
	padding1 = "\x00"*33
	padding1_version9 = "\x00"*31
	
	loginAsSysdba = LOGIN_AS_SYSDBA_ALLOWED
	
	sidName = ""
	sidNameMaxSize = 30
	
	flag = 1 # Don't know... (?)

	internal = "INTERNAL"
	internalUserMaxSize = 32
	padding2 = "\x00"*3

	internalPassword = "AB27B53EDC5FEF41"
	internalPasswordMaxSize = 32
	padding3 = "\x00"*31
	padding3_version9 = "\x00"*35

	internalAsSysDba = "\x1f"
	internalPassword11g = "\xfd\xd4\x8a\xc6\x9b\xd7\xd8\xa2\x3d\x86\x73\xd8\x29\x34\x73\xbf\x8d\xd9\x39\x46\x40\x2a\x35\x1a\xc3\x36\x25\xbe\xce\xf9"

	sys = "SYS"
	sysPassword = "77F67DE94989CEFF"
	sysAsSysdba = "\x1f"
	sysPassword11g = "\x74\x7a\xc5\xb8\x46\x48\x35\x88\xf6\x26\x87\x03\xe4\x29\xf4\xba\xe6\xca\x70\x74\x29\x4e\xa8\x39\xab\x84\xe9\xe2\xc7\x07"
	padding4 = "\x00"*3 + "\x0f" + "\x00"*47
	padding4_version9 = "\x00"*7 + "\x0f" + "\x00"*47
	padding4_version11 = "\x00"*3

	# Just for Oracle 10g and higher
	padding5 = "\x00"*68 + "\x80" + "\x00"*635

	def __init__(self):
		self.clearData()

	def _getData(self):

		if self.version == ORACLE_VERSION_8_OR_LOWER:
			buf = ""
		else: # ORACLE_VERSION_9_OR_HIGHER
			buf = self.header

		buf += self.strHeader + "\x00"*(self.strHeaderMaxSize-len(self.strHeader)) + chr(len(self.strHeader))
		
		if self.version == ORACLE_VERSION_11:
			self.flag = 3

		if self.version == ORACLE_VERSION_8_OR_LOWER:
			buf += self.padding1
		else: # Oracle 9i or higher
			buf += "\x00" + self.sidName + "\x00"*(self.sidNameMaxSize-len(self.sidName)) + chr(len(self.sidName))
			buf += "\x00"*1 + chr(self.flag)
			buf += self.padding1_version9

		buf += self.internal + "\x00"*(self.internalUserMaxSize-len(self.internal)) + chr(len(self.internal))
		buf += self.padding2
		buf += self.internalPassword + "\x00"*(self.internalPasswordMaxSize-len(self.internalPassword))
		buf += chr(len(self.internalPassword))
		
		if self.version == ORACLE_VERSION_8_OR_LOWER:
			buf += self.padding3
		elif self.version == ORACLE_VERSION_11:
			buf += "\x00"*3
			buf += self.loginAsSysdba + self.internalPassword11g + "\x00"
		else:
			buf += self.padding3_version9

		buf += self.sys + "\x00"*(self.internalUserMaxSize-len(self.sys)) + chr(len(self.sys)) + "\x00"*3
		buf += self.sysPassword + "\x00"*(self.internalPasswordMaxSize-len(self.sysPassword))
		buf += chr(len(self.sysPassword))
		
		if self.version == ORACLE_VERSION_11:
			buf += self.padding4_version11
			buf += self.loginAsSysdba + self.sysPassword11g
			buf += "\x00"*17
		else:
			buf += self.padding4

		if self.version >= ORACLE_VERSION_9_OR_HIGHER:
			buf += self.padding5

		return buf

	def clearData(self):
		self.internalPassword = ""
		self.sysPassword = ""
		self.version = ORACLE_VERSION_9_OR_HIGHER
		self.sidName = ""

	def readPasswodFile(self, filename):
		f = file(filename, "rb")
		data = f.read()
		f.close()
		
		if data.startswith(self.header):
			self.version = ORACLE_VERSION_9_OR_HIGHER
		elif data.startswith(self.strHeader):
			self.version = ORACLE_VERSION_8_OR_LOWER

		pos = data.find(self.strHeader)
		if pos == -1:
			return False
		
		pos += self.strHeaderMaxSize + 2
		auxBuf = data[pos:]
		
		if auxBuf.startswith("\x00"):
			self.sidName = ""
			endPos = self.sidNameMaxSize
		else:
			endPos = auxBuf.find("\x00")
			
			if endPos == -1:
				return False

			self.sidName = auxBuf[:endPos]
		
		pos += endPos + len(self.sidName)
		auxBuf = data[pos:]
		newPos = auxBuf.find("INTERNAL")
		
		if newPos == -1:
			return False
		
		pos += newPos + self.internalUserMaxSize + 4
		auxBuf = data[pos:]
		
		endPos = auxBuf.find("\x00")
		if endPos < 1:
			return False
		
		self.internalPassword = auxBuf[:endPos]
		pos += endPos
		auxBuf = data[pos:]
		newPos = auxBuf.find("SYS")
		
		if newPos < 1:
			return False
		pos += newPos + self.internalUserMaxSize+4

		auxBuf = data[pos:]
		newPos = auxBuf.find("\x00")
		
		if newPos < 1:
			return False
		
		self.sysPassword = auxBuf[:newPos]

		return True

	def getPasswordFile(self, internalPassword, sysPassword):
		self.internalPassword = internalPassword
		self.sysPassword = sysPassword
		
		return self._getData()

def testSave():
	objPwdFile = COraPwdFile()
	#data = objPwdFile.getPasswordFile("AB27B53EDC5FEF41", "8A8F025737A9097A")
	#objPwdFile.sidName = "ORCL"
	objPwdFile.version = ORACLE_VERSION_11
	data = objPwdFile.getPasswordFile("AB27B53EDC5FEF41", "8A8F025737A9097A")
	#filename = raw_input("Filename: ")
	filename = "test11.ora"
	f = file(filename, "wb")
	f.write(data)
	f.close()

def main():
	objPwdFile = COraPwdFile()

	print "[+] Reading password file test11.ora"
	if objPwdFile.readPasswodFile("test11.ora"):
		if objPwdFile.version == ORACLE_VERSION_8_OR_LOWER:
			print "Password File Version: Oracle 8 or lower"
		else:
			print "Password File Version: Oracle 9 or higher"
		
		if objPwdFile.sidName != "":
			print "Oracle SID           : " + objPwdFile.sidName
		
		print "Internal password    : " + objPwdFile.internalPassword
		print "Sys password         : " + objPwdFile.sysPassword
	else:
		print "Error reading password file"
	print

if __name__ == "__main__":
	testSave()
	main()

