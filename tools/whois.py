from os import popen
import re

find_record = re.compile("\s+([^:]+): (.*)\s*").match
for line in popen("whois tuenti.com"):
    match = find_record(line)
    if not match:
        continue
    print "%s --> %s" % (match.groups()[0], match.groups()[1])
