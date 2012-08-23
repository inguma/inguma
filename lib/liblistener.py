#       liblistener.py
# encoding: utf-8
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#       Copyright 2012 David Martínez Moreno <ender@debian.org>
#       Based on code from w3af by Andres Riancho (w3af.sourceforge.net)
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

import errno
import lib.globals as glob
import socket

class Listener:
    """ Main listener class """

    def __init__(self):

        self.SIZE = 512

        self.clientsock = None
        self.conn = False
        self.keep = 1

    def __del__(self):
        """Destructor for the Listener class."""

        if self.clientsock:
            self.socket.shutdown(socket.SHUT_RDWR)

        self.socket.close()

    def run(self, port, host, type=''):
        if type == 'local':
            self.create_local_listener(port, host)
        else:
            # WIP
            pass

    def create_local_listener(self, port, host='127.0.0.1', platform=''):
        """Create and return a new local listener"""

        try:
            self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            glob.gom.echo("Error in creating socket %s: " % e, False)
            return False

        self.sockfd.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

        try:
            self.sockfd.bind((host, port))
        except socket.error, e:
            glob.gom.echo("Error in binding : %s" % e, False)
            return False


        glob.gom.echo("== New listener created on %s:%d ==" % (host, port), False)

        self.sockfd.listen(1)
        while self.keep: # listen for connections
            self.conn = False
            try:
                self.clientsock, clientaddr = self.sockfd.accept()
                self.conn = True
            except socket.error, e:
                # Just catch the [Errno 22] Invalid argument.
                if not e.errno == errno.EINVAL:
                    raise
            if self.conn:
                glob.gom.update_listener_status(clientaddr[0], port)
                while 1:
                    data = self.clientsock.recv(1024)
                    if not data: break
                    glob.gom.echo(data)

#            while 1:  
#                try:
#                    cmd = raw_input('--> ')
#                except:
#                    break
#
#                # close the connection
#                if cmd == 'close': # close the connection
#                    glob.gom.echo("== Connection Closed ==", False)
#                    self.clientsock.shutdown(0)
#                    break
#                # close the listener
#                elif cmd == 'g0dby3':
#                    self.exit()
#                    return False
#                else:
#                    self.clientsock.send(cmd + '\n')
#                    output = self.clientsock.recv(self.SIZE).strip()
#                    glob.gom.echo("Command Output :- \n" + output + "\r\n", False)
#
#        glob.gom.echo(">>>> Server Terminated <<<<<", False)

    def exit(self):
        self.keep = 0
        if self.conn:
            self.clientsock.shutdown(2)
            self.clientsock.close()
            self.conn = False

        self.sockfd.shutdown(socket.SHUT_RDWR)
        self.sockfd.close()
        glob.gom.echo(">>>> Server terminated <<<<<", False)

    def create_remote_listener(self, port, host='127.0.0.1', platform=''):
        """Create and return a new remote listener"""

        try:
            self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            glob.gom.echo("Error in creating socket : ", e)
            return False

        self.sockfd.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

        try:
            #sockfd.bind((host, port))
            # To be used for remote listener
            self.sockfd.connect((host,port))
        except socket.gaierror, e:
            glob.gom.echo("Error (address-related) while connecting to server : ",e)
        except socket.error, e:
            glob.gom.echo("Error while connecting to server : ",e)
            return False
#        except socket.error, e:
#            glob.gom.echo("Error in Binding : ", e)
#            return False

        glob.gom.echo("\n\n======================================================")
        glob.gom.echo("----------  Connected to %s %d ----------------" % (host, port) )
        glob.gom.echo("======================================================\n\n")

        while self.keep: # listen for connections  
            self.conn = True
            while 1:  
                try:
                    cmd = raw_input('--> ')
                except:
                    break

                # close the connection
                if cmd == 'close': # close the connection
                    glob.gom.echo("\n-----------Connection closed----------------")
                    self.sockfd.close()
                    break
                else:
                    self.sockfd.send(cmd + '\n')
                    output = self.sockfd.recv(self.SIZE).strip()
                    glob.gom.echo("Command output :- \n" + output + "\r\n")

        glob.gom.echo("\n\n>>>> Server terminated <<<<<\n")
        return False
