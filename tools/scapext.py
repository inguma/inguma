#!/usr/bin/env python

# Scapy Extended
#
# 0.1.4 :
# - Added GeoIP support (with GeoIP Python API, see
#   http://www.maxmind.com/download/geoip/api/python/). This enables to use
#   (at least) GeoLite Country (http://www.maxmind.com/app/geoip_country)
#   and GeoLite City (http://www.maxmind.com/app/geolitecity). Use
#   conf.GeoIP_(country|city) to tell scapext where your DB files are
#   (default to /var/lib/GeoIP/). This provides, for now, host2coords and
#   host2country, and an updated version of TracerouteResult.world_trace.
# - Added ASN resolution (taken from scapy.py:TracerouteResult.makegraph,
#   might be usefull in other places)
# 0.1.3 :
# - Updated SunRPC support
# 0.1.2 :
# - GRE support (zer0@droids-corp.org)
#   http://trac.secdev.org/scapy/ticket/21
# 0.1.1 :
# - PFLog support
#   http://trac.secdev.org/scapy/ticket/7
# - Early and experimental SunRPC support
# 
# see http://pierre.droids-corp.org/scapy/

from scapy import *

EXTVERSION="0.1.4"


#### GeoIP support

conf.GeoIP_country = "/var/lib/GeoIP/GeoIP.dat"
conf.GeoIP_city = "/var/lib/GeoIP/GeoLiteCity.dat"
conf.gnuplot_world = "/usr/share/doc/gnuplot-4.0.0/demo/world.dat"

try:
    import GeoIP
    geoipcountry = GeoIP.open(conf.GeoIP_country, GeoIP.GEOIP_MEMORY_CACHE)
    geoipcity = GeoIP.open(conf.GeoIP_city, GeoIP.GEOIP_MEMORY_CACHE)
except ImportError:
    log_loading.warning("Cannont import GeoIP. Won't be able to provide IP localisation.")

def host2coords(host):
    try:
        rec = geoipcity.record_by_addr(host)
    except SystemError:
        try:
            rec = geoipcity.record_by_name(host)
        except SystemError:
            return None
    return rec['longitude'], rec['latitude']

def host2country(host):
    try:
        code = geoipcountry.country_code_by_addr(host)
        name = geoipcountry.country_name_by_addr(host)
    except SystemError:
        code = geoipcountry.country_code_by_name(host)
        name = geoipcountry.country_name_by_name(host)
    if code == None:
        return None
    return code, name

# we want to use this for TracerouteResult.world_trace

def TracerouteResult_world_trace(self):
    ips = {}
    rt = {}
    ports_done = {}
    for s,r in self.res:
        ips[r.src] = None
        if s.haslayer(TCP) or s.haslayer(UDP):
            trace_id = (s.src,s.dst,s.proto,s.dport)
        elif s.haslayer(ICMP):
            trace_id = (s.src,s.dst,s.proto,s.type)
        else:
            trace_id = (s.src,s.dst,s.proto,0)
        trace = rt.get(trace_id,{})
        if not r.haslayer(ICMP) or r.type != 11:
            if ports_done.has_key(trace_id):
                continue
            ports_done[trace_id] = None
        trace[s.ttl] = r.src
        rt[trace_id] = trace

    trt = {}
    for trace_id in rt:
        trace = rt[trace_id]
        loctrace = []
        for i in range(max(trace.keys())):
            ip = trace.get(i,None)
            if ip is None:
                continue
            loc = host2coords(ip)
            if loc is None:
                continue
            #loctrace.append((ip,loc)) # no labels yet
            loctrace.append(loc)
        if loctrace:
            trt[trace_id] = loctrace

    tr = map(lambda x: Gnuplot.Data(x,with="lines"), trt.values())
    g = Gnuplot.Gnuplot()
    world = Gnuplot.File(conf.gnuplot_world,with="lines")
    g.plot(world,*tr)
    return g

TracerouteResult.world_trace = TracerouteResult_world_trace
del(TracerouteResult_world_trace)



#### ASN resolution

