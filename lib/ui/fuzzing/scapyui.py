##      scapyui.py
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

import gtk
import gobject
import threading

from scapy.all import *

class ScapyUI(gtk.Frame):
    def __init__(self, ip_entry, port_entry):
        super(ScapyUI,self).__init__()

        self.send = True
        self.ip_entry = ip_entry
        self.port_entry = port_entry

        self.label = gtk.Label()
        quote = "<b>Scapy Fuzzer</b>"
        self.label.set_markup(quote)
        self.set_label_widget(self.label)

        # VBox to add panels and buttons
        self.vbox = gtk.VBox(False, 2)

        # HBox to add panels
        self.panels_hbox = gtk.HBox(False, 10)

        # File selector
        self.info_hbox = gtk.HBox(False, 2)
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.file_label = gtk.Label('Step 2: Select the directory to save sent packages:')
        self.file_label.set_padding(0, 3)
        self.info_hbox.pack_start(self.info, False, False, 2)
        self.info_hbox.pack_start(self.file_label, False, False, 2)

        self.vbox.pack_start(self.info_hbox, False, False, 2)

        self.filechooserbutton = gtk.FileChooserButton('Select a directory', backend=None)
        self.filechooserbutton.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)

        self.vbox.pack_start(self.filechooserbutton, False, False, 2)

        # Information label, icon and HBox
        self.info_hbox = gtk.HBox(False, 2)
        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 3: Add the layers that you want to fuzz on to the right column:')
        self.desc_label.set_padding(0, 4)
        self.info_hbox.pack_start(self.info, False, False, 2)
        self.info_hbox.pack_start(self.desc_label, False, False, 2)

        # Panels
        #

        # Scapy layers panel
        self.layers_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.layers_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Scapy layers Treeview
        self.layers_store = gtk.ListStore(str)
        self.layers_tv = gtk.TreeView(self.layers_store)
        self.layers_tv.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_resizable(True)
        self.layers_tv.append_column(column)
        self.layers_tv.set_model(self.layers_store)

        self.layers_sw.add(self.layers_tv)

        # Selected layers Treeview
        self.selected_sw = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.selected_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.selected_store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN)
        self.selected_tv = gtk.TreeView(self.selected_store)
        self.selected_tv.set_rules_hint(True)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Selected Layers", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_clickable(False)
        self.selected_tv.append_column(column)

        self.toggle_column = gtk.TreeViewColumn("Fuzz")
        self.toggle_column.set_expand(False)
        self.toggle = gtk.CellRendererToggle()
        self.toggle.set_property('activatable', True)
        self.toggle.connect('toggled', self.activatePlugin)
        self.toggle_column.pack_start(self.toggle, False)
        self.toggle_column.add_attribute(self.toggle, "active", 1)
        self.toggle_column.add_attribute(self.toggle, "inconsistent", 2)
        self.selected_tv.append_column(self.toggle_column)

        self.selected_tv.set_model(self.selected_store)

        self.selected_sw.add_with_viewport(self.selected_tv)

        # Treeviews Drag and Drop stuff
        self.layers_tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("text/plain", gtk.TARGET_SAME_APP, 80)], gtk.gdk.ACTION_COPY)
        self.layers_tv.connect("drag-data-get", self.drag_data_get_cb)

        self.selected_tv.enable_model_drag_dest([("text/plain", 0, 80)], gtk.gdk.ACTION_COPY)
        self.selected_tv.drag_source_set(gtk.gdk.BUTTON1_MASK, [("text/plain", gtk.TARGET_SAME_APP, 80)], gtk.gdk.ACTION_MOVE)
        #self.selected_tv.connect("drag-begin", self.drag_selected_begin_cb)
        #self.selected_tv.connect("drag-end", self.drag_selected_end_cb)
        self.selected_tv.connect("drag-data-received", self.drag_data_received_cb)


        self.hseparator = gtk.HSeparator()

        #
        # Start/stop buttons and HBox

        # HBoxes for buttons
        self.buttons_hbox = gtk.HBox(False, 3)
        self.buttons_left_hbox = gtk.HBox(False, 3)
        self.buttons_right_hbox = gtk.HBox(True, 1)

        self.info = gtk.Image()
        self.info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.desc_label = gtk.Label('Step 4: Start fuzzing!')
        self.desc_label.set_padding(0, 4)
        self.buttons_left_hbox.pack_start(self.info, False, False, 2)
        self.buttons_left_hbox.pack_start(self.desc_label, False, False, 2)

        # Start/stop buttons
        self.start = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_PLAY)
        self.start_image = gtk.Image()
        self.start_image.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
        self.start.set_size_request(60, 30)
        self.start.connect('clicked', self.get_active_plugins)
        self.stop = gtk.Button(label=None, stock=gtk.STOCK_MEDIA_STOP)
        self.stop.set_size_request(60, 30)
        self.stop.connect('clicked', self.stop_fuzzing)

        # Remove labels from buttons... sigh
        label = self.start.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')
        label = self.stop.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')

        self.buttons_right_hbox.add(self.start)
        self.buttons_right_hbox.add(self.stop)
        self.halign = gtk.Alignment(0.97, 0, 0, 0)
        self.halign.add(self.buttons_right_hbox)

        self.buttons_hbox.pack_start(self.buttons_left_hbox)
        self.buttons_hbox.pack_start(self.halign)

        # Throbber image
        self.throbber = gtk.Image()
        self.img_path = 'lib' + os.sep + 'ui' + os.sep + 'data' + os.sep
        self.throbber.set_from_file(self.img_path + 'throbber_animat_small.gif')

        # Delete button
        self.del_icon = gtk.Image()
        self.del_icon.set_padding(5, 5)
        self.del_icon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_SMALL_TOOLBAR)

        # Delete button drag and drop stuff
        self.del_icon.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP, [ ( "text/plain", gtk.TARGET_SAME_APP, 80) ], gtk.gdk.ACTION_MOVE)
        self.del_icon.connect("drag_drop", self.drag_drop_cb)
        #self.del_icon.set_no_show_all(True)
        #self.del_icon.hide()

        self.eb = gtk.EventBox()
        #self.eb.set_no_show_all(True)
        #self.eb.hide()
        self.eb.add(self.del_icon)
        self.eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#d9e4f2'))

        self.right_vbox = gtk.VBox(False, 0)
        self.right_vbox.pack_start(self.selected_sw, True, True, 1)
        self.right_vbox.pack_start(self.eb, False, False, 1)

        # Add panels and buttons
        self.panels_hbox.pack_start(self.layers_sw, True, True, 1)
        self.panels_hbox.pack_start(self.right_vbox, True, True, 1)

        self.vbox.pack_start(self.info_hbox, False, False, 2)
        self.vbox.pack_start(self.panels_hbox, True, True, 1)
        self.vbox.pack_start(self.hseparator, False, False, 3)
        self.vbox.pack_start(self.buttons_hbox, False, False, 3)

        self.add(self.vbox)

        self.get_layers()

    ###############################
    # Drag and drop related methods

    def drag_drop_cb(self, button, context, x, y, timestamp):
        selection = self.selected_tv.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
        return

