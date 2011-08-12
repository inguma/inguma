##      main.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
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
import sys
import platform
import threading

if sys.platform != "win32":
    # Need root for most modules, so...
    if os.geteuid() != 0:
        print "You must be root to run most of the modules."
        answer = raw_input("Do you want to continue [y/N]? ")
        if answer.lower() != 'y':
            sys.exit(1)

# Perform the GTK UI dependency check here
from . import dependencyCheck
import lib.ui.config as config
dependencyCheck.gtkui_dependency_check(config)

# Now that I know that I have them, import them!
import gtk, gobject

# This is just general info, to help people knowing their system
print "Starting Inguma, running on:"
print "  Python version:"
print "\n".join("    "+x for x in sys.version.split("\n"))
print "  GTK version:", ".".join(str(x) for x in gtk.gtk_version)
print "  PyGTK version:", ".".join(str(x) for x in gtk.pygtk_version)
print

# Threading initializer
if sys.platform == "win32":
    gobject.threads_init()
else:
    gtk.gdk.threads_init()

# Load the theme (this fixes a bug on windows)
if sys.platform == "win32":
    gtk.rc_add_default_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'inguma_gtkrc')

# splash!
from lib.ui.splash import Splash
splash = Splash()

# Import ui modules
splash.push(("Loading UI modules"))
import lib.ui.core as core
import lib.ui.propDialog as propDialog
import lib.ui.kbwin as kbwin
import lib.ui.om as om
import lib.ui.graphTBar as graphTBar
import lib.ui.kbtree as kbtree
import lib.ui.nodeMenu as nodeMenu
import lib.ui.altNodeMenu as altNodeMenu
import lib.ui.graphMenu as graphMenu
import lib.ui.target_dialog as target_dialog
import lib.ui.exploits as exploits
import lib.ui.libTerminal as libTerminal
import lib.ui.threadstv as threadstv
import lib.ui.reportWin as reportWin
import lib.ui.libAutosave as libAutosave
import lib.ui.bokken.main as bokken
# Fuzzers
import lib.ui.fuzzing.fuzz_frame as fuzz_frame

from lib.core import check_distorm_lib

MAINTITLE = "Inguma - A Free Penetration Testing and Vulnerability Research Toolkit"

ui_menu = """
<ui>
  <toolbar name="Toolbar">
    <toolitem action="Load"/>
    <toolitem action="Save"/>
    <toolitem action="Import"/>
    <toolitem action="Edit"/>
    <separator name="s1"/>
    <toolitem action="Proxy"/>
    <toolitem action="Web Server"/>
    <toolitem action="Sniffer"/>
    <separator name="s3"/>
    <toolitem action="Scapy"/>
    <separator name="s4"/>
    <toolitem action="Add Target"/>
    <toolitem action="Preferences"/>
    <toolitem action="Show Log"/>
    <toolitem action="Show KB"/>
    <separator name="s5"/>
    <toolitem action="Report"/>
    <separator name="s6"/>
    <toolitem action="Quit"/>
  </toolbar>
</ui>
"""

class MainApp:
    '''Main GTK application'''

    def __init__(self):

#        #################################################################################################################################
#        # Load and apply gtkrc
#        #################################################################
#        # No exception control because rc_parse doesn't throw exception on fail... sad but true ;)
#        ORIGDIR = os.getcwd()
#        os.chdir('lib/ui/data/Brave/gtk-2.0/')
#        gtk.rc_parse('gtkrc')
#        os.chdir(ORIGDIR)

        from lib.core import create_profile_dir
        create_profile_dir()

        # Load Output Manager
        self.gom = om.OutputManager('gui')

        #################################################################################################################################
        # Create a new window
        #################################################################
        splash.push(("Creating main window..."))
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_icon_from_file('logo' + os.sep + 'icon.png')
        self.window.set_focus = True
