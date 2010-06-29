##      rcecore.py
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

import sys, os, shutil
import cPickle as pickle
from config import *

def uploadFile(poc):
    '''Everything starts here...'''

    DIS_PATH="dis/dis.py"

    # Clean input file
    theFile = poc.split('/')[-1]
    # Let's call dis.py to generate pickle with disassembly
    os.system(DIS_PATH  + " -s=" + theFile + ".kb " + poc )
    # And also the sqlite one...
    os.system(DIS_PATH + " -sdb=" + theFile + ".sqlite " + poc )
    #Move file to data directory
    shutil.move(theFile + '.kb', 'dis/navigator/dbs/')
    shutil.move(theFile + '.sqlite', 'dis/navigator/dbs/')
    print "Binary " + poc + " disassembled!"

def generate_graphs(poc):
    '''generate graph for each function'''

    # Add dis/ to sys.path to access asmclasses
    sys.path.append('dis/')

    GEN_PATH = "dis/printblocks.py"

    data = _load_dasm(poc)
    theFile = poc.split('/')[-1]
    os.mkdir('dis/navigator/dbs/' + theFile)
    for function in data[1]:
        print "Creating graph for function:", function.name
        os.system(GEN_PATH + " dis/navigator/dbs/" + theFile + ".kb " + function.name)
        shutil.move(function.name + ".dot", "dis/navigator/dbs/" + theFile)
        shutil.move(function.name + ".jpg", "dis/navigator/dbs/" + theFile)

def get_complete_dasm(poc):
    '''loads dasm from pickle and returns complete dasm'''

    buf = ''

    data = _load_dasm(poc)
    for element in data[1]:
        #for function in element:
        buf += '\n'
        buf += '; FUNCTION ' + element.name + '\n'
        for line in element.lines:
            buf += '0x' + str(line.address) + '\t\t' + str(line.code)
            if line.description:
                buf += '\t\t' + str(line.description).rstrip('\n') + '\n'
            else:
                buf += "\n"

    return buf, data[1]
        

def _load_dasm(poc):
    '''Loads pickle and returns data'''

    # Add dis/ to sys.path to access asmclasses
    sys.path.append('dis/')

    theFile = poc.split('/')[-1]
    file = open('dis/navigator/dbs/' + theFile + '.kb', 'r')
    data = pickle.load(file)
    file.close()

    return data

def get_dot_code(func, poc):
    ''' Get dotcode for function'''

    theFile = poc.split('/')[-1]
    f = open('dis/navigator/dbs/' + theFile + '/' + func + '.dot', 'r')
    dotcode = f.read()
    f.close()

    return dotcode
