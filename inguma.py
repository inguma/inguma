#!/usr/bin/python
# encoding: utf-8
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007, 2008 Joxean Koret, joxeankoret [at] yahoo.es
Copyright (c) 2009 - 2011 Hugo Teso, hugo.teso [at] gmail.com
Copyright (c) 2012 David Martínez Moreno <ender@debian.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

import os
import sys
import time
import readline
import lib.core as core
import lib.globals as glob
import lib.ui.cli.core as uicore

from reports import generateReport

from lib.printwrapper import CPrintWrapper

# Import Output Manager
import lib.ui.output_manager as om

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

from discover import *
from gather import *
from rce import *

global target
global targets
global otherTargets
global services
global port
global covert
global timeout
global waittime
global wizard
global user
global password
global dad
global sid
global ostype
global payload
global listenPort
global hash
global ignore_host
global url

wizard = False
target = ""
targets = []
otherTargets = []
services = {}
port = 0
covert = 0
timeout = 1
waittime = 0.1
user = ""
password = ""
url = ""
ostype = 1
payload = 2
listenPort = 4444
hash = ""

# Colors
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

discovers = []
gathers = []
rces = []
fuzzers = []
brutes = []
classes = []
others = []
exploits = []

vars = globals()

# ------------------------------ Start of Inguma class ------------------------------

class Inguma:
    """ Master class for an Inguma CLI instance. """

    def __init__(self, has_scapy = False):
        self.has_scapy = has_scapy

    def show_help(self):
        glob.gom.echo()
        glob.gom.echo('+----------------------------------------------------------------------------+')
        glob.gom.echo('| load kb                 | Load the knowledge base                          |')
        glob.gom.echo('| save kb                 | Save the knowledge base                          |')
        glob.gom.echo('| clear kb                | Clear the knowledge base\'s data                  |')
        glob.gom.echo('| show kb                 | Shows the knowledge base\'s data (very verbose)   |')
        glob.gom.echo('| report                  | Generate a report                                |')
        glob.gom.echo('|----------------------------------------------------------------------------|')
        glob.gom.echo('| show discover           | Show discover modules                            |')
        glob.gom.echo('| show gather             | Show gather modules                              |')
        glob.gom.echo('| show rce                | Show RCE modules                                 |')
        glob.gom.echo('| show fuzzers            | Show fuzzing modules                             |')
        glob.gom.echo('| show exploits           | Show available exploits                          |')
        glob.gom.echo('| show brute              | Show brute force modules                         |')
        glob.gom.echo('| show options            | Show options                                     |')
        glob.gom.echo('| payload                 | Show the supported OS types and payloads         |')
        glob.gom.echo('| info <exploit>          | Show additional information about an exploit     |')
        glob.gom.echo('|----------------------------------------------------------------------------|')
        glob.gom.echo('| autoscan                | Perform an automatic scan                        |')
        glob.gom.echo('| autoexploit             | Exploit wizard                                   |')
        #glob.gom.echo('fuzz                     Fuzz a target (Unavailable)')
        glob.gom.echo('| exploit                 | Run an exploit against a target or targets       |')
        glob.gom.echo('|----------------------------------------------------------------------------|')
        glob.gom.echo('| use <mod>               | Load all modules from a directory                |')
        glob.gom.echo('| ! <command>             | Run an operating system command                  |')
        glob.gom.echo('| exit | quit | ..        | Exit Inguma                                      |')
        glob.gom.echo('| help | h | ?            | Show this help                                   |')

        if self.has_scapy:
            glob.gom.echo('|----------------------------------------------------------------------------|')
            glob.gom.echo('|                                                                            |')
            glob.gom.echo('| To see registered scapy commands execute command \'scapy.lsc()\'             |')
            glob.gom.echo('|----------------------------------------------------------------------------|')
            glob.gom.echo('|                                                                            |')
            glob.gom.echo('| NOTE: Remember to use \'scapy.<function>\' to use.                           |')
            glob.gom.echo('|                                                                            |')
            glob.gom.echo('| Type \'scapy.interact()\' to start an scapy session.                         |')
            glob.gom.echo('| To get help for scapy commands type help(scapy.<scapy command>).           |')

        glob.gom.echo('+----------------------------------------------------------------------------+')
        glob.gom.echo()
        glob.gom.echo('Any other typed text will be evaluated - with eval() - as a Python expression.')
        glob.gom.echo()