#        self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.connect("delete_event", self.quit)
        splash.push(("Loading..."))
        gtk.settings_get_default().set_long_property("gtk-button-images", True, "main") 

        # Title
        self.window.set_title(MAINTITLE)

        # Positions
        self.window.resize(800, 600)
        self.window.move(25, 25)
        # Maximize window
        self.window.maximize()

        #################################################################################################################################
        # Load core...
        #################################################################
        #Initialize KB
        splash.push(("Loading KB..."))
        self.uicore = core.UIcore()
        self.uicore.add_local_asn()
        self.gom.set_core(self.uicore)

        # Check module window prefs
        setattr(self.uicore, 'SHOW_MODULE_WIN', config.SHOW_MODULE_WIN)
        self.uicore.set_om(self.gom)

        #################################################################################################################################
        # Main VBox
        #################################################################
        mainvbox = gtk.VBox(False, 1)
        mainvbox.set_border_width(1)
        self.window.add(mainvbox)
        mainvbox.show()

        #################################################################################################################################
        # Tool Bars HBox
        #################################################################
        tbhbox = gtk.HBox(False, 1)
        mainvbox.pack_start(tbhbox, False, False, 1)
        tbhbox.show()

        #################################################################################################################################
        # UIManager for MAP Toolbar
        #################################################################
        # to make it nice we'll put the toolbar into the handle box,
        # so that it can be detached from the main window
        self.handlebox = gtk.HandleBox()
        tbhbox.pack_start(self.handlebox, True, True, 1)

        # Create a UIManager instance
        splash.push(("Creating menu and toolbar..."))
        uimanager = gtk.UIManager()
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)
        self._actiongroup = actiongroup = gtk.ActionGroup('UIManager')

        # Create actions
        actiongroup.add_actions([
            # xml_name, icon, real_menu_text, accelerator, tooltip, callback

            ('Load', gtk.STOCK_OPEN, ('Load'), None, ('Load new KB'), self.loadKB),
            ('Save', gtk.STOCK_SAVE, ('Save'), None, ('Save curren KB'), self.saveKB),
            ('Import', gtk.STOCK_CONVERT, ('Import'), None, ('Import Nmap/CSV file'), self.importScan),
            ('Edit', gtk.STOCK_EDIT, ('Edit'), None, ('Open editor'), self.loadEditor),
            ('Proxy', gtk.STOCK_CONNECT, ('Proxy'), None, (''), gtk.main_quit),
            ('Web Server', gtk.STOCK_EXECUTE, ('Web'), None, ('Web'), gtk.main_quit),

            ('Sniffer', gtk.STOCK_NETWORK, ('Sniffer'), None, ('Open network sniffer'), self.run_sniffer),
            ('Scapy', gtk.STOCK_HELP, ('Scapy'), None, ('Start Scapy'), self.show_term),
            ('Add Target', gtk.STOCK_ADD, ('Add Target'), None, ('Add a new target'), self.addTarget),
            ('Preferences', gtk.STOCK_PREFERENCES, ('Preferences'), None, ('Open preferences dialog'), self.showPref),
            ('Show Log', gtk.STOCK_DND, ('Show Log'), None, ('Show/Hide Log panel'), self.show_log),
            ('Show KB', gtk.STOCK_DND, ('Show KB'), None, ('Show/Hide KB panel'), self.show_kb),
            ('Report', gtk.STOCK_INDEX, ('Report'), None, ('Show KB report'), self.report),
            ('Quit', gtk.STOCK_QUIT, ('Quit'), None, ('Quit Inguma'), gtk.main_quit),
        ])

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(ui_menu)

        # Toolbar
        toolbar = uimanager.get_widget('/Toolbar')
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        # Disabled until I get them working
        button_proxy = uimanager.get_widget('/Toolbar/Proxy')
        button_proxy.set_sensitive(False)
        button_web = uimanager.get_widget('/Toolbar/Web Server')
        button_web.set_sensitive(False)

        # Disable if not GtkSourceView2
        if not config.HAS_SOURCEVIEW:
            button_edit = uimanager.get_widget('/Toolbar/Edit')
            button_edit.set_sensitive(False)

        # Disable if not Vte
        if not config.HAS_VTE:
            button_sniffer = uimanager.get_widget('/Toolbar/Sniffer')
            button_sniffer.set_sensitive(False)
            button_scapy = uimanager.get_widget('/Toolbar/Scapy')
            button_scapy.set_sensitive(False)

        self.handlebox.add(toolbar)
        toolbar.show()
        self.handlebox.show()

        #################################################################################################################################
        # Map tab
        #################################################################
        # Will contain on top the notebook and on bottom log window
        self.vpaned = gtk.VPaned()
        # Will contain xdot widget and kb window
        self.hpaned = gtk.HPaned()

        #################################################################
        # KB Textview
        #################################################################
        self.textview = kbwin.KBwindow()
        #self.gom.set_kbwin(self.textview)

        #################################################################
        # KB TreeView
        #################################################################
        self.treeview = kbtree.KBtree()
        self.tree = self.treeview.createTree()
        self.treeview.updateTree()
        self.gom.set_kbwin(self.treeview)
        self.tree.show()

        #################################################################
        # xdot map
        #################################################################
        from . import inxdot

        # nodeMenu initialization stuff
        self.uiman = nodeMenu.UIManager(self.gom, self.uicore, config)
        self.uiman.set_data(None)
        accel = self.uiman.get_accel_group()
        self.window.add_accel_group(accel)

        # graphMenu initialization stuff
        self.graph_uiman = graphMenu.UIManager(self.gom, self.uicore)
        graph_accel = self.graph_uiman.get_accel_group()
        self.window.add_accel_group(graph_accel)

        # altNodeMenu initialization stuff
        self.altnode_uiman = altNodeMenu.UIManager(self.gom, self.uicore)
        altnode_accel = self.altnode_uiman.get_accel_group()
        self.window.add_accel_group(altnode_accel)

        self.xdotw = inxdot.MyDotWidget(self.uiman, self.graph_uiman, self.altnode_uiman, self.uicore)
        setattr(self.graph_uiman, 'xdot', self.xdotw)
        setattr(self.altnode_uiman, 'xdot', self.xdotw)

        self.gom.set_map(self.xdotw)
        setattr(self.uicore, 'xdot', self.xdotw)
        self.uicore.getDot(doASN=False)

        self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
        self.xdotw.zoom_image(1.0)

        #################################################################
        # Graph Menu
        #################################################################
        gmenu = graphTBar.GraphMenu(self.xdotw, self.uicore)
        #################################################################
        # HBox for Map and GraphMenu
        #################################################################
        menubox = gtk.HBox()
        menubox.pack_start(self.xdotw, True, True)
        menubox.pack_start(gmenu, False, False)
        # Show elements
        gmenu.show()
        menubox.show()

        #################################################################
        # Scrolled Window
        #################################################################
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.set_size_request(250,-1)

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self.tree)

        #################################################################
        # Map Iface
        #################################################################
        label = gtk.Label('Map')

        # Test XDOT MAP
        self.hpaned.show()
        self.hpaned.pack1(menubox, True, True)
        self.hpaned.pack2(self.scrolled_window, False, False)
        self.textview.show()

        # Check visibility on config preferences
        if config.SHOW_KBTREE:
            self.scrolled_window.show()
            self.scrolled_window.is_visible = True
        else:
            self.scrolled_window.is_visible = False

        self.hpaned.show()
        self.xdotw.show()

        label = gtk.Label(' Map')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        #################################################################
        # Notebook
        #################################################################
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.notebook.append_page(self.hpaned, b)
        self.notebook.connect("switch_page", self.on_switch)

        #################################################################################################################################
        # Consoles Tab
        #################################################################
        label = gtk.Label(' Term')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        term_box = gtk.VBox()
        term_button = gtk.Button("New Tab")
        # Disable if VTE not available
        if not config.HAS_VTE:
            term_button.set_sensitive(False)
        term_box.pack_start(term_button,False)
        self.term_notebook = libTerminal.TerminalNotebook()
        term_button.connect("clicked", self.new_tab)
        term_box.pack_start(self.term_notebook)
        setattr(self.uiman, 'termnb', self.term_notebook)
        setattr(self.uiman, 'mainnb', self.notebook)

        self.notebook.append_page(term_box, b)
        term_box.show_all()

        #################################################################################################################################
        # RCE Iface
        #################################################################

        label = gtk.Label(' RCE')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        # Create bokken UI and add to the Notebook
        self.bokken = bokken.MainApp('')
        self.rcevb = self.bokken.get_supervb()
        self.rcevb.show_all()
        self.notebook.append_page(self.rcevb, b)

        #################################################################################################################################
        # Xploit Iface
        #################################################################
        # Exploits Notebook for Exploit DB, Fuzzing and Exploit Dev
        self.exploits_nb = gtk.Notebook()
        self.exploits_nb.set_tab_pos(gtk.POS_LEFT)

        #
        # Exploits DB
        #

        label = gtk.Label(' Exploits DB')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        self.exploitsInst = exploits.Exploits(config, self.term_notebook)
        exploitsGui = self.exploitsInst.get_widget()
        setattr(self.exploitsInst, 'gom', self.gom)
        exploitsGui.show_all()
        self.exploits_nb.append_page(exploitsGui, b)

        #
        # Fuzzers
        #

        label = gtk.Label(' Fuzzing')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        # Fuzzers Box to contain krash and scapy fuzzers
        self.fuzz_frame = fuzz_frame.FuzzFrame()
        setattr(self.fuzz_frame.scapyui, 'gom', self.gom)
        self.exploits_nb.append_page(self.fuzz_frame, b)

        # Add exploits notebook and text/label to main notebook
        label = gtk.Label(' Exploit')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        self.notebook.append_page(self.exploits_nb, b)

        self.vpaned.add1(self.notebook)
        self.exploits_nb.show_all()
        self.notebook.show()


        #################################################################################################################################
        # Log Window
        #################################################################
        self.logtext = gtk.TextView(buffer=None)

        # Some eye candy
        self.logtext.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(16400, 16400, 16440))
        self.logtext.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(60535, 60535, 60535, 0))
        self.logtext.set_left_margin(10)

        self.logtext.set_wrap_mode(gtk.WRAP_NONE)
        self.logtext.set_editable(False)
        self.logbuffer = self.logtext.get_buffer()
        self.logbuffer.set_text('Loading Inguma...\n')
        self.logtext.show()

        #################################################################
        # Log Scrolled Window
        #################################################################
        self.log_scrolled_window = gtk.ScrolledWindow()
        self.log_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.log_scrolled_window.is_visible = True

        #Always on bottom on change
        self.vajd = self.log_scrolled_window.get_vadjustment()
        self.vajd.connect('changed', lambda a, s=self.log_scrolled_window: self.rescroll(a,s))
        
        # Add Textview to Scrolled Window
        self.log_scrolled_window.add_with_viewport(self.logtext)

        # Set logtext as output for gui
        self.gom.set_gui(self.logbuffer)

        # Add Scrolled Log Window to Bottom Notebook
        ############################################

        # Notebook for bottom panel
        self.bottom_nb = gtk.Notebook()
        self.bottom_nb.set_size_request(-1, 110)
        self.bottom_nb.set_tab_pos(gtk.POS_LEFT)

        # Icon and label for Logs tab
        label = gtk.Label(' Logs')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_JUSTIFY_FILL, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        self.bottom_nb.append_page(self.log_scrolled_window, b)

        # Icon and label for Actions tab
        label = gtk.Label(' Actions')
        label.set_angle(90)
        b_factory = gtk.VBox
        b = b_factory(spacing=1)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU)
        b.pack_start(label)
        b.pack_start(i)
        b.show_all()

        # Add Threads TreeView
        self.threadsInst = threadstv.ThreadsTv()
        threadsGui = self.threadsInst.get_widget()
        setattr(self.threadsInst, 'uicore', self.uicore)
        threadsGui.show_all()

        self.bottom_nb.append_page(threadsGui, b)

        setattr(self.fuzz_frame.scapyui, 'bottom_nb', self.bottom_nb)

        # Check visibility on config preferences
        if config.SHOW_LOG:
            self.bottom_nb.is_visible = True
            self.bottom_nb.show()
        else:
            self.bottom_nb.is_visible = False

        self.vpaned.pack2(self.bottom_nb, False, False)
        mainvbox.pack_start(self.vpaned, True, True, 1)
        self.log_scrolled_window.show()

        self.bottom_nb.set_current_page(0)

        # Add threadtv to core
        self.uicore.set_threadtv(self.threadsInst)
        setattr(self.graph_uiman, 'threadtv', self.threadsInst)
        setattr(self.altnode_uiman, 'threadtv', self.threadsInst)
        # And to exploit management module
        setattr(self.exploitsInst, 'threadsInst', self.threadsInst)

        #################################################################################################################################
        #StatusBar
        #################################################################
        from lib.core import get_inguma_version
        self.statusbar = gtk.Statusbar() 
        mainvbox.pack_end(self.statusbar, False, False, 1)
        context_id = self.statusbar.get_context_id('Inguma ' + get_inguma_version())
        message_id = self.statusbar.push(context_id, 'Inguma ' + get_inguma_version())
        self.statusbar.show()

        #################################################################################################################################
        # finish it
        #################################################################
        self.vpaned.show()
        self.window.show()
        splash.destroy()

        # Check for autosaved KB and ask for loading
        if not libAutosave.check_kb():
            print "Autosaved KB not found, skipping..."
        else:
            toload = libAutosave.ask_dialog()
            if toload:
                kbpath = libAutosave.get_kb_path()
                self.uicore.loadKB(kbpath)
                libAutosave.remove_kb()
                
                # Update KB textview
                self.textview.updateWin()
                self.treeview.updateTree()
    
                # Adding text to Log window
                self.gom.echo( 'Loaded' , False)
            else:
                libAutosave.remove_kb()

        # To keep record of kb file name
        self.kbfile = ''

        # Update Map
        self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
        self.xdotw.zoom_image(1.0)

        gtk.main()

