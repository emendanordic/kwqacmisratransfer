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
import sys,re,os
import fileinput
import time
import datetime
from collections import Counter

import kwqacmisratransfer.Common
from kwqacmisratransfer.KWConnect import KWConnect
from kwqacmisratransfer.Deviationfile import Deviationfile
from kwqacmisratransfer.Cfile import Cfile
from kwqacmisratransfer.MISRAMapQAC2004 import misraMapQAC2004
from kwqacmisratransfer.MISRAMap20042012 import misraMap20042012

class Main:
    def __init__(self):
        self.qacmisra2004mappath = None
        self.misra20042012mappath = None
        self.PRQAMISRA2004 = None
        self.MISRA20042012 = None        

        self.cfiles = []
        self.inputFileText = ""
        self.inputFiles = []
        self.deviationsTable = None
        self.verbose = False

        self.kwuser = None
        self.reportfile = None

        self.countDevFilesIn = 0
        self.countDevFiles = 0
        self.countDevFileEntries = 0
        self.countDeviations = 0
        self.countDevInFiles = 0
        self.countDev2M2004 = 0
        self.countDev2M2012 = 0
        self.countDev2Klocwork = 0
        self.countKWIssues = 0
        self.countErrors = 0

        self.noM2012Ids = []

        self.kwPrefix = ""
        self.projectPrefix = ""

    def SetFilePathPrefixes(self, optKWPrefix, optProjectPrefix):
        self.kwPrefix = optKWPrefix
        self.projectPrefix = optProjectPrefix

    def SetFilePaths(self, filepaths):
        self.inputFileText = filepaths

    def SetMISRAMapPaths(self, qacmisra2004mappath, misra20042012mappath):
        self.qacmisra2004mappath = qacmisra2004mappath
        self.misra20042012mappath = misra20042012mappath

    def PrintVerbose(self, string):
        if self.verbose == True:
            print "Main :: " + string

    def WriteToReport(self, string):
        if self.reportfile is not None:
            self.reportfile.write(str(string) + "\n")

    def IsFileReadable(self, filepath):    
        if not os.path.isfile(filepath):
            print "ERROR: " + str( filepath ) + " cannot be found/is not a valid file."
            self.countErrors = self.countErrors + 1
            return False

        thefile = Deviationfile(self.verbose)
        thefile.SetFileName(filepath)
        if not thefile.IsReadable():
            print "ERROR: " + str( filepath ) + " cannot be opened for reading."
            self.countErrors = self.countErrors + 1
            return False

        return True


    def ProcessDeviationFile(self, devFilePath):
        self.PrintVerbose( "ProcessDeviationFile :: Searching for file: " + str(devFilePath) )
           
        if not self.IsFileReadable(devFilePath):
            self.PrintVerbose( "ProcessDeviationFile :: File not OK. End of function." )
            return False
 
        self.PrintVerbose( "ProcessDeviationFile :: File is readable. Beginning to process..." )
        devFile = Deviationfile(self.verbose)
        devFile.SetFileName(devFilePath)

        for dev in devFile.Parse():
            key = dev.filepath + "@" + dev.deviationTag
            #self.PrintVerbose( "ProcessDeviationFile :: Searching for file " + dev.filename + " at path: " + dev.filepath )
          
            if self.IsFileReadable(dev.filepath): 
                #self.PrintVerbose( "ProcessDeviations :: File OK. Appending key: " + key + " to key table and adding " + dev.filepath + " to list of C files." )
                self.deviationsTable[key] = dev
                if dev.filepath not in self.cfiles:
                    self.cfiles.append( dev.filepath )
            else:                
                self.countErrors = self.countErrors + 1
                print "ERROR: File " + dev.filepath + " not found. Key " + key + " will not be added to file list."

        self.PrintVerbose( "ProcessDeviationFile :: End of function." )
        return True



    def ProcessDeviations(self):
        self.PrintVerbose( "ProcessDeviations :: Running some simple assertions..." )
        assert self.inputFileText != "" 
        assert self.inputFiles == []

        self.PrintVerbose( "ProcessDeviations :: Assertions complete. Processing input file list and reporting any files which are not found...")

        #Start by processing list of input files, ensure each one exists
        self.deviationsTable = {}
        for devFilePath in self.inputFileText.split(','):
            self.countDevFilesIn = self.countDevFilesIn + 1
            if self.ProcessDeviationFile(devFilePath):
                self.countDevFiles = self.countDevFiles + 1

        self.countDevFileEntries = len( self.deviationsTable )
        
        #Parse c files - we need to get the line number for each deviation
        #We also get any labels that are used in PRQA deviations (sometimes)
        self.PrintVerbose( "ProcessDeviations :: Loading deviation file numbers and lables from C files...")
        self.cfilesPRQA = []
        self.cfilesPRQAlabels = []
        for cFilePath in self.cfiles:
            cFile = Cfile()
            cFile.SetFileName(cFilePath)
            self.cfilesPRQA.extend(cFile.GetPrqaRefs(self.verbose))
            self.cfilesPRQAlabels.extend(cFile.GetPrqaLabels(self.verbose))

        self.countDeviations = len(self.cfilesPRQA)

        #Prepare QACMisra2004 map
        self.PrintVerbose( "ProcessDeviations :: Loading QAC -> MISRA 2004 map file..." + str(self.qacmisra2004mappath))
        self.PRQAMISRA2004 = misraMapQAC2004(self.verbose)
        self.PRQAMISRA2004.loadMapFile(self.qacmisra2004mappath)

        #Prepare MISRA20042012 map
        self.PrintVerbose( "ProcessDeviations :: Loading MISRA 2004 -> MISRA 2012 map file..." + str(self.misra20042012mappath))
        self.MISRA20042012 = misraMap20042012()
        self.MISRA20042012.loadMapFile(self.misra20042012mappath)

        self.PrintVerbose( "ProcessDeviations :: Loading of maps complete. Matching C file deviations to deviation table entries...")

        deviationsWithMISRACodes = []

        self.PrintVerbose("ProcessDeviations :: Current deviationTable values are:")
        for devprint in self.deviationsTable:
            self.PrintVerbose( str(devprint) )

        #Do the matching of tag in C file to the Deviation file
        for cfilePRQA in self.cfilesPRQA:
            key = str(cfilePRQA.filename) + "@" + str(cfilePRQA.deviationTag)
            #self.PrintVerbose( "ProcessDeviations :: Processing key: " + key)
            if not key in self.deviationsTable:
                #The deviation tag is not found in the deviation file
                #self.PrintVerbose( "ProcessDeviations :: Deviation not found in devation file. Key: " + key)
                continue
            else:
                #The was a match but the content must also match
                dev = self.deviationsTable[key]
                assert dev != None
                if dev.prqaId != cfilePRQA.prqaId :
                    #self.PrintVerbose( "ProcessDeviations :: Key " + key + ". ID " + dev.prqaId + " does not match ID " + cfilePRQA.prqaId)
                    cfilePRQA.prqaInDeviationFile = dev.prqaId
                    continue 
                if dev.prqaScope != cfilePRQA.prqaScope :
                    #self.PrintVerbose( "ProcessDeviations :: Key " + key + ". Scope " + dev.prqaScope + " does not match scope " + cfilePRQA.prqaScope)
                    cfilePRQA.scopeInDeviationFile = dev.prqaScope
                    continue
            
            self.countDevInFiles = self.countDevInFiles + 1
            #self.PrintVerbose( "ProcessDeviations :: Convering QAC key " + cfilePRQA.prqaId + " to MISRA 2012, via 2004...")

            #Convert QAC ID to MISRA 2004 Rule
            cfilePRQA.m2004Rule = self.PRQAMISRA2004.getValue(cfilePRQA.prqaId)
            #self.PrintVerbose( "ProcessDeviations :: MISRA 2004 code: " + str(dev.m2004Rule))
            if cfilePRQA.m2004Rule is None or len(cfilePRQA.m2004Rule) < 1:
                self.noM2012Ids.append( str(cfilePRQA.prqaId) )
                continue
            self.countDev2M2004 = self.countDev2M2004 + 1
            #Convert MISRA 2004 Rule to MISRA 2012 Rule/Directive
            cfilePRQA.m2012Rules = self.MISRA20042012.getValues(cfilePRQA.m2004Rule)
            #self.PrintVerbose( "ProcessDeviations :: MISRA 2012 codes: ")
            #Just printing the rules...
            if cfilePRQA.m2012Rules is None or len(cfilePRQA.m2012Rules) < 1:
                self.noM2012Ids.append( str(cfilePRQA.prqaId) )
                continue
            self.countDev2M2012 = self.countDev2M2012 + 1
                #for rule in misra2012rules:
                    #self.PrintVerbose(str(rule))
            #else:
                #self.PrintVerbose("ProcessDeviations :: No MISRA 2012 matches found!")
            
            #Copy over the approval, we'll need it later
            cfilePRQA.approval = dev.approval
            #Append the cfile deviation to the list of deviations with corresponding MISRA codes
            deviationsWithMISRACodes.append(cfilePRQA)

            #Print information about the deviation that has made it all the way to MISRA 2012
            self.PrintVerbose("ProcessDeviations :: Deviation successfully transferred to one or more MISRA 2012 rules:")
            self.PrintVerbose("  File:         " + dev.filename )
            self.PrintVerbose("  Line number:  " + str(cfilePRQA.prqaRow) )
            self.PrintVerbose("  Scope:        " + str(cfilePRQA.prqaScope) )
            self.PrintVerbose("  QAC issue ID: " + dev.prqaId )
            self.PrintVerbose("  MISRA 2004:   " + str(cfilePRQA.m2004Rule) )
            for rule in cfilePRQA.m2012Rules:
                self.PrintVerbose("  MISRA 2012:   " + str(rule) )
            
        #self.WriteToReport("Number of deviation entries in deviation file: " + str( len(self.deviationsTable)) )
        #self.WriteToReport("Number of deviations found in C source files: " + str( len(self.cfilesPRQA)) )
        #self.WriteToReport("Number of deviations successfully mapped to MISRA 2004 rules: " + str(self.countDev2M2004) )
        #self.WriteToReport("Number of deviations successfully mapped to MISRA 2012 rules: " + str(self.countDev2M2012) )
        #self.WriteToReport("Number of deviations which were not mapped to MISRA 2012 and will not be migrated to Klocwork: " + str( len(self.cfilesPRQA) - self.countDev2M2012) )

        return deviationsWithMISRACodes
            
            
    def GetKWUpdateStringFromPRQADeviation(self, kwIssues, dev):
        updateCmds = []
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: ******************")
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Processing deviation " + str(dev.filename) + "@" + str(dev.deviationTag) + ". Checking scope: " + str(dev.prqaScope))
        #Calculate the scope of the deviation
        if dev.prqaScope is None:
            #the line the comment is on
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Scope is none")
            scopeBegin = dev.prqaRow
            scopeEnd =   dev.prqaRow
        elif dev.prqaScope == 'EOF':
            #until end-of-file
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Scope is EOF")
            scopeBegin = dev.prqaRow
            scopeEnd =   None
        elif dev.prqaScope.isdigit() == True:
            #specific line number: from current line to the given line number
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Scope is line number range")
            scopeBegin = dev.prqaRow
            scopeEnd =   dev.prqaScope
        else:
            labelLineNo = self.GetLabelLineNo(dev.prqaScope, dev.filename)
            if labelLineNo > 0:
                #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Scope is label, until lineNo " + str(labelLineNo))
                #label - from current line to the line in the code with the label
                scopeBegin = dev.prqaRow
                scopeEnd =   labelLineNo
            else:
                #Unhandled scope, flag error
                self.PrintVerbose("ERROR GetKWUpdateStringFromPRQADeviation :: Scope is Unknown")
                self.countErrors = self.countErrors + 1
                return

        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Searching for matching KW issue:")
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: filename = " + str(dev.filename))
        if dev.m2012Rules is None:
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Deviation does not map to a MISRA 2012 rule/directive. Moving to next deviation.")
            return
        #for rule in dev.misra2012rules:
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: misra2012rule = " + str(rule))
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: scopeBegin = " + str(scopeBegin))
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: scopeEnd = " + str(scopeEnd))
    
        #Iterate through Klocwork issues, find any matches
        #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Beginning to iterate through Klocwork issues, searching for match...")
        #Remove the prefix from the source file path
        projectSourcefilePath = dev.filename.replace( self.projectPrefix, "")
        #And remove the drive
        drive, projectSourcefilePath = os.path.splitdrive(projectSourcefilePath)
        for issue in kwIssues:
            #To compare paths, we must remove prefixes from the paths
            kwSourcefilePath = issue.src
            kwSourcefilePath = kwSourcefilePath.replace( self.kwPrefix, "") #replace the prefix with ""
            kwSourcefilePath = kwSourcefilePath.replace('\\','/')
            #Remove the drive
            drive, kwSourcefilePath = os.path.splitdrive(kwSourcefilePath)
            #self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Comparing to Klocwork issue src: " + str(kwSourcefilePath) + " line: " + str(issue.line))
            if kwSourcefilePath == projectSourcefilePath and issue.line >= scopeBegin and (issue.line <= scopeEnd or scopeEnd == None): 
                #Because we are working with MISRA 2012, there can be many MISRA Rules/Directives per QAC/KW issue
                #So we have to check a many:many relationship
                self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Klocwork issue " + str(issue.id) + " in file " + kwSourcefilePath + " : " + str(issue.line) )
                self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: matches deviation in file " + dev.filename + " : " + str(dev.prqaRow) ) 
                self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Klocwork issue MISRA 2012 codes:")
                for therule in issue.rules: self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: " + str(therule) )
                self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Deviation MISRA 2012 codes:")
                for therule in dev.m2012Rules : self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: " + str(therule) )
                dev.kwMatch = False
                for misra2012rule in issue.rules:
                    if misra2012rule in dev.m2012Rules:
                        dev.kwMatch = True
                        self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: Match found! Adding KW update command to command list...")
                        #filename, issuetype (misra code) and linenumber match, update the issue
                        kwnewstatus = "Ignore"
                        #build a comment from fields comment & approval (incl. approval date, approvers & approval comment)
                        kwnewcomment = dev.comment + dev.rationale
                        for approval in dev.approval:
                             kwnewcomment = kwnewcomment + "\nApproval date: " + str(approval.date)
                             kwnewcomment = kwnewcomment + "\nApproval comment: " + str(approval.comment)
                             kwnewcomment = kwnewcomment + "\nApproved by:"
                             for approver in approval.approver:
                                 kwnewcomment = kwnewcomment + "\n" + approver.encode('ascii', 'ignore')
                        updateCmds.append({'id' : str(issue.id), 'status' : kwnewstatus, 'comment' : kwnewcomment}) 
                        #"&owner=new_owner")
                        #TODO incremental/diff update
                        #updateCmds.append("action=update_status&user=" + kwuser + "&project="+ kwproject + "&ids=" + str(issue.id) + "&status=" + kwnewstatus + "&comment=" + kwnewcomment) #"&owner=new_owner")
                if not dev.kwMatch:
                    self.PrintVerbose("GetKWUpdateStringFromPRQADeviation :: No match found.")

        return updateCmds



    def GetLabelLineNo(self, labelarg, filenamearg):
        for label in self.cfilesPRQAlabels:
            if labelarg == label.labelId and filenamearg == label.filename:
                return label.lineNo
        return 0 #no match found


    def Runkwqacmisratransfer(self, kwurl, akwuser, optVerbose, kwmisrataxonomy, optReportFilePath, optDryRun):
        
        self.verbose = optVerbose

        self.PrintVerbose("Runkwqacmisratransfer :: Start of program. Hello! Time and date: " + str(datetime.datetime.now()) )
        if len(optReportFilePath) > 0:
            self.PrintVerbose("Runkwqacmisratransfer :: Opening report file for write.")
            self.reportfile = open(optReportFilePath, 'w')
        self.WriteToReport("=====================================================")
        self.WriteToReport("kwqacmisratransfer :: New execution. Datetime: " + str(datetime.datetime.now()) )
        deviations = []
        updateCmds = []
        self.PrintVerbose("Runkwqacmisratransfer :: Creating kwconnector...")
        kwconnector = KWConnect(kwurl, akwuser, optVerbose, kwmisrataxonomy)
        self.WriteToReport("Klocwork url: " + kwurl)
        
        self.PrintVerbose("Runkwqacmisratransfer :: Using kwconnector to fetch Klocwork issues...")
        kwIssues = kwconnector.GetKWIssues()
        self.countKWIssues = len(kwIssues)
        
        deviations = self.ProcessDeviations()
        self.PrintVerbose("Runkwqacmisratransfer :: Processing deviations in C source files complete. Now matching to Klocwork issues and generating update commands...")
        
        noKWMatchDeviations = []
        for deviation in deviations:
            newUpdateCmd = self.GetKWUpdateStringFromPRQADeviation(kwIssues, deviation)
            if newUpdateCmd is not None and len(newUpdateCmd) > 0: 
                self.countDev2Klocwork = self.countDev2Klocwork + 1
                updateCmds.extend(newUpdateCmd)
            else:
                noKWMatchDeviations.append( deviation )

        self.WriteToReport("========")
        self.WriteToReport("Summary:")
        self.WriteToReport("Number of deviation files which were input: " + str(self.countDevFilesIn) )
        self.WriteToReport("Number of deviation files which were processed: " + str(self.countDevFiles) )
        self.WriteToReport("Number of deviation file entries discovered: " + str(self.countDevFileEntries) )
        self.WriteToReport("Number of deviations in C files: " + str(self.countDeviations) )
        self.WriteToReport("Number of deviations which were matched to a PrqaDeviation.xml file: " + str(self.countDevInFiles) )
        self.WriteToReport("Number of deviations for which a matching MISRA 2004 rule was found: " + str(self.countDev2M2004) )
        self.WriteToReport("Number of deviations for which a matching MISRA 2012 rule was found: " + str(self.countDev2M2012) )
        self.WriteToReport("Number of deviations for which one or more matching Klocwork issues were found: " + str(self.countDev2Klocwork) )
        self.WriteToReport("Number of Klocwork issues fetched from the Klocwork server: " + str(self.countKWIssues) )
        self.WriteToReport("Number of Klocwork issues which will be updated: " + str (len(updateCmds) ) )
        self.WriteToReport("Number of errors in script: " + str(self.countErrors) )
        
        self.WriteToReport("========")
        self.WriteToReport("Detail:")
        if len( self.noM2012Ids ) > 0:
            self.WriteToReport("The following PRQA IDs could not be converted to MISRA 2012 (with count in parentheses):")
            idcount = Counter(self.noM2012Ids)
            for key, count in idcount.most_common():
                self.WriteToReport( str(key) + " (" + str(count) + ")")
        
        #Print information on the (file-level) deviations which could not be matched with KW issues
        self.WriteToReport("") 
        self.WriteToReport( str(self.countDev2M2012 - self.countDev2Klocwork) + " file-level deviations that were matched to one or more MISRA 2012 rules could not be matched to any Klocwork issues. A summary of the deviations grouped by QAC ID:") 
        noKWMatchDeviationsKeys = []
        for dev in noKWMatchDeviations: noKWMatchDeviationsKeys.append( dev.prqaId )
        noMatchCount = Counter(noKWMatchDeviationsKeys)
        for key, c in noMatchCount.most_common():
            self.WriteToReport(" " + key + " (" + str(c) + ")" )
            misra2004value = self.PRQAMISRA2004.getValue(key)
            self.WriteToReport("  " + str(misra2004value) ) 
            misra2012values =  self.MISRA20042012.getValues(misra2004value)
            if misra2012values is None or len(misra2012values) < 1:
                self.WriteToReport("  No MISRA-2012 matches..?")
            else:
                for m in misra2012values:
                    self.WriteToReport("  " + str(m) ) 
                    kwcodes = kwconnector.GetKWCodesFromMISRA(m)
                    if kwcodes is None or len(kwcodes) < 1:
                        self.WriteToReport("  No Klocwork checkers exist for this MISRA 2012 rule.")
                    else:
                        for kwcode in kwcodes:
                            self.WriteToReport("  Klocwork code: " + str(kwcode) )

        #Print the count again, but list the file locations of each Prqa Id
        self.WriteToReport("")
        self.WriteToReport("File-level deviations listed in the same PrqaId order:")
        for key, c in noMatchCount.most_common():
            self.WriteToReport(" " + key + " (" + str(c) + ")" )
            for dev in noKWMatchDeviations:
                if dev.prqaId == key:
                    self.WriteToReport("  " + dev.filename + " : " + str(dev.prqaRow) )
 
        self.WriteToReport("")
        self.WriteToReport("List of update commands sent to server:")
        #Execute the update commands
        for cmd in updateCmds:
            self.PrintVerbose("Runkwqacmisratransfer :: Updating issue ID " + cmd['id'] + " to status " + cmd['status'] + " with comment " + cmd['comment'])
            self.WriteToReport("")
            if not optDryRun:
                kwconnector.UpdateIssues(cmd['id'], cmd['status'], cmd['comment'])
                self.WriteToReport( str(kwconnector.GetLastQuery()) )
            else:
                self.WriteToReport( "Updating issue ID " + cmd['id'] + " to status " + cmd['status'] + " with comment " + cmd['comment'])
            #self.PrintVerbose(str(cmd))
       
        if self.reportfile is not None:
            self.PrintVerbose("Runkwqacmisratransfer :: Closing report file.")
            self.reportfile.close()
        
        self.PrintVerbose("Runkwqacmisratransfer :: End of program.")
        