# ------------------------------ End of Inguma class ------------------------------

def load_module(path, atype, marray, bLoad = True):
    """ Module loader for Inguma.
    Arguments:
    path:   module category path (modules/discover)
    atype:  module category (discover)
    marray: module category list (discovers)
    """

    sys.path.append(path)

    for complete_filename in os.listdir(path):
        # Load all modules in the path, unless:
        if complete_filename.startswith("_") or complete_filename.startswith(".") or complete_filename.endswith("pyc"):
            continue

        if bLoad:
            # Get file name
            file = complete_filename[:complete_filename.find(".py")]
        else:
            if not os.path.isdir("%s%s%s" % (path, os.sep, complete_filename)):
                continue

        # Protect ourselves against weird filenames.
        if not file:
            continue

        uicore.debug_print("Loading " + atype + " module", file)

        if bLoad:
            try:
                if file.isalnum():
                    exec("import " + file)
                    exec("global " + marray)
                else:
                    print "The module %s%s%s has errors or a non-alphanumeric name." % (path, os.sep, complete_filename)
                    continue

                try:
                    if "globals" in dir(eval(file)):
                        # Load module global variables
                        moduleGlobals = eval(file).globals

                        for aGlobal in moduleGlobals:
                            if aGlobal.isalnum():
                                exec ("global " + aGlobal)
                                glob.GLOBAL_VARIABLES += "global " + aGlobal + ";"
                            else:
                                print "The global variable of the module %s%s%s doesn't appear to be a variable..." % (path, os.sep, complete_filename)
                                print "The suspicious code:"
                                print aGlobal
                except:
                    uicore.debug_print(FAIL + "Error loading global variables" + ENDC)
                    print sys.exc_info()[1]

                exec(marray + ".append(eval(file))")
                # Do this in the meantime to populate the glob.* structures.
                exec('glob.' + marray + ".append(eval(file))")

                glob.commands[eval(file).name] = eval(file)

                if atype == "unknown":
                    if eval(file).type == "gather":
                        exec("gathers.append(eval(file))")
                    elif eval(file).type == "discover":
                        exec("discovers.append(eval(file))")
                    elif eval(file).type == "rce":
                        exec("rces.append(eval(file))")
                    elif eval(file).type == "fuzzers":
                        exec("fuzzers.append(eval(file))")
                    elif eval(file).type == "brute":
                        exec("brutes.append(eval(file))")

                for x in filter(lambda x: x.startswith("C"), dir(eval(file))):
                    classes.append(file + "." + x)
                    uicore.debug_print("Registering class",file + "." + x)
                    uicore.debug_print("Creating a base object ....")

                    obj = eval(file + "." + x +"()")
                    del obj
            except:
                uicore.debug_print(FAIL + "Error loading module", file, ":" + ENDC,sys.exc_info()[1])
                if file.lower().find("smtp") > -1:
                    raise
        else:
            if file.isalnum():
                eval(marray).append(file)
            else:
                print WARNING + "The module %s appears to be a non-valid module" + ENDC % file
                continue

def readCommands():
    uicore.debug_print("Reading modules ... ")
    uicore.debug_print()

    modules = {
        'discovers': 'discover',
        'gathers': 'gather',
        'rces': 'rce',
        'fuzzers': 'fuzzers',
        'brutes': 'brute',
        'exploits': 'exploits'
    }

    # Load all modules.
    for exploit_type, exploit_dir in modules.iteritems():
        path = "modules" + os.sep + exploit_dir
        load_module(path, exploit_dir, exploit_type)

