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

def create_kb_file(outfile, poc):
    """
    Call dis.py to create .kb file in given 'outfile'

    @param outfile: kdb file to write
    @type: str
    @param poc: 
    @type: str
    """
    os.system(DIS_PATH  + " -s=" + outfile + ".kb " + poc)

def create_db_file(outfile, poc):
    """
    Call dis.py to create .sqlite file

    @param outfile: sqlite file to write
    @type: str
    @param poc: 
    @type: str
    """
    os.system(DIS_PATH + " -sdb=" + outfile + ".sqlite " + poc )

def uploadFile(poc):
    '''Everything starts here...'''

    # Clean input file
    theFile = poc.split('/')[-1]
    # Let's call dis.py to generate pickle with disassembly
    create_kb_file(theFile, poc)
    # And also the sqlite one...
    create_db_file(theFile, poc)
    #Move file to data directory
    try:
        shutil.move("%s.kb" % theFile, DBS_PATH)
    except shutil.Error:
        print "%s.kb already existed it will be overwritten" % theFile
        os.unlink("%s%s.kb" % (DBS_PATH, theFile))
        create_kb_file(theFile, poc)
    finally:
        shutil.move("%s.kb" % theFile, DBS_PATH)
    try:
        shutil.move("%s.sqlite" % theFile, DBS_PATH)
    except shutil.Error:
        print "%s.sqlite already existed it will be overwritten" % theFile
        os.unlink("%s%s.sqlite" % (DBS_PATH, theFile))
        create_db_file(theFile, poc)
    finally:
        shutil.move("%s.sqlite" % theFile, DBS_PATH)
    print "Binary " + poc + " disassembled!"

def generate_graphs(poc):
    '''generate graph for each function'''

    # Add dis/ to sys.path to access asmclasses
    sys.path.append('dis/')

    data = _load_dasm(poc)
    theFile = poc.split('/')[-1]
    try:
        os.mkdir(DBS_PATH + theFile)
    except OSError:
        dir = "%s/%s" % (DBS_PATH, theFile)
        [os.unlink("%s/%s" % (dir, f)) for f in os.listdir(dir)]
        os.rmdir(dir)
        os.mkdir(dir)
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
    file = open(DBS_PATH + theFile + '.kb', 'r')
    data = pickle.load(file)
    file.close()

    return data

def get_dot_code(func, poc):
    ''' Get dotcode for function'''

    theFile = poc.split('/')[-1]
    f = open(DBS_PATH + theFile + '/' + func + '.dot', 'r')
    dotcode = f.read()
    f.close()

    return dotcode
