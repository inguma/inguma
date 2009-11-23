#!/usr/bin/python

import os
import sys

import hashlib
import base64
import binascii

from core import str2uni

"""
Support for haslib (Version >= 2.5)
"""
hasHashlib = False
pyVersion = int(sys.version.split(" ")[0][:3].replace(".", ""))

if pyVersion >= 25:
    try:
        import hashlib
        hasHashlib = True
    except:
        pass

hasCrypt = False

try:
    import crypt
    hasCrypt = True
except:
    hasCrypt = False

class CAutoCrack:
    password = ""
    hash = ""
    salt = ""

    algorithm = []
    debugLevel = 1
    
    _hash = ""

    def clean(self, x):
        # Remove the most common uninteresting characters
        return x.replace(" ", "").replace("\r", "").replace("\n", "").replace("\t", "").replace("\x00", "").replace("\b", "")

    def pCompare(self, a, b):

        if a == b:
            return 0

        tmpPassword = self.clean(a)
        tmpHash = self.clean(b)

        if tmpHash == tmpPassword:
            return 0

        if self.salt != "":
            if a + self.salt.lower() == b or b + self.salt.lower() == a or self.salt.lower() + a == b or self.salt.lower() + b == a:
                return 0

        if tmpHash.find(tmpPassword) > -1:
            return 1

        if tmpHash == tmpPassword[::-1]:
            return 2

        return -1

    def printMsg(self, ret,msg):
        if ret == 0:
            print "  --> Uses %s" % msg
        elif ret == 1 and self.debugLevel > 0:
            if not msg in ["Base32", "Base64", "BinAscii"]:
                print "  --> Appears to use %s?" % msg
        elif ret == 2:
            print "  --> Uses %s (reverse)" % msg

    def tryMd5(self, password):
        tmpPassword = hashlib.md5(password).hexdigest()
        tmpHash = self.hash
        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "MD5")
        
        return ret

    def getMd5(self, password):
        return hashlib.md5(password).hexdigest()

    def trySha1(self, password):
        tmpPassword = hashlib.sha1(password).hexdigest().lower()
        tmpHash = self.hash.lower()

        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "SHA1")
        return ret
    
    def getSha1(self, password):
        return hashlib.sha1(password).hexdigest()

    def tryCrypt(self, password):
        tmpPassword = crypt.crypt(password, self.hash).lower()
        tmpHash = self.hash.lower()

        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "Crypt")
        return ret

    def getCrypt(self, password):
        return crypt.crypt(password, self.hash)

    def tryBase64(self, password):
        tmpPassword = base64.b64encode(password).lower()
        tmpHash = self.hash.lower()

        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "Base64")
        return ret

    def getBase64(self, password):
        return base64.b64encode(password)

    def tryBase32(self, password):
        tmpPassword = base64.b32encode(password).lower()
        tmpHash = self.hash.lower()

        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "Base32")
        return ret

    def getBase32(self, password):
        return base64.b32encode(password)

    def tryBinAscii(self, password):
        tmpPassword = base64.binascii.b2a_hex(password).lower()
        tmpHash = self.hash.lower()

        ret = self.pCompare(tmpPassword, tmpHash)
        self.printMsg(ret, "BinAscii")
        return ret

    def getBinAscii(self, password):
        return base64.binascii.b2a_hex(password)

    def method00Plain(self, tries, gets):
        ret = self.doMethodPlain(tries, gets, self.password)
        if not ret:
            ret = self.doMethodPlain(tries, gets, str2uni(self.password), True)
            if ret:
                self.algorithm.append("unicode")

        return ret

    def doMethodPlain(self, tries, gets, password, isUnicode = False):
        for property in tries:
            if isUnicode:
                if not self.supportUnicode(property):
                    continue

            # Try encrypting it one time
            fTry = eval("self." + property)
            ret = fTry(password)

            if ret == 0:
                self.algorithm.append(property[3:])
                return True
            elif ret == 1:
                pass # Continue, we are unsure...

    def method98TwoTimes(self, tries, gets):
        ret = self.doMethodTwoTimes(tries, gets, self.password)
        if not ret:
            ret = self.doMethodTwoTimes(tries, gets, str2uni(self.password), True)
            if ret:
                self.algorithm.append("unicode")

        return ret

    def supportUnicode(self, method):
        if method.lower()[3:].find("crypt") == 0:
            return False
        
        return True

    def doMethodTwoTimes(self, tries, gets, password, isUnicode = False):
        for property in tries:
            fGet = eval("self." + property.replace("try", "get"))
            
            if isUnicode:
                if not self.supportUnicode(property):
                    continue

            tmp = fGet(password)

            # Encrypt the hash with every hash algorithm
            for get in tries:
                if isUnicode:
                    if not self.supportUnicode(get):
                        continue

                fGet = eval("self." + get)
                ret = fGet(tmp)

                if ret == 0:
                    self.printMsg(ret, property[3:].upper())
                    self.algorithm.append(property[3:])
                    self.algorithm.append(get[3:])
                    self.algorithm.reverse()
                    return True
                elif ret == 1:
                    self.printMsg(ret, property[3:].upper())
                    pass

            #FIXME: Fixme immediately!!!!!!!!
            fGet = eval("self." + property.replace("try", "get"))
            isUnicode = True
            tmp = fGet(str2uni(password))

            # Encrypt the hash with every hash algorithm (uses Unicode)
            for get in tries:
                fGet = eval("self." + get)
                ret = fGet(tmp)

                if ret == 0:
                    self.printMsg(ret, property[3:].upper())
                    self.algorithm.append(property[3:])
                    self.algorithm.append("unicode")
                    self.algorithm.append(get[3:])
                    self.algorithm.reverse()
                    return True
                elif ret == 1:
                    self.printMsg(ret, property[3:].upper())
                    pass
            #FIXME: Fixme immediately!!!

    def method99SaltInHash(self, tries, gets):
        ret = self.doMethodSaltInHash(tries, gets, self.password)
        if not ret:
            ret = self.doMethodSaltInHash(tries, gets, str2uni(self.password), True)
            if ret:
                self.algorithm.append("unicode")

        return ret

    def doMethodSaltInHash(self, tries, gets, password, isUnicode = False):
        # Plain text salt
        for i in range(0, len(self.hash)):
            salt = self.hash[0:i]
            self.salt = salt
            ret = self.doMethodPlain(tries, gets, password + salt, True)
            if not ret:
                # Unicode text salt
                ret = self.doMethodPlain(tries, gets, str2uni(password + self.hash[0:i]), True)
                if ret:
                    self.algorithm.append("unicode")
                    self.algorithm.append("salt = (hash[0:%d)" % i)
                    return ret
            else:
                self.algorithm.append("salt = (hash[0:%d)" % i)
                return ret

        # Reverse search
        for i in range(0, len(self.hash)):
            salt = self.hash[len(self.hash)-i:]
            self.salt = salt
            ret = self.doMethodPlain(tries, gets, password + salt, True)
            if not ret:
                ret = self.doMethodPlain(tries, gets, str2uni(salt), True)
                if ret:
                    self.algorithm.append("unicode")
                    self.algorithm.append("salt = (unicode(hash[len(hash)-%d:len(hash)]))" % i)
                    return ret
            else:
                self.algorithm.append("salt = (hash[len(hash)-%d:])" % i)
                return ret

        # FIXME: Fixme immediately!!!!!!
        for i in range(0, len(self.hash)):
            salt = self.hash[len(self.hash)-i:]
            self.salt = salt
            try:
                salt = binascii.unhexlify(salt)
            except:
                continue

            ret = self.doMethodPlain(tries, gets, password + salt, True)
            if not ret:
                try:
                    ret = self.doMethodPlain(tries, gets, str2uni(password + binascii.unhexlify(self.hash[0:i])), True)
                    if ret:
                        self.algorithm.append("unicode")
                        self.algorithm.append("salt = (hex2bin(hash[0:%d]))" % i)
                        return ret
                except:
                    if str(sys.exc_info()[1]) == "Non-hexadecimal digit found":
                        pass # Just ignore
                    else:
                        raise
            else:
                self.algorithm.append("salt = (hex2bin(hash[0:%d]))" % i)
                return ret

        # Reverse search
        for i in range(0, len(self.hash)):
            salt = self.hash[len(self.hash)-i:]
            self.salt = salt
            try:
                salt = binascii.unhexlify(salt)
            except:
                continue

            ret = self.doMethodPlain(tries, gets, password + salt, True)
            if not ret:
                ret = self.doMethodPlain(tries, gets, str2uni(password + self.hash[0:i]), True)
            else:
                return ret
        
        self.salt = ""

    def run(self):
    
        self.algorithm = []

        tries = []
        gets = []

        for property in dir(self):
            if property.find("try") == 0:
                tries.append(property)
            elif property.find("get") == 0:
                gets.append(property)
        
        ret = self.realRun(tries, gets)
        
        if ret:
            return ret

        self._hash = self.hash
        for i in range(1, len(self.hash)):
            self.hash = self._hash[i:]

        print "[+] Mal rollito ... "

    def realRun(self, tries, gets):
        for x in dir(self):
            if x.find("method") == 0:
                f = eval("self." + x)
                if f(tries, gets):
                    self.printMsg(0, x[8:])
                    return True

