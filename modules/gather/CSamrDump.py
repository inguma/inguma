#!/usr/bin/python
#
# Modified version of the CORE's script "samrdump.py" adapted for Inguma
#
# Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
# Copyright (c) 2003 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# $Id: samrdump.py,v 1.2 2003/11/14 21:26:07 jkohen Exp $
#
# Description: DCE/RPC SAMR dumper.
#
# Author:
#  Javier Kohen <jkohen@coresecurity.com>
#
# Reference for:
#  DCE/RPC.

import socket
import string
import sys
import types

from impacket import uuid
from impacket.dcerpc import dcerpc_v4, dcerpc, transport, samr
from lib.module import CIngumaModule

name = "samrdump"
brief_description = "Dump the SAM database"
type = "gather"

class ListUsersException(Exception):
    pass

class SAMRDump(CIngumaModule):
    KNOWN_PROTOCOLS = {
        '139/SMB': (r'ncacn_np:%s[\pipe\samr]', 139),
        '445/SMB': (r'ncacn_np:%s[\pipe\samr]', 445),
        }

    entries = []
    debug = False
    
    dict = {}

    def __init__(self, protocols = None,
                 username = '', password = '', gom=None):
        if not protocols:
            protocols = SAMRDump.KNOWN_PROTOCOLS.keys()

        self.__username = username
        self.__password = password
        self.__protocols = protocols
        self.gom = gom

    def debugPrint(self, *params):
        self.gom.echo( str(params) )

    def dump(self, addr):
        """Dumps the list of users and shares registered present at
        addr. Addr is a valid host name or IP address.
        """

        encoding = sys.getdefaultencoding()

        self.gom.echo( '[+] Retrieving endpoint list from %s' % addr )

        # Try all requested protocols until one works.
        entries = []
        for protocol in self.__protocols:
            protodef = SAMRDump.KNOWN_PROTOCOLS[protocol]
            port = protodef[1]

            self.gom.echo( "[+] Trying protocol %s..." % protocol )
            rpctransport = transport.SMBTransport(addr, port, r'\samr', self.__username, self.__password)

            try:
                entries = self.__fetchList(rpctransport)
            except Exception, e:
                self.gom.echo( '[!] Protocol failed: %s' % e )
                raise
            else:
                # Got a response. No need for further iterations.
                break

        # Display results.
        for entry in entries:
            (username, uid, user) = entry

            if user.is_enabled():
                self.addToDict(addr + "_users", username.replace("\x00", ""))

            buf = "User %s" % username
            self.gom.echo( buf )
            self.gom.echo( "-"*len(buf) )
            self.gom.echo( "" )
            
            base = "%s (%d)" % (username, uid)
            self.gom.echo( base + 'Enabled:' + str( ('false', 'true')[user.is_enabled()] ) )
            
            try:
            	self.gom.echo( base + 'Last Logon:' + str(user.get_logon_time()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'Last Logoff:' + str(user.get_logoff_time()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'Kickoff:' + str(user.get_kickoff_time()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'Last PWD Set:' + str(user.get_pwd_last_set()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'PWD Can Change:' + str(user.get_pwd_can_change()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'PWD Must Change:' + str(user.get_pwd_must_change()) )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'Group id: %d' % user.get_group_id() )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            	
            try:
            	self.gom.echo( base + 'Bad pwd count: %d' % user.get_bad_pwd_count() )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            
            try:
            	self.gom.echo( base + 'Logon count: %d' % user.get_logon_count() )
            except:
            	self.gom.echo( sys.exc_info()[1] )
            	
            try:
            	items = user.get_items()
            except:
            	self.gom.echo( sys.exc_info()[1] )

            for i in samr.MSRPCUserInfo.ITEMS.keys():
                name = items[samr.MSRPCUserInfo.ITEMS[i]].get_name()
                name = name.encode(encoding, 'replace')
                self.gom.echo( base + ' ' + i + ': ' + name )

            self.gom.echo( "" )

        if entries:
            num = len(entries)
            if 1 == num:
                self.gom.echo( 'Received one entry.' )
            else:
                self.gom.echo( 'Received %d entries.' % num )
        else:
            self.gom.echo( 'No entries received.' )

        self.entries = entries

    def __fetchList(self, rpctransport):
        dce = dcerpc.DCERPC_v5(rpctransport)

        encoding = sys.getdefaultencoding()
        entries = []

        dce.connect()
        dce.bind(samr.MSRPC_UUID_SAMR)
        rpcsamr = samr.DCERPCSamr(dce)

        try:
            resp = rpcsamr.connect()
            if resp.get_return_code() != 0:
                raise ListUsersException, 'Connect error'

            _context_handle = resp.get_context_handle()
            resp = rpcsamr.enumdomains(_context_handle)
            if resp.get_return_code() != 0:
                raise ListUsersException, 'EnumDomain error'

            domains = resp.get_domains().elements()

            self.gom.echo( 'Found domain(s):' )
            self.gom.echo( '' )
            for i in range(0, resp.get_entries_num()):
                self.gom.echo( " . %s" % domains[i].get_name() )

            self.gom.echo( '' )
            self.gom.echo( "Looking up users in domain %s ... " % domains[0].get_name() )
            self.gom.echo( '' )
                            
            resp = rpcsamr.lookupdomain(_context_handle, domains[0])
            if resp.get_return_code() != 0:
                raise ListUsersException, 'LookupDomain error'

            resp = rpcsamr.opendomain(_context_handle, resp.get_domain_sid())
            if resp.get_return_code() != 0:
                raise ListUsersException, 'OpenDomain error'

            domain_context_handle = resp.get_context_handle()
            resp = rpcsamr.enumusers(domain_context_handle)
            if resp.get_return_code() != 0:
                raise ListUsersException, 'OpenDomainUsers error'

            for user in resp.get_users().elements():
                uname = user.get_name().encode(encoding, 'replace')
                uid = user.get_id()

                r = rpcsamr.openuser(domain_context_handle, uid)
                self.gom.echo( "Found user: %s, uid = %d" % (uname, uid) )

                if r.get_return_code() == 0:
                    info = rpcsamr.queryuserinfo(r.get_context_handle()).get_user_info()
                    entry = (uname, uid, info)
                    entries.append(entry)
                    c = rpcsamr.closerequest(r.get_context_handle())
            self.gom.echo( '' )
        except ListUsersException, e:
            self.gom.echo( "Error listing users: %s" % e )

        dce.disconnect()

        return entries

class CSamrDump:

    target = ""
    port = 0
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    _dumper = None
    interactive = True
    user = ""
    password = ""

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print
        print "Optional:"
        print "username = <username>"
        print "password = <password>"

    def run(self):
        self.gom.echo( "[+] Trying an anonymous connection ... " )
        if self.port in (139, 445):
            proto = "%d/SMB" % self.port
            self.gom.echo( "[+] Using protocol %s" % str(proto) )
            self._dumper = SAMRDump(proto, self.user, self.password, self.gom)
        else:
            self._dumper = SAMRDump(username=self.user, password=self.password, gom=self.gom)

        self._dumper.dict = self.dict
        self._dumper.dump(self.target)
        self.dict = self._dumper.dict

        return True

# Process command-line arguments.
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "Usage: %s [username[:password]@]<address> [protocol list...]" % sys.argv[0]
        print "Available protocols: %s" % SAMRDump.KNOWN_PROTOCOLS.keys()
        print "Username and password are only required for certain transports, eg. SMB."
        sys.exit(1)

    import re

    username, password, address = re.compile('(?:([^@:]*)(?::([^@]*))?@)?(.*)').match(sys.argv[1]).groups('')

    if len(sys.argv) > 2:
        dumper = SAMRDump(sys.argv[2:], username, password)
    else:
        dumper = SAMRDump(username = username, password = password)
    dumper.dump(address)
