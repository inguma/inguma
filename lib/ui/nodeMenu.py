##      nodeMenu.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
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

import gtk

from . import discover_dialog
from . import bruteDialog
from . import gather_dialog
from . import config
from . import reportWin

class UIManager(gtk.UIManager):

    def __init__(self, gom, core, config):
        gtk.UIManager.__init__(self)

        self.ui_id = 0
        self.gom = gom
        self.uicore = core

        # Add the accelerator group
        self.accel = self.get_accel_group()

        # Create an ActionGroup
        self.actiongroup = gtk.ActionGroup('Base')

        # Parse config file
        categories = getattr(config, 'categories')
        subdiscovers = getattr(config, 'subdiscovers')
        subgathers = getattr(config, 'gathers')

        self.menu_base = ''
        for category in categories:

            #Create menu for category

            self.menu_base += '<menu action="' + category.capitalize() + '">'
            self.actiongroup.add_actions( [(category.capitalize(), gtk.STOCK_EXECUTE, '  ' + category.capitalize())] )

            #print category
            subcategories = getattr(config, 'sub' + category)
            for subcat in subcategories.keys():
                self.menu_base += '<menu action="' + subcat + '">'
                self.actiongroup.add_actions( [(subcat, None, '  ' + subcat.capitalize() + '  ')] )
                #print '\t' + subcat

                for element in subcategories[subcat]:
                    self.menu_base += '<menuitem action="' + element + '">'
                    if category == 'discovers':
                        # xml_name, icon, real_menu_text, accelerator, tooltip, callback
                        self.actiongroup.add_actions([(element, gtk.STOCK_QUIT, element, None, element, self.showDialog)])
                    elif category == 'gathers':
                        self.actiongroup.add_actions([(element, gtk.STOCK_QUIT, element, None, element, self.showGather)])

                    self.menu_base += '</menuitem>'
                    #print '\t\t' + element
                self.menu_base += '</menu>'

            self.menu_base += '</menu>'

        self.menu_base += '''</popup>
        </ui>'''

        self.insert_action_group(self.actiongroup, 0)

    # Functions

    def set_data(self, ip=None):
        ''' called on click to prepend target info on the popup menu'''

        self.ip = ip

        if self.get_uiID() != 0:
            self.remove_ui(self.ui_id)
        # Empty target_menu
        self.target_menu = '''<ui>
        <popup name="Popup">
        '''

        if not ip:
            self.actiongroup2 = gtk.ActionGroup('Target')

            self.target_menu += self.menu_base
    
            # Add the actiongroup to the uimanager
            self.insert_action_group(self.actiongroup2, 0)
        else:
            self.remove_action_group(self.actiongroup2)
            self.actiongroup2 = gtk.ActionGroup('Target')

            kb = self.uicore.get_kbList()

            # Add menu elements in reverse order to be shown correctly    
            # Target Services
            self.actiongroup2.add_actions( [('services', gtk.STOCK_NETWORK, '  Services')] )
            self.target_menu += '<menu action="services" position="top">'

            if kb.__contains__(ip + '_tcp_ports'):
                for port in kb[ip + '_tcp_ports']:

#                    if kb.__contains__(ip + '_passwords'):
#                        self.actiongroup2.add_actions( [('pass', None, 'user/password')] )
#                        self.target_menu += '<menuitem action="pass">'
#
#                        self.actiongroup2.add_actions( [(kb[ip + 'passwords'], None, str(kb[ip + 'passwords']))] )
#                        self.target_menu += '<menuitem action="' + kb[ip + '_passwords'] + '">'

                    self.actiongroup2.add_actions( [(str(port), None, str(port))] )
                    self.target_menu += '<menu action="' + str(port) + '">'

                    # Menuitems for connect and browser
                    self.actiongroup2.add_actions( [(str(port) + '_browser', gtk.STOCK_YES, 'Open with browser', None, None, self.show_browser)], [str(port), ip] )
                    self.target_menu += '<menuitem action="' + str(port) + '_browser"/>'
                    self.actiongroup2.add_actions( [(str(port) + '_connect', gtk.STOCK_CONNECT, 'Open with terminal', None, None, self.open_terminal)], [str(port), ip] )
                    self.target_menu += '<menuitem action="' + str(port) + '_connect"/>'

                    # Add web vulns...
                    if kb.__contains__(ip + "_" + str(port) + '-web-vulns'):
                        #print "* We have port %s with vulns!" % port
                        # Menu for vulnerabilities
                        self.actiongroup2.add_actions( [(str(port) + '_vulns', gtk.STOCK_DIALOG_WARNING, 'Vulns')] )
                        self.target_menu += '<menu action="' + str(port) + '_vulns' + '">'

                        # Menuitems for each vuln
                        vuln_id = 0
                        for vuln in kb[ip + '_' + str(port) + '-web-vulns']:
                            self.actiongroup2.add_actions( [(str(port) + '_' + vuln[0] + str(vuln_id), gtk.STOCK_YES, 'OSVDB:' + vuln[0] + ' ' + vuln[1], None, None, self.show_browser)], [str(port), ip, vuln[1]] )
                            self.target_menu += '<menuitem action="' + str(port) + '_' + vuln[0] + str(vuln_id) + '"/>'
                            vuln_id += 1
                        self.target_menu += '</menu>'

                    # Add services info
                    if kb.__contains__(ip + "_" + str(port) + '-info'):
                        #print "* We have port %s with info!" % port
                        # Menu for service info
                        self.actiongroup2.add_actions( [(str(port) + '_info', gtk.STOCK_INFO, 'Info')] )
                        self.target_menu += '<menu action="' + str(port) + '_info' + '">'

                        # Menuitems for each info
                        for info in kb[ip + '_' + str(port) + '-info']:
                            self.actiongroup2.add_actions( [(str(port) + '_' + info, gtk.STOCK_YES, info, None, None, None)]  )
                            self.target_menu += '<menuitem action="' + str(port) + '_' + info + '"/>'
                        self.target_menu += '</menu>'

                    # Menu for brute modules
                    self.actiongroup2.add_actions( [(str(port) + '_brutes', None, 'Bruteforce')] )
                    self.target_menu += '<menu action="' + str(port) + '_brutes' + '">'
                    #Brute menuitems for each module
                    for brute in getattr(config, 'brutes'):
                        id = ip + '_' + str(port) + '_' + brute
                        self.actiongroup2.add_actions( [(id, gtk.STOCK_REFRESH, 'Brute ' + brute.split('brute')[-1].upper(), None, "tooltip", \
self.showBrute )], user_data=[ip, port] )
                        self.target_menu += '<menuitem action="' + id + '"/>'
                    self.target_menu += '</menu>'
                    self.target_menu += '</menu>'
                        

