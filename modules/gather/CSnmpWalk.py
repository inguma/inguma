#!/usr/bin/python

"""
Module snmpwalk for Inguma
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL version 2
"""

"""
NOTE: Must be enhanced with, in example, an SNMP fuzzer.
"""

import sys

from pysnmp import asn1, v1, v2c
from pysnmp import role

from lib.libsnmp import oidToHuman, rootMibs
from lib.module import CIngumaModule

name = "snmpwalk"
brief_description = "Snmp walk module for Inguma"
type = "gather"

class CSnmpWalk(CIngumaModule):
    port = 161
    waitTime = 0
    timeout = 1
    exploitType = 1
    services = {}
    results = {}
    community = "public"
    dict = None
    retries = 1
    interactive = True

    def showHelp(self):
        print 
        print "Inguma's SNMP Tool Help"
        print "-----------------------"
        print
        print "run                          Walk over the complete tree"
        print "raw <tree>                   Walk over the specified tree"
        print "help                         Show this help"
        print "exit                         Exit from the snmp interface"
        print
        print "Other commands to see special trees:"
        print

        for x in rootMibs:
            print "  " + rootMibs[x]

        print
    def snmpLoop(self):
        while 1:
            try:
                res = raw_input("SNMP> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() in ["exit", "quit"]:
                break
            elif words[0].lower() in ["walk", "run"]:
                self.runWalk()
            elif words[0].lower() == "raw":
                if len(words) > 1:
                    data = words[1:]
                    print data
                    self.showOid(data)
            elif words[0].lower() == "help":
                self.showHelp()
            else:
                flag = False
                for x in rootMibs:
                    if rootMibs[x].lower() == words[0].lower():
                        self.showOid([x[1:]])
                        flag = True
                        break

                if not flag:
                    print "Unknow command or option '%s'" % res

    def run(self):
    
        if self.port == 0:
            self.port = 161 

        if self.interactive:
            return self.snmpLoop()
        else:
            self.showOid(["1.3.6.1"])
            return True

    def runWalk(self):
        self.showOid(["1.3.6.1"])

    def showOid(self, head_oids):
        # Create SNMP manager object
        client = role.manager((self.target, self.port))
        
        # Pass it a few options
        client.timeout = self.timeout
        client.retries = self.retries
        
        # Create a SNMP request&response objects from protocol version
        # specific module.
        try:
            req = v1.GETREQUEST()
            nextReq = v1.GETNEXTREQUEST()
            rsp = v1.GETRESPONSE()

        except (NameError, AttributeError):
            print sys.exc_info()[1]
            return False
        
        # Store tables headers
        #head_oids = ["1.3.6.1."]
        
        try:
            # BER encode initial SNMP Object IDs to query
            encoded_oids = map(asn1.OBJECTID().encode, head_oids)
        except:
            print "Error.", sys.exc_info()[1]
            return

        # Traverse agent MIB
        while 1:
            # Encode SNMP request message and try to send it to SNMP agent
            # and receive a response
            (answer, src) = client.send_and_receive(\
                            req.encode(community=self.community, encoded_oids=encoded_oids))
        
            # Attempt to decode SNMP response
            rsp.decode(answer)
        
            # Make sure response matches request (request IDs, communities, etc)
            if req != rsp:
                raise Exception('Unmatched response: %s vs %s' % (str(req), str(rsp)))
        
            # Decode BER encoded Object IDs.
            oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, \
                                           rsp['encoded_oids']))
        
            # Decode BER encoded values associated with Object IDs.
            vals = map(lambda x: x[0](), map(asn1.decode, rsp['encoded_vals']))
        
            # Check for remote SNMP agent failure
            if rsp['error_status']:
                # SNMP agent reports 'no such name' when walk is over
                if rsp['error_status'] == 2:
                    # Switch over to GETNEXT req on error
                    # XXX what if one of multiple vars fails?
                    if not (req is nextReq):
                        req = nextReq                
                        continue
                    # One of the tables exceeded
                    for l in oids, vals, head_oids:
                        del l[rsp['error_index']-1]
                else:
                    raise Exception('SNMP error #' + str(rsp['error_status']) + ' for OID #' \
                          + str(rsp['error_index']))
        
            # Exclude completed OIDs
            while 1:
                for idx in range(len(head_oids)):
                    if not asn1.OBJECTID(head_oids[idx]).isaprefix(oids[idx]):
                        # One of the tables exceeded
                        for l in oids, vals, head_oids:
                            del l[idx]
                        break
                else:
                    break
        
            if not head_oids:
                return False

            # Print out results
            for (oid, val) in map(None, oids, vals):
                if str(val) != "":
                    print oidToHuman(oid) + ' = ' + str(val)

            # BER encode next SNMP Object IDs to query
            encoded_oids = map(asn1.OBJECTID().encode, oids)

            # Update request object
            req['request_id'] = req['request_id'] + 1
        
            # Switch over GETNEXT PDU for if not done
            if not (req is nextReq):
                req = nextReq

        return True