def allTests():
    objCrack = CAutoCrack()
    objCrack.debugLevel = 0
    # Note: The common password for the test is "test" :)
    objCrack.password = "test"

    print "[+] MD5 based hash"
    objCrack.hash = "098f6bcd4621d373cade4e832627b4f6"
    objCrack.run()

    print "[+] SHA1 based hash"
    objCrack.hash = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
    objCrack.run()
    
    print "[+] Unix Crypt based"
    objCrack.hash = "$1$Zfn8aEtA$wYhuRA9cKWz3Imi9LukZ6/"
    objCrack.run()
    
    print "[+] Base64 based"
    objCrack.hash = "dGVzdA=="
    objCrack.run()

    print "[+] Base32 based"
    objCrack.hash = "ORSXG5A="
    objCrack.run()

    print "[+] BinAscii based"
    objCrack.hash = "74 65 73 74"
    objCrack.run()

    print "[+] BinAscii based (with spaces)"
    objCrack.hash = "74 65 73 74"
    objCrack.run()

    print "[+] MD5 based reverse hash with space characters"
    objCrack.hash = "6f\t\t4b\n72\b62\r38e\t4edac373d126\r4dc     b 6f 890"
    objCrack.run()

    print "[+] SHA(MD5) based"
    objCrack.hash = "4028a0e356acc947fcd2bfbf00cef11e128d484a"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] SHA(MD5) based (password Oracle)"
    objCrack.hash =  "69f21f8927eec194eb9c9caa7c722d9496101f5c"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] MD5(SHA) based (password Oracle)"
    objCrack.password = "0ec91911004615451fa1629545a6aaf5"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] BASE64(MD5) based (password Oracle)"
    objCrack.hash = "YTE4OWM2MzNkOTk5NWUxMWJmODYwNzE3MGVjOWE0Yjg="
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] MD5(MD5) based (password oracle)"
    objCrack.hash = "700060520cdef81bc316909e28783feb"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] MD5(BASE64) based (password oracle)"
    objCrack.hash = "fdfbbd449f9254fc0daa6e031cf3db2b"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] MD5(UNICODE) based (password oracle)"
    objCrack.hash = "561a0f31b5fcc9ef37c12672224c92e4"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] MD5(UNICODE(BASE64)) based (password oracle)"
    objCrack.hash = "291204a91f232548b69bcb0431c17b4f"
    objCrack.password = "oracle"
    objCrack.run()
    print "  -->", objCrack.algorithm

    print "[+] Oracle 11g Algorithm based (password SHAlala)"
    objCrack.hash = "2BFCFDF5895014EE9BB2B9BA067B01E0389BB5711B7B5F82B7235E9E182C"
    objCrack.password = "SHAlala"
    objCrack.run()
    print "  -->", objCrack.algorithm

def main():
    import time

    t = time.time()
    allTests()
    print
    print "Time to crack 17 different algorithms: %s second(s)" % str(time.time() - t)

if __name__ == "__main__":
    main()


