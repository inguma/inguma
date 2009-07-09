#!/usr/bin/python

"""
Oracle PL/SQL Fuzzer for Inguma
Copyright(c) 2006, 2007 Joxean Koret

 * Added more "funnydata" pointed to me by Alexander Kornbrust. Thanks you!
"""

import sys
import cx_Oracle

cx_Oracle.OPT_Threading = 1

import thread

global connection

funnydata = ("TEST", "SCOTT", "XMLREF", '" || XMLREF() || "', 'TEST" A A ', "'", '"', "A"*30, "A"*100, "A"*128,"A"*256,"A"*512,"A"*1024,
"A"*2048,"A"*3000,"A"*4000,"A"*5000,"A"*6000,"A"*7000,"A"*8000, "A"*9000, "A"*10000, "A"*20000, "A"*30000, "A"*32700,
-1, -2, 0, 1, 2, 2147483647, -2147483647, 2147483648, -2147483648,
"ROWID", "PRIMARY KEY", "%s%s%s%s%s%s%s", "%x%x%x%x%x%x", "%d%d%d%d%d%d",
"'' mysearchstring", "' or test.xmlref --", "F1", "' || TEST.XMLREF || '",
"''" + "\b"*100 + "INJECTED","' or 1=TEST.F1 --","' and 1=TEST.F1 --","GRANT DBA TO TEST", "' OR '1'='1","TEST.F1", "TEST.F1--","*/","'*/","/*","' /*","--","'--","SYS.DUAL","SYS","DUAL","USER","CAT")

def fuzzData(data, index, func = False, types=None):
    global connection

    if len(types) == 0:
        return

    for x in funnydata:
        try:
            varList = []
            if func:
                varList.append(None)

            i = -1

            for var in range(index):
                i += 1

                if func and i == 0:
                    continue

                if types[i].upper() in ('NUMBER', 'FLOAT', 'BINARY_INTEGER', 'BINARY_FLOAT') and type(x) is str:
                    varList.append(0)
                elif types[i].upper() not in ('VARCHAR2', 'RAW', 'NCHAR', 'BINARY_INTEGER', 'BINARY_FLOAT',
                    'CHAR', 'NVARCHAR2', 'NUMBER', 'FLOAT', 'LONG RAW'):
                    varList.append(None)
                else:
                    varList.append(x)

            cur = connection.cursor()
            cur.execute(data, varList)
        except KeyboardInterrupt:
            print "Aborted."
            raise
        except:
            error = str(sys.exc_info()[1])
            #print error

            if error.upper().find("ORA-00970") > -1 or error.upper().find("ORA-00907") > -1 or error.upper().find("ORA-00933") > -1 or error.upper().find("ORA-01756:") > -1 or error.upper().find("ORA-00923:") > -1 or error.upper().find("PLS-00103:") > -1 or error.upper().find("ORA-00900") > -1:
                print "----------"
                print data.lstrip().rstrip()
                print "----------"

                print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                print error
                print "*** POSSIBLE SQL INJECTION FOUND ***"
            elif error.upper().find("LPX-00601") > -1:
                print "----------"
                print data.lstrip().rstrip()
                print "----------"
                print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                print error
                print "*** POSSIBLE XPATH INJECTION ***"
            elif error.upper().find("ORA-00604") > -1:
                print "----------"
                print data.lstrip().rstrip()
                print "----------"
                print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                print error
                print "*** POSSIBLE EXPLOITABLE SQL INJECTION FOUND ***"
            #elif error.upper().find("ORA-00942") > -1:
            #    print "*** LOOKING FOR A TABLE OR VIEW. CHECK IF UID=0 ***"
            elif error.upper().find("ORA-03113") > -1:
                if len(str(x)) > 15:
                    print "----------"
                    print data.lstrip().rstrip()
                    print "----------"
                    print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                    print error
                    print "*** POSSIBLE BUFFER OVERFLOW ***"
                else:
                    print "----------"
                    print data.lstrip().rstrip()
                    print "----------"
                    print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                    print error
                    print "*** INSTANCE CRASHED ***"

                print "Reconnecting ... "
                connect()
            elif error.upper().find("ORA-03114") > -1 or error.upper().find("ORA-01012") > -1:
                print "Not connected. Reconnecting ... "
                connect()
            elif error.upper().find("ORA-00600") > -1:
                print "----------"
                print data.lstrip().rstrip()
                print "----------"
                print "Data is " + str(x)[0:4] + " of length " + str(len(str(x)))
                print "*** INTERNAL ERROR ***"
            elif error.upper().find("PLS-") > -1:
                sys.stderr.write("Currently unfuzzable??? May be an internal fuzzer error :(\n")
                sys.stderr.write(str(sys.exc_info()[1]) + "\n")
                sys.stderr.write("----------\n")
                sys.stderr.write(data.lstrip().rstrip()+"\n")
                sys.stderr.write("----------\n")
                sys.stderr.flush()
                #raw_input()
                #continue
		break

