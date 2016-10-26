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
# Description: Creates a map from MISRA 2004 rules to MISRA 2012 Rules/Directives


import sys,re,os, tempfile, shutil
import fileinput, string

class keyPair:
    def __init__(self, key, values):
        self.key = key
        self.values = values

class misraMap20042012:
    def __init__(self):
        self.keymap = []

    def getValues(self, key):
        for pair in self.keymap:
            if pair.key == key:
                return pair.values

    def extendValues(self, key, values):
        for pair in self.keymap:
            if pair.key == key:
                pair.values.extend(values)

    def loadMapFile(self, filename):
        key = ''
        values = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) < 1:
                    #next line will be a new key
                    #store existing key and values if not stored already, else append
                    if self.getValues(key) == None:
                        keypair = keyPair(key, values)
                        self.keymap.append(keypair)
                    else:
                        self.extendValues(key, values)
                    key = ''
                    values = []
                elif len(key) < 1:
                    #new key
                    key = "MISRA-C:2004 " + line
                else:
                    #value - either a Rule, Dir or Deleted
                    if line == 'Deleted':
                        continue
                    else:
                        values.append("MISRA-C:2012 " + line)

def main():
    themap = misraMap20042012()

if __name__ == '__main__':
    main()
