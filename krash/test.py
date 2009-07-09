#!/usr/bin/python

import sys
import socket

def test():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((sys.argv[1], int(sys.argv[2])))
	s.send(file(sys.argv[3], "r").read())
	print s.recv(4096)

def usage():
	print sys.argv[0], "<hostname> <port> <packet file>"
	print

def main():
	if len(sys.argv) != 4:
		usage()
	else:
		test()

if __name__ == "__main__":
	main()