def connect():
    global connection

    #link    = "test/test@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.1.10)(PORT=1521)))"
    #link += "(CONNECT_DATA=(SID=AV)))"

    link    = "test/test@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521)))"
    link += "(CONNECT_DATA=(SID=INFRA)))"

    #link    = "test/test@localhost/orcl1"
    connection = cx_Oracle.connect(link)
    connection.rollback()
    connection.commit()

    cur = connection.cursor()
    #cur.execute("ALTER SESSION SET SQL_TRACE = TRUE")
    cur.execute(""" alter session set nls_date_format='"'' and test.xmlref()=1--"'   """)
    cur.execute("""  ALTER SESSION SET NLS_NUMERIC_CHARACTERS = ''' or test.xmlref() == 1.'   """)
    print "Tracing ... "

def main():
    global connection

    fuzzPackages = """
 select distinct owner           "Owner",
       package_name    "Package",
       object_name     "Program_Unit"
  from sys.all_arguments x
 where owner = 'XDB'
  order by owner desc, package_name, object_name
        """

    packageProcedures = """
select position        "Position",
       argument_name   "Argument",
       data_type       "Data type",
       initcap(in_out) "In_Out",
       owner            sdev_link_owner,
       package_name     sdev_link_name,
       'PACKAGE'        sdev_link_type
  from sys.all_arguments
 where owner = :1
   and package_name = :2
   and object_name = :3
  order by owner, package_name, object_name, position nulls first
        """

    connect()

    bStart = False

    try:
        cursor = connection.cursor()
        cursor.execute(fuzzPackages)

        pkgName = ""

        print "Running first query. It may take a long while ... "
        done = False
        for pkgData in cursor.fetchall():

            if not done:
                print "Done first query, fuzzing silently..."
                done = True

            if not pkgData[1] is None:
                pkgName = pkgData[0] + "." + pkgData[1] + "." + pkgData[2]
            else:
                pkgName = pkgData[0] + "." + pkgData[2]

            procCursor = connection.cursor()
            procCursor.execute(packageProcedures, pkgData)

            procCursorData = procCursor.fetchall()
            func = 0

            if len(procCursorData) > 0:
                for elem in procCursorData:
                    if elem[1] is None:
                        func = 1
                        break

            if int(func) == 0:
                data = """BEGIN
  """ + pkgName + """("""
            else:
                data = """select  """ + pkgName + """("""

            index = 0
            mtypes = ()

            for x in procCursorData:
                if x[1] is None:
                    continue

                index += 1
                mtypes += (x[2],)
                
                if func == 0:
                    if index == 1:
                        data += str(x[1]) + "=>:" + str(index)
                    else:
                        data += "," + str(x[1]) + "=>:" + str(index)
                else:
                    if index == 1:
                        data += ":" + str(index)
                    else:
                        data += ",:" + str(index)

            if func == 0:
                data += """);
END;"""
            else:
                data += """) from dual"""

            fuzzData(data, index, func == 1, mtypes)
            #connection.close()
            #connect()
            #thread.start_new_thread(fuzzData, (data, index, func == 1, mtypes))

        connection.close()
    except Exception, e:
        print "Error",e
        raise e

if __name__ == "__main__":
    main()
    