#################################################################################################################################
# Functions
#################################################################

    def loadKB(self, widget):
        from lib.core import get_profile_file_path
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder(get_profile_file_path('data/'))
        chooser.resize(100,100)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.gom.echo( 'Loading KB...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()
            self.uicore.loadKB(res)

            # Update KB textview
            self.textview.updateWin()
            self.treeview.updateTree()
            # Update Map
            self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.xdotw.zoom_image(1.0)

            # Adding text to Log window
            self.gom.echo( 'Loaded' , False)
            self.kbfile = res

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)
        chooser.destroy()

    def saveKB(self, widget):
        from lib.core import get_profile_file_path
        if self.kbfile == '':
            chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.set_current_folder(get_profile_file_path('data/'))
            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                filename = chooser.get_filename()
                self.uicore.saveKB(filename)
                self.gom.echo( filename + ' selected' , False)
                libAutosave.remove_kb()
                self.kbfile = filename
            elif response == gtk.RESPONSE_CANCEL:
                self.gom.echo( 'Closed, no files selected' , False)
            chooser.destroy()
        else:
            self.uicore.saveKB(self.kbfile)
            self.gom.echo( self.kbfile + ' selected' , False)
            libAutosave.remove_kb()

    def importScan(self, widget):
        """ Parse and import nmap scan """

        # Choose nmap scan file
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        
        filter = gtk.FileFilter()
        filter.set_name('Nmap scan')
        filter.add_pattern('*.xml')
        chooser.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name('Host list')
        filter.add_pattern('*.csv')
        chooser.add_filter(filter)

        # Try to parse and import data
        response = chooser.run()
        filter = chooser.get_filter()
        if response == gtk.RESPONSE_OK and filter.get_name() == 'Nmap scan':
            self.gom.echo( 'Loading Nmap Scan...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()

            import lib.ui.nmapParser as nmapParser
            try:
                self.gom.echo( 'Parsing scan results...', False)
                nmapData = nmapParser.parseNmap(res)
                self.gom.echo( 'Inserting data in KB...', False)
                nmapParser.insertData(self.uicore, nmapData)

                askASN = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Resolve ASN of IP addresses?")
                do_asn = askASN.run()

                self.gom.echo( 'Loaded\nUpdating Graph', False)

                if do_asn == gtk.RESPONSE_YES:
                    doASN=True
                else:
                    doASN=False

                t = threading.Thread(target=self.uicore.getDot, args=(doASN,))
                t.start()

                askASN.destroy()

                gobject.timeout_add(1000, self.update_graph, t)

            except:
                md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Error loading file")
                md.run()
                md.destroy()

        elif response == gtk.RESPONSE_OK and filter.get_name() == 'Host list':
            self.gom.echo( 'Loading Host list...', False)
            self.gom.echo(  chooser.get_filename() + ' selected' , False)
            res = chooser.get_filename()
            try:
                hfile = open(res, 'r')
                hlist = hfile.readlines()
                hfile.close()
                hlist = hlist[0].split(',')

                self.gom.echo( 'Inserting data in KB...', False)
                for host in hlist:
                    self.uicore.set_kbfield('targets', host.strip())
                    self.uicore.set_kbfield('hosts', host.strip())

                # Update graph
                self.uicore.getDot(doASN=False)
                self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            except:
                print "Your lack of faith on my parsing capabilities is disturbing..."

        elif response == gtk.RESPONSE_CANCEL:
            self.gom.echo( 'Closed, no files selected', False)

        chooser.destroy()

    def update_graph(self, thread):

        if thread.isAlive() == True:
            return True
        else:
            self.xdotw.set_dotcode( self.uicore.get_kbfield('dotcode') )
            self.gom.kbwin.updateTree()
            return False


    def loadEditor(self, widget):
        """ Loads module editor """

        import lib.ui.editor as editor
        editor.main()

    def showPref(self, widget):
        # FIXME: Change propWhatever to prefWhatever.
        propDialog.propDialog(self.uicore, self.gom, self.threadsInst, config)

    def show_term(self, widget):
        self.new_tab('scapy', 'scapy')

    def run_sniffer(self, widget):
        self.new_tab('sniffer', 'tools/sniffer')

    def new_tab(self, widget, command=''):
        self.term_notebook.new_tab(command)
        self.notebook.set_current_page(1)

    def report(self, widget):

        reportWin.reportWin(self.uicore)

    def show_log(self, widget):
        ''' Show/hide log panel'''

        if self.bottom_nb.is_visible == True:
            self.bottom_nb.hide()
            self.bottom_nb.is_visible = False

        else:
            self.bottom_nb.show()
            self.bottom_nb.is_visible = True

    def show_kb(self, widget):
        ''' Show/hide KB panel'''

        if self.scrolled_window.is_visible == True:
            self.scrolled_window.hide()
            self.scrolled_window.is_visible = False

        else:
            self.scrolled_window.show()
            self.textview.updateWin()
            self.treeview.updateTree()
            self.scrolled_window.is_visible = True

    def on_switch(self, widget, data, more):
        from lib.core import get_profile_file_path
        if more == 2:
            # Check if the disassembly library is present
            # Check only for Linux platform
            if platform.system() == 'Linux':
                path = get_profile_file_path('data' + os.sep)
                has_distorm = check_distorm_lib(path)
                if not has_distorm:
                    md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format='distorm64 library not found.\nDownload it at the preferences dialog, on the "Update" tab.')
                    md.run()
                    md.destroy()

            self.handlebox.hide()
            self.bottom_nb.hide()
            self.statusbar.hide()
        elif more == 1:
            self.handlebox.show()
            self.bottom_nb.hide()
            self.statusbar.show()
        else:
            self.handlebox.show()
            self.bottom_nb.show()
            self.bottom_nb.is_visible = True
            self.statusbar.show()

    def addTarget(self, event):

        addtgt = target_dialog.TargetDialog(self.uicore, self.gom, self.threadsInst, config, self.xdotw)

    def rescroll(self, adj, scroll):
        adj.set_value(adj.upper-adj.page_size)
        scroll.set_vadjustment(adj)

    def quit(self, widget, event, data=None):
        '''Main quit.

        @param widget: who sent the signal.
        @param event: the event that happened
        @param data: optional data to receive.
        '''
        msg = ("Do you really want to quit?")
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        opt = dlg.run()
        dlg.destroy()

        if opt != gtk.RESPONSE_YES:
            return True

        self.gom.echo( 'Exit!', False)
        gtk.main_quit()
        return False

    def run_debugger(self, widget):
        '''run vdbbin GUI'''

        import threading
        t = threading.Thread( target=os.popen('lib/debugger/vdbbin -G') )
        t.start()

def main():
    MainApp()