def getASNlist_ra(list):
    
    def parseWhois(x):
        asn,desc = None,""
        for l in x.splitlines():
            if not asn and l.startswith("origin:"):
                asn = l[7:].strip()
            if l.startswith("descr:"):
                if desc:
                    desc += r"\n"
                desc += l[6:].strip()
            if asn is not None and desc:
                break
        return asn,desc.strip()
    
    ASNlist = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("whois.ra.net",43))
    for ip in list:
        s.send("-k %s\n" % ip)
        asn,desc = parseWhois(s.recv(8192))
        ASNlist.append((ip,asn,desc))
    return ASNlist

def getASNlist_cymru(list):
    ASNlist = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("whois.cymru.com",43))
    s.send("begin\r\n"+"\r\n".join(list)+"\r\nend\r\n")
    r = ""
    while 1:
        l = s.recv(8192)
        if l == "":
            break
        r += l
    s.close()
    for l in r.splitlines()[1:]:
        asn,ip,desc = map(str.strip, l.split("|"))
        if asn == "NA":
            continue
        asn = "AS" + asn
        ASNlist.append((ip,asn,desc))
    return ASNlist


#### SunRPC support + "state engine"

# let's read /etc/rpc to resolv rpc progs numbers

RPC_PROGRAMS={}
try:
    f=open("/etc/rpc")
    for l in f:
        try:
            if l[0] in ["#","\n"]:
                continue
            lt = tuple(re.split(spaces, l))
            if len(lt) < 2:
                continue
            RPC_PROGRAMS.update({lt[0]:int(lt[1])})
        except:
            log_loading.info("Couldn't parse one line from rpc file (" + l + ")")
    f.close()
except IOError,msg:
    log_loading.info("Can't open /etc/rpc file")


# now the generic Packet.update_states() method : we just need it to be recursive
# This should be added in Packet(Gen) definition.

def Packet_update_states(self):
    if type(self.payload) is not NoPayload:
        self.payload.update_states()

Packet.update_states = Packet_update_states
del(Packet_update_states)


# the packet classes :

class SunRPC(Packet):
    name = "SunRPC"
    longname = "Sun Remote Procdeure Call"
    fields_desc = [ ConditionalField(BitField("lastfrag", 1, 1), "underlayer", lambda x: type(x) is TCP),
                    ConditionalField(BitField("fraglen", 0, 31), "underlayer", lambda x: type(x) is TCP),
                    XIntField("XID", 0),
                    IntEnumField("msgtype", 0, {0:"Call", 1:"Reply"}) ]


class SunRPCCall(Packet):
    name = "SunRPCCall"
    longname = "Sun RPC Call"
    fields_desc = [ IntField("RPCversion", 2),
                    IntEnumField("program", 100000, RPC_PROGRAMS),
                    IntField("progversion", 0),
                    IntEnumField("procedure", 0, { 0 : "null", 1 : "set",
                                                   2 : "unset", 3 : "getport",
                                                   4 : "dump", 5 : "callit" }),
                    IntEnumField("credflavor", 0, {0:"null"}),
                    FieldLenField("credlen", None, "credentials", fmt="I"),
                    StrLenField("credentials", "", "credlen"),
                    IntEnumField("verifflavor", 0, {0:"null"}),
                    FieldLenField("veriflen", None, "verifier", fmt="I"),
                    StrLenField("verifier", "", "veriflen") ]

    def update_states(self):
        if type(self.underlayer) is SunRPC:
            xid = self.underlayer.XID
            undt = type(self.underlayer)
            if xid in states[undt]:
                # FIXME : two calls with same xid ?
                log_interactive.warning("redefining state for xid " + str(xid))
            states[undt][xid] = { "program" : self.program, "packets" : [ self ] }
        if type(self.payload) is not NoPayload:
            self.payload.update_states()
    
    def mysummary(self):
        return self.sprintf("Sun RPC Call program %program%, procedure %procedure%")
    


