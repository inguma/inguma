##      CHexDump.py
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

from lib.module import CIngumaRCEModule

name = "hexdump"
brief_description = "A simple HexDump utility"
type = "rce"

globals = ['dumpSize', ]

class CHexDump(CIngumaRCEModule):
    """ Module to do an hexadecimal dump of a file. """

    startOffset = 0
    dumpSize = -1
    bytesPerGroup = 4
    groupsPerLine = 5
    spacesBetweenGroup = 1
    showOffset = 'y'
    offsetInHex = 'y'
    printAscii = 'y'

    def help(self):
        """ This is the entry point for info <module> """
        self.gom.echo("target = < Target file >")
        self.gom.echo("dumpSize = < Size of data to dump >")

    def run(self):
        """ This is the main entry point of the module """

        self.gom.echo("dumpSize %s" % self.dumpSize)
        try:
            file = open(self.target, 'rb')
        except:
            self.gom.echo("Cannot open file %s" % self.target)
            return False

        # if self.dumpSize was not provided, make it size of file
        if (self.dumpSize < 0):
            try:
                file.seek(0, 2)
                self.dumpSize = file.tell()
            except:
                self.gom.echo('Cannot determine size of %s' % self.target)
                return False

        try:
            file.seek(self.startOffset)
        except:
            self.gom.echo('Cannot use startOffset %d in %s' % (self.startOffset, self.target))
            return False

        maxReadBlock = self.bytesPerGroup * self.groupsPerLine
        currByteOffset = file.tell()
        bytesRead = 0

        while self.dumpSize > 0:

            if (self.dumpSize > maxReadBlock):
                currReadblock = maxReadBlock
            else:
                currReadblock = self.dumpSize

            data = file.read(currReadblock)
            bytesRead = len(data)

            if bytesRead == 0:
                break

            self.dumpSize -= bytesRead
            lineBuffer = ''

            if (self.showOffset == 'y'):
                if (self.offsetInHex == 'y'):
                    lineBuffer += '0x%08x:' % currByteOffset
                else:
                    lineBuffer += '%8d:' % currByteOffset
                lineBuffer += str(' ') * self.spacesBetweenGroup

            for index in range(maxReadBlock):
                if index > 0 and index % self.bytesPerGroup == 0:
                    lineBuffer += '%s' % str(' ') * self.spacesBetweenGroup
                if index < bytesRead:
                    lineBuffer += '%02x' % ord( data[index] )
                else:
                    lineBuffer += '  '

            # self.gom.echo(ascii?)
            if (self.printAscii == 'y'):
                lineBuffer += '%s|%s' % (str(' ') * self.spacesBetweenGroup, str(' ') * self.spacesBetweenGroup)
                for index in range(bytesRead):
                    if (data[index] >= '!' and data[index] <= '~'):
                        lineBuffer += data[index]
                    else:
                        lineBuffer += "'"

            try:
                self.gom.echo(lineBuffer)
            except:
                break

            currByteOffset += bytesRead

        file.close()
