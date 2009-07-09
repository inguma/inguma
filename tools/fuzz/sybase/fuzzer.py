#!/usr/bin/python

"""
MS SQL Server/Sybase Stored Procedures Fuzzing Tool

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
import pymssql

connection = None

funnydata = ("TEST", "SA", "''", '"', "A"*30, "A"*100, "A"*128,"A"*256,"A"*512,"A"*1024,
                        "A"*2048,"A"*3000,"A"*4000,"A"*5000,"A"*6000,"A"*7000,"A"*8000,"A"*10000,"A"*15000,"A"*20000,"A"*25000,
                        "A"*30000,"A"*32767, -1, -2, 0, 1, 2, 2147483647, -2147483647, 2147483648, 
                        -2147483648,
                        "OID", "%s%s%s%s%s%s%s", "%x%x%x%x%x%x", "%d%d%d%d%d%d", "%f%f%f%f%f%f",
                        "A"*8000 + "\?", "./", "../../../../../../../../tmp", "dir > c:\\fuzzy.txt",
                        "550e8400-e29b-41d4-a716-446655440000", "ffffffff-ffff-ffff-ffff-ffffffffffff",
                        "00000000-0000-0000-0000-000000000000", "0.0.0.0", "localhost",
                        "255.255.255.255", "http//www.google.com", "www.google.com",
                        #"convert(varbinary(1024), replicate('a', 1024))",
                        #"convert(varbinary(2048), replicate('a', 2048))",
                        #"convert(varbinary(4096), replicate('a', 4096))",
                        #"convert(varbinary(5000), replicate('a', 5000))",
                        #"convert(varbinary(6000), replicate('a', 6000))",
                        #"convert(varbinary(7000), replicate('a', 7000))",
                        #"convert(varbinary(8000), replicate('a', 8000))")
                        "")

def getTypes(name):

    global connection

    mTypes = ()
    
    sql = """
    Select st.name
  FROM master..syscolumns sc,
	   master..systypes st,
       master..sysobjects so 
 WHERE sc.id in (select id 
				   from master..sysobjects 
                  where type ='P')
   AND so.type ='P'
   AND sc.id = so.id
   AND sc.type = st.type
   AND sc.type <> 39
   AND so.name = '%s'
 order by 1""" % (name)
 
    try:
        cur = connection.cursor()
        cur.execute(sql)
        
        for value in cur.fetchall():
            mTypes += (value, )
    except:
        mTypes = ()

    return mTypes

def isCompatible(types, index, data):

    remoteType = types[index][0]

    if type(data) is str:
        return remoteType in ('uniqueidentifier', 'varbinary', 'binary', 'text', 'ntext', 'char', 'varchar', 'nchar', 'nvarchar', 'image', 'xml')
    else:
        return remoteType in ('float', 'money', 'int', 'numeric', 'bit', 'smallint')

def fuzzFunction(name, args):

    global funnydata
    global connection

    try:
            mTypes = getTypes(name)
            data = "EXEC " + name + " "

            for i in range(args):
                if i == 0:
                    data += "'%s'"
                else:
                    data += ", '%s'"

            data += ""
            mBreak = False

            for funny in funnydata:
                for refunny in funnydata:
                    params = ()

                    for i in range(args):
                        if i == 1 and args > 1:
                            if not isCompatible(mTypes, i, refunny):
                                mBreak = True
                                break

                            params += (refunny, )
                        else:
                            if not isCompatible(mTypes, i, funny):
                                mBreak = True
                                break

                            params += (funny, )
                    
                    if mBreak:
                        mBreak = False
                        continue

                    cur = connection.cursor()
                    curData = data % (params)
                    
                    if type(funny) is int:
                        log = "Number", funny
                    else:
                        log = "String",len(str(funny))
                    
                    if args > 1:
                        if type(refunny) is int:
                            log += "Number", refunny
                        else:
                            log += "String",len(str(refunny))

                    try:
                        if curData.find("'convert(varbinary")>-1:
                            curData = curData.replace("'convert", "convert")
                            curData = curData.replace("))'", "))")

                        print log, curData[0:60]
                        cur.execute(curData)
                    except:
                        print "From server.",str(sys.exc_info()[1])[0:80]

                    if args == 1:
                        break
    except KeyboardInterrupt:
        print "Aborted."
        sys.exit(0)
    except:
        print "Exception:",sys.exc_info()[1]
        #sys.exit(0)

def connect():
    global connection

    connection = pymssql.connect(host='192.168.1.14:1050', user='test', password='1234')

def main():
    connect()
    cur = connection.cursor()
    cur.execute("""
               Select so.name, count(distinct sc.name)
  FROM master..syscolumns sc,
	   master..systypes st,
       master..sysobjects so 
 WHERE sc.id in (select id 
				   from master..sysobjects 
                  where type ='P')
   AND so.type ='P'
   AND sc.id = so.id
   AND sc.type = st.type
   AND sc.type <> 39
 group by so.name
 order by 1""")
    
    i = 0

    for proName in cur.fetchall():
        i += 1

        print proName[0]
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
