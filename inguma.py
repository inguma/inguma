#!/usr/bin/python

"""
Inguma Penetration Testing Toolkit 0.2
Copyright (c) 2006, 2007, 2008 Joxean Koret, joxeankoret [at] yahoo.es
Copyright (c) 2009 - 2011 Hugo Teso, hugo.teso [at] gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
import sys
import stat
import time
import pickle

from reports import generateReport

from lib.core import isIpAddr4
from lib.printwrapper import CPrintWrapper

# Import Output Manager
import lib.ui.om as om

try:
    import scapy.all as scapy

    hasScapy = True
except:
    hasScapy = False

from discover import *
from gather import *
from rce import *

isGui = False

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
ports = []
ostype = 1
payload = 2
listenPort = 4444
hash = ""

try:
    f = file("data/ports", "r")
    
    for line in f:
        ports.append(int(line))

except:
    print sys.exc_info()[1]
    pass

# Colors
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

#global user_data

user_data = {}
user_data["target"] = ""
user_data["targets"] = []
user_data["port"] = ""
user_data["covert"] = 0
user_data["timeout"] = 5
user_data["user"] = ""
user_data["password"] = ""
user_data["waittime"] = ""
user_data["services"] = []
user_data["hosts"] = []
user_data["wizard"] = []
user_data["base_path"] = os.path.dirname (sys.argv[0])
user_data["dict"] = user_data["base_path"] + "data" + os.sep + "dict"
user_data["ports"] = ports
user_data["isGui"] = False

GLOBAL_VARIABLES = """
global target; global targets; global port; global covert; global timeout; global waittime; global debug
global otherTargets; global services; global wizard; global user_data; global user;
global password; global domain; global payload; global ostype; global command; 
global listenPort; global ignore_host;
"""

debug = False
version = "0.2"
prompt = "inguma> "

commands = {}
discovers = []
gathers = []
rces = []
fuzzers = []
brutes = []
classes = []
others = []
exploits = []

vars = globals()

def printBanner():
    print "Inguma Version",version
    print "Copyright (c) 2006-2008 Joxean Koret <joxeankoret@yahoo.es>"
    print "Copyright (c) 2009-2011 Hugo Teso <hugo.teso@gmail.com>"
    print

def usage():
    print "Usage:", sys.argv[0], " <flag>"
    print
    print "-d      Show debug information"
    print "-h      Show this help and exit"
    print

def checkArgs():

    global debug

    for arg in sys.argv:
        if arg.lower() == "-d" or arg.lower() == "-debug":
            debug = True
        elif arg.lower() == "-h" or arg.lower() == "--help":
            usage()
            sys.exit(0)

    return True

def debugPrint(*args):

    global debug

    if not debug:
        return

    outStr = ""
    for x in args:
        outStr += str(x) + " "

    print outStr

def loadModule(path, atype, marray, bLoad = True):

    global GLOBAL_VARIABLES

    sys.path.append(path)

    for f in os.listdir(path):
        if f.startswith("_") or f.endswith("pyc"):
            continue
        
        if bLoad:
            f = f[:f.find(".")]
        else:
            if not stat.S_ISDIR(os.stat(path + os.sep + f)[stat.ST_MODE]):
                continue

        debugPrint("Loading " + atype + " module",f)

        if bLoad:
            try:
                if f.isalnum():
                    exec("import " + f)
                    exec("global " + marray)
                else:
                    print "The, supposed, module %s appears to be a non valid module" % f
                    continue

                try:
                    if "globals" in dir(eval(f)):
                        moduleGlobals = eval(f).globals

                        for aGlobal in moduleGlobals:
                            if aGlobal.isalnum():
                                exec ("global " + aGlobal)
                                GLOBAL_VARIABLES += "global " + aGlobal + ";"
                            else:
                                print "The, supposed, global variable of the module %s doesn't appears to be a variable..." % f
                                print "The suspicious code:"
                                print aGlobal
                except:
                    debugPrint(FAIL + "Error loading global variables" + ENDC)
                    print sys.exc_info()[1]

                exec(marray + ".append(eval(f))")

                commands[eval(f).name] = eval(f)
                
                if atype == "unknown":
                    if eval(f).type == "gather":
                        exec("gathers.append(eval(f))")
                    elif eval(f).type == "discover":
                        exec("discovers.append(eval(f))")
                    elif eval(f).type == "rce":
                        exec("rces.append(eval(f))")
                    elif eval(f).type == "fuzzers":
                        exec("fuzzers.append(eval(f))")
                    elif eval(f).type == "brute":
                        exec("brutes.append(eval(f))")

                for x in dir(eval(f)):
                    if x.startswith("C"):
                        classes.append(f + "." + x)
                        debugPrint("Registering class",f + "." + x)
                        debugPrint("Creating a base object ....")

                        obj = eval(f + "." + x +"()")
                        del obj
            except:
                debugPrint(FAIL + "Error loading module",f,":" + ENDC,sys.exc_info()[1])
                if f.lower().find("smtp") > -1:
                    raise
        else:
            if f.isalnum():
                eval(marray).append(f)
            else:
                print WARNING + "The, supposed, module %s appears to be a non valid module" + ENDC % f
                continue

def readDiscover():
    global commands
    
    path = "modules" + os.sep + "discover"
    loadModule(path, "discover", "discovers")

def readGather():
    global commands
    
    path = "modules" + os.sep + "gather"
    loadModule(path, "gather", "gathers")

def readRce():
    global commands
    
    path = "modules" + os.sep + "rce"
    loadModule(path, "rce", "rces")

def readBrute():
    global commands
    
    path = "modules" + os.sep + "brute"
    loadModule(path, "brute", "brutes")

def readExploits():
    global commands
    
    path = "modules" + os.sep + "exploits"
    loadModule(path, "exploit", "exploits")

def readFuzzers():
    global commands
    
    path = "modules" + os.sep + "fuzzers"
    loadModule(path, "fuzz", "fuzzers")

def readCommands():
    debugPrint("Reading modules ... ")
    debugPrint()
    readDiscover()
    readGather()
    readRce()
    readFuzzers()
    readBrute()
    readExploits()

def showHelp():
    print
    print "+----------------------------------------------------------------------------+"
    print "| load kb                 | Load the knowledge base                          |"
    print "| save kb                 | Save the knowledge base                          |"
    print "| clear kb                | Clear the knowledge base's data                  |"
    print "| show kb                 | Shows the knowledge base's data (very verbose)   |"
    print "| report                  | Generate a report                                |"
    print "|----------------------------------------------------------------------------|"
    print "| show discover           | Show discover modules                            |"
    print "| show gather             | Show gather modules                              |"
    print "| show rce                | Show RCE modules                                 |"
    print "| show fuzzers            | Show fuzzing modules                             |"
    print "| show exploits           | Show available exploits                          |"
    print "| show brute              | Show brute force modules                         |"
    print "| show options            | Show options                                     |"
    print "| payload                 | Show the supported OS types and payloads         |"
    print "| info <exploit>          | Show additional information about an exploit     |"
    print "|----------------------------------------------------------------------------|"
    print "| autoscan                | Perform an automatic scan                        |"
    print "| autoexploit             | Exploit wizard                                   |"
    #print "fuzz                     Fuzz a target (Unavailable)"
    print "| exploit                 | Run an exploit against a target or targets       |"
    print "|----------------------------------------------------------------------------|"
    print "| use <mod>               | Load all modules from a directory                |"
    print "| ! <command>             | Run an operating system command                  |"
    print "| exit | quit             | Exit from Inguma                                 |"
    print "| help                    | Show this help                                   |"
    print "|----------------------------------------------------------------------------|"

    if hasScapy:
        print "|                                                                            |"
        print "| To see registered scapy commands execute command 'scapy.lsc()'             |"
        print "|----------------------------------------------------------------------------|"
        print "|                                                                            |"
        
        """
        try:
            exec("scapy.lsc()")
            print
        except:
            print "Error getting scapy commands :( No scapy support?"
            print sys.exc_info()[1]
        """

        print "| NOTE: Remember to use 'scapy.<function>' to use.                           |"
        print "|                                                                            |"
        print "| Type 'scapy.interact()' to start an scapy session.                         |"
        print "| To get help for scapy commands type help(scapy.<scapy command>).           |"
        print "+----------------------------------------------------------------------------+"
    else:
        print

    print
    print "Any other typed text will be evaled as a Python expression."
    print

def exploitWizard():

    global target
    global port
    global covert
    global timeout
    global waittime
    global wizard

    i = 0

    global target
    global isGui

    if target == "" or target == None:
        if not isGui:
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
    if not isGui:
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

    mType = commands[cmd].type
    vars = globals()

    if mVars != None:
        for x in mVars:
            vars[x] = mVars[x]

    if mType in ["gather", "exploit", "brute", "fuzzer",  "rce"]:
        ret = runGatherModule(vars, commands[cmd], user_data, gom)
    elif mType == "discover":
        ret = runModule(vars, commands[cmd], user_data, gom)
    else:
        print "Unknown module type '" + str(mType) + "'"

    if ret:
        user_data = ret
    
    return ret

def showInfo(cmd):

    global exploits
    global classes

    for mod in exploits:
        if mod.name == cmd.lower():
            try:
                print "Information"
                print "-----------"
                print
                print "Name:", mod.name
                print "Type:",mod.category
                print "Discoverer:",mod.discoverer
                print "Module author:", mod.author
                print "Description:", mod.brief_description
                print "Affected versions:"
                print 
                for affected in mod.affects:
                    print "\t",affected
                print
                print "Notes:\r\n",mod.description
                print
                print "Patch information:", mod.patch
                print
            except:
                print "Error getting module's information:",sys.exc_info()[1]

            return

    for command in commands:
        if command == cmd.lower():
            try:
                module = commands[command]
                if module.__name__.isalnum():
                    obj = eval("module."+module.__name__ +"()")
                    obj.help()
            except:
                print "Module has no help information"

            return

    print "Exploit does not exists"

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

                if commands.has_key(word.lower()):
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
                loadModule(word, "unknown", "others")
                return True
            elif mode == "info":
                showInfo(word)
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

    for x in exploits:
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

def clearKb():
    global user_data
    global target

    user_data = {}
    user_data["target"] = ""
    user_data["port"] = ""
    user_data["covert"] = 0
    user_data["timeout"] = 5
    user_data["user"] = ""
    user_data["password"] = ""
    user_data["waittime"] = ""
    user_data["services"] = []
    user_data["wizard"] = []
    user_data["base_path"] = os.path.dirname (sys.argv[0])

def saveKb(theFile = None):
    global user_data
    global target

    try:
        res = raw_input("Filename [data.kb]: ")
        
        if res == "" or res == None:
            res = "data.kb"

        if target != "":
            user_data["target"] = target

        output = open(res, 'wb')
        pickle.dump(user_data, output)
        output.close()
    except:
        print "Error loading knowledge base:", sys.exc_info()[1]

def loadKb():
    global user_data
    global target

    try:
        print "* Warning! Warning! Warning! Warning! Warning! Warning! *"
        print "*** Never load kb files received from untrusted sources ***"
        res = raw_input("Filename [data.kb]: ")

        if res == "":
            res = "data.kb"

        input = open(res, 'r')
        user_data = pickle.load(input)

        if target == "":
            if user_data.has_key("target"):
                print "Setting target (%s)" % user_data["target"]
                target = user_data["target"]

        input.close()
    except:
        print "Error loading knowledge base:", sys.exc_info()[1]

def showKb():
    global user_data
    
    for x in user_data:
        if type(user_data[x]) == str or type(user_data[x]) == int or type(user_data[x]) == float or type(user_data[x]) == bool:
            print x, "->", user_data[x]
        else:
            print str(x) + ":"
            data = user_data[x]

            for y in data:
                print "  ", y

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
    global isGui
    global sid
    global ignore_host
    global ports

    oldfile = sys.stdout
    f = None

    try:
        wizard = False

        if target == "" and not isGui:
            target = raw_input("Target host or network: ")

        if not isGui:
            guestPasswords = raw_input("Brute force username and passwords (y/n)[n]: ")
        else:
            guestPasswords = guest
            print "Guest passwords set to", guest

        if guestPasswords.lower() == "y" or guestPasswords.lower() == "yes":
            guestPasswords = True
        else:
            guestPasswords = False

        if not isGui:
            autoFuzz = raw_input("Automagically fuzz available targets (y/n)[n]: ")
        else:
            autoFuzz = fuzz

        if autoFuzz.lower() == "y" or autoFuzz.lower() == "yes":
            autoFuzz = True
        else:
            autoFuzz = False

        if not isGui:
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

            if not isIpAddr4(target) and target.lower().strip(" ") != "localhost":
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

                #showLaunch("portscan", "Port scanning target %s\n" % target)
                showLaunch("tcpscan", "TCP scanning target %s\n" % target)
                
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

def mainLoop():

    global prompt
    global target
    global port
    global covert
    global timeout
    global waittime
    global oldPrompt
    global prevRes

    oldPrompt = ""
    prevRes = ""

    while 1:
        try:
            res = raw_input(prompt)
        except KeyboardInterrupt:
            print "Aborted."
            sys.exit(0)
        except EOFError:
            print "Exit."
            sys.exit(0)
        except:
            print "INTERNAL ERROR:",sys.exc_info()[1]

        if res.lower() == "quit" or res.lower() == "exit" or res.lower() == "urten": # :P
            break
        else:
            runInterfaceCommand(res)

def runInterfaceCommand(res):

    global prompt
    global oldPrompt
    global prevRes
    global target
    global port
    global covert
    global timeout
    global waittime
    global debug

    if res.lower() == "help":
        showHelp()
    elif res == "" and prevRes == "":
        pass
    elif res == "save kb":
        saveKb()
    elif res == "clear kb":
        clearKb()
    elif res == "load kb":
        loadKb()
    elif res == "show kb":
        showKb()
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

            exec(GLOBAL_VARIABLES + res)

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
                exec(GLOBAL_VARIABLES + res)
        except:
            print "Internal error.",sys.exc_info()[1]
            
            if debug:
                raise

def printPayloads():
    global payload

    print "Payloads"
    print "--------"
    print
    print "ostype:"
    print
    print "1) Linuxx86Syscall"
    print "2) FreeBSDx86Syscall"
    print "3) OpenBSDx86Syscall"
    print "4) Solarisx86Syscall"
    print
    print "payload:"
    print
    print "1) runcommand"
    print "2) bindshell"
    print "3) connectback"
    print "4) xorbindshell"
    print 
    print "Payload arguments:"
    print
    print "1) runcommand"
    print
    print "command = <command to run>"
    print
    print "2) bindshell, connectback, xorbindshell"
    print
    print "listenPort = <remote or local listening port>"
    print 
    print 'NOTE: "listenPort" will be the local port to connect back or the remote port to connect.'
    print

def saveHistory():
    import readline
    historyPath = os.path.expanduser("inguma_history")
    readline.write_history_file(historyPath)

def loadHistory():
    import readline
    historyPath = os.path.expanduser("inguma_history")
    
    if os.path.exists(historyPath):
        readline.read_history_file(historyPath)

def set_om():
    # Set OM type
    global gom
    if isGui == True:
        gom = om.OutputManager('gui')
    else:
        gom = om.OutputManager('console')

def setupAutoCompletion():
    global commands

    try:
        import atexit
        import readline
        import rlcompleter

        readline.set_completer(rlcompleter.Completer(commands).complete)
        readline.parse_and_bind("tab: complete")

        loadHistory()
        atexit.register(saveHistory)
    except:
        print sys.exc_info()[1]

def main():

    if hasScapy:
        scapy.conf.verb = 0

    if not checkArgs():
        usage()
        sys.exit(0)

    set_om()
    readCommands()
    setupAutoCompletion()
    mainLoop()

if __name__ == "__main__":
    printBanner()
    main()
