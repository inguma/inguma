#!/usr/bin/python
#
# Modified version of the CORE's script "rpcdump.py" adapted for Inguma
#
# Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>
# Copyright (c) 2003 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE.core file
# for more information.
#
# $Id: rpcdump.py,v 1.2 2003/10/28 21:02:20 jkohen Exp $
#
# DCE/RPC endpoint mapper dumper.
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
from impacket.dcerpc import dcerpc_v4, dcerpc, transport, epm
from lib.module import CIngumaModule

name = "rpcdump"
brief_description = "DCE/RPC endpoint mapper dumper"
type = "gather"

class RPCDump(CIngumaModule):
    KNOWN_PROTOCOLS = {
        '139/SMB': (r'ncacn_np:%s[\pipe\epmapper]', 139),
        '445/SMB': (r'ncacn_np:%s[\pipe\epmapper]', 445),
        '135/TCP': (r'ncacn_ip_tcp:%s', 135),
        '135/UDP': (r'ncadg_ip_udp:%s', 135),
        '80/HTTP': (r'ncacn_http:%s', 80),
        }

    dict = None

    def __init__(self, protocols = None,
                 username = '', password = ''):
        if not protocols:
            protocols = RPCDump.KNOWN_PROTOCOLS.keys()

        self.__username = username
        self.__password = password
        self.__protocols = protocols

    def dump(self, addr, gom):
        """Dumps the list of endpoints registered with the mapper
        listening at addr. Addr is a valid host name or IP address in
        string format.
        """

        self.gom = gom
        self.gom.echo( '[+] Retrieving endpoint list from %s' % addr )

        # Try all requested protocols until one works.
        entries = []
        for protocol in self.__protocols:
            protodef = RPCDump.KNOWN_PROTOCOLS[protocol]
            port = protodef[1]

            self.gom.echo( "[+] Trying protocol %s..." % protocol )
            stringbinding = protodef[0] % addr

            rpctransport = transport.DCERPCTransportFactory(stringbinding)
            rpctransport.set_dport(port)
            if hasattr(rpctransport, 'set_credentials'):
                # This method exists only for selected protocol sequences.
                rpctransport.set_credentials(self.__username, self.__password)

            try:
                entries = self.__fetchList(rpctransport)
            except Exception, e:
                self.gom.echo( '[!] Protocol failed: %s' % e )
            else:
                # Got a response. No need for further iterations.
                break


        # Display results.
        self.gom.echo( "" )

        for entry in entries:
            base = entry.getUUID()
            self.addToDict(addr + "_rpc_endpoints", base)

            if 'unknown' != entry.getProviderName():
                self.gom.echo( base + '/Provider: ' + entry.getProviderName() )
                self.addToDict(addr + "_rpc_endpoints", ["provider", entry.getProviderName()])

            self.gom.echo( base + '/Version: ' + entry.getVersion() )
            self.addToDict(addr + "_rpc_endpoints", ["version", entry.getVersion()])

            if entry.getAnnotation():
                self.gom.echo( base + '/Annotation: ' + entry.getAnnotation() )
                self.addToDict(addr + "_rpc_endpoints", ["annotation", entry.getAnnotation()])

            objbase = base
            if not entry.isZeroObjUUID():
                objbase += '/' + entry.getObjUUID()
                self.addToDict(addr + "_rpc_endpoints", ["obj_uuid", entry.getObjUUID()])

            stringbinding = transport.DCERPCStringBindingCompose('', entry.getProtocol(), '', entry.getEndpoint())
            self.gom.echo( objbase + '/StringBindings: ' + stringbinding )
            self.addToDict(addr + "_rpc_endpoints", ["stringbindings", stringbinding])
            self.gom.echo( "" )

        if entries:
            num = len(entries)
            if 1 == num:
                self.gom.echo( 'Received one endpoint.' )
            else:
                self.gom.echo( 'Received %d endpoints.' % num )
        else:
            self.gom.echo( 'No endpoints found.' )


    def __fetchList(self, rpctransport):
        # UDP only works over DCE/RPC version 4.
        if isinstance(rpctransport, transport.UDPTransport):
            dce = dcerpc_v4.DCERPC_v4(rpctransport)
        else:
            dce = dcerpc.DCERPC_v5(rpctransport)

        entries = []

        dce.connect()
        dce.bind(epm.MSRPC_UUID_PORTMAP)
        rpcepm = epm.DCERPCEpm(dce)

        resp = rpcepm.portmap_dump()
        while resp.get_entries_num() != 0:
            rpc_handle = resp.get_handle()
            ndrentry = resp.get_entry().get_entry()
            sb = transport.DCERPCStringBinding(ndrentry.get_string_binding())
            entry = epm.EpmEntry(uuid.bin_to_string(ndrentry.get_uuid()),
                                 ndrentry.get_version(),
                                 ndrentry.get_annotation(),
                                 uuid.bin_to_string(ndrentry.get_objuuid()),
                                 sb.get_protocol_sequence(),
                                 sb.get_endpoint())
            entries.append(entry)
            resp = rpcepm.portmap_dump(rpc_handle)

        dce.disconnect()

        return entries

class CRpcDump:

    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    user = ""
    password = ""

    def help(self):
        print "target = <target host or network>"
        print "port = <target port>"
        print
        print "Optional:"
        print "user = <username>"
        print "password = <password>"

    def run(self):
        self.gom.echo( "[+] Trying an anonymous connection ... " )
        self._dumper = RPCDump(username=self.user, password=self.password)
        self._dumper.dict = self.dict

        return True

    def printSummary(self):
        self.gom.echo( "" )
        self.gom.echo( "Gathered data" )
        self.gom.echo( "-------------" )
        self.gom.echo( "" )
        self._dumper.dump(self.target, self.gom)

# Process command-line arguments.
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "Usage: %s [username[:password]@]<address> [protocol list...]" % sys.argv[0]
        print "Available protocols: %s" % RPCDump.KNOWN_PROTOCOLS.keys()
        print "Username and password are only required for certain transports, eg. SMB."
        sys.exit(1)

    import re

    username, password, address = re.compile('(?:([^@:]*)(?::([^@]*))?@)?(.*)').match(sys.argv[1]).groups('')

    if len(sys.argv) > 2:
        dumper = RPCDump(sys.argv[2:], username, password)
    else:
        dumper = RPCDump(username = username, password = password)
    dumper.dump(address)
