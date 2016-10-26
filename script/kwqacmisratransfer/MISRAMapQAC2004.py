# **************************************************************************************************
#  Created by: Emenda
#
#  $LastChangedBy: Andreas Larfors
#  $LastChangedDate: 2016-09-20
#  $Version: 1.0
#
# Disclaimer: Please note that this software or software component is released by Emenda on a 
# non-proprietary basis for commercial or non-commercial use with no warranty. Emenda will not be 
# liable for any damage or loss caused by the use of this software. Redistribution is only allowed 
# with prior consent.
#
# **************************************************************************************************
# Description: Creates a map from QAC-specific issue IDs to MISRA error codes
#   e.g. 3458 -> MISRA-C:2004 Rule 19.4


import sys,re,os, tempfile, shutil
import fileinput, string

keyPairRegex = re.compile(r"""(^[0-9]{3,4})\s*RULE[0]*([0-9]+_[0-9]+)""", re.VERBOSE) #matches e.g. 3447 RULE008_8

class keyPair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class misraMapQAC2004:
    def __init__(self, verbose):
        self.keymap = []
        self.verbose = verbose

    def PrintVerbose(self, string):
        if self.verbose == True:
            print "MISRAMapQAC2004 :: " + string

    def getValue(self, key):
        #Strip out leading 0s (0310 -> 310)
        key = key.lstrip('0')
        #self.PrintVerbose("GetValue :: Looking for key " + key)
        for pair in self.keymap:
            #self.PrintVerbose("GetValue :: Comparing " + key + " with " + str(pair.key))
            if pair.key == key:
                #self.PrintVerbose("GetValue :: Match found! Value: " + str(pair.value))
                return pair.value
        #self.PrintVerbose("GetValue :: Match not found.")

    def loadMapFile(self, filename):
        with open(filename, 'r') as f:
            self.PrintVerbose("loadMapFile :: Successfully opened file " + str(filename))
            for line in f:
                #self.PrintVerbose("loadMapFile :: Running keyPairRegex on the following line: " + line)
                if keyPairRegex.search(line) != None:
                    #self.PrintVerbose("***************************************************************************")
                    #self.PrintVerbose("loadMapFile :: new keyPairRegex match found! Loading key & value pair...")
                    for match in keyPairRegex.finditer(str(line)):
                        key = match.group(1)
                        #self.PrintVerbose("loadMapFile :: key = " + str(key))
                        if self.getValue(key) == None:
                            value = "MISRA-C:2004 Rule " + match.group(2)
                            value = string.replace(value, "_", ".") #replace _ with . to make MISRA rules read correctly
                            keypair = keyPair(key, value)
                            #self.PrintVerbose("loadMapFile :: Key-value pair is not yet in table, adding value " + value + " with key " + key)
                            self.keymap.append(keypair)

def main():
    themap = misraMapQAC2004()
    for pair in themap.keymap:
        print(pair.key)
        print(pair.value)

if __name__ == '__main__':
    main()