#            elif kb.__contains__(ip + '_tcp_ports'):
#                for port in kb[ip + '_tcp_ports']:
#
##                    if kb.__contains__(ip + '_passwords'):
##                        self.actiongroup2.add_actions( [('pass', None, 'user/password')] )
##                        self.target_menu += '<menuitem action="pass">'
##
##                        self.actiongroup2.add_actions( [(kb[ip + 'passwords'], None, str(kb[ip + 'passwords']))] )
##                        self.target_menu += '<menuitem action="' + kb[ip + '_passwords'] + '">'
#
#                    self.actiongroup2.add_actions( [(str(port), None, str(port))] )
#                    self.target_menu += '<menu action="' + str(port) + '">'
#    
#                    for brute in getattr(config, 'brutes'):
#                        id = ip + '_' + str(port) + '_' + brute
#                        self.actiongroup2.add_actions( [(id, gtk.STOCK_REFRESH, 'Brute ' + brute.split('brute')[-1].upper(), None, "tooltip", \
#self.showBrute )], user_data=[ip, port] )
#                        self.target_menu += '<menuitem action="' + id + '"/>'
#                    self.target_menu += '</menu>'
                        
            self.target_menu += '</menu><separator/>'

            self.target_menu += '<menuitem action="Fuzz"/>'
            self.actiongroup2.add_actions([('Fuzz', gtk.STOCK_EXECUTE, '  Fuzz target', None, 'Fuzz target', self._fuzz_target)], user_data=[ip])

            # Add target's information
            self.actiongroup2.add_actions( [('Information', gtk.STOCK_INFO, '  Information')] )
            self.target_menu += '<menu action="Information" position="top">'

            if kb.__contains__(ip + '_name'):
                # Host name 
                self.actiongroup2.add_actions( [('host', None, 'Host Name')] )
                self.target_menu += '<menuitem action="host"/>'
                self.actiongroup2.add_actions( [('name', None, kb[ip + '_name'][0] )] )
                self.target_menu += '<menuitem action="name"/><separator/>'

            if kb.__contains__(ip + '_asn'):
                # ASN Information
                self.actiongroup2.add_actions( [('asname', None, 'ASN')] )
                self.target_menu += '<menuitem action="asname"/>'
                self.actiongroup2.add_actions( [('tasn', None, kb[ip + '_asn'][-1] )] )
                self.target_menu += '<menuitem action="tasn"/><separator/>'
    
            if kb.__contains__(ip + '_os'):
                # OS Information
                self.actiongroup2.add_actions( [('osname', None, 'OS')] )
                self.target_menu += '<menuitem action="osname"/>'
                self.actiongroup2.add_actions( [('tos', None, kb[ip + '_os'][-1] )] )
                self.target_menu += '<menuitem action="tos"/><separator/>'
    
            self.target_menu += '</menu>'
    
            # Add target's report button
            self.actiongroup2.add_actions( [('Report', gtk.STOCK_INFO, '  Report', None, None, self.showReport )], user_data=[ip] )
            self.target_menu += '<menuitem action="Report" position="top"/>'
   
            # Add IP Address
            self.actiongroup2.add_actions( [(ip, None, '  ' + ip + '  ')] )
            self.target_menu += '<menuitem action="' + ip + '" position="top">'
            self.target_menu += '</menuitem>'
    
            self.target_menu += self.menu_base

            # Add the actiongroup to the uimanager
            self.insert_action_group(self.actiongroup2, 0)

        # Menu
        ui_id = self.add_ui_from_string(self.target_menu)
        self.set_uiID(ui_id)
        self.popmenu = self.get_widget('/Popup')

    def _fuzz_target(self, widget, data):
        self.notebook.set_current_page(3)
        exploits_nb = self.notebook.get_children()[3]
        exploits_nb.set_current_page(1)
        self.fuzz_frame.ip_entry.set_text(data[0])

    def set_uiID(self, id):
        self.ui_id = id

    def get_uiID(self):
        return self.ui_id

    def show_browser(self, action, data):
        from webbrowser import open_new

        if 'poc_' in data:
            open_new(data.split('poc_')[1])
        elif len(data) == 3:
            port, ip, vuln = data
            open_new('http://' + ip + ':' + port + vuln)
        elif len(data) == 2:
            port, ip = data
            open_new('http://' + ip + ':' + port)
        else:
            open_new('http://osvdb.org/show/osvdb/' + data)

    def open_terminal(self, action, data):
        if config.HAS_VTE:
            port, ip = data
            command = 'tools/nc'
            self.termnb.new_tab(command, [command, ip, port])
            self.mainnb.set_current_page(1)

    def showDialog(self, action):
        module = action.get_name()
        tg = discover_dialog.DiscoverDialog(module, self.uicore)

    def showGather(self, action):
        module = action.get_name()
        inputs = getattr(config, module)

        if type(inputs) == dict:
            exec 'import ' + inputs.keys()[0]
            dialog = eval(inputs.keys()[0] + '.' + inputs.values()[0] + '(ip=\'' + str(self.ip) + '\')')
            setattr(dialog, 'uicore', self.uicore)
            setattr(dialog, 'gom', self.gom)
            setattr(dialog, 'module', module)
        elif not inputs:
            tg = gather_dialog.GatherDialog(module, gtk.STOCK_NEW, ["target", "port", "timeout"], self.uicore)
        else:
            tg = gather_dialog.GatherDialog(module, gtk.STOCK_NEW, inputs, self.uicore)

    def showBrute(self, action, params):
        module = action.get_name().split('_')[-1]
        inputs = getattr(config, module)
        defaults = ["target", "port", "user"]

        if not inputs:
            tg = bruteDialog.BruteDialog(module, gtk.STOCK_NEW, defaults, self.uicore, params)
        else:
            for input in inputs:
                defaults.append(input)
            tg = bruteDialog.BruteDialog(module, gtk.STOCK_NEW, defaults, self.uicore, params)

    def showReport(self, action, host):
        #print "Generating report for host:", host[0]
        reportWin.reportWin(self.uicore, host[0])