#    def drag_selected_begin_cb(self, treeview, context):
#        self.eb.show()
#        self.del_button.show()
#
#    def drag_selected_end_cb(self, treeview, context):
#        self.eb.hide()
#        self.del_button.hide()

    def drag_data_get_cb(self, treeview, context, selection, info, timestamp):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        text = model.get_value(iter, 0)
        selection.set('text/plain', 8, text)
        return

    def drag_data_received_cb(self, treeview, context, x, y, selection, info, timestamp):
        obj = eval(selection.data)

        layers = {}
        layers[selection.data] = []

        if isinstance(obj, type) and issubclass(obj, Packet):
            for f in obj.fields_desc:
                layers[selection.data].append(str(f.name))
            self.add_layer(layers)

    ##################################
    # Packet creation and send methods

    def activate(self, cell, path, model):
        model[path][1] = not model[path][1]
        return

    def stop_fuzzing(self, widget):

        self.send = False

        # Change start button image
        self.start.set_image(self.start_image)
        self.start.set_use_stock(True)
        label = self.start.get_children()[0]
        label = label.get_children()[0].get_children()[1]
        label = label.set_label('')

    def activatePlugin(self, cell, path):
        '''Handles the plugin activation/deactivation.

        @param cell: the cell that generated the signal.
        @param path: the path that clicked the user.

        When a child gets activated/deactivated, the father is also refreshed
        to show if it's full/partially/not activated. 

        If the father gets activated/deactivated, all the children follow the
        same fate.
        '''

        treerow = self.selected_store[path]

        # invert the active state and make it consistant
        newvalue = not treerow[1]
        treerow[1] = newvalue
        treerow[2] = False

        # path can be "?" if it's a father or "?:?" if it's a child
        if ":" not in path:
            # father: let's change the value of all children
            for childtreerow in self.get_children(path):
                if childtreerow[0] == "gtkOutput":
                    childtreerow[1] = True
                    if newvalue is False:
                        # we're putting everything in false, except this plugin
                        # so the father is inconsistant
                        treerow[2] = True
                else:
                    childtreerow[1] = newvalue
        else:
            # child: let's change the father status
            pathfather = path.split(":")[0]
            father = self.selected_store[pathfather]
            vals = []
            for treerow in self.get_children(pathfather):
                vals.append(treerow[1])
            if all(vals):
                father[1] = True
                father[2] = False
            elif not any(vals):
                father[1] = False
                father[2] = False
            else:
                father[2] = True

    def get_children(self, path):
        '''Finds the children of a path.

        @param path: the path to find the children.
        @return Yields the childrens.
        '''

        father = self.selected_store.get_iter(path)
        howmanychilds = self.selected_store.iter_n_children(father)
        for i in range(howmanychilds):
            child = self.selected_store.iter_nth_child(father, i)
            treerow = self.selected_store[child]
            yield treerow

    def get_active_plugins(self, widget):
        '''Return the activated plugins.

        @return: all the plugins that are active.
        '''

        self.target = self.ip_entry.get_text()
        self.port = self.port_entry.get_text()

        if not self.target or not self.port:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "Fill IP address and Port entries")
            md.run()
            md.destroy()
        else:
            self.bottom_nb.set_current_page(0)
            self.dest_dir = self.filechooserbutton.get_filename()

            result = {}
            for row in self.selected_store:
                father = self.selected_store.get_iter(row.path)
                layer = self.selected_store[father][0].strip()
                result[layer] = []
                for childrow in self.get_children(row.path):
                    if childrow[1]:
                        result[layer].append(childrow[0])
            if result:
                self.send = True
                # Change start button image
                self.start.set_image(self.throbber)
                label = self.start.get_children()[0]
                label = label.get_children()[0].get_children()[1]
                label = label.set_label('')
    
                self.compose_packet(result)
            else:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "First drag some layers to the right tree")
                md.run()
                md.destroy()

    def compose_packet(self, fuzzeables):
        # create the packet object
        packet = ''
        self.fields = []

        for layer in fuzzeables.keys():
            # Add destination
            if layer == 'IP':
                packet += layer + '(dst="' + self.target + '")/'
            # Add port
            elif layer in ['TCP', 'UDP']:
                packet += layer + '(dport=' + self.port + ')/'
            else:
                packet += layer + '()/'

            self.fields.extend(fuzzeables[layer])
        packet = eval(packet[:-1])
        packet = self.fuzz_packet(packet)
        self.srloop(packet)

    def fuzz_packet(self, packet, _inplace=0):
        # add fuzz values to selected fields 
        if not _inplace:
            packet = packet.copy()
        q = packet
        while not isinstance(q, NoPayload):
            for field in q.fields_desc:
                # Just fuzz selected fields
                if field.name in self.fields:
                    if isinstance(field, PacketListField):
                        for attribute in getattr(q, field.name):
                            print "fuzzing", repr(attribute)
                            fuzz(attribute, _inplace=1)
                    elif field.default is not None:
                        rnd = field.randval()
                        if rnd is not None:
                            q.default_fields[field.name] = rnd
            q = q.payload
        return packet

    def add_layer(self, layers):
        for layer in layers.keys():
            parent = self.selected_store.append( None, (layer, None, None) )
            for element in layers[layer]:
                self.selected_store.append( parent, (element, None, None) )

    def get_layers(self):

        import __builtin__
        all = __builtin__.__dict__.copy()
        all.update(globals())
        objlst = sorted(conf.layers, key=lambda x:x.__name__)
        for o in objlst:
            short = "%-10s" % (o.__name__)
            #long = "%s" % (o.name)
            iter = self.layers_store.append([short])

    def srloop(self, pkts, *args, **kargs):
        """Send a packet at layer 3 in loop and print the answer each time
    srloop(pkts, [prn], [inter], [count], ...) --> None"""

        if not self.gom:
            self.gom = gom

        t = threading.Thread(target=self.__sr_loop, args=(sr, pkts))
        t.start()
        #return self.__sr_loop(sr, pkts, *args, **kargs)

    def __sr_loop(self, srfunc, pkts, prn=lambda x:x[1].summary(), prnfail=lambda x:x.summary(), inter=1, timeout=None, count=None, verbose=None, store=1, *args, **kargs):
        verbose = 2
        count = None
        n = 0
        r = 0
        ct = conf.color_theme
        if verbose is None:
            verbose = conf.verb
        parity = 0
        ans=[]
        unans=[]
        if timeout is None:
            timeout = min(2*inter, 5)
        try:
            while self.send:
                parity ^= 1
                col = [ct.even,ct.odd][parity]
                if count is not None:
                    if count == 0:
                        break
                    count -= 1
                start = time.time()
                res = srfunc(pkts, timeout=timeout, verbose=0, chainCC=1, *args, **kargs)
                n += len(res[0])+len(res[1])
                r += len(res[0])
                if verbose > 1 and prn and len(res[0]) > 0:
                    msg = "RECV %i:\t" % len(res[0])
                    self.gom.echo(  ct.success(msg), newline=False )
                    for p in res[0]:
                        self.gom.echo( col(prn(p)) )
                        self.gom.echo( " "*len(msg) )
                if verbose > 1 and prnfail and len(res[1]) > 0:
                    msg = "Fail %i:\t" % len(res[1])
                    self.gom.echo( ct.fail(msg), newline=False )
                    for p in res[1]:
                        self.gom.echo( col(prnfail(p)) )
                        self.gom.echo( " "*len(msg) )
                if verbose > 1 and not (prn or prnfail):
                    self.gom.echo( "recv:%i  fail:%i" % tuple(map(len, res[:2])) )
                if store:
                    ans += res[0]
                    unans += res[1]
                end=time.time()
                if end-start < inter:
                    time.sleep(inter+start-end)
        except KeyboardInterrupt:
            pass
     
        if verbose and n>0:
            self.gom.echo( ct.normal("\nSent %i packets, received %i packets. %3.1f%% hits." % (n,r,100.0*r/n)) )

        # Convert tuples to list to write to pcap
        list_ans = []
        for x in ans:
            for y in x:
                list_ans.append(y)

        if unans:
            wrpcap(self.dest_dir + os.sep + self.target + '-' + self.port + '-unans.pcap', unans)
            self.gom.echo("\nUnanswered packets saved as:\t" + self.dest_dir + os.sep + self.target + '-' + self.port + '-unans.pcap')
        if ans:
            wrpcap(self.dest_dir + os.sep + self.target + '-' + self.port + '-ans.pcap', list_ans)
            self.gom.echo("Answered packets saved as:\t\t" + self.dest_dir + os.sep + self.target + '-' + self.port + '-ans.pcap')
