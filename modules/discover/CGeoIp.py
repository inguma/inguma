##      CGeoIp.py
#       
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
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

import os
import urllib, gzip
from lib.module import CIngumaDiscoverModule
from lib.core import get_profile_file_path

name = "geoip"
brief_description = "Get geographic information of an IP address"
type = "discover" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

class CGeoIp(CIngumaDiscoverModule):
    """ Get geographic data of an IP address using GeoIp """

    def check_db(self):
        """ Checks if the Maxmind GeoIP is already downloaded. """
        geoip_db_path = get_profile_file_path('data/GeoLiteCity.dat')
        if os.path.isfile(geoip_db_path):
            return True
        else:
            return False

    def help(self):
        self.gom.echo("target = <target IP>")
        self.gom.echo("         <if set to \"all\", all IP stored on KB will be used>")
        self.gom.echo("         <if set to \"download\", GeoIP database will be downloaded>")

    def download_db(self):
        """ Download the Maxmind DB. """
        geoip_db_path = get_profile_file_path('data/GeoLiteCity.dat')
    
        page = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"
        self.gom.echo("Downloading " + page, False )
        urllib.urlretrieve(page, geoip_db_path + '.gz')
    
        # Extract DB and remove original file
        self.gom.echo("Extracting files...", False)
        gz = gzip.open(geoip_db_path + '.gz')
        db = gz.read()
        gz.close()
        os.remove(geoip_db_path + '.gz')
        geodb = open(geoip_db_path, 'w')
        geodb.write(db)
        geodb.close()
        self.gom.echo("Operation complete", False)

        return True

    def run(self):
        try:
            import GeoIP
        except:
            self.gom.echo("No GeoIp library found, please install it")
            return False

        if self.target == "download":
            self.download_db()
            return False
        elif self.target == "all":
            self.targets = self.user_data['hosts']
        else:
            self.targets = [self.target]

        if self.check_db() == False:
            self.gom.echo('GeoIP database not found, install it setting target = \"download\" and running geoip again')
            return False
        else:
            geoip_db_path = get_profile_file_path('data/GeoLiteCity.dat')
            self.gi = GeoIP.open(geoip_db_path, GeoIP.GEOIP_STANDARD)
            
            return True

    def print_summary(self):
        self.gom.echo('%-15s  |  %15s %15s %15s %15s %15s ' % ('IP', 'Latitude', 'Longitude', 'Country', 'City', 'Region'))
        self.gom.echo('+----------------+--------------------------------------------------------------------------------+')
        for ip in self.targets:
            try:
                gir = self.gi.record_by_addr(ip)
                ### look up the ip
                lat = gir['latitude']
                lon = gir['longitude']
                country = gir['country_name']
                region = gir['region']
                city = gir['city']
#                self.gom.echo(ip, lat, lon, country, region, city)
                self.gom.echo('%-15s ==> %15s %15s %15s %15s %15s ' % (ip, lat, lon, country, city, region))
            except:
                self.gom.echo("%-15s ==>" % (ip))
                #pass
        self.gom.echo('+-------------------------------------------------------------------------------------------------+')