def exploitWizard():

    global target
    global port
    global covert
    global timeout
    global waittime
    global wizard

    i = 0

    if target == "" or target == None:
        if not glob.isGui:
            target = raw_input("Target: ")
        else:
            print "[!] You need to specify the target"

    wizard = True

    """
    print
    print "Exploit list"
    print "------------"
    print

    for mod in exploits:
        i += 1
        print str(i) + " " + mod.name, " \t\t", mod.brief_description
    print
    """
    if not glob.isGui:
        res = raw_input("Select module [all]: ")
    else:
        res = ""

    if res != "":
        try:
            runRegisteredCommand(exploits[int(res)-1].name, locals())
        except:
            runRegisteredCommand(res, locals())
    else:
        for mod in exploits:
            try:
                print "Running",mod.name,"..."
                runRegisteredCommand(mod.name, locals())
            except:
                print "Error",sys.exc_info()[1]

def runRegisteredCommand(cmd, mVars = None):

    global user_data

    mType = glob.commands[cmd].type
    vars = globals()

    if mVars != None:
        for x in mVars:
            vars[x] = mVars[x]

    if mType in ["gather", "exploit", "brute", "fuzzer",  "rce"]:
        ret = runGatherModule(vars, glob.commands[cmd], user_data, gom)
    elif mType == "discover":
        ret = runModule(vars, glob.commands[cmd], user_data, gom)
    else:
        print "Unknown module type '" + str(mType) + "'"

    if ret:
        user_data = ret

    return ret

def execute(command, index):

    if len(command) < index:
        print "Not enough arguments"
        return
    else:
        cmd = ""
        words = command[index-1:]

        for aux in words:
            cmd += aux + " "

    os.system(cmd)

def runCommand(data, mVars = None):

    global target

    mode = ""

    words = data.split(" ")
    index = 0

    for word in words:
        index += 1

        if index == 1:
            if word.lower() == "show":
                mode = "show"
            elif word.lower() == "use":
                mode = "use"
            elif word.lower() in ["info", "help"]:
                mode = "info"
            elif word == "!":
                mode = "!"
            elif word.lower() == "exploit":
                exploitWizard()
                return True
            else:

                if glob.commands.has_key(word.lower()):
                    runRegisteredCommand(word.lower(), mVars)
                    return True
                else:
                    return False
        else:
            if mode == "show":
                if word.lower() == "exploits":
                    showExploits()
                    return True
                elif word.lower() == "options":
                    showOptions()
                    return True
                else:
                    print "Unknown option",word,"for show command"
                    return True
            elif mode == "use":
                load_module(word, "unknown", "others")
                return True
            elif mode == "info":
                uicore.show_exploit_info(word)
                return True
            elif mode == "!": #Execute command
                execute(words, index)
                return True

    return False

def showOptions():

    global target
    global port
    global covert
    global timeout
    global waittime
    global wizard

    if target == "":
        mTarget = "Not specified"
    else:
        mTarget = target

    print "Options"
    print
    print "Target:  \t\t", mTarget
    print "Port:    \t\t", port
    print "Covert level:\t\t", covert
    print "Timeout:\t\t", timeout
    print "Wait time:\t\t", waittime
    print "Wizard mode:\t\t", wizard
    print

def showDiscover():
    print
    print "List of discover modules"
    print "------------------------"
    print

    for x in discovers:
        print x.name + "    \t\t" + x.brief_description
    print

def showGather():
    print
    print "List of gather modules"
    print "----------------------"
    print
    for x in gathers:
        cmd = x.name

        if len(cmd) < 4:
            cmd += "  "

        print cmd + "    \t\t" + x.brief_description
    print

def showRce():
    print
    print "List of rce modules"
    print "-------------------"
    print

    for x in rces:
        print x.name + "    \t\t" + x.brief_description
    print

def showBrutes():
    print
    print "List of brute force modules"
    print "---------------------------"
    print
    for x in brutes:
        cmd = x.name

        if len(cmd) < 4:
            cmd += "  "

        print cmd + "    \t\t" + x.brief_description
    print

