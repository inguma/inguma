# Copyright (C) 2007 Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
"""
Core nmap xml output parser.
"""

from collections import defaultdict

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

FAILURE = "'%s' won't be parsed."

def _element_to_dict(content):
    """
    Receives an Element object thas has a format like this:
    [(a, b), (c, d) .. ] and return {a: b, c: d, ..}
    """
    return dict(content.items())

def _children_to_list(element):
    """
    Receives an Element object which possibly has several children
    and return their contents as dicts in a list.
    """
    return [_element_to_dict(child) for child in element.getchildren()]

def _parse_host_extraports(extraports):
    """
    Expects a extraports Element from port.

    This will return something in this format:

    {'extraports': [{count0: value, state0: value,
                     reasons0: [{reason0}, .., {reasonN}]},
                    {count1: value, state1: value,
                     reasons1: [{reason0}, .., {reasonN}]},
                    .
                    .,
                    {countN: value, stateN: value,
                     reasonsN: [{reason0}, .., {reasonN}]}
                   ]
    }

    Where:
        reason may have this format:
        {'count': count, 'reason': reason}
    """
    temp = _element_to_dict(extraports)
    temp['reasons'] = [_element_to_dict(reason)
                       for reason in extraports.getchildren()]

    return temp

def _parse_host_ports(ports):
    """
    Expects a port Element from host.

    This will return something in this format:

    {'ports': {'extraports': <return from parse_host_extraports>},
              {'ports': [{portdata0}, .., {portdataN}]}
    }

    Where:
        portdata may have this format (some keys may be missing depending
        the options used in scan):
        {'protocol': protocol, 'name': name, 'reason': reason,
         'reason_ttl': reason_ttl, 'state': state, 'conf': conf,
         'portid': portid, 'method': method, 'product': product,
         'hostname': hostname, 'extrainfo': extrainfo,
         'version': version, 'servicefp': service fingerprint}
    """
    temp = defaultdict(list)
    ports_tmp = []

    for port in ports.getchildren():
        if port.tag == 'extraports':
            temp[port.tag].append(_parse_host_extraports(port))
            continue

        curr_port = _element_to_dict(port)
        ports_tmp.append(curr_port)

        for items in port.getchildren():
            if items.tag == 'script':
                # one port may have several <script ... /> so it is needed
                # to keep them all in a list.
                curr_port.setdefault(items.tag, []).append(
                    _element_to_dict(items))
                continue

            curr_port.update(items.items())

    temp['ports'] = ports_tmp
    return temp

def _parse_host_trace(trace):
    """
    Expects a trace Element from host.

    This will return something in this format:

    {'trace': {'port': someport,
               'proto': protocol,
               'hop': [{hopdata0}, {hopdata1}, .., {hopdataN}]
              }
    }

    Where:
        hopdata may have this format (some keys may be missing if they
        weren't present in the xml):
        {'rtt': rtt, 'ipaddr': ip, 'ttl': ttl}
    """
    temp = _element_to_dict(trace)
    temp['hop'] = [_element_to_dict(hop) for hop in trace.getchildren()]

    return temp

def _parse_host_os(oshost):
    """
    Expects an os Element from host.

    This will return something in this format:

    {'osclass': [{osclassdata0}, .., {osclassdataN}],
     'osmatch': [{osmatchdata0}, .., {osmatchdataN}],
     'portused': [{portuseddata0}, , .., {portuseddataN}],
     'osfingerprint': [{osfingerprintdata0}, , .., {osfingerprintdataN}]
    }

    Where:
        osclassdata may have this format:
        {'type': type, 'osfamily': osfamily, 'vendor': vendor, 'osgen': osgen,
         'accuracy': accuracy}

        osmatchdata may have this format:
        {'name': name, 'accuracy': accuracy}

        portuseddata may have this format:
        {'state': state, 'portid': portid, 'proto': protocol}

        osfingerprintdata may have this format:
        {'fingerprint': fingerprint}
    """
    temp = defaultdict(list)

    for item in oshost.getchildren():
        temp[item.tag].append(_element_to_dict(item))

    return temp

