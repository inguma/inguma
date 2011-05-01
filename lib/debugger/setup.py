import sys
from distutils.core import setup, Extension

# To gen docs:
# /opt/local/Library/Frameworks/Python.framework/Versions/2.4/bin/epydoc --html -o docs -c docs/epydoc.css vtrace

packages = [
    'vtrace','vtrace.platforms','vtrace.archs','vtrace.tools',
    'envi','envi.disassemblers','envi.disassemblers.libdisassemble',
    'cobra',
    'Elf',
    'vstruct',
    'vwidget',
    'vdb','vdb.extensions','vdb.gui','vdb.gui.extensions',
]

mods = []
pkgdata = {}

if sys.platform == "darwin":
    mods.append(Extension('mach', sources = ['mach/machmodule.c','mach/task.c', 'mach/thread.c', 'mach/utility.c']))

# Install the dbghelp library
pkgdata["vtrace"] = ["platforms/dbghelp.dll","platforms/symsrv.dll"]
pkgdata["vdb"] = ["configs/*","glade/*"]

setup  (name        = 'VDB',
        version     = '2.0',
        description = 'VDB',
        packages  = packages,
        package_data = pkgdata,
        scripts = ["vdbbin",],
        ext_modules = mods,
       )


