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
import xml.etree.ElementTree as ET
import sys,os
from kwqacmisratransfer.Common import *

NS = "{prqaDeviationSchema}"
#NS = ""
try:
    register_namespace = ET.register_namespace
except AttributeError:
    def register_namespace(prefix, uri):
        ET._namespace_map[uri] = prefix


register_namespace("pd", "prqaDeviationSchema")

def sortDev(prqaDeviationElement):
    if ET.iselement(prqaDeviationElement):
       return [prqaDeviationElement.findtext("FILENAME"), prqaDeviationElement.findtext("DEVIATION-TAG")]
       

class Deviationfile:
    def __init__(self, optVerbose):
      self.filename = None
      self.document = None
      
      self.verbose = optVerbose
 
    def SetFileName(self, filename):
      self.filename = filename
   
    def GetFileName(self):
      return self.filename
      
    def IsReadable(self):
      assert self.filename != None
      return os.access(self.filename, os.R_OK)
   
    def IsWriteable(self):
      assert self.filename != None
      if not self.Exists():
         #Does not exist 
         return True
      return os.access(self.filename, os.W_OK)

    def Exists(self):
      assert self.filename != None
      return os.path.isfile(self.filename)
     
    def PrintVerbose(self, printstring):
      if self.verbose:
        print "Deviationfile :: " + printstring
 
    def CreateTemplate(self):
      #return ET.XML("""<?xml version="1.0"?><PRQA-DEVIATIONS></PRQA-DEVIATIONS>""")
      return ET.XML("""<?xml version="1.0"?><pd:PRQA-DEVIATIONS xmlns:pd="prqaDeviationSchema"></pd:PRQA-DEVIATIONS>""")

    import os.path


    def ApproverExample(self):
      return """
<!-- Example of how an approval looks like
<APPROVAL>
   <APPROVER>Approver1</APPROVER>
   <APPROVER>Approver2</APPROVER>
   <APPROVER>Approver3</APPROVER>
   <COMMENT>Formal review</COMMENT>
   <DATE>2010-10-10</DATE>
</APPROVAL>-->
"""
   
    def TextSubElement(self,root, node, text):
      if text != None:
         data = ET.SubElement(root, node)
         data.text = text
      
    def AppendPrqaDeviation(self, prqaDeviation):
      assert not "wasReadFromFile" in prqaDeviation.__dict__
      
      root =  ET.Element("PRQA-DEVIATION")
      
      self.TextSubElement(root, "DEVIATION-TAG", prqaDeviation.deviationTag)
      self.TextSubElement(root, "FILENAME", prqaDeviation.filename)
      self.TextSubElement(root, "PRQA-ID", prqaDeviation.prqaId)
      self.TextSubElement(root, "INSTANCE-COUNT", str(prqaDeviation.instanceCount))
      self.TextSubElement(root, "SCOPE", prqaDeviation.prqaScope)
      self.TextSubElement(root, "PRQA-MESSAGE", prqaDeviation.message)
      self.TextSubElement(root, "RATIONALE",prqaDeviation.rationale)
      self.TextSubElement(root, "COMMENT", prqaDeviation.comment)
      self.TextSubElement(root, "CLEARQUEST", prqaDeviation.cqId)
      for approval in prqaDeviation.approval:
         aroot =  ET.Element("APPROVAL")
         for approver in approval.approver:
            self.TextSubElement(aroot, "APPROVER", approver)
         self.TextSubElement(aroot, "COMMENT", approval.comment)
         self.TextSubElement(aroot, "DATE", approval.date)
         root.append(aroot)
      
      return root
        
         
    def Parse(self):
      assert self.IsReadable()
      self.document = ET.parse(self.filename).getroot()
      
      prqaDeviations = []
      for prqaDeviationElement in self.document:
         assert prqaDeviationElement.tag != "PRQA-DEVIATIONS"
         prqaDeviation = PrqaDeviation()
         prqaDeviation.deviationTag    = prqaDeviationElement.findtext("DEVIATION-TAG")
         prqaDeviation.filename       = prqaDeviationElement.findtext("FILENAME")
         prqaDeviation.prqaId       = prqaDeviationElement.findtext("PRQA-ID").lstrip('0')         
         prqaDeviation.instanceCount = prqaDeviationElement.findtext("INSTANCE-COUNT")
         prqaDeviation.prqaScope    = prqaDeviationElement.findtext("SCOPE")
         prqaDeviation.message      = prqaDeviationElement.findtext("PRQA-MESSAGE")
         prqaDeviation.rationale     = prqaDeviationElement.findtext("RATIONALE")
         prqaDeviation.comment       = prqaDeviationElement.findtext("COMMENT")
         prqaDeviation.cqId          = prqaDeviationElement.findtext("CLEARQUEST")
         for approval in prqaDeviationElement.findall("APPROVAL"):
            ap = Approval()
            for approver in approval.findall("APPROVER"):
               ap.approver.append(approver.text)
            ap.comment = approval.findtext("COMMENT")
            ap.date = approval.findtext("DATE")
            prqaDeviation.approval.append(ap)
         
         #Path to the referenced c file = dirname of current deviation file + filepath in dev entry
         prqaDeviation.filepath = os.path.realpath( os.path.join( os.path.dirname(self.filename), prqaDeviation.filename ) )

         prqaDeviation.wasReadFromFile = True
         prqaDeviations.append(prqaDeviation)
      
      self.PrintVerbose( "Deviationfile.Parse() :: End of function. Number of deviations parsed: " + str(len(prqaDeviations)) )

      return prqaDeviations
    
    
    def indent(self,elem, level=0):
      i = "\n" + level*"  "
      if len(elem):
         if not elem.text or not elem.text.strip():
            elem.text = i + "  "
         for e in elem:
            self.indent(e, level+1)
            if not e.tail or not e.tail.strip():
               e.tail = i + "  "
         if not e.tail or not e.tail.strip():
            e.tail = i
      else:
         if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
    
    def Write(self, newPrqaDeviation):
      assert self.IsWriteable()
      if self.document == None:
         self.document = self.CreateTemplate()
      
      for new in newPrqaDeviation:
         tree = self.document
         assert tree.tag == NS + "PRQA-DEVIATIONS"
         tree.append(self.AppendPrqaDeviation(new))

      self.indent(self.document)
      ET.ElementTree(self.document).write(self.filename, encoding="iso-8859-1")
      
      #Append an example how the approval should look like
      fd = open(self.filename,"a")
      fd.write(self.ApproverExample())
      fd.close()

      
      
      
      
      
      
      
      
