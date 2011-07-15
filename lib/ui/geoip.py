##      geoip.py
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
import gtk, cairo

import GeoIP

class Gui(gtk.Window):
    def __init__(self, core):
        super(Gui,self).__init__()

        # Data to be mapped
        self.geodata = []
        self.tooltips = {}
        self.uicore = core
        self.ips = self.uicore.get_kbfield('hosts')

        # Window properties
        self.connect("destroy", self.destroy)
        self.set_title("GeoIP for Inguma")
#        self.set_size_request(1002, 602)
        self.maximize()
        self.set_resizable(True)

        # Drawing area for the map and the points
        self.drawarea = gtk.DrawingArea()
        self.drawarea.set_size_request(2048, 1025)
        pangolayout = self.drawarea.create_pango_layout("")
        self.drawarea.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.drawarea.props.has_tooltip = True
        self.drawarea.connect("expose-event", self.drawarea_expose)
        self.drawarea.connect("query-tooltip", self.query_tooltip_drawing_area_cb)

        # ScrolledWindow to contain the map (DrawingArea)
        self.scrolledw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.scrolledw.set_size_request(1000, 502)
        self.scrolledw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledw.add_with_viewport(self.drawarea)

        # The list of IP addresses and data
        self.geovbox = self.dialogGeoIP()

        # Vertical Panel to contain the map and the list
        self.vpane = gtk.VPaned()
        self.vpane.add1(self.scrolledw)
        self.vpane.add2(self.geovbox)

        self.add(self.vpane)

        self.show_all()

    def drawarea_expose(self, drawarea, event):

        # Clean the data to be mapped
        self.geodata = []
        # Paint the map in the DrawArea
        mapstyle = self.drawarea.get_style()
        self.mapgc = mapstyle.fg_gc[gtk.STATE_NORMAL]
        
        self.font = 0
        
        mapname = "lib/ui/data/map4.png"

        image = cairo.ImageSurface.create_from_png(mapname)

        sizeDrawarea = self.drawarea.get_allocation()
        self.pixmap  = gtk.gdk.Pixmap(None, sizeDrawarea.width, sizeDrawarea.height, 24)

        imagepattern = cairo.SurfacePattern(image)

        scaler = cairo.Matrix()

        scaler.scale(float(image.get_width())/float(sizeDrawarea.width), float(image.get_height())/float(sizeDrawarea.height))
        imagepattern.set_matrix(scaler)

        imagepattern.set_filter(cairo.FILTER_BEST)
        
        context = self.pixmap.cairo_create()
        
        context.set_source(imagepattern)

        drawable = self.drawarea.window
        self.linegc = drawable.new_gc()
        self.pointgc = drawable.new_gc(line_width = 20)

        context.paint()

        self.drawarea.window.draw_drawable(self.mapgc, self.pixmap, 0, 0, 0, 0, -1, -1)

        # Paint the IP addresses on the map
        for ip in self.ips:
            lat, lon = self.geopos(ip)
            if lat and lon:
                self.paint_ip(lat, lon, ip)

        self.tooltips = {}
        for element in self.geodata:
            if element['city'] not in self.tooltips:
                self.tooltips[element['city']] = element['ip']
            else:
                self.tooltips[element['city']] += '\n' + element['ip']

        # Refresh the list of IP and their data
        self.refreshListstore(self.liststore)

        return

    def paint_ip(self, lat, lon, ip):
        sizeDrawarea = self.drawarea.get_allocation()
        windowSizeY  = sizeDrawarea.height
        windowSizeX  = sizeDrawarea.width

        # Calculate coordinates on map pixels
        pxlon = lon*(float(windowSizeX)/360)+(float(windowSizeX)/2)
        pxlon = int(pxlon)

        pxlat = (-lat)*(float(windowSizeY)/180)+(float(windowSizeY)/2)
        pxlat = int(pxlat)

        # Paint a red point on the map
        self.pointgc.set_rgb_fg_color( gtk.gdk.Color(red=1.0, green=1.0, blue=1.0) )
        self.drawarea.window.draw_arc(self.pointgc, True, pxlon-2, pxlat-2, 6, 6, 0, 360*64)

        self.pangolayout = self.drawarea.create_pango_layout("")
        self.pangolayout.set_text(str(self.geodata[-1]['city']) + '/' + str(self.geodata[-1]['country']))
        self.drawarea.window.draw_layout(self.pointgc, pxlon+8, pxlat-5, self.pangolayout)

        # Add the coordinates in pixels to the IP data
        self.geodata[-1]['px_x'] = pxlon
        self.geodata[-1]['px_y'] = pxlat
        self.geodata[-1]['ip'] = ip

    def geopos(self, ip):
        # Load GeoIP database
        from lib.core import get_profile_file_path
        # It's a shame that we cannot use the system GeoIP yet.
        geoip_db_path = get_profile_file_path('data' + os.sep + 'GeoLiteCity.dat')
        gi  = GeoIP.open(geoip_db_path, GeoIP.GEOIP_STANDARD)
        gir = gi.record_by_addr(ip)
        if gir:
            # Get Geoip information
            lat = gir['latitude']
            lon = gir['longitude']