def showExploits():
    print
    print "List of exploit modules"
    print "-----------------------"
    print

    mList = []
    zerodays = []

    for x in glob.exploits:
        if x.brief_description.startswith("[0day]"):
            zerodays.append(x.name + "    \t\t" + x.brief_description)
        else:
            mList.append(x.name + "    \t\t" + x.brief_description)

    zerodays.sort()
    for x in zerodays:
        print x
    print

    mList.sort()
    for x in mList:
        print x
    print

def showFuzzers():
    print
    print "List of fuzzing modules"
    print "-----------------------"
    print

    for x in fuzzers:
        if type(x) is str:
            print " " + x
        else:
            print " " + x.name + "    \t\t" + x.brief_description

    print

def showLaunch(module, message):
    global target
    global user_data

    print message

    try:
        interactive = False
        runCommand(module, locals())
    except:
        print module + ":", sys.exc_info()[1]

def doAutoScan(guest = "no", fuzz = "no"):
    global target
    global user_data
    global wizard
    global user
    global sid
    global ignore_host
    global ports

    oldfile = sys.stdout
    f = None

    try:
        wizard = False

        if target == "" and not glob.isGui:
            target = raw_input("Target host or network: ")

        if not glob.isGui:
            guestPasswords = raw_input("Brute force username and passwords (y/n)[n]: ")
        else:
            guestPasswords = guest
            print "Guest passwords set to", guest

        if guestPasswords.lower() == "y" or guestPasswords.lower() == "yes":
            guestPasswords = True
        else:
            guestPasswords = False

        if not glob.isGui:
            autoFuzz = raw_input("Automagically fuzz available targets (y/n)[n]: ")
        else:
            autoFuzz = fuzz

        if autoFuzz.lower() == "y" or autoFuzz.lower() == "yes":
            autoFuzz = True
        else:
            autoFuzz = False

        if not glob.isGui:
            printTo = raw_input("Print to filename (enter for stdout): ")

            if printTo != "":
                f = file(printTo, "w")
                objPrintWrapper = CPrintWrapper()
                objPrintWrapper.realFile = f
                objPrintWrapper.oldFile = sys.stdout
                sys.stdout = objPrintWrapper

        x = "Inguma 'autoscan' report started at " + time.ctime()
        print x
        print "-"*len(x)
        print

        try:
            if target.find("/") > -1:
                showLaunch("arping", "Detecting hosts in network %s\n" % target)
            else:
                if user_data.has_key("hosts"):
                    user_data["hosts"].append(target)
                else:
                    user_data["hosts"] = [target]

            if not core.is_ip_addr4(target) and target.lower().strip(" ") != "localhost":
                showLaunch("whois", "Getting whois database information target %s\n" % target)

            if target.find("/") == -1:
                mHosts  = [target]
            else:
                mHosts = user_data["hosts"]

            for host in mHosts:
                target = host

                if user_data.has_key("ignore_host"):
                    if host in user_data["ignore_host"]:
                        continue

                showLaunch("portscan", "Port scanning target %s\n" % target)
                #showLaunch("tcpscan", "TCP scanning target %s\n" % target)

                if host not in ["localhost", "127.0.0.1"]:
                    showLaunch("getmac", "MAC Address target %s\n" % target)
                    # It's more than slow...
                    #showLaunch("portscan", "SYN scanning target %s\n" % target)

                showLaunch("ispromisc", "Checking if is in promiscuous state target %s\n" % target)
                showLaunch("identify", "Identifying services target %s\n" % target)
                if user_data.has_key(target + "_tcp_ports"):
                    ports = user_data[target + "_tcp_ports"]

                    showLaunch("isnated",  "Checking what ports are nated target %s\n" % target)

                    if len(ports) > 0:
                        # The first port will be used as the opened port
                        oport = ports[0]
                        # The last port + 1 will be used as the closed port
                        cport = ports[len(ports)-1]+1

                showLaunch("nmapfp", "Detecting operating system target %s\n" % target)

                if os.name == "nt":
                    showLaunch("winspdetect", "Detecting service pack level target %s\n" % target)

                if 135 in ports or 139 in ports or 445 in ports:
                    # CIFS compatible server, surely
                    showLaunch("nmbstat", "Gathering NetBIOS information target %s\n" % target)
                    showLaunch("smbclient", "Connecting to the CIFS server target %s\n" % target)
                    showLaunch("rpcdump", "Dumping RPC endpoints target %s\n" % target)
                    showLaunch("samrdump", "Dumping SAM database target %s\n" % target)

                    if user_data.has_key(target + "_users") and guestPasswords:
                        userList = user_data[target + "_users"]
                        for mUser in userList:
                            user = mUser
                            showLaunch("brutesmb", "Brute forcing CIFS username and passwords target %s\n" % target)

                    showLaunch("smbgold", "Finding 'gold' anonymously in the CIFS shares target %s" % target)

                    if user_data.has_key(target + "_passwords"):
                        for userPass in user_data[target + "_passwords"]:
                            user, password = userPass.split("/")
                            showLaunch("smbgold", "Finding 'gold' as %s/%s in the CIFS shares target %s" % (user, password, target))

                if user_data.has_key(target + "_services"):
                    for service in user_data[target + "_services"]:
                        if service.find("/tns") > -1:
                            port = int(service.split("/")[0])
                            # TNS Listener
                            showLaunch("tnscmd", "Getting information from the Oracle TNS Listener target %s\n" % target)

                            if guestPasswords:
                                showLaunch("sidguess", "Getting the Oracle TNS Listener's sid target %s\n" % target)

                                if user_data.has_key(target + "_sid"):
                                    sid = user_data[target + "_sid"]
                                    user = ""
                                    showLaunch("bruteora", "Brute forcing Oracle's username/passwords target %s\n" % target)

                        elif service.find("/ftp") > -1:
                            port = int(service.split("/")[0])

                            if guestPasswords:
                                if user_data.has_key(target + "_users"):
                                    for luser in user_data[target + "_users"]:
                                        user = luser
                                        # FTP Server
                                        showLaunch("bruteftp", "Brute forcing FTP Server at port %d target %s" % (port, target))

                            if autoFuzz:
                                showLaunch("ftpfuzz", "Fuzzing FTP server at port %d target %s" % (port, target))
                        elif service.find("/ssh") > -1:
                            port = int(service.split("/")[0])

                            if guestPasswords:
                                if user_data.has_key(target + "_users"):
                                    for luser in user_data[target + "_users"]:
                                        user = luser
                                        # SSH Server
                                        showLaunch("brutessh", "Brute forcing SSH Server at port %d target %s" % (port, target))

                    for service in user_data[target + "_services"]:
                        if service.find("/http") > -1:
                            port = int(service.split("/")[0])
                            print "will use port %d" % port

                            # Oracle E-Business Suite 11i
                            showLaunch("apps11i", "Getting information from the Oracle E-Business Suite 11i target %s\n" % target)
                            # Oracle Applications Server
                            showLaunch("oascheck", "Getting Oracle Applications Server known vulnerable urls target %s\n" % target)
                            # Nikto plugin
                            showLaunch("nikto", "Using nikto to gather known vulnerable urls target %s\n" % target)

                if 143 in ports and guestPasswords: # IMAP Server
                    if user_data.has_key(target + "_users"):
                        for luser in user_data[target + "_users"]:
                            user = luser
                            showLaunch("bruteimap", "Brute forcing IMAP server target %s" % target)

                if 21 in ports and guestPasswords: # POP Server
                    if user_data.has_key(target + "_users"):
                        for luser in user_data[target + "_users"]:
                            user = luser
                            showLaunch("brutepop", "Brute forcing POP server target %s" % target)

        except:
            print "AUTOSCAN ERROR:", sys.exc_info()[1]

    except:
        print "Error.", sys.exc_info()[1]

    if f:
        f.close()

    sys.stdout = oldfile

