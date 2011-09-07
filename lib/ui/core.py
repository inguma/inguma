##      core.py
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
sys.path.append('../..')
import gobject

import pickle, os, platform
import inguma

import threading
import scapy.all as scapy
scapy.conf.verb = 0
import dotgen

import lib.IPy as IPy

#inguma.debug = True
inguma.isGui = True
inguma.user_data["isGui"] = True
inguma.user_data["interactive"] = False

# Fix for bug 1807529 (andresriancho)
inguma.user_data["base_path"] = '.'

inguma.readCommands()
inguma.interactive = False

class UIcore():

    def __init__(self):
        self.user_data = inguma.user_data

    def add_local_asn(self):
        inguma.user_data['graph'] = { 'ASNs':{}, 'ASDs':{} }

        ip = self.getLocalIP()
        gw = self.getLocalGW()

        if (gw is None):
            # We don't have a gateway at the moment.
            print "\nERROR: Houston, we have a problem.  It's been impossible to determine your current gateway.  I cannot continue."
            sys.exit(1)

        #Get localhost information
        local_info = platform.uname()
        local_os, local_name = local_info[0], local_info[1]
        inguma.user_data[ip + '_os'] = [local_os]
        inguma.user_data[ip + '_name'] = [local_name]

        inguma.user_data['graph']['ASNs']['local'] = [ip, gw]
        inguma.user_data['graph']['ASDs']['local'] = 'Local Network'
        inguma.user_data[ip + '_trace'] = [ip, gw]
        inguma.user_data['hosts'].append(ip)
        inguma.user_data['hosts'].append(gw)
        inguma.user_data['targets'].append(ip)

        inguma.user_data[ip + 'asn'] = True
        inguma.user_data[gw + 'asn'] = True

    def loadUserPasswords(self):
        users = file(inguma.user_data["base_path"] + "/data/users", "r").readlines()
        passwds = file(inguma.user_data["base_path"] + "/data/dict", "r").readlines()

    def loadKB(self, res):

        input = open(res, 'r')
        inguma.user_data = pickle.load(input)
        self.user_data = inguma.user_data

        if inguma.target == "":
            if inguma.user_data.has_key("target"):
                #print "Setting target (%s)" % inguma.user_data["target"]
                inguma.target = inguma.user_data["target"]

        input.close()

    def saveKB(self, res):

        output = open(res, 'wb')
        pickle.dump(inguma.user_data, output)
        output.close()

    def get_modules(self, category):
        ''' Returns an aray with the modules for one category'''

        modules = eval('inguma.' + category)
        return modules

    def get_categories(self):
        ''' returns an array with the categories of modules'''

        categories = ['discovers', 'gathers', 'brutes','exploits'] 
        return categories

    def get_kbcontent(self):

        buf = ""
        for x in inguma.user_data:
            if x != "ports":
                buf += x + "=" + str(inguma.user_data[x]) + os.linesep

        return buf

    def get_kbList(self):

        return inguma.user_data

    def get_var(self, field):
        return getattr(inguma, field)

    def get_kbfield(self, field):
        '''Returns the content of the field on the KB'''

        return inguma.user_data[field]

    def get_vulns(self):
        vulns = 0
        for element in inguma.user_data:
            if '-vulns' in element:
                vulns += len(element)
        return vulns

    def set_kbfield(self, field, new_content):
        '''Updates KB field contents'''

        if inguma.user_data.has_key(field):
            #print "Existing field", field, "content", new_content
            if type(inguma.user_data[field]) is list:
                #print "\tField is list"
                # Check if value exists
                for x in inguma.user_data[field]:
                    if x == new_content:
                        #print "\tSkip existing content"
                        return
                # If not, add it
                #print "\tAppending non existing content"
                inguma.user_data[field] += [new_content]
            else:
                inguma.user_data[field] = new_content
        else:
            #print "Adding non-existing field", field, "content", new_content
            inguma.user_data[field] = [new_content]

        setattr(inguma, field, new_content)

    def set_om(self, om):
        self.gom = om
        setattr(self.gom, 'SHOW_MODULE_WIN', self.SHOW_MODULE_WIN)
        setattr(self.gom, 'isGui', inguma.isGui)
        self.gom.set_new_nodes(False)

    def get_interfaces(self):
        return scapy.get_if_list()

    def set_interface(self, iface):
        scapy.conf.iface = iface

    def getLocalIP(self):
        return scapy.get_if_addr(scapy.conf.iface)

    def getLocalGW(self):
        for net,msk,gw,iface,addr in scapy.read_routes():
            if iface == scapy.conf.iface and gw != '0.0.0.0':
                return gw

    def getLocalNetwork(self):
        for net,msk,gw,iface,addr in scapy.read_routes():
            if iface == scapy.conf.iface and scapy.ltoa(msk) != '0.0.0.0':
                net = IPy.IP( str(net) + "/" + scapy.ltoa(msk) )
                return net

    def getIfaceList(self):
        return scapy.get_if_list()

    def getTargetPath(self):
        steps = []
        for target in inguma.user_data['targets']:
            try:
                steps.append(inguma.user_data[target + '_trace'])
            except:
                pass
