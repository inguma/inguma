
from xml import sax

class NmapHandler(sax.ContentHandler):

    def __init__(self):
        self.isOpen = 0
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
                self.state = ""
        elif name == 'service':
#            self.output += "Service:\t" + self.serv + " " + self.product + " " + self.version + "\n\n"
            self.output['ports'][self.port].append( str(self.serv) )
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
            self.output['hops'].append( str(self.hopip) )
        elif name == 'host':
            if self.isOpen > 0:
#                print self.output
                self.isOpen = 0

def parseNmap(file):

    parser = sax.make_parser()
    curHandler = NmapHandler()
    parser.setContentHandler(curHandler)
    parser.parse(open(file))

    return curHandler.output

def insertData(uicore, output):

    # Add a new target, hostname and OS
    uicore.set_kbfield( 'targets', output['hostip'] )
    uicore.set_kbfield( output['hostip'] + '_name', output['hostname'] )
    uicore.set_kbfield( output['hostip'] + '_os', output['os'] )

    # Add Open ports and services
    print output['ports']
    for port in output['ports'].keys():
        uicore.set_kbfield( output['hostip'] + '_ports', port )
        try:
            uicore.set_kbfield( output['hostip'] + '_' + port + '-vulns', output['ports'][port][1] )
        except:
            pass

    # Add traceroute
    for host in output['hops']:
        uicore.set_kbfield( 'hosts', host )
        uicore.set_kbfield( output['hostip'] + '_trace', host )
