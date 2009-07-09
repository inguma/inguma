'''
(c) 2008 Adam Pridgen adam@thecoverofnight.com,
The Cover of Night, LLC
trace_route_combine.py
Scapy traceroute collector and aggregator class.  its been through some testing, not much,

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''


from scapy import *


class TracerouteCollection:
    def __init__(self):
        self.traceroute_paths = []
        self.traceroute_paths_hosts = {}
        self.traceroute_dsts = {}
        self.traceroute_srcs = {}
        self.graph = None
        self.traceroutes = {}
        self.traceroute_nodes = set()
        self.traceroute_incomplete = {}
        self.traceroute_complete = {}
    def uniquify_nodes(self, traceroute):
    	tr = TracerouteResult()
    	uniquify = set()
    	for i in traceroute.res:
    		if not i[1].src in uniquify:
    			uniquify.add(i[1].src)
    			tr.res.append(i)
    	return tr
 
    def add_dst(self, path, traceroute):
        if not path in self.traceroute_dsts:
            self.traceroute_dsts[path] = set()       
        self.traceroute_dsts[path].add(traceroute[0][0].dst)

    def add_src(self, path, traceroute):
        if not path in self.traceroute_srcs:
            self.traceroute_srcs[path] = set()       
        self.traceroute_srcs[path].add(traceroute[0][0].src)        
    def add_path(self, path, host):
        if not path in self.traceroute_paths:
            self.traceroute_paths.append(path)
            self.traceroute_paths_hosts[path] = []
        self.traceroute_paths_hosts[path].append(host)

    def add_tr(self, path, traceroute):
        #print traceroute
        if not path in self.traceroutes:
            self.traceroutes[path] = traceroute
        else:
            n = traceroute.res
            tr = self.traceroutes[path]
            tr.res += n
    
    def add_complete_path(self, path, dst):    
        if not path in self.traceroute_complete:
            self.traceroute_complete[path] = set()       
        self.traceroute_complete[path].add(dst)
    
    def add_incomplete_path(self, path, dst):    
        if not path in self.traceroute_incomplete:
            self.traceroute_incomplete[path] = set()       
        self.traceroute_incomplete[path].add(dst)
    def add_nodes(self, graph):
        for i in graph:
            self.traceroute_nodes.add(i)
    
    def get_ordered_path(self, traceroute):
        path_ttl = {}
        max_ttl = 0
        order_traceroute = []
        for i in traceroute.res:
            path_ttl[i[0].ttl] = i[1]
            if i[0].ttl > max_ttl:
                max_ttl = i[0].ttl
        g = set()
        for i in xrange(1,max_ttl+1 ):
            if i in path_ttl and not path_ttl[i].src in g:
                order_traceroute.append(path_ttl[i])
                g.add(path_ttl[i].src)
        return order_traceroute
       
    def add_route(self, traceroute, min_path_len = 2):
    	#trace_route = self.uniquify_nodes(traceroute)
    	trace_route = traceroute
    	dst = trace_route.res[0][0].dst
        src = trace_route.res[0][0].src
        graph = []
        g = set()
        otr = self.get_ordered_path(trace_route)
        for i in otr:
            graph.append( i.src)

        if len(graph) < min_path_len:
    		return
    	elif len(graph) == min_path_len:
    		path = src+"=>" + "=>".join(graph)
    	else:
    		path = src+"=>" +"=>".join(graph[:-1])
    	for i in graph:
            print i
        traceroute.show()
        print path
        
        self.add_nodes(graph)
        self.add_nodes([src,dst])
        
        host = graph[-1]
        #print path
        if host == dst and len(graph) > min_path_len:
            self.add_complete_path(path, dst)
        else:
            self.add_incomplete_path(path+"=>"+host, dst)
        
        self.add_dst(path, traceroute)
        self.add_src(path, traceroute)
        self.add_path(path, host)
        self.add_tr(path, traceroute)
    	#print path
    	#print host
    
    def get_complete_paths(self):
        paths = []
        for path in self.traceroute_complete:
            for dst in self.traceroute_complete[path]:
                paths.append(path+"=>"+dst)
        return paths

    def get_incomplete_paths(self):
        paths = []
        for path in self.traceroute_incomplete:
            for dst in self.traceroute_incomplete[path]:
                paths.append(path+"x>"+dst)
        return paths
    
    def build_cpath_graph(self, forecolorlist):
        complete_paths = self.get_complete_paths()
        cp = ""
        path_to_ens = {}
        asn_lookup = set()
        for path in complete_paths:
            enode = path.split("=>")[-1]
            path = "=>".join(path.split("=>")[0:-1])
            if not path in path_to_ens:
                path_to_ens[path] = set()
            path_to_ens[path].add(enode)
        #print path_to_ens
        # build graph for nodes
        for path in path_to_ens:
            #bad_labels.append(path_to_bns[ipath])
            enode = [i for i in path_to_ens[path]][0]
            cp += "\n#-- ['%s', '%s']\n"%(path.split("=>")[0], enode)
            nodes = []
            for node in path.split("=>"):
                asn_lookup.add(node)
                nodes.append('"%s"'%node)
            nodes.append('"%s"'%enode)
            asn_lookup.add(enode)
            cp += '\n\tedge [color="#%s%s%s"];' % forecolorlist.next()
            cp += "\n\t"+"->\n\t".join(nodes) + ";\n"
        e = "\n#Reachable Hosts\n\t"
        for path in path_to_ens:
            n = [i for i in path_to_ens[path]]
            l = "\\n".join(n)
            e += '"%s" [shape=record,color=black,fillcolor=green,style=filled,label="%s"];\n\t'%(n[0],l)
        return e+"\n"+cp, asn_lookup
        
        
    def build_ipath_graph(self, forecolorlist):
        incomplete_paths = self.get_incomplete_paths()
        icp = ""
        path_to_bns = {}
        asn_lookup = set()
        # accumulate the nodes
        for path in incomplete_paths:
            bnode = path.split("x>")[-1]
            ipath = path.split("x>")[0]
            if not ipath in path_to_bns:
                path_to_bns[ipath] = []
            path_to_bns[ipath].append(bnode)
        print path_to_bns
        # build graph for nodes
        for ipath in path_to_bns:
            #bad_labels.append(path_to_bns[ipath])
            bnode = path_to_bns[ipath][0]
            icp += "\n#-- ['%s', '%s']\n"%(ipath.split("=>")[0], bnode)
            nodes = []
            for node in ipath.split("=>"):
                asn_lookup.add(node)
                nodes.append('"%s"'%node)
            icp += "\n\t"+'\n\tedge [color="#%s%s%s"];\n' % forecolorlist.next()
            asn_lookup.add(bnode)
            nodes.append('"%s"'%bnode)
            icp += "\n\t"+"->\n\t".join(nodes) + ";\n"
        # group the unreachable nodes
        b = "\n#Unreachable Hosts\n\t"
        for ipath in path_to_bns:
            n = [i for i in set(path_to_bns[ipath])]
            l = "\\n".join(n)
            b += '"%s" [shape=octagon,color=black,fillcolor=red,style=filled, label="%s"];\n\t'%(n[0],l)
        return b+"\n"+icp, asn_lookup
    
    def build_asn_graphs(self, ASNs, ASDs, backcolorlist):
        ''' Code modified from TracerouteResult by Philippe Biondi'''
        s = ""
        for asn in ASNs:
            s += '\tsubgraph cluster_%s {\n' % asn
            col = backcolorlist.next()
            s += '\t\tcolor="#%s%s%s";\n' % col
            s += '\t\tnode [fillcolor="#%s%s%s",style=filled];\n' % col
            s += '\t\tfontsize = 10;\n'
            s += '\t\tlabel = "%s\\n[%s]"\n' % (asn,ASDs[asn])
            for ip in ASNs[asn]:
                s += '\t\t"%s";\n'%ip
            s += "\t}\n"
        return s

    def process_asnlist(self, ASNlist):
        ''' Code modified from TracerouteResult by Philippe Biondi'''
        ASNs = {}
        ASDs = {}
        for ip,asn,desc, in ASNlist:
            if asn is None:
                continue
            iplist = ASNs.get(asn,[])
            iplist.append(ip)
            ASNs[asn] = iplist
            ASDs[asn] = desc
        return ASNs, ASDs
    
    def build_graph(self, ASres = None):
        s = "digraph trace {\n"
        s+= "\n\tnode [shape=ellipse,color=black,style=solid];\n"
        backcolorlist=colgen("60","86","ba","ff")
        forecolorlist=colgen("a0","70","40","20")
        #build the complete paths
        cp,asn_lookup = self.build_cpath_graph(forecolorlist)
        
        #build the incomplete path
        icp, asn_lookup2 = self.build_ipath_graph(forecolorlist)
        asn_lookup = asn_lookup.union(asn_lookup2)
        # perform asn clustering
        if ASres is None:
            ASres = conf.AS_resolver
        ASN_query_list = [i for i in asn_lookup] 
        #print ASN_query_list
        ASNlist = ASres.resolve(*ASN_query_list)            
        #print ASNlist
        ASNs, ASDs = self.process_asnlist(ASNlist)
        asng = "\n#ASN clustering\n"+self.build_asn_graphs(ASNs, ASDs, backcolorlist)
        s+= asng+cp+icp+ "\n}\n";
        return s
    
    def get_merged_traceroutes(self):
    	merged = TracerouteResult()
    	nodes = set()
    	for path in self.traceroutes:
    		merged.res += self.traceroutes[path].res
    	return merged
    
    def get_paths_to_hosts(self):
        paths = []
        paths += self.get_complete_paths()
        paths += self.get_incomplete_paths()
        return paths
    def get_paths(self):
    	return self.traceroute_paths
    def get_traceroutes(self):
    	return [self.traceroutes[path] for path in self.traceroute_paths]
    def do_graph(self):
        self.graph = self.build_graph()
        do_graph(self.graph)
    def write_graph(self, filename):
        p = self.build_graph()
        f = open(filename, 'w')
        f.write(p)
    
    def write_paths(self, filename):
        p = self.get_paths()
        f = open(filename, 'a')
        f.write("\n".join(p))
    def read_paths_from_file(self, filename):
        f = "".join(open(filename).readlines())
        for i in f.split("\n"):
            if i.find("x>") > -1:
                path = i.split("x>")[0]
                target = i.split("x>")[1]
                dst = path.split("=>")[-1]
                self.add_incomplete_path(path, host, dst)
                continue
            path = i.split("=>")
            dst = path[-1]
            host = path[-2]
            path = "=>".join(path[:-1])
            self.add_complete_path(path, host, dst)
