# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (C) 2011 Hugo Teso <hugo.teso@gmail.com>
This software is not affiliated in any way with Facebook, my current employer.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import urllib
import socket
import thread
import StringIO

class KrashLib:

    def __init__(self, om):

        # Output manager instance
        self.om = om

        self.separators = [" ", ".", "/", "&", "=", "?", ":", "\r", "\n", "\x00", "@", "-", "*" , "\\", "(", ")", "[", "]", "!", "|",
        		"#", "$",  "<", ">", ";", "%"]
        self.ignorechars = [" ", "<", ">", '"', "\r", "\n", "?", "&", "=", "%"]

        self.last_error = ""

        self.verbose = True
        self.line_mode = False
        self.ssl_mode = False
        self.url_mode = False
        self.web_mode = False

        self.numthreads = 0
        self.maxthreads = 1

        self.health = True
        self.last_packet = None
        self.start_command = None

        self.wait_time = 0
        self.threads = 0

        self.stop = False
    def token2str(self, token):
        buffer = ""
    
        for character in token:
            buffer += str(character)
    
        return buffer

    def sendssl(self, packet, host, port):

        self.numthreads += 1
    
        try:
            socket.setdefaulttimeout(3000)
            ssl_sock = None
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
            if self.verbose:
                self.om.echo("Connecting to %s:%d" % (host, int(port)))
            else:
                if self.verbose:
                    sys.stdout.write(".")
                    sys.stdout.flush()
    
            s.connect((host, int(port)))
            ssl_sock = socket.ssl(s)
    
            if self.verbose or self.web_mode:
                self.om.echo("Request (size %d):" % (len(packet)))
                
                if not self.web_mode:
                    self.om.echo(repr(packet[0:1024]))
                    self.om.echo()
    
            if not self.line_mode:
                ssl_sock.send(packet)
                res = ssl_sock.recv(128)
    
                if self.verbose:
                    if not self.web_mode:
                        self.om.echo("Response:")
                        self.om.echo(repr(res))
                    else:
                        if res.find("500") > -1:
                            self.om.echo("***Interesting response")
                            self.om.echo(repr(res))
            else:
                for line in StringIO.StringIO(packet):
                    ssl_sock.send(line)
                    res = ssl_sock.recv(128)
    
                    if self.verbose:
                        self.om.echo("Response:")
                        self.om.echo(repr(res))
        except:
            if self.last_error != str(sys.exc_info()[1]):
                if self.verbose:
                    self.om.echo("Exception:")
                    last_error = str(sys.exc_info()[1])
                    self.om.echo(last_error)
    
            if sys.exc_info()[1][0] == 111:
                self.om.echo("*** Found a bug?")
                self.om.echo("Waiting for a while....")
                
                if self.maxthreads == 1:
                    time.sleep(1)
    
