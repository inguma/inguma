import sys

#------------------------------------------------------------------------------------------------------------------

def ascii2binary(ascii, one='1', zero='0'):
	output = ""
	for x in range(len(ascii)):
		temp = ""
		byt = ord(ascii[x])
		for i in range(8,0,-1):
			c = byt / (2**(i-1))
			#print ("%d / %d: %d"%(byt,2**(i-1),c))
			if (c == 1):  byt -= (2**(i-1))
			temp += (zero, one)[c]
				
		output += temp
	return output


def bin2ascii(binarystr,one='1', zero='0'):
    output = ""
    x=0
    while (x < len(binarystr)-1):
        byt = 0
        offset = 0
        for ci in xrange(8):
            try:
                i = binarystr[x+offset+ci]
                while i not in [one, zero]:
                    offset += 1
                    i = binarystr[x+offset+ci]
                byt *= 2
                if i == one:  
                    byt += 1
            except Exception,e:
                print("Error '%s'...  Problems in char %s.  Not binary?  Should be either a '0' or a '1'"%(e,i))
                
        output += chr(byt)
        x += 8 + offset
    return output

#------------------------------------------------------------------------------------------------------------------

def ascii2hex(ascii):
	output = ""
	for x in range(len(ascii)):
		output += "%.02x"%ord(ascii[x])
	return output

def hex2ascii(inp):
    outputline = ""
    for i in range(len(inp)/2):
      outputline += chr(int(inp[(i*2):(i*2)+2],16))
    return outputline

#------------------------------------------------------------------------------------------------------------------

def ascii2octal(ascii):
	output = ""
	for x in range(len(ascii)):
		output += "%.03o"%ord(ascii[x])
	return output

def octal2ascii(inp):
    outputline = ""
    for i in range(len(inp)/3):
      outputline += chr(int(inp[(i*3):(i*3)+3],8))
    return outputline
