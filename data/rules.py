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
NOTE: It was created as a fast way to check for rules and IDS evasion techniques *BUT*
NOTE: is subject to be removed.
"""
rule1 = {}
rule1["name"] = "oracletnsdos"
rule1["type"] = "Denial of service"
rule1["description"] = "Oracle test rule for the Inguma's IDS module"
rule1["default_port"] = 1521
rule1["data"] = ".*\s*COMMAND\s*=\s*stop\s*.*"
rule1["attack"] = """An attempt to stop the Oracle TNS Listener was made."""
rule1["tip"] = """Setup a password in the Oracle TNS Listener to prevent a denial of 
service against the server."""
rule1["ids"] = """To evade IDS detection fragment the packet at TNS level (2048 bytes
each or SDU = 512) or TCP level."""

rule2 = {}
rule2["name"] = "oracletnsversion"
rule2["type"] = "Gather information"
rule2["description"] = "Oracle test rule for the Inguma's IDS module"
rule2["default_port"] = 1521
rule2["data"] = ".*\s*COMMAND\s*=\s*version\s*.*"
rule2["attack"] = """An attempt to get version information from TNS Listener was made."""
rule2["tip"] = """Setup a password in the Oracle TNS Listener to prevent attacks."""
rule2["ids"] = """Calculate yourself the version by doing a 'tnsping' and reading the 
VSNNUM which is the decimal Oracle version, convert it to hexadecimal. 
TNS Ping is not commonly checked by IDS software."""

rule3 = {}
rule3["name"] = "oraclesqlinjection"
rule3["type"] = "SQL Injection"
rule3["description"] = "Oracle test rule for the Inguma's IDS module"
rule3["default_port"] = 1521
rule3["data"] = ".*\s*((\")*CTXSYS(\")*\.){0,1}\s*\s*(\")*DRILOAD(\")*\s*\.\s*(\")*VALIDATE_STMT(\")*"
rule3["attack"] = """An attempt to execute the well know vulnerable Oracle package
CTXSYS.DRILOAD was detected."""
rule3["tip"] = """Revoke execution privileges from PUBLIC in the PACKAGE or apply
the correspondient CPU (Critical Patch Update)."""
rule3["ids"] = """Fragment the TNS Packets (2048 bytes each or SDU=512) or try executing it 
via "EXECUTE IMMEDIATE 'sql command';"."""

rule4 = {}
rule4["name"] = "oraclesqlinjection"
rule4["type"] = "SQL Injection"
rule4["description"] = "Oracle test rule for the Inguma's IDS module"
rule4["default_port"] = 1521
rule4["data"] = ".*\s*((\")*SYS(\")*\.){0,1}\s*\s*(\")*DBMS_CDC_IMPDP(\")*\s*\.\s*(\")*BUMP_SEQUENCE(\")*"
rule4["attack"] = """An attempt to execute the well know vulnerable Oracle package
SYS.DBMS_CDC_IMPDP.BUMP_SEQUENCE was detected."""
rule4["tip"] = """Revoke execution privileges from PUBLIC in the PACKAGE or apply
the correspondient CPU (Critical Patch Update)."""
rule4["ids"] = """Fragment the TNS Packets (2048 bytes each or SDU=512) or try executing it 
via "EXECUTE IMMEDIATE 'sql command';"."""

rules = []
rules.append(rule1)
rules.append(rule2)
rules.append(rule3)
rules.append(rule4)

