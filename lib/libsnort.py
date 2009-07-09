#!/usr/bin/python
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
"""
NOTE: Subject to be removed.
"""
import os
import re
import sys

from core import regexp2pyre

class CSnortRule:
    msg = ""
    flow = ""
    contents = []
    classtype = ""
    sid = ""
    rev = ""
    pcre = ""
    reference = ""
    
    def getProperties(self):
        return ("msg", "flow", "content", "classtype", "sid", "rev", "pcre", "reference")
    
    def setProperty(self, param, value):
    
        if value.startswith('"') and value.endswith('"'):
            # Strip the starting and ending quotes
            value = value[1:len(value)-1]

        if param.lower() == "msg":
            self.msg = value
        elif param.lower() == "flow":
            self.flow = value
        elif param.lower() == "content":
            self.contents.append(value)
        elif param.lower() == "classtype":
            self.classtype = value
        elif param.lower() == "sid":
            self.sid = value
        elif param.lower() == "rev":
            self.rev = value
        elif param.lower() == "pcre":
            self.pcre = regexp2pyre(value)
        elif param.lower() == "reference":
            self.reference = value
        else:
            print "Unknow option", param

class CSnortRuleParser:

    path = ""
    rules = []

    def __init__(self, rulepath = "/etc/snort/rules/"):
        self.path = rulepath

    def processLine(self, line):
        """
        
        Example rule: 

        alert tcp $EXTERNAL_NET any -> $SQL_SERVERS $ORACLE_PORTS (msg:"ORACLE misparsed login response"; flow:from_server,established; 
        content:"description=|28|"; nocase; content:!"connect_data=|28|sid="; nocase; content:!"address=|28|protocol=tcp"; nocase; 
        classtype:suspicious-login; sid:1675; rev:4;)
        """
        data = line
        pos = data.find("(")
        
        if pos == -1:
            return False

        data = data[pos+1:len(data)-1]
        objRule = CSnortRule()
        
        for element in data.split(";"):
            properties = element.split(":")
            
            if len(properties) == 2:
                if properties[0].lstrip() in objRule.getProperties():
                    objRule.setProperty(properties[0].lstrip(), properties[1])

        self.rules.append(objRule)

    def parse(self, mfile):
        
        f = file(self.path + os.sep + mfile, "r")

        for line in f:
            if not line.startswith("#") and len(line.replace(" ", "")) > 0:
                self.processLine(line)

def main():
    snortRuleParser = CSnortRuleParser()
    #
    # This is the most important one
    #
    #snortRuleParser.parse("oracle.rules")
    import os
    for x in os.listdir("/etc/snort/rules"):
        if x.endswith(".rules"):
            snortRuleParser.parse(x)

    for rule in snortRuleParser.rules:
        if rule.pcre != "":

            try:
                print rule.msg, repr(rule.pcre)
                p = re.compile(rule.pcre, re.IGNORECASE)
            except:
                print "Rule does not compile:", sys.exc_info()[1]

if __name__ == "__main__":
    main()

