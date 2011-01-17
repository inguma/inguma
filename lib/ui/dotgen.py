##      dotgen.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
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

import sys

def generate_dot(localip, gateway, targets=[], steps=[], locals=[], ASNs={}, ASDs={}, direction='TD', user_data=None):

    dotcode = "digraph G {\n\n\t"

#    # To be used with twopi layout
#    dotcode += 'overlap = "scale"\n'
#    dotcode += 'sep = 0.5\n'
#    dotcode += 'ranksep = "0.25 equally"\n'

    dotcode += 'rankdir="' + direction + '"\n'
    dotcode += "bgcolor=\"#475672\"\n\n"
    dotcode += 'root="' + localip + '";\n\n'
    dotcode += 'concentrate="true";\n\n'
    dotcode += '\nnode [shape=record, color=azure3, fontcolor=azure3, style="filled,rounded", fillcolor="#373D49"];\n'

    #######################################
    #
    # Create ASN clusters
    #
    #######################################
    dotcode += "\n#ASN clustering\n"
    for asn in ASNs:
        dotcode += '\tsubgraph cluster_%s {\n' % asn
        if asn == 'local':
            dotcode += '\t\tfillcolor="#373D49";'
            dotcode += '\t\tcolor="mediumseagreen";'
            dotcode += '\t\tfontcolor="mediumseagreen";'
        else:
            dotcode += '\t\tcolor="#373D49";'
            dotcode += '\t\tfontcolor="azure3";'
        dotcode += '\t\tfontsize = 10;'
        dotcode += '\t\tstyle=\"rounded,filled\";'
        dotcode += '\t\tlabel = "%s\\n[%s]"\n' % (asn,ASDs[asn])
        for ip in ASNs[asn]:

            dotcode += '\t\t"%s";\n'%ip
        dotcode += "\t}\n"

    #######################################
    #
    # Asign URLs
    #
    #######################################
    for target in targets:
        dotcode += '\t"' + target + '" [URL="' + target + '"]\n'
    for local in locals:
        dotcode += '\t"' + local + '" [URL="' + local + '"]\n'
    for step in steps:
        for node in step:
            dotcode += '\t"' + node + '" [URL="' + node + '"]\n'


    #######################################
    #
    # Targets with diferent color
    #
    #######################################
    if len(targets) != 0 or len(locals) != 0:
        for target in targets:

            # I don't like this code...
            try:
                # Get OS String
                target_os = target + '_os'
                target_os = user_data[target_os][0]
                target_os = target_os.split(' ')
                # Get just two words if OS name is too large
                if len(target_os) > 1:
                    target_os = ' '.join([target_os[0], target_os[1], '...'])
                else:
                    target_os = target_os[0]
                dotcode += '\t"' + target +  '"' + ' [shape=record,color=indianred3,fontcolor=indianred1,label="' + target + '\\n' + target_os + '"];' + "\n"
            except:
                dotcode += '\t"' + target +  '"' + ' [shape=record,color=indianred3,fontcolor=indianred1,label="' + target + '"];' + "\n"

        dotcode += "\n"
    
        i = 0
        for target in targets:
            # If there are steps for that target
            try:
                for step in steps[i][0:-1]:
                    dotcode += '\t"' + step + '"->' + "\n"
            except:
                pass
            dotcode += '\t"' + target + '" [color="azure3"];' + "\n\n"
            i = i + 1
    
        for local in locals:
            dotcode += '\t"' + localip + '"->' + "\n"
            dotcode += '\t"' + local + '" [color="azure3"];' + "\n\n"

    dotcode += "}"

    return dotcode

def generate_folded(kb):

    dotcode = '''
    graph G {
        graph [ overlap="scale", bgcolor="#475672", concentrate="true", root="Internet"]
            node [color=azure3, fontcolor=white, fillcolor="#373D49", shape=circle, style=filled, fixedsize=true, height=0.9,width=0.9];

            "Internet" [style=filled, fillcolor="#5E82C6", fixedsize=true, height=1.0,width=1.0, shape=doublecircle]
    '''

    for target in kb['targets']:
        dotcode += '"' + target + '" [style=filled, fillcolor="#373D49", fixedsize=true, height=0.9,width=0.9, URL="' + target + '"]\n'
        dotcode += '"Internet" -- "' + target + '" [len=1.50, color=azure3];\n'

    dotcode += '\n}'

    return dotcode