def main_loop():
    """ Main execution loop after initialization. """

    global prompt
    global oldPrompt
    global prevRes
    global target
    global port
    global covert
    global timeout
    global waittime

    oldPrompt = ""
    prevRes = ""
    inguma = Inguma(hasScapy)

    while 1:
        res = uicore.unified_input_prompt(inguma)
        if res == None:
            glob.gom.echo("Exit.")
            return False

        if res == "" and prevRes == "":
            pass
        elif res.lower() == "save kb":
            # FIXME: We cannot use globals inside the KnowledgeBase class, so
            # we have to assign the 'target' global variable to a glob attribute
            # prior to calling the class method.
            glob.target = target
            res = raw_input('Filename [%s]: ' % glob.kb.default_filename)
            if res:
                glob.kb.save(res)
            else:
                glob.kb.save()
            # FIXME: We cannot use globals inside the KnowledgeBase class, so
            # we have to reassign the 'target' global variable after calling
            # it. 'global target' is defined above in the function,
            target = glob.target
        elif res.lower() == "clear kb":
            glob.kb.reset()
        elif res.lower() == "load kb":
            # FIXME: We cannot use globals inside the KnowledgeBase class, so
            # we have to assign the 'target' global variable to a glob attribute
            # prior to calling the class method.
            glob.target = target
            glob.gom.echo('* Warning! Warning! Warning! Warning! Warning! Warning! *')
            glob.gom.echo('*** Never load KB files received from untrusted sources ***')
            res = raw_input('Filename [%s]: ' % glob.kb.default_filename)

            if res:
                glob.kb.load(res)
            else:
                glob.kb.load()
            # FIXME: We cannot use globals inside the KnowledgeBase class, so
            # we have to reassign the 'target' global variable after calling
            # it. 'global target' is defined above in the function,
            target = glob.target
        elif res.lower() == "show kb":
            glob.gom.echo(glob.kb.format_text())
        elif res.lower() == "show discover":
            showDiscover()
        elif res.lower() == "show gather":
            showGather()
        elif res.lower() == "show rce":
            showRce()
        elif res.lower() == "show fuzzers":
            showFuzzers()
        elif res.lower() == "show brute":
            showBrutes()
        elif res.lower() == "autoscan":
            doAutoScan()
        elif res.lower() == "report":
            generateReport(user_data)
        elif res.lower() == "payload":
            printPayloads()
        elif res != "" and prevRes != "":
            prevRes += "\n" + res
        elif res == "" and prevRes != "":
            try:
                if prevRes != "":
                    prevRes += "\n" + res
                    res = prevRes

                exec(glob.GLOBAL_VARIABLES + res)

            except:
                print "Exec error:",sys.exc_info()[1]

            prevRes = ""
            if oldPrompt != "":
                prompt = oldPrompt
                oldPrompt = ""
        elif res[len(res)-1] == ":":
            oldPrompt = prompt
            prompt = ">>>>>>> "
            prevRes = res
        else:
            try:
                if not runCommand(res, locals()):
                    exec(glob.GLOBAL_VARIABLES + res)
            except:
                print "Internal error.",sys.exc_info()[1]

                if glob.debug:
                    raise

