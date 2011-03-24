
import os
from xml import sax

class NmapHandler(sax.ContentHandler):

    def __init__(self):
        self.isOpen = 0
        self.outputs = []
        self.output = {}
        self.output['ports'] = {}
        self.output['hops'] = []

    def startElement(self, name, attrs):
        if name == 'address':
            if attrs.get('addrtype',"") == 'ipv4':
                self.address = attrs.get('addr',"")
        elif name == 'hostname':
            self.hostname = attrs.get('name',"")
        elif name == 'port':
            self.port = attrs.get('portid',"")
        elif name == 'state':
            self.state = attrs.get('state',"")
        elif name == 'service':
            self.serv = attrs.get('name',"")
            self.product = attrs.get('product',"")
            self.version = attrs.get('version',"")
        elif name == 'script':
            self.vuln = attrs.get('output',"")
        elif name == 'osmatch':
            self.os = attrs.get('name',"")
            self.acc = attrs.get('accuracy',"")
        elif name == 'trace':
            self.trace = attrs.get('port', "")
        elif name == 'hop':
            self.hopip = attrs.get('ipaddr', "")
            self.hopname = attrs.get('host', "")

    def endElement(self,name):
        if name == 'address' and self.address != "":
            self.output['hostip'] = str(self.address)
            self.address = ""
        elif name == 'hostname':
            self.output['hostname'] = str(self.hostname)
        elif name == 'state':
            if self.state == 'open' or self.state == 'filtered':
                self.isOpen += 1
                self.output['ports'][self.port] = []
                self.output['ports'][self.port].append( str(self.state) )
                self.state = ""
        elif name == 'service':
            try:
                self.output['ports'][self.port].append( str( self.serv + ' (' + self.product + ' ' + self.version + ')' ) )
            except:
                pass
            self.serv = ""
            self.product = ""
            self.version = ""
        elif name == 'script':
            self.output['ports'][self.port].append( str(self.vuln) )

        elif name == 'osmatch':
            self.output['os'] = str(self.os)
            self.os = ""
            self.acc = ""
        elif name == 'trace':
            pass
        elif name == 'hop':
            self.output['hops'].append( [str(self.hopip), self.hopname] )
        elif name == 'host':
            if self.isOpen > 0:
#                print self.output
                self.outputs.append(self.output)

                # Clean to add new host data
                self.output = {}
                self.isOpen = 0
                self.output['ports'] = {}
                self.output['hops'] = []

def parseNmap(file):

    parser = sax.make_parser()
    curHandler = NmapHandler()
    parser.setContentHandler(curHandler)
    parser.parse(open(file))
#    os.remove(file)

    return curHandler.outputs

def insertData(uicore, outputs):

    for output in outputs:
        
        # Add a new target, hostname and OS
        uicore.set_kbfield( 'targets', output['hostip'] )
        if 'hostname' in output.keys():
            uicore.set_kbfield( output['hostip'] + '_name', output['hostname'] )
        if 'os' in output.keys():
            uicore.set_kbfield( output['hostip'] + '_os', output['os'] )
    
        # Add Open ports and services
#        print output['ports']
        for port in output['ports'].keys():
            if output['ports'][port][0] == 'open':
                uicore.set_kbfield( output['hostip'] + '_tcp_ports', port )
                try:
                    uicore.set_kbfield( output['hostip'] + '_' + port + '-info', output['ports'][port][1] )
                    uicore.set_kbfield( output['hostip'] + '_' + port + '-info', output['ports'][port][2] )
                except:
                    pass
    
        # Add traceroute
        localip = uicore.getLocalIP()
        uicore.set_kbfield( output['hostip'] + '_trace', localip )
        for host in output['hops']:
            uicore.set_kbfield( 'hosts', host[0] )
            if host[1] != '':
                uicore.set_kbfield( host[0] + '_name', host[1] )
            uicore.set_kbfield( output['hostip'] + '_trace', host[0] )

#if __name__ == '__main__':
#   import sys
#   parseNmap(sys.argv[1])