def graph_weighted(kb, type):

    dotcode = '''
    graph G {
    graph [ overlap="scale", bgcolor="#475672", rankdir="LR"]
        node [color=azure3, fontcolor=white, fillcolor="#373D49", shape=circle, style=filled];
    '''

    if type == 'ip':
        # Calculate IP weight
        weights = {}
        for target in kb['targets']:
            weights[target] = 0.5
            try:
                for port in kb[target + '_tcp_ports']:
                    weights[target] += 0.3
            except:
                pass
    elif type == 'port':
        # Calculate Port weight
        weights = {}
        for target in kb['targets']:
            if target + '_tcp_ports' in kb:
                for port in kb[target + '_tcp_ports']:
                    if not port in weights.keys():
                        weights[port] = 0.5
                    else:
                        weights[port] += 0.3
#    print weights

    # Add weight ordered nodes
    for weight in weights:
        dotcode += '"' + weight + '" [style=filled, fillcolor="#5E82C6", fixedsize=1, height=' + str(weights[weight]) + ', width=' + str(weights[weight]) + ', shape=circle]\n'

    # Add edges
    target_pairs = pairs( weights.keys() )
    for pair in target_pairs[0:-1]:
        dotcode += '"' + pair[0] + '" -- "' + pair[1] + '" [style="invis", minlen=2]\n'

    dotcode += '}'

    return dotcode

def pairs(dlist):
    return zip(dlist,dlist[1:]+[dlist[0]])

def graph_to_from(kb, type):

    dotcode = '''
    graph G {
        graph [ overlap="scale", bgcolor="#475672", concentrate="true", root="Invisnode"]
		    node [color=azure3, fontcolor=white, fillcolor="#373D49", shape=circle, style=filled, fixedsize=1, height=0.7,width=0.7];
    '''
    #bgcolor="#475672"
    dotcode += '"Invisnode" [style=invis, fixedsize=1, height=1, width=1, shape=circle]\n'
    if type == 'ports_ip':
        for target in kb['targets']:
            dotcode += '"' + target + '" [shape="doublecircle", style=filled, fillcolor="#5E82C6", fixedsize=1, height=0.9, width=0.9, URL="' + target + '"]\n'
            dotcode += '"Invisnode" -- "' + target + '" [style=invis]\n'
            try:
                for port in kb[target + '_tcp_ports']:
                    dotcode += '"' + target + '_'+ str(port) + '" [label="' + str(port) + '"]\n'
                    dotcode += '"' + target + '" -- "' + target + '_'+ str(port) + '" [len=1.25, color=azure3];\n'
            except:
                #print sys.exc_info()
                pass

        target_pairs = pairs(kb['targets'])
        print target_pairs
        for pair in target_pairs[0:-1]:
            dotcode += '"' + pair[0] + '" -- "' + pair[1] + '" [style="invis"]\n'

    elif type == 'ip_ports':
        for target in kb['targets']:
            try:
                for port in kb[target + '_tcp_ports']:
                    dotcode += '"' + str(port) + '" [shape="doublecircle", style=filled, fillcolor="#5E82C6", fixedsize=1, height=0.7,width=0.7]\n'
                    dotcode += '"' + str(port) + '_' + target + '" [label="' + target + '"]\n'
                    dotcode += '"' + str(port) + '" -- "' + str(port) + '_' + target + '" [len=1.25, color=azure3];\n'
            except:
                #print sys.exc_info()
                pass

    elif type == 'ports_vuln':
        for target in kb['targets']:
            dotcode += '"' + target + '" [shape="doublecircle", style=filled, fillcolor="#5E82C6", fixedsize=1, height=0.9, width=0.9, URL="' + target + '"]\n'
            dotcode += '"Invisnode" -- "' + target + '" [style=invis]\n'
            try:
                for port in kb[target + '_tcp_ports']:
                    vuln_id = 0
                    if target + "_" + str(port) + '-web-vulns' in kb:
                        dotcode += '"' + target + '_'+ str(port) + '" [label="' + str(port) + '", shape=doublecircle]\n'
                    else:
                        dotcode += '"' + target + '_'+ str(port) + '" [label="' + str(port) + '"]\n'
                    dotcode += '"' + target + '" -- "' + target + '_'+ str(port) + '" [len=1.25, color=azure3];\n'
                    for vuln in kb[target + "_" + str(port) + '-web-vulns']:
                        dotcode += '"' + vuln[0] + str(vuln_id) + '" [style=filled, fillcolor=indianred4, fixedsize=1, height=0.9, width=0.9, label=\"OSVDB:' + vuln[0] + '\"]\n'
                        dotcode += '"' + target + '_' + str(port) + '" -- "' + vuln[0] + str(vuln_id) + '" [len=1.25, color=azure3];\n'
                        vuln_id += 1
            except:
                #print sys.exc_info()
                pass

        target_pairs = pairs(kb['targets'])
        print target_pairs
        for pair in target_pairs[0:-1]:
            dotcode += '"' + pair[0] + '" -- "' + pair[1] + '" [style="invis"]\n'

    dotcode += '\n}'

    #print dotcode
    return dotcode