class SunRPCReply(Packet):
    name = "SunRPCReply"
    longname = "Sun RPC Reply"
    fields_desc = [ IntEnumField("state", 0, {0:"accepted"}),
                    IntEnumField("verifflavor", 0, {0:"null"}),
                    FieldLenField("veriflen", None, "verifier", fmt="I"),
                    StrLenField("verifier", "", "veriflen"),
                    IntEnumField("acceptstate", 0, {0:"success"}) ]

    # todo : function find_request(self)
    def guess_payload_class(self, payload):
        if type(self.underlayer) is not SunRPC:
            return Raw
        undt = type(self.underlayer)
        xid = self.underlayer.XID
        if xid in states[undt] and 'program' in states[undt][xid]:
            prog = states[undt][xid]['program']
            if prog == RPC_PROGRAMS['portmapper']:
                for p in states[undt][xid]['packets']:
                    if SunRPCCall in p and p[SunRPCCall].procedure == 3:
                        return PortmapGetPortReply
                # default to this. - Why ? - Why not ?
                return PortmapEntry
            #elif prog == RPC_PROGRAMS['nfs']:
            #    return NFS
        transport = self.underlayer.underlayer
        if type(transport) in [ TCP, UDP ]:
            if type(transport) == TPC:
                services = TCP_SERVICES
            else:
                services = UDP_SERVICES
            if transport.sport == services['sunrpc']:
                return PortmapEntry
            #elif transport.sport == services['nfs']:
            #    return NFS
            else:
                return Raw
        else:
            return Raw
    
    def update_states(self):
        if type(self.underlayer) is SunRPC:
            xid = self.underlayer.XID
            undt = type(self.underlayer)
            if xid in states[undt]:
                if 'packets' in states[undt][xid]:
                    if self not in states[undt][xid]['packets']:
                        states[undt][xid]['packets'].append(self)
                else:
                    states[undt][xid]['packets'] = [self]
            else:
                states[undt][xid] = { 'packets' : [self] }
        if type(self.payload) is not NoPayload:
            self.payload.update_states()
    
    def mysummary(self):
        undt = type(self.underlayer)
        if type(undt) is SunRPC:
            xid = self.underlayer.XID
            if xid in states[undt] and 'program' in states[undt][xid]:
                for p in states[undt][xid]['packets']:
                    if SunRPCCall in p:
                        return p.sprintf("Sun RPC Reply program %program%, procedure %procedure%")
        return self.sprintf("Sun RPC Reply XID %XID%")


class PortmapEntry(Packet):
    name = "PortmapEntry"
    longname = "Portmap Entry"
    show_indent = 0
    fields_desc = [ IntEnumField("valuefollows", 1, {1:"Yes", 0:"No"}),
                    ConditionalField(IntEnumField("program", 0, RPC_PROGRAMS), "valuefollows", lambda x:x==1),
                    ConditionalField(IntField("version", 0), "valuefollows", lambda x:x==1),
                    ConditionalField(IntEnumField("protocol", 0, IP_PROTOS), "valuefollows", lambda x:x==1),
                    ConditionalField(IntField("port", 0), "valuefollows", lambda x:x==1)
                    ]

class PortmapGetPort(Packet):
    name = "PortmapGetPort"
    longname = "Portmap Get Port"
    show_indent = 0
    fields_desc = [ IntEnumField("program", 0, RPC_PROGRAMS),
                    IntField("version", 0),
                    IntEnumField("protocol", 0, IP_PROTOS),
                    IntField("port", 0), ## ignored
                    ]

    def mysummary(self):
        return self.sprintf("Portmap GetPort for program %program% version %version%")

class PortmapGetPortReply(Packet):
    name = "PortmapGetPortReply"
    longname = "Portmap Get Port Reply"
    show_indent = 0
    fields_desc = [ IntField("port", 0),
                    ]
    
    def mysummary(self):
        if type(self.underlayer) is SunRPCReply:
            undt = type(self.underlayer.underlayer)
            if undt is SunRPC:
                xid = self.underlayer.underlayer.XID
                if xid in states[undt] and 'program' in states[undt][xid]:
                    for p in states[undt][xid]['packets']:
                        if PortmapGetPort in p:
                            if self[PortmapGetPortReply].port == 0:
                                resp = p[PortmapGetPort].sprintf("Portmap GetPort Reply program %program% not registered")
                            else:
                                resp = p[PortmapGetPort].sprintf("Portmap GetPort Reply program %program%")
                                resp += self.sprintf(" at port %port%")
                            return resp
        return self.sprintf("Portmap GetPort Reply port %port%")



