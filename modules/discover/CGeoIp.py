#!/usr/bin/python

##      GeoIp.py
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

import sys, os
import urllib, gzip
from lib.libexploit import CIngumaModule

name = "geoip"
brief_description = "Get geographic information of an IP address"
type = "discover" # The type of a module, currently, can only be 'gather', 'exploit', 'discover', 'fuzz' or 'brute'

class CGeoIp(CIngumaModule):
    """ Get geographic data of an IP address using GeoIp """

    target = ""

    def help(self):
        print "target = <target IP>"
        print "         <if set to \"all\", all IP stored on KB will be used>"
        print "         <if set to \"download\", GeoIP database will be downloaded>"

    def run(self):
        try:
            import GeoIP
        except:
            print "No GeoIp library found, please install it"
            sys.exit(0)

        if self.target == "download":

            self.GEOIP_DIR='data/'        
            self.INGUMA_DIR = os.getcwd()
    
            page = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"
            self.gom.echo( "Downloading " + page, False )
            urllib.urlretrieve(page, "data/GeoLiteCity.dat.gz")
    
            # Extract DB and remove original file
            self.gom.echo( "Extracting files...", False )
            gz = gzip.open("data/GeoLiteCity.dat.gz")
            db = gz.read()
            gz.close()
            os.remove("data/GeoLiteCity.dat.gz")
            geodb = open('data/GeoLiteCity.dat', 'w')
            geodb.write(db)
            geodb.close()
            self.gom.echo( "Operation Complete", False )

            return True

        elif self.target == "all":
            targets = self.user_data['hosts']
        else:
            targets = [self.target]

        gi  = GeoIP.open('data/GeoLiteCity.dat', GeoIP.GEOIP_STANDARD)
        print '%-15s  |  %15s %15s %15s %15s %15s ' % ('IP', 'Latitude', 'Longitude', 'Country', 'City', 'Region')
        print '+----------------+--------------------------------------------------------------------------------+'
        for ip in targets:
            try:
                gir = gi.record_by_addr(ip)
                ### look up the ip
                lat = gir['latitude']
                lon = gir['longitude']
                country = gir['country_name']
                region = gir['region']
                city = gir['city']
#                print ip, lat, lon, country, region, city
                print '%-15s ==> %15s %15s %15s %15s %15s ' % (ip, lat, lon, country, city, region)
            except:
                print "%-15s ==>" % (ip)
                #pass
        print '+-------------------------------------------------------------------------------------------------+'
        
        return False

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
