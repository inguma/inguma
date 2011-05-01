
def vdbExtension(vdb, trace):
    vdb.setConfig("Aliases","db","mem -F Bytes")
    vdb.setConfig("Aliases","dw","mem -F u_int_16")
    vdb.setConfig("Aliases","dd","mem -F u_int_32")
    vdb.setConfig("Aliases","dq","mem -F u_int_64")