def printPayloads():
    global payload

    glob.gom.echo('Payloads')
    glob.gom.echo('--------')
    glob.gom.echo()
    glob.gom.echo('ostype:')
    glob.gom.echo()
    glob.gom.echo('1) Linuxx86Syscall')
    glob.gom.echo('2) FreeBSDx86Syscall')
    glob.gom.echo('3) OpenBSDx86Syscall')
    glob.gom.echo('4) Solarisx86Syscall')
    glob.gom.echo()
    glob.gom.echo('payload:')
    glob.gom.echo()
    glob.gom.echo('1) runcommand')
    glob.gom.echo('2) bindshell')
    glob.gom.echo('3) connectback')
    glob.gom.echo('4) xorbindshell')
    glob.gom.echo()
    glob.gom.echo('Payload arguments:')
    glob.gom.echo()
    glob.gom.echo('1) runcommand')
    glob.gom.echo()
    glob.gom.echo('command = <command to run>')
    glob.gom.echo()
    glob.gom.echo('2) bindshell, connectback, xorbindshell')
    glob.gom.echo()
    glob.gom.echo('listenPort = <remote or local listening port>')
    glob.gom.echo()
    glob.gom.echo('NOTE: \'listenPort\' will be the local port to connect back or the remote port to connect.')
    glob.gom.echo()

