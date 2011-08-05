#!/usr/bin/python

##      CRceToolBox.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

import sys, os, string
from lib.libasciienc import *
from lib.librcetools import *
from lib.module import CIngumaModule

name = "toolbox"
brief_description = "A module with many RCE tools"
type = "rce"

class CRceToolBox(CIngumaModule):
    interactive = True

    def help(self):
        print "A module with many RCE tools"

    def showHelp(self):
        print 
        print "Inguma's RCE Toolbox Help"
        print "========================="
        print
        print "help                     Show this help"
        print "exit                     Exit from RCE Toolbox"
        print 
        print "Convertion tools"
        print "----------------"
        print 
        print "ascii2bin                Convert ASCII to Binary"
        print "ascii2oct                Convert ASCII to Octal"
        print "ascii2hex                Convert ASCII to Hexadecimal"
        print "ascii2str                Convert ASCII to string"
        print
        print "bin2ascii                Convert Binary to ASCII"
        print "oct2ascii                Convert Octal to ASCII"
        print "hex2ascii                Convert Hexadecimal to ASCII"
        print "str2ascii                Convert string to ASCII"
        print
        print "Misc"
        print "----"
        print
        print "pattern                  pattern <length> <string>"
        print

    def ascii2bin(self, asciistr):
        print "ASCII:\t\t" + asciistr
        #asciistr = asciistr.split("ascii2bin ")
        print "Binary:\t\t" + ascii2binary(asciistr)

    def ascii2oct(self, octstr):
        print "ASCII:\t\t" + octstr
        print "Octal:\t\t" + ascii2octal(octstr)

    def ascii2hex(self, hexstr):
        print "ASCII:\t\t" + hexstr
        print "Hexadecimal:\t" + ascii2hex(hexstr)

    def bin2ascii(self, binstr):
        print "Binary:\t\t" + binstr
        print "ASCII:\t\t" + bin2ascii(binstr)

    def oct2ascii(self, octstr):
        print "Octal:\t\t" + octstr
        print "ASCII:\t\t" + octal2ascii(octstr)

    def hex2ascii(self, hexstr):
        print "Hexadecimal:\t" + hexstr
        print "ASCII:\t\t" + hex2ascii(hexstr)

    def str2ascii(self, data):
        print encrypt(data)

    def ascii2str(self, data):
        print unencrypt(data)

    def pattern(self, input):

        try:
            patlen, patstr=input.split(' ')
            search = True
        except:
            patlen = input
            search = False
        #print "patlen: " + patlen
        #print "patstr: " + patstr

        stop = int(patlen) / 3 + 1
        patend = int(patlen)
        patrange = range(0,stop,1)
        first = 65
        second = 97
        third = 0
        item = ""

        for i in patrange:
            reset_first = False
            reset_second = False
            if third == 10:
                third = 0
                second += 1
            if second == 123:
                first +=1
                reset_second = True
            if first == 92:
                reset_first = True
            item += chr(first)
            item += chr(second)
            item += str(third)
            third += 1
            if reset_first:
                first = 65
            if reset_second:
                second = 97

        if search == False:
            sys.stdout.write(item[0:patend])
            print item[0:patend]
        else:
            location = item.find(patstr)
            if location == -1:
                print patstr + " not found in buffer."
                sys.exit()
            print location

    def runLoop(self):
        while 1:
            try:
                res = raw_input("RCE> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "ascii2bin" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.ascii2bin(mystring)
            elif words[0].lower() == "ascii2oct" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.ascii2oct(mystring)
            elif words[0].lower() == "ascii2hex" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.ascii2hex(mystring)
            elif words[0].lower() == "bin2ascii" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.bin2ascii(mystring)
            elif words[0].lower() == "oct2ascii" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.oct2ascii(mystring)
            elif words[0].lower() == "hex2ascii" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.hex2ascii(mystring)
            elif words[0].lower() == "pattern" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.pattern(mystring)
            elif words[0].lower() == "str2ascii" and len(words)>1:
                mystring = string.join(words[1:], ' ')
                self.str2ascii(mystring)
            elif words[0].lower() == "ascii2str" and len(words)>1:
                mystring = string.join(words[1:])
                self.ascii2str(mystring)
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() in ["exit", "quit"]:
                break
            else:
                print "Unknow option or command '%s'" % res

    def run(self):

        self.runLoop()

        return True