# pseudo states engine. Hehe...

states={}

def clean_states():
    states.clear()
    for proto in [ SunRPC ]:
        states[proto]={}

clean_states()


# the functions that "create" Packet objects (by reading pcap files or by
# sniffing the network) need to be updated


## rdpcap()
def rdpcap(filename, count=-1, update=True):
    """Read a pcap file and return a packet list
count: read only <count> packets
update: run update_states() method for each packet"""
    return PcapReader(filename).read_all(count=count, update=update)


## PcapReader.read_all()
def PcapReader_read_all(self, count=-1, update=True):
    """return a list of all packets in the pcap file
    """
    res=[]
    while count != 0:
        count -= 1
        p = self.read_packet()
        if p is None:
            break
        if update:
            p.update_states()
        res.append(p)
    return PacketList(res,name = os.path.basename(self.filename))

PcapReader.read_all = PcapReader_read_all
del(PcapReader_read_all)


## sniff()
def sniff(count=0, store=1, offline=None, prn = None, lfilter=None, update=True, L2socket=None, timeout=None, *arg, **karg):
    """Sniff packets
sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] [update=False,] + L2ListenSocket args) -> list of packets

  count: number of packets to capture. 0 means infinity
  store: wether to store sniffed packets or discard them
    prn: function to apply to each packet. If something is returned,
         it is displayed. Ex:
         ex: prn = lambda x: x.summary()
lfilter: python function applied to each packet to determine
         if further action may be done
         ex: lfilter = lambda x: x.haslayer(Padding)
offline: pcap file to read packets from, instead of sniffing them
update:  wether to run update_states() method when a packet is sniffed or not
timeout: stop sniffing after a given time (default: None)
L2socket: use the provided L2socket
    """
    c = 0

    if offline is None:
        if L2socket is None:
            L2socket = conf.L2listen
        s = L2socket(type=ETH_P_ALL, *arg, **karg)
    else:
        s = PcapReader(offline)

    lst = []
    if timeout is not None:
        stoptime = time.time()+timeout
    remain = None
    while 1:
        try:
            if timeout is not None:
                remain = stoptime-time.time()
                if remain <= 0:
                    break
            sel = select([s],[],[],remain)
            if s in sel[0]:
                p = s.recv(MTU)
                if p is None:
                    break
                if lfilter and not lfilter(p):
                    continue
                if store:
                    lst.append(p)
                c += 1
                if prn:
                    r = prn(p)
                    if r is not None:
                        print r
                if update:
                    p.update_states()
                if count > 0 and c >= count:
                    break
        except KeyboardInterrupt:
            break
    return PacketList(lst,"Sniffed")


#### PFLog support

class PFLog(Packet):
    name = "PFLog"
    # from OpenBSD src/sys/net/pfvar.h and src/sys/net/if_pflog.h
    fields_desc = [ ByteField("hdrlen", 0),
                    ByteEnumField("addrfamily", 2, {socket.AF_INET: "IPv4",
                                                    socket.AF_INET6: "IPv6"}),
                    ByteEnumField("action", 1, {0: "pass", 1: "drop",
                                                2: "scrub", 3: "no-scrub",
                                                4: "nat", 5: "no-nat",
                                                6: "binat", 7: "no-binat",
                                                8: "rdr", 9: "no-rdr",
                                                10: "syn-proxy-drop" }),
                    ByteEnumField("reason", 0, {0: "match", 1: "bad-offset",
                                                2: "fragment", 3: "short",
                                                4: "normalize", 5: "memory",
                                                6: "bad-timestamp",
                                                7: "congestion",
                                                8: "ip-options",
                                                9: "proto-cksum",
                                                10: "state-mismatch",
                                                11: "state-insert",
                                                12: "state-limit",
                                                13: "src-limit",
                                                14: "syn-proxy" }),
                    StrFixedLenField("iface", "", 16),
                    StrFixedLenField("ruleset", "", 16),
                    SignedIntField("rulenumber", 0),
                    SignedIntField("subrulenumber", 0),
                    SignedIntField("uid", 0),
                    IntField("pid", 0),
                    SignedIntField("ruleuid", 0),
                    IntField("rulepid", 0),
                    ByteEnumField("direction", 255, {0: "inout", 1: "in",
                                                     2:"out", 255: "unknown"}),
                    StrFixedLenField("pad", "\x00\x00\x00", 3 ) ]
    def mysummary(self):
        return self.sprintf("%PFLog.addrfamily% %PFLog.action% on %PFLog.iface% by rule %PFLog.rulenumber%")


