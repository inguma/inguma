##      CSqlServerCrack.py
#
#       Copyright 2010 Joxean Koret <joxeankoret@yahoo.es>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from lib.module import CIngumaFuzzerModule
from lib.libSQLServerPassword import CSQLServerPassword

name = "mssqlcrack"
brief_description = "Crack a MS SQL Server 7 or 2000 password"
type = "fuzzer"

globals = ["hash", ]

class CSqlServerCrack(CIngumaFuzzerModule):

    hash = ""

    def help(self):
        self.gom.echo("hash = <hash of the password>")

    def findHash(self, hash):

        if not hash.isalnum():
            self.gom.echo("[!] Invalid hash: Non alphanumeric characters")
            return False

        objMSSQL = CSQLServerPassword(self.hash)
        objMSSQL.print_summary()

        for passwd in self.get_password_list(self.dict['base_path']):
            passwd = passwd.strip()
            x = objMSSQL.encrypt(passwd)[2:]

            if hash.find(x) > -1:
                self.add_data_to_kb(hash, passwd)
                self.gom.echo("[+] Password:", passwd)
                return True

        self.gom.echo("[!] No match")
        self.gom.echo(objMSSQL.encrypt("sa"))
        self.gom.echo(self.hash)
        return False

    def run(self):

        if self.hash == "":
            self.gom.echo("[!] No hash specified")
            return False
        else:
            self.findHash(self.hash)

        return True
