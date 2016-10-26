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
#	e.g. 3458 -> MISRA-C:2004 Rule 19.4


import sys,re,os, tempfile, shutil
import fileinput, string

keyPairRegex = re.compile(r"""(^[0-9]{3,4})\s*RULE[0]*([1-9]+_[0-9]+)""", re.VERBOSE) #matches e.g. 3447 RULE008_8

class keyPair:
	def __init__(self, key, value):
		self.key = key
		self.value = value

class misraMap:
	def __init__(self):
		self.keymap = []



	def getValue(self, key):
		for pair in self.keymap:
			if pair.key == key:
				return pair.value

	def loadMapFile(self, filename):
		f = open(filename, 'r')
		for line in f:
			if keyPairRegex.search(line) != None:
				for match in keyPairRegex.finditer(line):
					key = match.group(1)
					if self.getValue(key) == None:
						value = "MISRA-C:2004 Rule " + match.group(2)
						value = string.replace(value, "_", ".") #replace _ with . to make MISRA rules read correctly
						keypair = keyPair(key, value)
						self.keymap.append(keypair)

def main():
	themap = misraMap()
	for pair in themap.keymap:
		print(pair.key)
		print(pair.value)

if __name__ == '__main__':
	main()



