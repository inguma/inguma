#!/usr/bin/python

# Startup preferences
SHOW_LOG=True
SHOW_KBTREE=True

# Paths to externmal tools
NMAP_PATH = '/usr/bin/nmap'
W3AF_PATH = '/pentest/web/w3af/w3af_console'

# Tools Availability
HAS_NMAP = True
HAS_W3AF = True
HAS_SOURCEVIEW = True
HAS_VTE = True

NMAP_PROFILES = {
'Intense Scan' : 'nmap -T Aggressive -A -v ',
'Operating System Detection' : 'nmap -O -v ',
'Quick Full version Detection Scan' : 'nmap -T Aggressive -sV -n -O -v ',
'Quick Operating System detection' : 'nmap -T Aggressive -O -v ',
'Quick Scan' : 'nmap -T Aggressive -v -n ',
'Quick Services version detection' : 'nmap -T Aggressive -sV -v ',
'Quick and verbose scan' : 'nmap -d -T Aggressive --packet_trace -v -n ',
'Regular Scan' : 'nmap -v ',
'Sneaky Scan' : 'nmap --min_hostgroup 1 -sV -v -v  -T Sneaky --min_parallelism 1 -p21,80,110,139,161,256,389,443,445,500,1080,1433,1723,2001,3389,4001,5631 -n -O -sS --max_parallelism 1 --max_hostgroup 1 -iL "/home/hteso/Proyectos/Hispasec/primera/scans/hosts" -PN --max_retries 2 ',
'UDP Polite Scan' : 'nmap -v -v  -T Polite -n -sU -PN --max_retries 3 '
}

# Editor color themes
# classic.xml  cobalt.xml  kate.xml  oblivion.xml  styles.rng  tango.xml
theme = "oblivion"

# Categories
categories = ["discovers", "gathers"]

# Clases
discovers = [ "arping", "tcping", "udping", "asn", "bluetooth", "db2discover", "externip", "hostname", "ipaddr", "getmac", "icmping", "isnated", "netcraft", "ispromisc", "tcptrace", "whois", "wifi" ]
gathers = [ "apps11i", "archanix", "arppoison", "anticrypt", "dnsspoof", "dtspc", "fakearp", "firetest", "nids", "ikescan", "ifxinfo", "rainbowmd5", "nikto", "nmapfp", "nmapscan", "nmbstat", "oascheck", "oratool", "oracrack11g", "oratt70info", "osifuzz", "p0f", "portscan", "protoscan", "rainbow", "rpcdump", "samrdump", "identify", "smbclient", "smbgold", "sniffer", "snmpwalk", "mssqlcrack", "tcpproxy", "tcpscan", "tnscmd", "unicornscan", "webserver", "winspdetect", "xmlrpc" ]
brutes = ["bruteftp", "brutehttp", "bruteimap", "bruteifx", "bruteora", "brutepop", "brutesmb", "brutesmtp", "brutessh", "brutesyb"]

# Subclases Gather
subgathers = {
'arp' : ["arppoison", "fakearp"],
'databases' : [ "apps11i", "dtspc", "ifxinfo", "oascheck", "oratool", "oracrack11g", "oratt70info", "mssqlcrack", "tnscmd" ],
'other' : [ "dnsspoof", "nids", "osifuzz", "winspdetect"],
'netbios' : ["nmbstat", "smbclient", "smbgold"],
'os detection' : ["nmapfp", "p0f"],
'passwords' : ["anticrypt", "rainbow", "rainbowmd5"],
'rpc' : ["rpcdump", "samrdump", "xmlrpc"],
'scanners' : [ "archanix", "firetest", "identify", "nmapscan", "portscan", "protoscan", "tcpscan", "unicornscan" ],
'vpn' : ["ikescan"],
'web' : ["nikto"]
}

# Subclases Discover
subdiscovers = {
'dns' : ["hostname", "ipaddr"],
'pings' : ["arping", "icmping", "tcping", "udping"],
'routes' : ["tcptrace"],
'misc' : ["externip", "getmac", "isnated", "ispromisc"],
#'radio' : ["wifi", "bluetooth"],
'WHOIS' : ["asn", "netcraft", "whois"]
}

# Discovers
arping = []
tcping = []
udping = []
icmping = []
asn = []
bluetooth = []
db2discover = []
externip = []
hostname = []
ipaddr = []
getmac = []
isnated = []
netcraft = []
ispromisc = []
tcptrace = []
whois = []
wifi = []

# Gathers
apps11i = ["dad"]
archanix = []
arppoison = ["interval"]
anticrypt = ["hash", "password"]
dnsspoof = []
dtspc = []
fakearp = []
firetest = []
nids = []
ikescan = []
ifxinfo = []
rainbowmd5 = ["hash"]
nikto = []
nmapfp = ['target', 'oport', 'cport']
nmapscan = {'nmapscan':'NmapScan'}
nmbstat = []
oascheck = []
oratool = ["sid", "user", "password", "dad", "method"]
oracrack11g = ["hash"]
oratt70info = []
osifuzz = []
p0f = []
portscan = ["target", "port"]
protoscan = []
rainbow = ["hash"]
rpcdump = ["user", "password"]
samrdump = ["username", "password"]
identify = []
smbclient = []
smbgold = ["user", "password"]
sniffer = []
snmpwalk = []
mssqlcrack = ["hash"]
tcpproxy = []
tcpscan = ['target', 'timeout']
tnscmd = ["sid"]
unicornscan = []
webserver = []
winspdetect = []
xmlrpc = []

# Brutes 
# By default all have elements: target, port and user
bruteftp = []
brutehttp = ["url"]
bruteimap = []
bruteifx = []
bruteora = ["sid"]
brutepop = []
brutesmb = []
brutesmtp = []
brutessh = []
brutesyb = []
