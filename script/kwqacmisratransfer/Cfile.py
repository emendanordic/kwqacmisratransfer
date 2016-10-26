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
import sys,re,os, tempfile, shutil
import fileinput
from kwqacmisratransfer.MessageIndex import *

from Common import *

simplePrqaRegexp = re.compile(r"""(PRQA)     #PRQA string""", re.VERBOSE)

fullPrqaRegexp = re.compile(r"""((//|/\*)\s*          #Start of comment(including whitespace)
            PRQA\s*                    #PRQA string (including whitespace)
            S\s*)                   #Suspend order (including whitespace)
            ([0-9][0-9]*)(\s*,\s*(?:[0-9]{2,4}))*              #PRQA id number
            (\s\s*(\w+))?  #Scope Information (EOF or line number )""", re.VERBOSE)

dTagRegexp = re.compile(r"""(/\*\s*       #Start of comment(including whitespace)
            (d[0-9][0-9]*)          #Deviation tag number
            (\s*(\*/)\s*\Z))           #End of comment and must be at end of string""", re.VERBOSE)

labelPrqaRegexp = re.compile(r"""((//|/\*)\s*          #Start of comment(including whitespace)
            PRQA\s*)                    #PRQA string (including whitespace)
            (\s*L:(\w+))  #Scope Label""", re.VERBOSE)

def GetDeviationTag(str):
   match = dTagRegexp.search(str)
   if match != None: 
      return  match.group(2)
   else:
      return None
            
def LocatePrqaInLine(str, filename):
   deviations = []
   if simplePrqaRegexp.search(str) != None:
      for iter in fullPrqaRegexp.finditer(str):
         dev = PrqaDeviation()
         dev.prqaRow = None #for now
         dev.prqaId = iter.group(3).lstrip('0')
         dev.prqaPosition = iter.start()
         dev.prqaScope = iter.group(6)
         dev.misra2012rules = []
         dev.deviationTag = GetDeviationTag(str[:iter.start()])
         
         if iter.group(4) != None:
            print ' Warning: Multiple supressions ignored: %s: %s' % (filename, str.strip())
         if int(dev.prqaId) in MessageIndex.prqaMessage:
            dev.message = MessageIndex.prqaMessage[int(dev.prqaId)]
         else:
            dev.message = "No message exists for %s" % dev.prqaId
         deviations.append(dev)
   
   return deviations


def LocatePrqaLabelsInLine(str, filename):
    labels = []
    if simplePrqaRegexp.search(str) != None:
        for match in labelPrqaRegexp.finditer(str):
            label = PrqaLabel()
            label.labelId = match.group(3)
            
            labels.append(label)        

    return labels

   
def IsWriteable(filename):
   assert filename != None
   return os.access(filename, os.W_OK)

   
def IsDir(filename):
   return os.path.isdir(filename)

def ListDir(filename):
   return os.listdir(filename)

def IsFile(filename):
   return os.path.isfile(filename)
   
class Cfile:
   def __init__(self):
      self.filename = None
      pass
   
   def SetFileName(self, filename):
      self.filename = filename
   
   def GetFileName(self):
      return self.filename
      
   def IsReadable(self):
      assert self.filename != None
      return os.access(self.filename, os.R_OK)
   
   def IsWriteable(self):
      assert self.filename != None
      return os.access(self.filename, os.W_OK)

   def SetWriteable(self):
      pass
      
   def GetPrqaRefs(self, verbose):
      assert self.filename != None
      
      assert self.IsReadable() == True
      
      deviations = []
    
      for line in fileinput.input(self.filename):
         lineDeviations = LocatePrqaInLine(line, self.filename)
         for lineDeviation in lineDeviations:
            #if verbose == True:
                #print " Cfile :: GetPrqaRefs :: Deviation found! Line number: " + str(fileinput.lineno()) + " ID: " + str(lineDeviation.prqaId) + " Scope: " + str(lineDeviation.prqaScope)
            lineDeviation.prqaRow = fileinput.lineno()
            lineDeviation.filename = self.filename
         deviations.extend(lineDeviations)

      #if verbose == True:
        #print " Cfile :: GetPrqaRefs :: Processing of file complete. Number of deviations located: " + str(len(deviations))

      return deviations

   def GetPrqaLabels(self, verbose):
        assert self.filename != None
        assert self.IsReadable() == True

        labels = []

        for line in fileinput.input(self.filename):
            lineLabels = LocatePrqaLabelsInLine(line, self.filename)
            for lineLabel in lineLabels:
                #if verbose == True:
                    #print " Cfile :: GetPrqaLabels :: Label found! Label: " + str(lineLabel.labelId) + " LineNo: " + str(fileinput.lineno())
                lineLabel.lineNo = fileinput.lineno()
                lineLabel.filename = self.filename
            labels.extend(lineLabels)

        #if verbose == True:
            #print " Cfile :: GetPrqaLabels :: Processing of file complete. Number of labels found: " + str(len(labels))

        return labels