#            country = gir['country_name']
#            countryc = gir['country_code']
#            country3 = gir['country_code3']
#            region = gir['region']
#            regname = gir['region_name']
#            city = gir['city']
#            timezone = gir['time_zone']
#            areacode = gir['area_code']
#            metrocode = gir['metro_code']
#            postal = gir['postal_code']
#            dma = gir['dma_code']
            self.geodata.append({'lat':gir['latitude'], 'lon':gir['longitude'], 'country':gir['country_name'], 'countryc':gir['country_code'], \
                                 'region':gir['region'], 'regname':gir['region_name'], 'city':gir['city'], 'timezone':gir['time_zone']})

            return lat, lon
        else:
            return False, False

    def query_tooltip_drawing_area_cb(self, widget, x, y, keyboard_tip, tooltip, data=None):
        # Add tooltips for each point of the map
        if keyboard_tip:
            return False
        
        for i in range(len(self.geodata)):
            storedx = self.geodata[i]["px_x"]
            storedy = self.geodata[i]["px_y"]
            if(storedx - 10 < x and x < storedx + 10 and storedy - 10 < y and y < storedy + 10):
                tooltip.set_markup(self.tooltips[self.geodata[i]["city"]])
                return True;
        return False
    
    def destroy(self, widget):
            self.destroy()
            return 0

    def dialogGeoIP(self):
        # Text list of IP data
        self.liststore = gtk.ListStore(str, str, str, str, str, str, str, str, str)
        # ip lon lat city region country...
        self.liststore = self.refreshListstore(self.liststore)

        treeview = gtk.TreeView(self.liststore)
        treeview.set_rules_hint(True)

        #create the treeviewcolumn(tvc) object
        tvcIp         = gtk.TreeViewColumn('IP')
        tvcLat        = gtk.TreeViewColumn('Latitude')
        tvcLon        = gtk.TreeViewColumn('Longitude')
        tvcCity       = gtk.TreeViewColumn('City')
        tvcRegion     = gtk.TreeViewColumn('Region')
        tvcRegname    = gtk.TreeViewColumn('Region Name')
        tvcCountry    = gtk.TreeViewColumn('Country')
        tvcCountryc   = gtk.TreeViewColumn('Country Code')
        tvcTimezone   = gtk.TreeViewColumn('Time Zone')

        #add the self.liststore row to the treeview GUI backend
        treeview.append_column(tvcIp)
        treeview.append_column(tvcLat)
        treeview.append_column(tvcLon)
        treeview.append_column(tvcCity)
        treeview.append_column(tvcRegion)
        treeview.append_column(tvcRegname)
        treeview.append_column(tvcCountry)
        treeview.append_column(tvcCountryc)
        treeview.append_column(tvcTimezone)

        #create cell object
        cellIp         = gtk.CellRendererText()
        cellLat        = gtk.CellRendererText()
        cellLon        = gtk.CellRendererText()
        cellCity       = gtk.CellRendererText()
        cellRegion     = gtk.CellRendererText()
        cellRegname    = gtk.CellRendererText()
        cellCountry    = gtk.CellRendererText()
        cellCountryc   = gtk.CellRendererText()
        cellTimezone   = gtk.CellRendererText()
        
        #add cells to columns 
        tvcIp.pack_start(cellIp, True)
        tvcLat.pack_start(cellLat, True)
        tvcLon.pack_start(cellLon, True)
        tvcCity.pack_start(cellCity, True)
        tvcRegion.pack_start(cellRegion, True)
        tvcRegname.pack_start(cellRegname, True)
        tvcCountry.pack_start(cellCountry, True)
        tvcCountryc.pack_start(cellCountryc, True)
        tvcTimezone.pack_start(cellTimezone, True)
        
        #set properties for rows (text/background)
        tvcIp.set_attributes(cellIp, text=0)
        tvcLat.set_attributes(cellLat, text=1)
        tvcLon.set_attributes(cellLon, text=2)
        tvcCity.set_attributes(cellCity, text=3)
        tvcRegion.set_attributes(cellRegion, text=4)
        tvcRegname.set_attributes(cellRegname, text=5)
        tvcCountry.set_attributes(cellCountry, text=6)
        tvcCountryc.set_attributes(cellCountryc, text=7)
        tvcTimezone.set_attributes(cellTimezone, text=8)
        
        #make treeview sortable
        tvcIp.set_sort_column_id(0)
        tvcLat.set_sort_column_id(1)
        tvcLon.set_sort_column_id(2)
        tvcCity.set_sort_column_id(3)
        tvcRegion.set_sort_column_id(4)
        tvcRegname.set_sort_column_id(5)
        tvcCountry.set_sort_column_id(6)
        tvcCountryc.set_sort_column_id(7)
        tvcTimezone.set_sort_column_id(8)
        
        treeview.set_reorderable(0)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.add(treeview)

#        # Refresh button
#        refreshbt = gtk.Button("refresh")
#        refreshbt.connect("clicked", self.refreshButton)

        vbox = gtk.VBox(False, 0)
#        vbox.pack_start(refreshbt, False, True, 0)
        vbox.pack_start(scrolledwindow, True, True, 0)
        return vbox

#    def refreshButton(self, widget):
#    # Callback function for the refresh button
#        self.liststore = self.refreshListstore(self.liststore)
#        ### update the liststore
#        return
    
    def refreshListstore(self, list):
    # Takes an liststore object and fills it with the data
        self.liststore.clear()
        for ip in self.geodata:
            self.liststore.append([str(ip['ip']), str(ip['lat']), str(ip['lon']), str(ip['city']), str(ip['region']), str(ip['regname']),  \
                                   str(ip['country']), str(ip['countryc']), str(ip['timezone'])])
        return self.liststore
