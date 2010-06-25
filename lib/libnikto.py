"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
import sys
import urllib

DATABASE_URL = "http://www.cirt.net/nikto/UPDATES/2.01/db_tests"
BANNER = """
Nikto is a web server assessment tool designed to find various default and
insecure files, configurations and programs on any type of web server.

For updated databases and more information, navigate to:

http://www.cirt.net"""

SIGNATURES = []

class CNiktoRule:
    testId = None
    osvdbId = None
    tuningType = None
    uri = None
    method = None
    match1 = None
    match1And = None
    match1Or = None
    fail1 = None
    fail2 = None
    summary = None
    httpData = None
    headers = None
    
    def __init__(self, props):
        self.testId = props[0].strip('"')
        self.osvdbId = props[1].strip('"')
        self.tuningType = props[2].strip('"')
        self.uri = props[3].strip('"')
        self.method = props[4].strip('"')
        self.match1 = props[5].strip('"')
        self.match1And = props[6].strip('"')
        self.match1Or = props[7].strip('"')
        self.fail1 = props[8].strip('"')
        self.fail2 = props[9].strip('"')
        self.summary = props[10].strip('"')
        self.httpData = props[11].strip('"')
        self.headers = str(props[12:]).strip('"')

def readSignatures():
    try:
        f = file(os.path.join("data", "db_tests"), "r")
    except:
        print "*** Error reading Nikto's signatures"
        print sys.exc_info()[1]
        raise
    
    for line in f:
        line = line.strip("\r").strip("\n")
        
        if line.startswith("#") or line.replace(" ", "") == "":
            continue # Is a comment or a blank line
        
        props = line.split(",")
        SIGNATURES.append(props[0:12] + ["".join(props[12:]), ])

        # Extracted from http://www.cirt.net/nikto2-docs/ch07s03.html
        #testId, osvdbId, tuningType, uri, method, match1, match1And, match1Or, fail1, fail2, summary, httpData, headers = props
    return True

def getDatabases(update = False):
    print BANNER
    print

    if update:
        ret = updateDatabases()
    else:
        try:
            f = file(os.path.join("data", "db_tests"), "r")
            f.close()
            ret = readSignatures()
        except:
            ret = updateDatabases()

    return ret

def updateDatabases():

#    try:
#        res = raw_input("Do you want to download Nikto databases (y/n)? [n] ")
#        
#        if res.lower() != "y":
#            return False
#    except:
#        print "Aborted."
#        return False

    print "[+] Downloading nikto database ... "
    data = urllib.urlopen(DATABASE_URL).read()
    
    print "[+] Saving database ... "
    f = file(os.path.join("data", "db_tests"), "w")
    f.write(data)
    f.close()

    ret = readSignatures()
    return ret

if __name__ == "__main__":
    getDatabases(True)
    print "[+] Total of %d signature(s)" % len(SIGNATURES)
