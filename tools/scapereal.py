#! /usr/bin/env python

from scapy import *

try:
    import gobject
    import gtk
    GTK = 1
except ImportError:
    print "WARNING: did not find gtk module. Won't be able to use ethereal"
    GTK = 0

# ethereal-like viewer : only available with GTK
if GTK:

    def ethereal_display(packet, displayer, mid, midspace, end):
        text = ['']
        p = packet.__str__()
        while p != '':
            i, = struct.unpack("B", p[0])
            i = displayer(i)
            l = text[-1].__len__()
            if l == mid:
                text[-1] += midspace + i
            elif l == end:
                text.append(i)
            else:
                text[-1] += i
            p = p[1:]
        return string.join(text, '\n')

    def hexa_displayer(i):
        i = hex(i)[2:] + " "
        if i.__len__() == 2:
            i = "0" + i
        return i

    def ascii_displayer(i):
        if i > 32 and i < 127:
            return struct.pack("B", i)
        else:
            return '.'

    # Parts of the following code come from the pygtk demos

    (
        COLUMN_NO,
        COLUMN_TIME,
        COLUMN_SOURCE,
        COLUMN_DESTINATION,
        COLUMN_PROTO,
        COLUMN_INFO
    ) = range(6)

    class PacketTreeModel(gtk.GenericTreeModel):
        TREE_DEPTH = 2
        def __init__(self, p):
            self.packet = p
            i = 0
            x = p
            while type(x.payload) != NoPayload:
                x = x.payload
                i += 1
            self.TREE_SIBLINGS = i + 1
            gtk.GenericTreeModel.__init__(self)

        def on_get_flags(self):
            return 0
        def on_get_n_columns(self):
            return 1
        def on_get_column_type(self, index):
            return gobject.TYPE_STRING
        def on_get_path(self, node):
            return node
        def on_get_iter(self, path):
            return path
        def on_get_value(self, node, column):
            assert column == 0
            x = self.packet
            for i in range(node[0]):
                x = x.payload
            if len(node) == 1:
                return x.name + " (" + x.mysummary() + ")"
            else:
                f = x.fields_desc[node[1]]
                return f.name + ": " + str(f.i2repr(x,x.__getattr__(f)))
        def on_iter_next(self, node):
            if len(node) == 1:
                TREE_SIBLINGS = self.TREE_SIBLINGS
            else:
                x = self.packet
                for i in range(node[0]):
                    x = x.payload
                f = x.fields_desc
                TREE_SIBLINGS = len(x.fields_desc)
            if node[-1] == TREE_SIBLINGS - 1: # last node at level
                return None
            return node[:-1] +(node[-1]+1,)
        def on_iter_children(self, node):
            if node == None: # top of tree
                return(0,)
            if len(node) >= self.TREE_DEPTH: # no more levels
                return None
            return node +(0,)
        def on_iter_has_child(self, node):
            return len(node) < self.TREE_DEPTH
        def on_iter_n_children(self, node):
            if len(node) < self.TREE_DEPTH:
                return self.TREE_SIBLINGS
            else:
                return 0
        def on_iter_nth_child(self, node, n):
            if node == None:
                return(n,)
            if len(node) < self.TREE_DEPTH and n < self.TREE_SIBLINGS:
                return node +(n,)
            else:
                return None
        def on_iter_parent(self, node):
            if len(node) == 0:
                return None
            else:
                return node[:-1]


    class EtherealViewer(gtk.Window):
        def __init__(self, pl, parent=None):
            gtk.Window.__init__(self)
            try:
                self.set_screen(parent.get_screen())
            except AttributeError:
                self.connect('destroy', lambda *w: gtk.main_quit())

            self.set_title(self.__class__.__name__)
            self.packet_list = pl
            self.begin_time = pl[0].time
            self.set_default_size(-1, 500)
            self.set_border_width(8)

            vbox = gtk.VBox(False, 8)
            self.add(vbox)

            pktlist_sw = gtk.ScrolledWindow()
            pktlist_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            pktlist_sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            pktlist_sw.set_size_request(800,200)
            vbox.pack_start(pktlist_sw, False, False, 0)

            model = self.__create_model(pl)
            pktlist_tv = gtk.TreeView(model)
            pktlist_sw.add(pktlist_tv)

            column = gtk.TreeViewColumn('No', gtk.CellRendererText(),
                                        text=COLUMN_NO)
            column.set_sort_column_id(COLUMN_NO)
            pktlist_tv.append_column(column)

            column = gtk.TreeViewColumn('Time', gtk.CellRendererText(),
                                        text=COLUMN_TIME)
            column.set_sort_column_id(COLUMN_TIME)
            pktlist_tv.append_column(column)

            column = gtk.TreeViewColumn('Source', gtk.CellRendererText(),
                                        text=COLUMN_SOURCE)
            column.set_sort_column_id(COLUMN_SOURCE)
            pktlist_tv.append_column(column)

            column = gtk.TreeViewColumn('Destination', gtk.CellRendererText(),
                                        text=COLUMN_DESTINATION)
            column.set_sort_column_id(COLUMN_DESTINATION)
            pktlist_tv.append_column(column)

            column = gtk.TreeViewColumn('Protocol', gtk.CellRendererText(),
                                        text=COLUMN_PROTO)
            column.set_sort_column_id(COLUMN_PROTO)
            pktlist_tv.append_column(column)

            column = gtk.TreeViewColumn('Info', gtk.CellRendererText(),
                                        text=COLUMN_INFO)
            column.set_sort_column_id(COLUMN_INFO)
            pktlist_tv.append_column(column)


            model = PacketTreeModel(pl[0])
            pkt_tv = gtk.TreeView(model)
            pkt_tv.set_headers_visible(False)
            self.pkt_tv = pkt_tv

            pkt_sw = gtk.ScrolledWindow()
            pkt_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            pkt_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            pkt_sw.set_size_request(800,200)
            pkt_sw.add(pkt_tv)
            self.pkt_sw = pkt_sw

            cell = gtk.CellRendererText()
            column = gtk.TreeViewColumn("tuples", cell, text=0)
            pkt_tv.append_column(column)

            vbox.pack_start(pkt_sw, False, False, 0)

            hbox = gtk.HBox(False, 8)
            vbox.pack_end(hbox, False, False, 0)

            pkthexa_tv = gtk.TextView()
            pkthexa_buf = pkthexa_tv.get_buffer()
            pkthexa_buf.create_tag("monospace", family="monospace")
            pkthexa_buf.create_tag("red", background="red")
            pkthexa_buf.set_text(ethereal_display(pl[0], hexa_displayer, 24, " " * 3, 51))
            start, end = pkthexa_buf.get_bounds()
            pkthexa_buf.apply_tag_by_name("monospace", start, end)
            self.pkthexa_tv = pkthexa_tv

            pkthexa_sw = gtk.ScrolledWindow()
            pkthexa_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            pkthexa_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            pkthexa_sw.set_size_request(498,200)
            pkthexa_sw.add(pkthexa_tv)
            self.pkthexa_sw = pkthexa_sw

            hbox.pack_start(pkthexa_sw, False, False, 0)

            pktascii_tv = gtk.TextView()
            pktascii_buf = pktascii_tv.get_buffer()
            pktascii_buf.create_tag("monospace", family="monospace")
            pktascii_buf.create_tag("red", background="red")
            pktascii_buf.set_text(ethereal_display(pl[0], ascii_displayer, 8, " ", 17))
            start, end = pktascii_buf.get_bounds()
            pktascii_buf.apply_tag_by_name("monospace", start, end)
            self.pktascii_tv = pktascii_tv

            pktascii_sw = gtk.ScrolledWindow()
            pktascii_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            pktascii_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            pktascii_sw.set_size_request(298,200)
            pktascii_sw.add(pktascii_tv)
            self.pktascii_sw = pktascii_sw

            hbox.pack_end(pktascii_sw, False, False, 0)

            pktlist_sel = pktlist_tv.get_selection()
            pktlist_sel.set_mode(gtk.SELECTION_SINGLE)
            pktlist_sel.connect("changed", self.on_pktlist_sel_changed)

            pkt_sel = pkt_tv.get_selection()
            pkt_sel.set_mode(gtk.SELECTION_SINGLE)
            pkt_sel.connect("changed", self.on_pkt_sel_changed)

            self.show_all()


        def __create_model(self, pl):
            lstore = gtk.ListStore(
                gobject.TYPE_INT,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)
            i = 1
            for p in pl:
                iter = lstore.append()
                proto = p.lastlayer().name
                try:
                    if proto == 'Padding':
                        proto = p.lastlayer().underlayer.name
                    if proto == 'Raw':
                        proto = p.lastlayer().underlayer.name
                except:
                    proto = 'Unknown'
                if p.haslayer(IP):
                    lstore.set(iter,
                               0, i,
                               1, p.time - self.begin_time,
                               2, p.getlayer(IP).src,
                               3, p.getlayer(IP).dst,
                               4, proto,
                               5, p.summary())
                elif p.haslayer(Ether):
                    lstore.set(iter,
                               0, i,
                               1, p.time - self.begin_time,
                               2, p.getlayer(Ether).src,
                               3, p.getlayer(Ether).dst,
                               4, proto,
                               5, p.summary())
                else:
                    lstore.set(iter,
                               0, i,
                               1, p.time - self.begin_time,
                               2, "Unknown",
                               3, "Unknown",
                               4, proto,
                               5, p.summary())
                i += 1
            return lstore

        def on_pktlist_sel_changed(self, selection):
            pl = self.packet_list
            pktlist_tv = selection.get_tree_view()
            model, iter = selection.get_selected()

            if iter:
                no = model.get_value(iter, 0)

                model = PacketTreeModel(pl[int(no) - 1])
                pkt_tv = gtk.TreeView(model)
                pkt_tv.set_headers_visible(False)
                self.pkt_sw.remove(self.pkt_tv)
                self.pkt_tv.destroy()
                self.pkt_sw.add(pkt_tv)
                pkt_tv.show()
                self.pkt_sw.show()
                cell = gtk.CellRendererText()
                column = gtk.TreeViewColumn("tuples", cell, text=0)
                pkt_tv.append_column(column)
                self.pkt_tv = pkt_tv
            
                pkt_sel = pkt_tv.get_selection()
                pkt_sel.set_mode(gtk.SELECTION_SINGLE)
                pkt_sel.connect("changed", self.on_pkt_sel_changed)

                pkthexa_buf = self.pkthexa_tv.get_buffer()
                pkthexa_buf.set_text(ethereal_display(pl[int(no)-1], hexa_displayer, 24, " " * 3, 51))
                start, end = pkthexa_buf.get_bounds()
                pkthexa_buf.apply_tag_by_name("monospace", start, end)

                pktascii_buf = self.pktascii_tv.get_buffer()
                pktascii_buf.set_text(ethereal_display(pl[int(no)-1], ascii_displayer, 8, " ", 17))
                start, end = pktascii_buf.get_bounds()
                pktascii_buf.apply_tag_by_name("monospace", start, end)

        def on_pkt_sel_changed(self, selection):
            pkt_tv = selection.get_tree_view()
            model, iter = selection.get_selected()
            if iter:
                x = model.packet
                path = model.get_path(iter)
                total_len = len(x)
                for i in range(path[0]):
                    x = x.payload
                if isinstance(x, Padding):
                    beginlayer_len = len(x.load)
                    endlayer_len = len(x.payload)
                else:
                    beginlayer_len = len(x)
                    if isinstance(x.payload, Padding):
                        endlayer_len = len(x.payload.load)
                    else:
                        endlayer_len = len(x.payload)
                begin = total_len - beginlayer_len
                end = total_len - endlayer_len

                if len(path) == 2:
                    tmp = 0
                    for i in range(path[1]):
                        f = x.fields_desc[i]
                        if isinstance(f, BitField):
                            tmp += f.size
                            begin += tmp / 8
                            tmp %= 8
                        elif isinstance(f, StrField):
                            begin += f.i2repr(x,x.__getattr__(f)).__len__() - 2
                        else:
                            begin += f.sz
                    f = x.fields_desc[path[1]]
                    if isinstance(f, BitField):
                        tmp += f.size
                        end = begin + tmp / 8
                        tmp %= 8
                        if tmp != 0:
                            end += 1
                    elif isinstance(f, StrField):
                        end = begin + f.i2repr(x,x.__getattr__(f)).__len__() - 2
                    else:
                        end = begin + f.sz

                pkthexa_buf = self.pkthexa_tv.get_buffer()    
                begin_hexa = begin * 3
                if begin_hexa > 0:
                    begin_hexa += 3 * ((begin_hexa - 3)/ 24) - 2 * ((begin_hexa - 3) / 48)
                end_hexa = end * 3
                end_hexa += 3 * ((end_hexa - 3)/ 24) - 2 * ((end_hexa - 3) / 48) - 1
                # we do not select a space when nothing is selected :
                if end_hexa - begin_hexa < 2:
                    end_hexa = begin_hexa
                begin_hexa = pkthexa_buf.get_iter_at_offset(begin_hexa)
                end_hexa = pkthexa_buf.get_iter_at_offset(end_hexa)
                begin_hexa_buf, end_hexa_buf = pkthexa_buf.get_bounds()
                pkthexa_buf.remove_tag_by_name("red", begin_hexa_buf, end_hexa_buf)
                pkthexa_buf.apply_tag_by_name("red", begin_hexa, end_hexa)

                #pkthexa_buf.select_range(begin_hexa, end_hexa)

                pktascii_buf = self.pktascii_tv.get_buffer()
                begin_ascii = begin
                if begin > 0:
                    begin_ascii += (begin_ascii - 1)/ 8
                end_ascii = end
                end_ascii += (end_ascii - 1)/ 8
                begin_ascii = pktascii_buf.get_iter_at_offset(begin_ascii)
                end_ascii = pktascii_buf.get_iter_at_offset(end_ascii)
                begin_ascii_buf, end_ascii_buf = pktascii_buf.get_bounds()
                pktascii_buf.remove_tag_by_name("red", begin_ascii_buf, end_ascii_buf)
                pktascii_buf.apply_tag_by_name("red", begin_ascii, end_ascii)
                #pktascii_buf.select_range(begin_ascii, end_ascii)


    def ethereal(pl):
        """Displays a PacketList in an ethereal-like way."""
        old_color_theme = conf.color_theme
        conf.color_theme = ColorTheme
        EtherealViewer(pl)
        gtk.main()
        conf.color_theme = old_color_theme

    #pl=sniff(iface="vmnet8", count=10)
    #ethereal(pl)
