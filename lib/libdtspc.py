#!/usr/bin/python

import socket

def getDtspcInformation(target, port = 6112):

    buf  = "\x30\x30\x30\x30\x30\x30\x30\x32"
    buf += "\x30\x34\x30\x30\x30\x64\x30\x30"
    buf += "\x30\x31\x20\x20\x34\x20\x00\x72"
    buf += "\x6f\x6f\x74\x00\x00\x31\x30\x00"
    buf += "\x00"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target, int(port)))
    s.send(buf)
    res = s.recv(4096)
    ret = {}

    if len(res) > 64:
        res = res.strip("\x00")
        fields = res.split("\x00")
        boxFields = fields[len(fields)-1].split(":")

        ret["hostname"] = boxFields[0]
        ret["os"]       = boxFields[1]
        ret["version"]  = boxFields[2]
        ret["arch"]     = boxFields[3]

    s.close()
    return ret

