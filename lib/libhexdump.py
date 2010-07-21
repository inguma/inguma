#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys, os, traceback
from types import *

# BEGIN
# The following piece of code was found at:
# http://code.activestate.com/recipes/82748/
# END

class Display:
	def __init__(self):
		# display stuff
		self.clear		= ''
		self.lines_per_page	= 19
		self.chars_per_line	= 16
		self.oddity		= '.'
		
		self.line_width		= self.chars_per_line * 4 + 10
		self.dash		= '-' * self.line_width

		# other properties
		self.n_lines		= 0
		self.offset		= 0
		self.hand 		= -1
		
	def SetClear(self):
		# platform-dependent command to clear the display
		if sys.platform in ('linux-i386', 'linux2'):
			self.clear = 'clear'
		elif sys.platform in ('win32', 'dos', 'ms-dos'):
			self.clear = 'cls'
		
	def Clear(self):
		# clear screen using system command
		if self.clear:
			os.system(self.clear)
	
	def Header(self):
		# print header
		self.n_lines = 0
		self.Clear()
		print self.file
		print self.dash

	def Footer(self):
		# print footer
		print self.dash
		spacer = ' ' * (self.line_width - 27)
		s = raw_input(spacer + 'jump to... ')
		
		# if entry is...
		#   valid hex --> jump to that position
		#   x, q...   --> quit
		if s:
			s = s.lower().strip()
			if s in ('x', 'q', 'quit', 'exit', 'end'):
				raise NameError, 'Bye'
			for c in s:
				if c not in '0123456789abcdef':
					s = ''
					break
		if s:
			self.offset = eval('int(0x%s)' % s)
			self.hand.seek(self.offset)
		
	def MakeAscii(self, char):
		# ascii representation of character
		ascii = ord(char)
		if ascii < 32 or (ascii > 127 and ascii < 161):
			x = self.oddity
		else:
			x = char
		return x

	def MakeHex(self, char, length):
		# hex representation of character/integer
		if type(char) is StringType:
			char = ord(char)
		x = hex(char)[2:]
		while len(x) < length:
			x = '0' + x
		return x

	def PrintLine(self, l_hex, l_char):
		# output a line
		if len(l_char) > 0:
			while len(l_char) < 16:
				l_hex	+= '   '
				l_char	+= ' '
			print '%s:%s | %s' % (self.MakeHex(self.offset, 6), l_hex, l_char)
			self.offset += self.chars_per_line
			self.n_lines += 1

	def Process(self):
		l_hex, l_char, n_char = '', '', 0
		
		self.hand = open(self.file, 'rb')   
		self.Header()

		while 1:
			# read next character
			n_char += 1
			char = self.hand.read(1)
			if not char:
				break
			
			# accumulate hex and ascii representations
			l_hex	+= ' ' + self.MakeHex(char, 2)
			l_char	+= self.MakeAscii(char)
			
			# line done
			if n_char == self.chars_per_line:
				self.PrintLine(l_hex, l_char)
				
				l_hex, l_char, n_char = '', '', 0

				# end of page
				if self.n_lines == self.lines_per_page:
					self.Footer()
					self.Header()
		self.PrintLine(l_hex, l_char)
