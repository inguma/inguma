#!/usr/bin/python

import sys

sys.path.append("../../lib")
sys.path.append("../lib")
sys.path.append("lib")

import run_command
from oracleids import randomizeSpaces

data = """
BEGIN
  null;
END;
"""

name = "install_oraexec"
brief_description = "Install OraExec"

class CPayload:

    user = "TEST"
    function = "F1"
    useDML = False
    covert = 0
    verifyCommand = ""
    connection = None
    
    host = ""
    port = ""
    
    type = 1

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
        ret = objRun.run()

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
 