def _parse_host(host):
    """
    Parses host Element from nmap xml.

    This will return something in this format:

    {'host': [{hostdata0}, {hostdata1}, .., {hostdataN}]}

    Where:
        hostdata may have this format (some keys may be missing if they
        weren't present in the xml):
        {'status': {'state': state, 'reason': reason},
         'smurf': {'responses': value},
         'times': {'to': value, 'srtt': value, 'rttvar': value},
         'hostscript': <return from _parse_host_hostscript>,
         'distance': {'value': value},
         'trace': <return from _parse_host_trace>,
         'address': [{addrdata0}, {addrdata1}, .., {addrdataN}],
         'hostnames': <return from _parse_host_hostnames,
         'ports': {<return from _parse_hort_ports>},
         'uptime': {'seconds': seconds, 'lastboot': date},
         'tcpsequence': {'index': index, 'values': values, 'class': class},
         'tcptssequence': {'values': values, 'class': class},
         'ipidsequence': {'values': values, 'class': class},
         'os': <return from _parse_host_os>
        }

        Where:
            addrdata may have this format:
            {'addrtype': addrtype, 'addr': address, 'vendor': vendor}
    """
    temp = {}

    # Elements in host that needs special handling.
    specials = {
        'hostnames': _children_to_list, #_parse_host_hostnames,
        'hostscript': _children_to_list, #_parse_host_hostscript,
        'ports': _parse_host_ports,
        'trace': _parse_host_trace,
        'os': _parse_host_os}

    # Elements in host that may contain multiple values. In the
    # returned dict these elements (keys) will have a list as value.
    multiple = {'address': _element_to_dict}

    for children in host.getchildren():
        if children.tag in specials:
            temp[children.tag] = specials[children.tag](children)
            continue

        elif children.tag in multiple:
            temp.setdefault(children.tag, []).append(
                multiple[children.tag](children))
            continue

        temp.setdefault(children.tag, {}).update(_element_to_dict(children))

        for child in children.getchildren():
            temp[children.tag].setdefault(child.tag, {}).update(
                _element_to_dict(child))

    return temp

def parse_nmap_xml(xmlfile, *todiscard):
    """
    Expects a valid nmap xml file and return it parsed.

    This will return something in this format:

    {'nmaprun': {'scanner': scanner, 'version': version,
                 'start': timestamp, 'startstr': timestr,
                 'args': args, 'xmloutputversion': version },
     'runstats': {'finished': {'timestr': timestr, 'time': time},
                  'hosts': {'up': num_hostsup,
                  'down': num_hostsdown,
                  'total': num_hosts}},
     'verbose': {'level': level},
     'debugging': {'level': level},
     'scaninfo': [{scaninfodata0}, .., {scaninfodataN}],
     'taskbegin': [{taskdata0}, {taskdata1}, .., {taskdataN}],
     'taskprogress': [{taskdata0}, {taskdata1}, .., {taskdataN}],
     'taskend': [{taskdata0}, {taskdata1}, .., {taskdataN}],
     'host': [<return from parse_host>]
    }

    Where:
        taskdata may have this format:
        {'task': task, 'time': time}

        scaninfodata may have this format:
        {'services': services, 'type': type,
         'numservices': numservices, 'protocol': protocol}
    """
    try:
        parsed = ET.parse(xmlfile)
    except IOError, err:
        print "IOError: %s. %s" % (err, FAILURE % xmlfile)
        return
    except SyntaxError, err:
        print "SyntaxError: %s. %s" % (err, FAILURE % xmlfile)
        return

    root = parsed.getroot()

    root_d = {root.tag: _element_to_dict(root)}

    # Elements that may contain muliple entries in xml file. In the
    # returned dict these elements (keys) will have a list as value.
    multiple = {
        'host': _parse_host,
        'scaninfo': _element_to_dict,
        'taskbegin': _element_to_dict,
        'taskprogress': _element_to_dict,
        'taskend': _element_to_dict }

    for children in root:
        if children.tag in todiscard:
            # totally discard this element
            continue

        if children.tag in multiple:
            root_d.setdefault(children.tag, []).append(
                multiple[children.tag](children))
            continue

        root_d.setdefault(children.tag, {}).update(_element_to_dict(children))

        for child in children.getchildren():
            root_d[children.tag].setdefault(child.tag, {}).update(
                _element_to_dict(child))

    return root_d
