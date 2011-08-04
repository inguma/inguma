#
# Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
# Copyright (c) 2002, Core SDI S.A., Argentina
# All rights reserved
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither name of the Core SDI S.A. nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import sys
import time
import string
from impacket import smb
from lib.module import CIngumaModule

name = "smbclient"
brief_description = "A simple SMB Client"
type = "gather"

class CSmbClient(CIngumaModule):

    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    interactive = True

    def help(self):
        print "target = <target host or network>"

    def eval(self, s):
        l = string.split(s, ' ')
        cmd = l[0]
        
        try:        
            f = CSmbClient.__dict__[cmd]
            l[0] = self
            f(*l)
        except Exception, e:
            print "Error %s" % e

    def run(self):
        # Open the connection
        s = "open %s %d" % (self.target, self.port)
        self.eval(s)

        print "[+] Trying a NULL connection ... "
        try:
            self.login("", "")
            print "[+] Ok. It works."
            self.info()
            print
        except:
            print "[!]", sys.exc_info()[1]
            print "You will need to login first :("

        if self.interactive:
            try:
                self.runLoop()
            except KeyboardInterrupt:
                return True
            except EOFError:
                return True
            except:
                print "Error.", sys.exc_info()[1]
                return False

        return True

    def runLoop(self):
        while self.interactive:
            s = raw_input('SMB> ')

            if s.lower() == "exit" or s.lower() == "quit":
                break
            elif s.lower() == "close":
                self.smb.close(0, 0)
            elif s.lower() == "test":
                print dir(self.smb)
            elif s.lower() == "info":
                self.info()
            else:
                self.eval(s)

    def help(self):
        print """
 open hosport - opens a SMB connection against the target host/port
 login username passwd - logs into the current SMB connection
 login_hash username lmhash nthash - logs into the current SMB connection using the password hashes
 logoff - logs off
 info - Get information about the current connection
 shares - list available shares
 use sharename - connect to an specific share
 cd path - changes the current directory to {path}
 pwd - shows current remote directory
 ls wildcard - lists all the files in the current directory
 rm file - removes the selected file
 mkdir dirname - creates the directory under the current path
 rmdir dirname - removes the directory under the current path
 put filename - uploads the filename into the current path
 get filename - downloads the filename from the current path
 cat filename - Show the contents of the filename
 close - closes the current SMB Session
 exit - terminates the server process (and this session)

 An empty line finishes the session
 NOTE: the server is not terminated, although it is left unusable
"""

    def open(self,host,port):
        self.smb = smb.SMB("*SMBSERVER", host, port)

    def login(self,username, password):
        if not self.smb:
            print "Open a connection first."

        self.smb.login(username, password)

    def login_hash(self,username, lmhash, nthash):
        if not self.smb:
            print "Open a connection first."

        self.smb.login(username, '', lmhash=lmhash, nthash=nthash)

    def logoff(self):
        if not self.smb:
            print "Open a connection first."

        self.smb.logoff()
        self.smb = None

    def shares(self):
        if not self.smb:
            print "Open a connection first."

        print "List of remote shares"
        print "---------------------"
        print
        for share in self.smb.list_shared():
            print "Name:", share.get_name()
            print "Type:", share.get_type()
            print "Comment:", share.get_comment()
            print

    def use(self,sharename):
        if not self.smb:
            print "Open a connection first."

        self.share = sharename
        self.tid = self.smb.tree_connect(sharename)

    def cd(self, path):
        p = string.replace(path,'/','\\')
        if p[0] == '\\':
           self.pwd = path
        else:
           self.pwd += '/' + path

    def pwd(self):
        print self.pwd

    def ls(self, wildcard = None):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return

        if wildcard == None:
           pwd = self.pwd + '/*'
        else:
           pwd = self.pwd + '/' + wildcard
        print "self.share", self.share
        print "pwd", pwd

        for f in self.smb.list_path(self.share, pwd):
           print f.get_longname()

    def rm(self, filename):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return

        f = self.pwd + '/' + filename
        file = string.replace(f,'/','\\')
        self.smb.remove(self.share, file)
 
    def mkdir(self, path):
        if not self.smb:
            print "Open a connection first."

        p = self.pwd + '/' + path
        pathname = string.replace(p,'/','\\')
        self.smb.mkdir(self.share,pathname)

    def rmdir(self, path):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return
        
        p = self.pwd + '/' + path
        pathname = string.replace(p,'/','\\')
        self.smb.rmdir(self.share, pathname)

    def put(self, filename):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return
        
        fh = open(filename, 'rb')
        f = self.pwd + '/' + filename
        pathname = string.replace(f,'/','\\')
        self.smb.stor_file(self.share, pathname, fh.read)
        fh.close()

    def get(self, filename):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return
        
        fh = open(filename,'wb')
        f = self.pwd + '/' + filename
        pathname = string.replace(f,'/','\\')
        self.smb.retr_file(self.share, pathname, fh.write)
        fh.close()

    def info(self):
        if not self.smb:
            print "Open a connection first."

        domain = self.smb.get_server_domain()
        lanman = self.smb.get_server_lanman()
        serverName = self.smb.get_server_name()
        serverOs = self.smb.get_server_os()
        serverTime = self.smb.get_server_time()
        sessionKey = self.smb.get_session_key()
        loginRequired = self.smb.is_login_required()

        print "Current connection information"
        print "------------------------------"
        print
        print "Domain name      :", domain
        print "Lanman           :", lanman
        print "Server name      :", serverName
        print "Operative System :", serverOs
        print "Server Time      :", serverTime
        print "Session Key      :", sessionKey
        print
        print "Is login required?", loginRequired

        data = {}
        data["domain"] = domain
        data["lanman"] = lanman
        data["server_name"] = serverName
        data["os"] = serverOs
        data["time"] = (time.time(), serverTime)
        data["key"] = sessionKey
        data["login_required"] = loginRequired

        self.addToDict(self.target + "_os", serverOs)
        self.addToDict(self.target + "_smb", data)

    def cat(self, filename):
        if not self.smb:
            print "Open a connection first."

        if self.share == "" or self.share == None:
            print "No active share."
            return

        f = self.pwd + '/' + filename
        pathname = string.replace(f,'/','\\')
        print self.smb.retr_file(self.share, pathname, None)

    def close(self):
        if not self.smb:
            print "Open a connection first."

        self.smb.close();

def main():
    shell = CSmbClient()
    shell.runLoop()

if __name__ == "__main__":
    main()