#                    try:
#                        raw_input("Continue (Ctrl+C or Enter)?")
#                    except:
#                        self.om.echo("Ok. Aborted.")
#                        sys.exit(0)
    
        self.numthreads -= 1
        del ssl_sock
        s.close()
    
        if self.wait_time > 0:
            time.sleep(float(self.wait_time))

    def send(self, packet, host, port):

        self.numthreads += 1

        try:
            socket.setdefaulttimeout(0.3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
            if self.verbose:
                self.om.echo("Connecting to %s:%d" % (host, int(port)))
            else:
                if self.verbose:
                    sys.stdout.write(".")
                    sys.stdout.flush()
            s.connect((host, int(port)))
    
            if self.verbose and not self.line_mode:
                self.om.echo("Request (size %d):" % (len(packet)))
                self.om.echo(repr(packet[0:1024]))
                self.om.echo()
    
            if not self.line_mode:
                s.send(packet)
                res = s.recv(128)
                if self.verbose:
                    self.om.echo("Response:")
                    self.om.echo(repr(res))
            else:
                for line in StringIO.StringIO(packet):
                    if self.verbose:
                        self.om.echo("Request (size %d):" % (len(line)))
                        self.om.echo(repr(line[0:4096]))
    
                    res = s.recv(128)
        
                    if self.verbose:
                        self.om.echo("Response:")
                        self.om.echo(repr(res))
        except:
            if self.last_error != str(sys.exc_info()[1]):
                if self.verbose:
                    self.om.echo("Exception:")
                    last_error = str(sys.exc_info()[1])
                    self.om.echo(last_error)
    
            if sys.exc_info()[1][0] == 111:
                self.om.echo("*** Found a bug?")
                self.om.echo("Waiting for a while....")
                
                if self.maxthreads > 1:
                    time.sleep(1)

#                    try:
#                        raw_input("Continue (Ctrl+C or Enter)?")
#                    except:
#                        self.om.echo("Ok. Aborted.")
#                        sys.exit(0)
    
        self.numthreads -= 1
        s.close()
    
        if self.wait_time > 0:
            time.sleep(float(self.wait_time))

    def check_alive(self, host, port, times = 0):

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            s.close()
        except:
            if times == 0:
                time.sleep(0.1)
                self.check_alive(host, port, times = 1)
            else:
                if self.last_packet is None:
                    self.om.echo("Host appears to be down...")
                    self.om.echo("Startup it previous to try krashing something ;)")
                    #sys.exit(0)
    
                self.om.echo("HEALTH CHECK: Could not connect to host %s at %d" % (host, int(port)))
                self.om.echo("Host may be dead (Yippie!)")
                print
                self.om.echo("The last packet sent was the following (truncated at byte 2048):")
                self.om.echo("~"*80)
                self.om.echo(repr(self.last_packet)[0:2048])
                self.om.echo("~"*80)
                print
                self.om.echo("-"*80)
                #raise Exception("*** Found a bug?\r\n" + "-"*80)
            
                if self.start_command:
                    self.om.echo("[+] Starting up target program ...")
                    self.om.echo("[+] Running: %s " % self.start_command)
                    os.system(self.start_command)
                    time.sleep(1)
                    f = file("/var/TimesTen/tt70/timestend.pid", "r")
                    pid = f.read().strip("\r\n")
                    self.om.echo("PID: %s" % pid)
                    f.close()
                    cmd = "/home/joxean/proyectos/tool/krash/gdb.py %s >> audit.timesten.70.txt&" % pid
                    self.om.echo("Running %s " % cmd)
                    os.system(cmd)
                    self.om.echo("Waiting GDB to end reading the binary ... ")
                    time.sleep(3)

    def send_wrapper(self, packet, host, port):
    
        if self.health:
            self.check_alive(host, port)
    
        if self.maxthreads > 1 and self.verbose:
            self.om.echo("Using %d thread(s) out of a maximun of %d thread(s)" % (self.numthreads, self.maxthreads))
    
        self.last_packet = packet
    
        while self.numthreads > self.maxthreads:
            if self.verbose:
                self.om.echo("Waiting for child threads to end...")
    
            time.sleep(0.1)
    
        if self.maxthreads == 1:
            if not self.ssl_mode:
                self.send(packet, host, port)
            else:
                self.sendssl(packet, host, port)
        else:
            if self.numthreads >= self.maxthreads:
                time.sleep(0.5)
    
            if not self.ssl_mode:
                thread.start_new_thread(self.send, (packet, host, port))
            else:
                thread.start_new_thread(self.sendssl, (packet, host, port))

    def tokenize_packet(self, packet):
    
        ret = []
        buffer = ""
    
        for character in packet:
            if character in self.separators:
                if buffer != "":
                    ret.append(buffer)
                ret.append(character)
                buffer = ""
            else:
                buffer += character
    
        if buffer != "":
            ret.append(buffer)
    
        return ret

    def fuzz(self, base_packet, host, port, idx):

        mtokens = self.tokenize_packet(base_packet)

        # Fuzzing data
        strings = ("A", 
                   "%s", "%n", "%x", "%d", 
                   "/.", "\\\\", "C:\\", "../", "..\\")
        numbers = (-2, -1, 0, 1, 2147483647, 4294967294, -2147483647, -4294967294)
        sizes   = (1, 4, 100, 500, 2000, 5000, 9000, 10000)
    
        tokens = mtokens
        global_counter = 0
    
        # Go over the tokens starting at idx
        for index in range(int(idx), len(mtokens)):
            if not self.stop:
                tokens = self.tokenize_packet(base_packet)
                buffer = ""
        
                # Skip separators and characters to ignore
                if tokens[index] in self.separators:
                    if tokens[index] in self.ignorechars:
                        continue
        
                # Used to mark a token as URL parameter
                is_var = False
        
                if self.url_mode:
                    if tokens[index-1] == "&":
                        is_var = True
                        continue
                    else:
                        is_var = False
        
                counter = 0
        
                # Fuzz with numbers
                for num in numbers:
                    if not self.stop:
                        counter+= 1
                        if counter < 0:
                            continue
                            
                        if self.verbose:
                            self.om.echo("Fuzzing var %d:%d" % (index, counter))
                        buffer = tokens
                        buffer[index] = num
            
                        self.send_wrapper(self.token2str(buffer), host, port)
                        global_counter += 1
                    else:
                        break
        
                # Fuzz with different sizes
                for size in sizes:
                    if not self.stop:
        
                        # Fuzz using defined strings
                        for fuzz_str in strings:
                            if not self.stop:
                                counter += 1
                                if counter < 0:
                                    continue
                                
                                if self.verbose:
                                    self.om.echo("Fuzzing var %d:%d:%d" % (index, counter, size))
                                buffer = tokens
                                buffer[index] = fuzz_str*size
                                if not is_var:
                                    self.send_wrapper(self.token2str(buffer), host, port)
                                else:
                                    self.send_wrapper(urllib.quote(self.token2str(buffer)), host, port)
                
                                global_counter += 1
                            else:
                                break
            
                        # Fuzz using all caracters
                        for char in range(0, 255):
                            if not self.stop:
                        
                                if chr(char) in ["&", "="]:
                                    continue
                                counter += 1
                                if counter < 0:
                                    continue
                
                                if self.verbose:
                                    self.om.echo("Fuzzing var %d:%d:%d" % (index, counter, size))
                
                                buffer = tokens
                                buffer[index] = chr(char)*size
                                if not is_var:
                                    self.send_wrapper(self.token2str(buffer), host, port)
                                else:
                                    self.send_wrapper(urllib.quote(self.token2str(buffer)), host, port)
                                global_counter += 1
                            else:
                                break
                else:
                    break
            else:
                break
