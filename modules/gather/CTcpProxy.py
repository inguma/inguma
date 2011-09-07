#!/usr/bin/python

##      CTcpProxy.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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

from socket import *
from threading import Thread

from lib.module import CIngumaModule

name = "tcpproxy"
brief_description = "A simple TCP proxy for port forwarding"
type = "gather" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

globals = ['newport',]

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump(src, length=16):
    N=0; result=''
    while src:
        s,src = src[:length],src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
        N+=length
    return result

class CTcpProxy(CIngumaModule):
    """ The example module. The main class will always starts with the character "C". Any other class will be ignored """

    newport = 0

    def help(self):
        """ This is the entry point for info <module> """
        print "target = <target host or network>"
        print "port = <target port>"
        print "newport = <new target port>"

    def run(self):
        """ This is the main entry point of the module """
        print 'Starting TCP proxy'

        if self.newport == 0:
            self.newport = self.port
        Proxy( self.port, self.target, self.newport ).start()

class PipeThread( Thread ):

    pipes = []
    ascii = False

    def __init__( self, source, sink ):
        Thread.__init__( self )
        self.source = source
        self.sink = sink

        print 'Creating new pipe thread  %s ( %s -> %s )' % \
            ( self, source.getpeername(), sink.getpeername() )
        PipeThread.pipes.append( self )
        print '%s pipes active' % len( PipeThread.pipes )

    def run( self ):
        while 1:
            try:
                data = self.source.recv( 1024 )
                print dump(data)
                if not data: break
                self.sink.send( data )
            except:
                break

        #log( '%s terminating' % self )
        PipeThread.pipes.remove( self )
        #log( '%s pipes active' % len( PipeThread.pipes ))

class Proxy( Thread ):

    def __init__( self, port, newhost, newport ):
        Thread.__init__( self )
        print 'Redirecting: localhost:%s -> %s:%s' % ( port, newhost, newport )
        self.newhost = newhost
        self.newport = newport
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( '', port ))
        self.sock.listen(5)

    def run( self ):
        while 1:
            newsock, address = self.sock.accept()
            print 'Creating new session for %s %s ' % address
            fwd = socket( AF_INET, SOCK_STREAM )
            fwd.connect(( self.newhost, self.newport ))
            PipeThread( newsock, fwd ).start()
            PipeThread( fwd, newsock ).start()
        return False

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
