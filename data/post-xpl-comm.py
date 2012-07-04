win_sys_comm = [
                ["whoami", "Lists your current user"],
                ["whoami /all", "Lists current user info"],
                ["set", "Shows all current environmental variables"],
                ["fsutil fsinfo drives", "Lists the current drives"]
               ]

win_net_comm = [
                ["ipconfig /all", "Display full information about NIC"],
                ["ipconfig /displaydns", "Display local DNS cache."]
                ["netstat -nabo", ""],
                ["netstat -s -p [tcp|udp|icpm|ip]", ""],
                ["netstat -r", ""],
                ["netstat -na | findstr :445", ""],
                ["netstat -nao | findstr LISTENING", ""],
                ["netsh diag show all", ""],
                ["net view", ""],
                ["net view /domain", ""],
                ["net view /domain:otherdomain", ""],
                ["net user /domain", "List all of the domain users"],
                ["net accounts", "Print the password policy"],
                ["net accounts /domain", "Print the password policy for the domain"],
                ["net localgroup administrators", "Print the members of the Admin group"],
                ["net share", "Display shared SMB entries"],
                ["arp -a", "List ARP table"],
                ["route print", "Print routing table"],
                ["netsh wlan show profiles", "Saved wireless profiles"],
                ["netsh wlan export profile folder=. key=clear", "Export wifi profile with password"],
                ["wmic ntdomain list", "Retrieve information about Domain and DC"]
               ]

win_config_comm = [
                    ["sc qc", ""],
                    ["sc query", ""],
                    ["sc queryex", ""]
                  ]
