##      libTerminal.py
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

import pygtk
import gtk, gobject, pango
import lib.ui.config as config

if config.HAS_VTE:
    import vte

#global variables
window = None
notebook = None

class TerminalNotebook(gtk.Notebook):

  def __init__(self):
    gtk.Notebook.__init__(self)
    #set the tab properties
    self.set_property('homogeneous', True)
    #we do not show the tab if there is only one tab i total
#    self.set_property('show-tabs', False) 

  def new_tab(self, command='', args=[]):
    #we create a "Random" image to put in the tab
    #icons = [gtk.STOCK_ABOUT, gtk.STOCK_ADD, gtk.STOCK_APPLY, gtk.STOCK_BOLD] 
    image = gtk.Image()
    nbpages = self.get_n_pages()
    #icon = icons[nbpages%len(icons)]
    icon = gtk.STOCK_EXECUTE
    image.set_from_stock(icon, gtk.ICON_SIZE_DIALOG)
#    self.append_page(image)

    term = vte.Terminal()

    term.set_font(pango.FontDescription('mono 8'))
    if command:
        term.fork_command(command=command, argv=args)
    else:
        term.fork_command()
    term.set_scrollback_lines(500)
    term.set_scroll_on_output = True
    term.connect("child-exited", lambda w: term.destroy())
    term.show_all()

    self.append_page(term)
    
    #we want to show the tabs if there is more than 1
    if nbpages + 1 > 1:
      self.set_property('show-tabs', True)
    #creation of a custom tab. the left image and
    #the title are made of the stock icon name
    #we pass the child of the tab so we can find the
    #tab back upon closure
    #label = self.create_tab_label(icon, image)
    label = self.create_tab_label(command, term)
    label.show_all()
    
    self.set_tab_label_packing(image, True, True, gtk.PACK_START)
    #self.set_tab_label(image, label)
    self.set_tab_label(term, label)
    #image.show_all()
    term.show_all()
    self.set_current_page(nbpages)

  def create_tab_label(self, title, tab_child):
    box = gtk.HBox()
    icon = gtk.Image()
    if title == '':
        icon.set_from_stock('Bash', gtk.ICON_SIZE_MENU)
        label = gtk.Label('Bash')
    else:
        icon.set_from_stock(title, gtk.ICON_SIZE_MENU)
        label = gtk.Label(title)
    closebtn = gtk.Button()
    #the close button is made of an empty button
    #where we set an image
    image = gtk.Image()
    image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    closebtn.connect("clicked", self.close_tab, tab_child)
    closebtn.set_image(image)
    closebtn.set_relief(gtk.RELIEF_NONE)
    box.pack_start(icon, False, False)
    box.pack_start(label, True, True)
    box.pack_end(closebtn, False, False)
    return box

  def close_tab(self, widget, child):
    pagenum = self.page_num(child)
    
    if pagenum != -1:
      self.remove_page(pagenum)
      child.destroy()
