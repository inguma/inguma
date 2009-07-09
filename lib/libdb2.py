#!/usr/bin/python

import socket, sys

class CDb2Discover:

	target = '<broadcast>'
	targetPort = 523
	version = "SQL09050"
	timeout = 3
	_oldTimeout = None
	verbose = True

	def getDiscoverPacket(self):
		return "DB2GETADDR\x00%s\x00" % (self.version)

	def log(self, msg):
		if self.verbose:
			print msg

	def discover(self):
		dest = (self.target, self.targetPort)
		
		oldTimeout = socket.getdefaulttimeout()
		socket.setdefaulttimeout(self.timeout)

		serverList = []
		
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			s.sendto(self.getDiscoverPacket(), dest)

			servers = 0

			while 1:
				try:
					(buf, address) = s.recvfrom(2048)
				except:
					break

				if not len(buf):
					break

				servers += 1
				serverData = []
				serverData.append(address)

				self.log("  [+] IBM DB2 Server found at %s" % address[0])
				
				buf = buf.strip("\x00")
				data = buf.split("\x00")

				for element in data:
					if element and element != "DB2RETADDR":
						serverData.append(element)
						self.log("    " + element)

				self.log(" ")

				serverList.append(serverData)

			self.log("")
			self.log("Total of %d IBM server(s) found." % servers)
			self.log("")

			return serverList
		finally:
			socket.setdefaulttimeout(oldTimeout)
			return serverList

def banner():
	print "IBM DB2 Services Discoverer Version 1.0"
	print

if __name__ == "__main__":
	banner()

	db2Discover = CDb2Discover()
	
	if len(sys.argv) > 1:
		print "Using %s as target ... " % sys.argv[1]
		print
		db2Discover.target = sys.argv[1]

	db2Discover.verbose = False
	ret = db2Discover.discover()

	for server in ret:
		print "[+] IBM DB2 Server at %s:%d" % (server[0][0], server[0][1])
		print "  Version   : %s " % server[1]
		print "  Hostname  : %s " % server[2]
		print "  Servername: %s " % server[3]
		print

	print "Total of %d IBM DB2 Server(s) found." % len(ret)


