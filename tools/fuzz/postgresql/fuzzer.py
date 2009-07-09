#!/usr/bin/python

"""
PostgreSQL Database Functions Fuzzing Tool

Copyright (c) 2005, 2006 Joxean Koret, joxeankoret [at] yahoo.es

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

import sys
from pyPgSQL import PgSQL

connection = None

funnydata = ("TEST", "POSTGRES", "''", '"', "A"*30, "A"*100, "A"*128,"A"*256,"A"*512,"A"*1024,
                        "A"*2048,"A"*3000,"A"*4000,"A"*5000,"A"*6000,"A"*7000,"A"*8000,"A"*10000,"A"*15000,"A"*20000,"A"*25000,
                        "A"*30000,"A"*32767, -1, -2, 0, 1, 2, 2147483647, -2147483647, 2147483648, -2147483648,
                        "OID", "%s%s%s%s%s%s%s", "%x%x%x%x%x%x", "%d%d%d%d%d%d", "%f%f%f%f%f%f",
                        "A"*8000 + "\?", "./", "../../../../../../../../tmp", "`ls -lga`",
                        "array['a']",
                        "array['A'" + ",'A'"*5000 + "]", "array['" + "A"*5000 + "']",
                        "chr(0)")

def fuzzFunction(name, args):

    global funnydata
    global connection

    try:
            data = "SELECT " + name + "("

            for i in range(args):
                if i == 0:
                    data += "'%s'"
                else:
                    data += ", '%s'"

            data += ");"
            for funny in funnydata:

                if type(funny) is int:
                    print "Number", funny
                else:
                    print "String",len(str(funny))

                params = ()

                for i in range(args):
                    params += (funny, )

                connection.rollback()
                cur = connection.cursor()
                curData = data % (params)

                try:
                    if curData.find("array[") > -1:
                        curData = curData.replace("'array[", "array[")
                        curData = curData.replace("]'", "]")
                    elif curData.find("chr(0)") > -1:
                        curData = curData.replace("'chr", "chr")
                        curData = curData.replace("0)'", "0)")
                        print curData

                    cur.execute(curData)
                except:
                    print "From server.",str(sys.exc_info()[1])[0:80]
    except KeyboardInterrupt:
        print "Aborted."
        sys.exit(0)
    except:
        print "Exception:",sys.exc_info()[1]
        #sys.exit(0)

def connect():
    global connection
    
    connection = PgSQL.connect(host="localhost", database="testdb", client_encoding="utf-8", unicode_results=1,
                                                        user="test")

def main():
    connect()
    cur = connection.cursor()
    cur.execute("""
              select proname, pronargs 
    		     from pg_proc 
            where pronargs > 0 
              and proName not in ('substring', 'bpcharicregexeq', 'bpcharicregexne', 'bpcharregexeq', 
                                                    'bpcharregexne', 'nameicregexeq', 'nameicregexne', 'numeric_fac',
                                                    'numeric_power', 'regexnesel', 'regexp_replace', 'texticnlike',
                                                    'texticregexeq', 'texticregexne', 'texticregexeq', 'factorial', 'textregexq','textregexeq', 'textregexne')
		    order by proname""")
    
    i = 0

    for proName in cur.fetchall():
        i += 1

        print proName[0]
        continue
        print "Fuzzing",proName[0],"with",proName[1],"argument(s)"
        try:
            fuzzFunction(proName[0], proName[1])
        except:
            print "Error while fuzzing",proName[0],"(Index",i,")"
            raise

    print
    print "Fuzzed a total of",i,"functions(s)"
    print "Done."

if __name__ == "__main__":
    main()