def saveHistory():
    """ Saves previous history commands in the history file. """

    historyFile = core.get_profile_file_path("history")

    try:
        if os.path.exists(historyFile):
            readline.write_history_file(historyFile)
        return True
    except:
        return False

def loadHistory():
    """ Loads previous history commands and creates an empty history file. """

    historyFile = core.get_profile_file_path("history")

    if os.path.exists(historyFile):
        readline.read_history_file(historyFile)
    else:
        try:
            open(historyFile, 'w').close()
        except:
            print "Cannot create " + historyFile

def set_om(debug=glob.debug):
    """ Decides which version of OM should be loaded. """
    # Set OutputManager to be used by modules
    global gom
    if glob.isGui == True:
        gom = om.OutputManager('gui', debug=debug)
    else:
        gom = om.OutputManager('console', debug=debug)
    setattr(gom, 'isGui', glob.isGui)
    # DEPRECATE: Most of the above as soon as everything is moved to glob.gom.
    glob.gom = gom

def setup_auto_completion():
    """ Checks dependencies for autocompletion and sets it up. """

    try:
        import atexit
        import rlcompleter

        # Add commands to autocompletion
        readline.set_completer(rlcompleter.Completer(glob.commands).complete)
        if(sys.platform == 'darwin'):
            readline.parse_and_bind ("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        loadHistory()
        atexit.register(saveHistory)
    except:
        print sys.exc_info()[1]

def inguma_init():
    """Initializes very basic Inguma data structures."""
    #FIXME: This should go into the __init__ section of a future Inguma class.
    """NOTE: This function cannot be moved to lib/core.py.
    TL;DR; If this function is in another module, i.e. lib/core.py, 'global'
    won't be able to see global variables from this module.

    Explanation: The rationale is that the global keyword only works for every
    namespace, which sadly spans only to each module.  We will need to kill
    every global in the code before removing the GLUE CODE and moving this
    function somewhere else. :-(
    """

    import lib.globals as glob
    import lib.kb as kb

    # We init the KB.
    glob.kb = kb.KnowledgeBase()

    # Start up the HTTP server.
    if glob.http_server:
        import lib.http as httpd
        http = httpd.IngumaHttpServer()
        glob.gom.echo("\nBringing up HTTP server.")
        # We start the thread.
        http.start()
        time.sleep(0.2)
        # We put the http structure in glob to have it accessible in the global
        # __main__ handler.
        glob.http = http

    # GLUE CODE.
    # This code will try to deal with the horrible spaghetti that global
    # variables are in the code.  So what we do is to move them slowly to
    # lib.globals but leave global references with the old names around to
    # prevent old (i.e. not yet migrated) code from working.
    # These are the only global statements that we will add from now on.
    global ports
    global target
    global user_data

    target = ''
    ports = glob.ports
    user_data = glob.kb._kb

    try:
        # FIXME: This should have look up into the binary directory and not the actual one.
        f = file("data/ports", "r")

        for line in f:
            ports.append(int(line))

    except:
        # FIXME: Ugly, only for console version!
        print sys.exc_info()[1]
        pass

def main():
    """ Main program loop. """

    # Set OutputManager for modules
    set_om(debug=glob.debug)

    uicore.print_banner(glob.gom)

    # Check args and enable debug if requested
    if not core.check_args():
        uicore.usage(glob.gom)
        sys.exit(0)

    # Remove scapy output messages
    if hasScapy:
        if not glob.debug:
            scapy.conf.verb = 0
        else:
            scapy.conf.verb = 1

    # Create .inguma directory.
    core.create_profile_dir()

    readCommands()

    # Main initialization.
    inguma_init()

    # Display banner.
    glob.gom.echo("\nType 'help' for a short usage guide.")

    # Set autocompletion and load commands history
    setup_auto_completion()
    main_loop()
    if glob.http_server:
        glob.http.terminate()

if __name__ == "__main__":
    try:
        main()
    except:
        # We have to stop the HTTP server just in case.
        if glob.http_server:
            glob.http.terminate()

        import traceback
        traceback.print_exc()
