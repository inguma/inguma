#       liblistener.py
#       
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
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

import socket

class Listener:
    """ Main listener class """

    def __init__(self, om):

        self.gom = om

        self.PORT = 31337
        self.SIZE = 512
        self.HOST = '127.0.0.1'

        self.conn = False
        self.keep = True

    def run(self, port, host, type=''):
        if type == 'local':
            self.create_local_listener(port, host)
        else:
            # WIP
            pass

    def create_local_listener(self, port, host, platform=''):
        """Create and return a new local listener"""

        if not port:
            port = self.PORT
        if not host:
            host = self.HOST

        try:
            self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.gom.echo( "Error in creating socket : ", e, False)
            return False

        self.sockfd.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

        try:
            self.sockfd.bind((host, port))
        except socket.error, e:
            self.gom.echo( "Error in Binding : ", e, False)
            return False


        self.gom.echo( "== New Listener created on Port %d ==" % port, False)

        while self.keep: # listen for connections  
            self.sockfd.listen(1)
#            self.clientsock , clientaddr = self.sockfd.accept()
#            self.conn = True
#            self.gom.echo( "Got Connection from " + str(clientaddr), False )
#
#            while 1:  
#                try:
#                    cmd = raw_input('--> ')
#                except:
#                    break
#
#                # close the connection
#                if cmd == 'close': # close the connection
#                    self.gom.echo("== Connection Closed ==", False)
#                    self.clientsock.shutdown(0)
#                    break
#                # close the listener
#                elif cmd == 'g0dby3':
#                    self.exit()
#                    return False
#                else:
#                    self.clientsock.send(cmd + '\n')
#                    output = self.clientsock.recv(self.SIZE).strip()
#                    self.gom.echo("Command Output :- \n" + output + "\r\n", False)
#
#        self.gom.echo( ">>>> Server Terminated <<<<<", False)

    def exit(self):
#       if self.conn:
#            self.clientsock.shutdown(0)
#            self.conn = False
        self.keep = False
        self.sockfd.shutdown(0)
        self.gom.echo( ">>>> Server Terminated <<<<<", False)

    def create_remote_listener(self, port, host, platform=''):
        """Create and return a new remote listener"""

        if not port:
            port = self.PORT
        if not host:
            host = self.HOST

        try:
            self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.gom.echo("Error in creating socket : ", e)
            return False

        self.sockfd.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

        try:
            #sockfd.bind((host, port))
            # To be used for remote listener
            self.sockfd.connect((host,port))
        except socket.gaierror, e:
            self.gom.echo("Error (Address-Related) while Connecting to server : ",e)
        except socket.error, e:
            self.gom.echo("Error while Connecting to Server : ",e)
            return False
#        except socket.error, e:
#            self.gom.echo("Error in Binding : ", e)
#            return False

        self.gom.echo("\n\n======================================================")
        self.gom.echo( "----------  Connected to %s %d ----------------" % (host, port) )
        self.gom.echo("======================================================\n\n")

        while self.keep: # listen for connections  
            self.conn = True
            while 1:  
                try:
                    cmd = raw_input('--> ')
                except:
                    break

                # close the connection
                if cmd == 'close': # close the connection
                    self.gom.echo("\n-----------Connection Closed----------------")
                    self.sockfd.close()
                    break
                else:
                    self.sockfd.send(cmd + '\n')
                    output = self.sockfd.recv(self.SIZE).strip()
                    self.gom.echo("Command Output :- \n" + output + "\r\n")

        self.gom.echo("\n\n>>>> Server Terminated <<<<<\n")
        return False
