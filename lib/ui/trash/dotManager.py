##      dotManager.py
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

import sys
import lib.ui.trace_route_combine as tc

class TCombiner:
    '''Object to handle traceroute results and dot graphs'''

    def __init__(self):

        self.t = tc.TracerouteCollection()

#    def get_first_dot(self, localip, gw):
#        '''Creates initial dot for local ip -> gw'''
#
#        print "Launch Traceroute against", gw
#        ans,unans = tc.traceroute(gw)
#        print "TC result", ans
#        self.t.add_route(ans)

    def add_trace(self, ans):
        '''Adds new traceroute to collection'''

        self.t.add_route(ans)

    def get_graph(self):
        '''Generates the dot code'''

        return self.t.build_graph()

    def get_paths(self):
        '''get paths to all the trace routed hosts'''

        return self.t.get_paths_to_hosts()
