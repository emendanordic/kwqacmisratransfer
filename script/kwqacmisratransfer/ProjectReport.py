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

commonUtilDir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(commonUtilDir + '/lib/python')
#import cleartool
import string


from operator import itemgetter, attrgetter

from kwqacmisratransfer.Common import *
from kwqacmisratransfer.Deviationfile import *
from kwqacmisratransfer.MessageIndex import *


UNAPPROVED_INDEX = 0
APPROVED_INDEX = 1


#ct = cleartool.ClearTool()

class ProjectReport:
   def __init__(self, reportfilename, deviationfilename, inputFilePaths, optVerbose ):
      self.deviationfilename = deviationfilename
      self.filename = reportfilename
      self.inputFilePaths = inputFilePaths
      self.prqaDeviationFilePaths = None
      self.optVerbose = optVerbose
      
      self.prqaInstanceCount = {} #Count of how many times an PRQAid appears
      self.fileInstanceCount = {} #Count of number of prqas in a file
      self.approvedPrqas = []
      self.unApprovedPrqas = []
   
   def LocatePRQADeviationFiles(self):
      self.prqaDeviationFilePaths = []
      for inputFilePath in self.inputFilePaths:
         if os.path.isdir(inputFilePath):
            if self.optVerbose: print "Searching directory '%s' for deviation files" % inputFilePath
            ret = ct.cmd('find %s -name %s -print -nxn' % (inputFilePath, self.deviationfilename), True, True)
            assert(ret[-1] == '')
            fileList = map(lambda s: s.replace('\\', '/'), ret[0:-1])
            for fn in fileList:
               self.prqaDeviationFilePaths.append(fn)
         elif self.deviationfilename == os.path.basename(inputFilePath):
            self.prqaDeviationFilePaths.append(inputFilePath)
         else:
            print "INFO: Ignoring file %s" % (inputFilePath)
      if self.prqaDeviationFilePaths == []:
         print "Warning: No deviation files found"

   def CreateReportCss(self):
      return ET.XML("""<?xml version="1.0"?>
<html>
  <head>
    <meta content="NO-CACHE" http-equiv="CACHE-CONTROL" />
    <title>Report</title>
   <style type="text/css">
     table,th,td
     {
       border:1px solid black;
     }
   </style>
  </head>
</html>""")
   
   def ParseFiles(self):
      for prqaDeviationFilePath in self.prqaDeviationFilePaths:
         try: 
            if self.optVerbose: print "Parsing %s " % prqaDeviationFilePath
            file = Deviationfile()
            file.SetFileName(os.path.normpath(prqaDeviationFilePath))
            prqaDeviations = file.Parse()
            
            for prqaDeviation in prqaDeviations:
            
               #The c-file names should already be normalized to its deviation file, not to report origin
               prqaDeviation.filename = os.path.relpath(os.path.join(os.path.dirname(file.filename), prqaDeviation.filename))

               if len(prqaDeviation.approval) > 0:
                  indexToUse = APPROVED_INDEX
               else:
                  indexToUse = UNAPPROVED_INDEX
               if prqaDeviation.prqaId not in self.prqaInstanceCount:
                  self.prqaInstanceCount[prqaDeviation.prqaId] = [0,0]
               
               self.prqaInstanceCount[prqaDeviation.prqaId][indexToUse] += 1
               
               if prqaDeviation.filename not in self.fileInstanceCount:
                  self.fileInstanceCount[prqaDeviation.filename] = [0,0]
               
               self.fileInstanceCount[prqaDeviation.filename][indexToUse] += 1
               
               if len(prqaDeviation.approval) > 0:
                  self.approvedPrqas.append(prqaDeviation)
                  
               else:
                  self.unApprovedPrqas.append(prqaDeviation)
               
         except Exception , e:
            print "Failed while parsing %s" % prqaDeviationFilePath
            raise e
      
      
   def WriteReport(self):
      
      reportFile = Deviationfile()
      reportFile.SetFileName(self.filename)
      assert reportFile.IsWriteable()
      
      document = self.CreateReportCss()
      body = ET.SubElement(document, "body")
      
      #PRQA Summary Table
      self.TextSubElement(body, "h1", "PRQA Summary Table")
      table =  ET.SubElement(body, "table")
      tr =  ET.SubElement(table, "tr")
      self.TextSubElement(tr, "th", "Prqa")
      self.TextSubElement(tr, "th", "Un-approved d-tags")
      self.TextSubElement(tr, "th", "Approved d-tags")
      self.TextSubElement(tr, "th", "Prqa Message")

      for prqa in sorted(self.prqaInstanceCount):
         tr =  ET.SubElement(table, "tr")
         self.TextSubElement(tr, "td", prqa)
         self.TextSubElement(tr, "td", str(self.prqaInstanceCount[prqa][UNAPPROVED_INDEX]))
         self.TextSubElement(tr, "td", str(self.prqaInstanceCount[prqa][APPROVED_INDEX]))
         if int(prqa) in MessageIndex.prqaMessage:
            self.TextSubElement(tr, "td", MessageIndex.prqaMessage[int(prqa)])
         else:
            self.TextSubElement(tr, "td", "No message exists for %s" % prqa)
      
      
      #File Summary Table
      self.TextSubElement(body, "h1", "File Summary Table (number of d-tags)")
      table =  ET.SubElement(body, "table")
      tr =  ET.SubElement(table, "tr")
      self.TextSubElement(tr, "th", "Filename")
      self.TextSubElement(tr, "th", "Un-approved d-tags")
      self.TextSubElement(tr, "th", "Approved d-tags")

      #sort on primary key unapproved, secondary filename
      for file in sorted(sorted(self.fileInstanceCount), key=lambda file: self.fileInstanceCount[file][UNAPPROVED_INDEX], reverse = True):
         tr =  ET.SubElement(table, "tr")
         self.TextSubElement(tr, "td", file)
         self.TextSubElement(tr, "td", str(self.fileInstanceCount[file][UNAPPROVED_INDEX]))
         self.TextSubElement(tr, "td", str(self.fileInstanceCount[file][APPROVED_INDEX]))
      
      #Unapproved Table
      self.TextSubElement(body, "h1", "Unapproved prqas")
      self.FullTable(body, self.unApprovedPrqas, True)
      
      #Approved Table   
      self.TextSubElement(body, "h1", "Approved prqas")
      self.FullTable(body, self.approvedPrqas, False)   
      
      reportFile.indent(document)
      
      ET.ElementTree(document).write(reportFile.GetFileName())
   
   def FullTable(self, body, data,includeCq):
      table =  ET.SubElement(body,"table")
      tr =  ET.SubElement(table, "tr")
      self.TextSubElement(tr, "th", "Filename")
      self.TextSubElement(tr, "th", "Prqa Id")
      self.TextSubElement(tr, "th", "Deviation Tag")
      self.TextSubElement(tr, "th", "Instance Count")
      self.TextSubElement(tr, "th", "Scope")
      self.TextSubElement(tr, "th", "Prqa Message")
      self.TextSubElement(tr, "th", "Rationale")
      self.TextSubElement(tr, "th", "Comment")
      if includeCq:
         self.TextSubElement(tr, "th", "ClearQuest")
      for prqa in sorted(data, key=attrgetter('filename')):
         tr =  ET.SubElement(table, "tr")
      
         self.TextSubElement(tr, "td", prqa.filename)
         self.TextSubElement(tr, "td", prqa.prqaId)
         self.TextSubElement(tr, "td", prqa.deviationTag)
         self.TextSubElement(tr, "td", str(prqa.instanceCount))
         self.TextSubElement(tr, "td", prqa.prqaScope if prqa.prqaScope != None else "")
         self.TextSubElement(tr, "td", prqa.message)
         self.TextSubElement(tr, "td", prqa.rationale)
         self.TextSubElement(tr, "td", prqa.comment)
         if includeCq:
            self.TextSubElement(tr, "td", prqa.cqId)
      return table
      
   def RunGenerateReport(self):
      self.LocatePRQADeviationFiles()
      self.ParseFiles()
      self.WriteReport()
      return 0
   
   def TextSubElement(self,root, node, text):
      if text != None:
         data = ET.SubElement(root, node)
         data.text = text

   
      
