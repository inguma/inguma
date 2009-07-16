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

def generate_dot(localip, gateway, targets=[], steps=[], locals=[], ASNs={}, ASDs={}, direction='TD'):

    dotcode = "digraph G {\n\n\t"

#    # To be used with twopi layout
#    dotcode += 'overlap = "scale"\n'
#    dotcode += 'sep = 0.5\n'
#    dotcode += 'ranksep = "0.25 equally"\n'

    dotcode += 'rankdir="' + direction + '"\n'
    dotcode += "bgcolor=gray0\n\n"
    dotcode += 'root="' + localip + '";\n\n'
    #dotcode += "\nnode [shape=record,color=blue,style=filled fillcolor=skyblue];\n"
    dotcode += "\nnode [shape=record,color=blue, fontcolor=blue];\n"

    #######################################
    #
    # Create ASN clusters
    #
    #######################################
    dotcode += "\n#ASN clustering\n"
    for asn in ASNs:
        dotcode += '\tsubgraph cluster_%s {\n' % asn
        if asn == 'local':
            dotcode += '\t\tcolor="lawngreen";'
            dotcode += '\t\tfontcolor="lawngreen";'
        else:
            dotcode += '\t\tcolor="#608686";'
            dotcode += '\t\tfontcolor="#608686";'
        dotcode += '\t\tnode [fillcolor="#60baba"];'
        #dotcode += '\t\tnode [fillcolor="#60baba",style=filled];'
        dotcode += '\t\tfontsize = 10;'
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
            dotcode += '\t"' + target +  '"' + ' [shape=record,color=red3,fontcolor=red1,label="' + target + '"];' + "\n"
            #dotcode += '\t"' + target +  '"' + ' [shape=record,color=red3,fillcolor=red1,style=filled,label="' + target + '"];' + "\n"
        dotcode += "\n"
    
        i = 0
        for target in targets:
            for step in steps[i][0:-1]:
                dotcode += '\t"' + step + '"->' + "\n"
            dotcode += '\t"' + target + '" [color="blue"];' + "\n\n"
            i = i + 1
    
        for local in locals:
            dotcode += '\t"' + localip + '"->' + "\n"
            dotcode += '\t"' + local + '" [color="blue"];' + "\n\n"


#    #######################################
#    #
#    # Initial Local cluster
#    #
#    #######################################
#    else:
#        dotcode += "\n#ASN clustering\n"
#        dotcode += '\tsubgraph cluster_local {\n'
#        dotcode += '\t\tcolor="lawngreen";'
#        dotcode += '\t\tfontcolor="lawngreen";'
#        dotcode += '\t\tnode [fillcolor="#60baba",style=filled];'
#        dotcode += '\t\tfontsize = 10;'
#        dotcode += '\t\tlabel = "Local Network"\n'
#    
#        dotcode += '\t\t"' + localip + '";\n'
#        dotcode += '\t\t"' + gateway + '";\n'
#        dotcode += "\t}\n"
#
#        dotcode += '\t"' + localip +  '"' + ' [shape=record,color=blue,fillcolor=skyblue,style=filled,label="' + localip + '"];' + "\n"
#        dotcode += '\t"' + localip + '"->' + "\n"
#        dotcode += '\t"' + gateway + '" [color="blue"];' + "\n\n"

    dotcode += "}"

    return dotcode
