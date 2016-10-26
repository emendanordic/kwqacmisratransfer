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
isUnderTest = False

#prqaDeviationElement.findtext("RATIONALE")
         #prqaDeviationElement.findtext("COMMENT")
         #prqaDeviationElement.findtext("APPROVAL")

class Approval():
   def __init__(self):
      self.approver = []
      self.comment = None
      self.date = None

class PrqaDeviation():
   def __init__(self):
      self.prqaId = None
      self.prqaRow = None
      self.prqaPosition = None
      self.prqaScope = None
      self.deviationTag = None
      self.filename = None
      self.filepath = None
      self.instanceCount = 0
      self.message = None
      self.rationale = " "
      self.comment = " "
      self.cqId = " "
      self.approval = []
      self.kwMatch = False
      self.kwRules = []
      self.m2004Rule = ""
      self.m2012Rules = []      
   
   def AreStrictEqual(self,peer):
      if (peer == self):
         return True
      if (self.prqaId       != peer.prqaId)         : return False
      if (self.prqaRow       != peer.prqaRow)      : return False
      if (self.prqaPosition    != peer.prqaPosition)   : return False
      if (self.prqaScope      != peer.prqaScope)      : return False
      if (self.deviationTag   != peer.deviationTag)   : return False
      if (self.filename      != peer.filename)      : return False
      if (self.instanceCount   != peer.instanceCount)   : return False
      if (self.message      != peer.message)      : return False
      
      return True
   
   def __str__(self):
      s = ""
      for d in self.__dict__:
         s += "%s=%s, " % (d, str(self.__dict__[d]))
      return s
         
class PrqaLabel():
    def __init__(self):
        self.labelId = None
        self.filename = None
        self.lineNo = 0

    def __str__(self):
        return self.labelId + "@" + self.filename

class CommonException(Exception):
   def __init__(self, value = 2,message = "3"):
      self.value     = value
      self.message = message
      
   def __str__(self):
      return repr(self.value) + ":" + self.message


class Inconsistency:
   
   D_TAG_MISSING_IN_C_FILE = 10
   D_TAG_MISSING_IN_D_FILE = 20
   PRQA_ID_CHANGED         = 30
   SCOPE_CHANGED           = 40
   HIT_COUNT_EXCEEDED      = 50
   UNREFERENCED_D_TAG      = 60

   def __init__(self, type, prqaDeviation):
      self.type = type
      self.prqaDeviation = prqaDeviation
   
   @staticmethod
   def IncSort(s):
      return [s.prqaDeviation.filename, s.prqaDeviation.deviationTag, s.prqaDeviation.prqaId]
 
   @staticmethod
   def GetOfType(type,inconsistencys):
      list = []
      for inconsistency in inconsistencys:
         if inconsistency.type == type:
            list.append(inconsistency)
      
      return sorted(list, key=Inconsistency.IncSort)
   
   @staticmethod
   def Count(type,inconsistencys):
      return len(Inconsistency.GetOfType(type,inconsistencys))
   
