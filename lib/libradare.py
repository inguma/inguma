import sys, os

class Radare():

    def __init__(self):
        try:
            print os.popen('radare -V').read()
        except:
            print "Radare not found, install radare (http://www.radare.org)"

    def fileid(self, file=""):
        print os.popen("rabin -I " + file).read()

    def entrypoint(self, file=""):
        print os.popen('rabin -vve ' + file).read()

    def imports(self, file=""):
        print os.popen('rabin -vvi ' + file).read()

    def symbols(self, file=""):
        print os.popen('rabin -vvs ' + file).read()

    def libraries(self, file=""):
        print os.popen('rabin -l ' + file).read()

    def strings(self, file=""):
        print os.popen('rabin -zv ' + file).read()

    def sections(self, file=""):
        print os.popen('rabin -Svv ' + file).read()

    def rasm(self, data=""):
        print os.popen('rasm ' + data).read()

    def rdasm(self, data=""):
        print os.popen('rasm -d ' + data).read()

    def rasc_list(self):
        print os.popen('rasc -L').read()

    def rasc_gen(self, name="", cmd="", format="", port="", host=""):
        options=""

        if name != '':
            options = options + '-i ' + name

        if format == 'C':
            options = options + ' -c'
        elif format == 'string':
            options = options + ' -e'
        elif format == 'hex':
            options = options + ' -x'
        print "Options: " + options
        print os.popen('rasc ' + options).read()

    def radare(self, target='', debug=False, gui=False):
        if gui:
            options='gradare '
        else:
            options='radare '

        if debug:
            options = options + '-d '

        os.system(options + target)