#        print "Steps", steps, "\n"

        return steps

    def get_asn(self, ip):
        if IPy.IP(ip).iptype() != 'PRIVATE':
            self.gom.echo( "Getting ASN for: " + ip , False)
            #scapy.conf.AS_resolver = scapy.AS_resolver_radb()
            ASres = scapy.conf.AS_resolver
            asn = ASres.resolve(ip)

            return asn

    def getWeighted(self, type):
        self.xdot.set_filter('dot')
        dotcode = dotgen.graph_weighted(inguma.user_data, type)
        inguma.user_data['dotcode'] = dotcode

    def getToFromDot(self, type):
        self.xdot.set_filter('neato')
        dotcode = dotgen.graph_to_from(inguma.user_data, type)
        inguma.user_data['dotcode'] = dotcode

    def getFolded(self):
        self.xdot.set_filter('neato')
        dotcode = dotgen.generate_folded(inguma.user_data)
        inguma.user_data['dotcode'] = dotcode

    def getDot(self, doASN, direction='TD'):
        ''' Gets new dot code for graph '''

        self.xdot.set_filter('dot')
        self.getLocalNetwork()
        # Get local GW
        gw = self.getLocalGW()
        # Get local IP to be used always as first node
        local = self.getLocalIP()
        # Get targets (end points), paths (mid points) and locals (no mid points)
        paths = self.getTargetPath()

        if doASN:
            # Get host's ASN
            ASNlist = []
            for ip in inguma.user_data['targets']:
                if not inguma.user_data.has_key(ip + 'asn'):
                    asn = self.get_asn(ip)
                    if asn:
                        inguma.user_data[ip + 'asn'] = True
                        inguma.user_data[ip + '_asn'] = [str(asn[0][1]) + " " + asn[0][2]]
                        ASNlist.append(asn[0])
            for path in paths:
                for ip in path:
                    if not inguma.user_data.has_key(ip + 'asn'):
                        asn = self.get_asn(ip)
                        if asn:
                            inguma.user_data[ip + 'asn'] = True
                            inguma.user_data[ip + '_asn'] = [str(asn[0][1]) + " " + asn[0][2]]
                            ASNlist.append(asn[0])

            ASNs = {}
            ASDs = {}
            for ip,asn,desc, in ASNlist:
                if asn is None:
                    continue
                iplist = ASNs.get(asn,[])
                iplist.append(ip)
                ASNs[asn] = iplist
                ASDs[asn] = desc

            self.add_asns(ASNs)
            self.add_asds(ASDs)

        dotcode = dotgen.generate_dot(inguma.user_data, local, gw, direction)
        inguma.user_data['dotcode'] = dotcode

    def set_threadtv(self, threadtv):
        #print "Creating thread manager on core"
        self.threadtv = threadtv

    def uiRunModule(self, widget, callback_data, mod):
        '''Runs specified module and returns data'''

        vars = inguma.vars
        if self.SHOW_MODULE_WIN:
            self.gom.create_module_dialog()
        t = threading.Thread(target=inguma.runModule, args=(vars, inguma.commands[mod], inguma.user_data, self.gom))
        t.start()
        self.threadtv.add_action(mod, inguma.user_data['target'], t)

    def uiRunDiscover(self, mod, join=False):
        '''Runs specified module and returns data'''

        vars = inguma.vars
        if self.SHOW_MODULE_WIN:
            self.gom.create_module_dialog()
        t = threading.Thread(target=inguma.runModule, args=(vars, inguma.commands[mod], inguma.user_data, self.gom))
        t.start()
        self.threadtv.add_action(mod, inguma.user_data['target'], t)
        if join:
            t.join()

    def run_system_command(self, command):
        '''Manage the process of run a system command
           and get the output'''

        id = os.popen(command)
        output = id.read()
        print output
        if self.SHOW_MODULE_WIN:
            gobject.idle_add( self.gom.create_module_dialog )
        gobject.idle_add( self.gom.echo, output )

    #####################################
    #
    # Functions to manage graph structure
    #
    #####################################

    def add_asns(self, ASNs):

        for key in ASNs.keys():
            inguma.user_data['graph']['ASNs'][key] = ASNs[key]

        #print "user_data ASNs:\n", inguma.user_data['graph']['ASNs']

    def add_asds(self, ASDs):

        for key in ASDs.keys():
            inguma.user_data['graph']['ASDs'][key] = ASDs[key]
        #print "user_data ASDs:\n", inguma.user_data['graph']['ASDs']

    def has_asn(self, value):

        for x in inguma.user_data['graph']['ASNs'].values():
            try:
                x.index(value)
                #print str(x) + " == " + value
                return True
            except:
                #print str(x) + " != " + value
                return False

    def has_asd(self, value):
        pass

    def set_direction(self, direction):
        self.getDot(False, direction)
        return True

    def remove_node(self, node):

        #print "Removing node from kb..." + node
        # Get KB elements to remove for target
        steps = inguma.user_data[node + '_trace'][1:-1]
        toremove = []
        astoremove = []
        for element in inguma.user_data:
            if type(element) is dict or type(element) is list:
                pass
            elif node in element:
                #print "\tElement " + element + " would be removed"
                toremove.append(element)

        # Remove them
        for remove in toremove:
            del inguma.user_data[remove]
        inguma.user_data['targets'].remove(node)
        inguma.user_data['hosts'].remove(node)

        # Collect ASNs to remove
        for element in inguma.user_data['graph']['ASNs']:
            if node in inguma.user_data['graph']['ASNs'][element]:
                astoremove.append([element, node])
                #print inguma.user_data['graph']['ASNs'][element]
        # Remove collected ASNs
        for x in astoremove:
            inguma.user_data['graph']['ASNs'][x[0]].remove(x[1])
            # Remove empty ASNs
            if len( inguma.user_data['graph']['ASNs'][x[0]] ) == 0:
                del inguma.user_data['graph']['ASNs'][x[0]]

        #print "\n\nSteps!!"
        # Get KB elements to remove for steps
        for step in steps:
            toremove = []
            astoremove = []
            for element in inguma.user_data:
                if step in element:
                    #print "\tElement " + element + " would be removed"
                    toremove.append(element)

            # Remove them
            for remove in toremove:
                del inguma.user_data[remove]
            inguma.user_data['hosts'].remove(step)

            # Collect ASNs to remove
            for element in inguma.user_data['graph']['ASNs']:
                if step in inguma.user_data['graph']['ASNs'][element]:
                    astoremove.append([element, step])
                    #print inguma.user_data['graph']['ASNs'][element]

            # Remove collected ASNs
            for x in astoremove:
                inguma.user_data['graph']['ASNs'][x[0]].remove(x[1])
                # Remove empty ASNs
                if len( inguma.user_data['graph']['ASNs'][x[0]] ) == 0:
                    del inguma.user_data['graph']['ASNs'][x[0]]

        #print inguma.user_data['graph']
