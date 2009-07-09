# from scapy.all is imported in the trace_route_combine module
from trace_route_combine import *
t = TracerouteCollection()
x = traceroute("172.16.28.140", maxttl=18, dport=80)
t.add_route(x[0])
x = traceroute("172.16.28.141", maxttl=18, dport=80)
t.add_route(x[0])
x = traceroute("172.16.28.142", maxttl=18, dport=80)
t.add_route(x[0])
x = traceroute("172.16.27.140", maxttl=18, dport=80)
t.add_route(x[0])
x = traceroute("172.16.26.140", maxttl=18, dport=80)
t.add_route(x[0])
x = traceroute("172.16.24.140", maxttl=18, dport=80)
t.add_route(x[0])
# now to create the graph
t.do_graph()
# or get the graph string
gs = t.build_graph()
# get paths to all the trace routed hosts
# x> is a down host and => is an up host
paths = t.get_paths_to_hosts()