#### GRE support 

class GRErouting(Packet):
    name = "GRErouting"
    longname = "GRE routing informations"
    fields_desc = [ ShortField("address_family",0),
                    ByteField("SRE_offset", 0),
                    FieldLenField("SRE_len", None, "routing_info", "B"),
                    StrLenField("routing_info", "", "SRE_len"),
                    ]

del(GRE)
class GRE(Packet):
    name = "GRE"
    fields_desc = [ BitField("chksum_present",0,1),
                    BitField("routing_present",0,1),
                    BitField("key_present",0,1),
                    BitField("seqnum_present",0,1),
                    BitField("strict_route_source",0,1),
                    BitField("recursion control",0,3),
                    BitField("flags",0,5),
                    BitField("version",0,3),
                    XShortEnumField("proto", 0x0000, ETHER_TYPES),
                    ConditionalField(XShortField("chksum",None),["chksum_present","routing_present"],lambda x:x!=[0,0]),
                    ConditionalField(XShortField("offset",None),["chksum_present","routing_present"],lambda x:x!=[0,0]),
                    ConditionalField(XIntField("key",None),"key_present",lambda x:x==1),
                    ConditionalField(XIntField("seqence_number",None),"seqnum_present",lambda x:x==1),
                    ]
    def post_build(self, p, pay):
        p += pay
        if self.chksum_present and self.chksum is None:
            c = checksum(p)
            p = p[:4]+chr((c>>8)&0xff)+chr(c&0xff)+p[6:]
        return p


#### layer_bonds needed for protocols added

new_layer_bonds = [
    
    ## PFLog
    ( PFLog,        IP,             { "addrfamily" : socket.AF_INET } ),
    ( PFLog,        IPv6,           { "addrfamily" : socket.AF_INET6 } ),

    ## SunRPC
    ( UDP,          SunRPC,         { "dport":111 } ),
    ( UDP,          SunRPC,         { "sport":111 } ),
    ( TCP,          SunRPC,         { "dport":111 } ),
    ( TCP,          SunRPC,         { "sport":111 } ),
    ( SunRPC,       SunRPCCall,     { "msgtype":0 } ),
    ( SunRPC,       SunRPCReply,    { "msgtype":1 } ),
    ( SunRPC,       SunRPCCall,     { "msgtype":0 } ),
    ( SunRPC,       SunRPCReply,    { "msgtype":1 } ),
    ( SunRPCCall,   PortmapGetPort, { "program" : RPC_PROGRAMS['portmapper'],
                                      "procedure" : 3 } ),
    ( PortmapEntry, PortmapEntry,   { } ),

    ## GRE
    ( GRE,          GRErouting,      { "routing_present" : 1 } ),
    ( GRErouting,   Raw,             { "address_family" : 0,
                                       "SRE_len" : 0 } ),
    ( GRErouting,   GRErouting,      { } ),
    ## Those are already present in scapy
    ( GRE,          LLC,             { "proto" : 0x007a } ),
    ( GRE,          Dot1Q,           { "proto" : 0x8100 } ),
    ( GRE,          Ether,           { "proto" : 0x0001 } ),
    ( GRE,          ARP,             { "proto" : 0x0806 } ),
    ( GRE,          IP,              { "proto" : 0x0800 } ),
    ( GRE,          EAPOL,           { "proto" : 0x888e } ),
    ( IP,           GRE,             { "frag" : 0, "proto" : socket.IPPROTO_GRE  } ),
    
    ]

for l in new_layer_bonds:
    bind_layers(*l)
del(l)
del(new_layer_bonds)


#### LL stuff

LLTypes[117] = PFLog
LLNumTypes[PFLog] = 117


#### main

if __name__ == "__main__":
    interact(mydict=globals(), mybanner="Scapy Extended " + EXTVERSION)
