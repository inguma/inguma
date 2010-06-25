##       inxdot.py
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
import gtk.gdk

import sys
import xdot

class MyDotWidget(xdot.DotWidget):
    '''Working'''

    def __init__(self, cmenu, gmenu, core):
        self.context = cmenu
        self.graph_menu = gmenu
        self.core = core
        xdot.DotWidget.__init__(self)
#        self.set_filter('twopi')

    def on_area_button_release(self, area, event):
        if event.button == 3:
            x, y = int(event.x), int(event.y)
            url = self.get_url(x, y)
            if url is not None:
                self.core.set_kbfield('target', url.url)

            else:
                self.graph_menu.popmenu.popup(None, None, None, 1, event.time)
                
            jump = self.get_jump(x, y)
            if jump is not None:
                #Right Click on Node!!
                self.context.set_data(url.url)
                self.context.popmenu.popup(None, None, None, 1, event.time)

        else:
            super(MyDotWidget, self).on_area_button_release(area, event)

    def do_expose_event(self, event):
        cr = self.window.cairo_create()

        # set a clip region for the expose event
        cr.rectangle(
            event.area.x, event.area.y,
            event.area.width, event.area.height
        )
        cr.clip()

        cr.set_source_rgba(0.278, 0.337, 0.447, 255)
        #cr.set_source_rgba(0.0, 0.0, 0.0, 0.804)
        cr.paint()

        cr.save()
        rect = self.get_allocation()
        cr.translate(0.5*rect.width, 0.5*rect.height)
        cr.scale(self.zoom_ratio, self.zoom_ratio)
        cr.translate(-self.x, -self.y)

        self.graph.draw(cr, highlight_items=self.highlight)
        cr.restore()

        self.drag_action.draw(cr)

        return False
