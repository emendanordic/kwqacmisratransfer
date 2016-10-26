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
# Connect to the Klocwork server and retrieve the list of issues
#  for a particular project
# Version: 1.8
# Produced By: Emenda Software Ltd
# Version 1.9
# - Changed to read taxonomies in v11
# Version 1.8
# - Changed to use kwchangestatus in v10
# - No more requirement for local projects! 
# - Removed kwlp and issue inputs
# - Script now uses API so requires curl
# - Gets issues and file list from API
# Version 1.7
# - Improved METRIC handling
# Version 1.6
# - Added support for KW checkers mapped to multiple MISRA rules
# - Changed process to get file names from issues list rather
#       than BS. This allows support for header files.
# - Add support for "DG-"
# Version 1.5
# - Reported more information in comment
# Version 1.4
# - Added debug option
# Version 1.3
# - Added support for C style comments
# - Added support for multi DG's in single comment
# - Added support for Metric DG's
# Version 1.2
# - Added functionality for scopes (modules)
# - Removed kwcheck list, will be requirement for script
# Version 1.1
# - Removed kwcheck run, will be requirement for script


import sys, os, platform, subprocess
import argparse, re, datetime
import urllib, urllib2, socket, json


class KWIssue:
    def __init__(self, issue, ruleText, misraChecks):
        self.id = str(issue['id'])
        self.src = issue['file']
        self.line = int(issue['line'])
        # Taxonomy => MISRA Rule
        self.rules = []
        if ruleText == "":
            self.rules.append(issue['code'])
        else:
            for rule in misraChecks[issue['code']]:
                if "Dir" in rule:
                    self.rules.append(ruleText + " " + str(rule)) 
                else:
                    self.rules.append(ruleText + " Rule " + str(rule)) 

class KWConnect:

    def __init__(self, aurl, auser, averbose, ataxonomy):
        # Data storage
        self.kwIssues = [] # Array of KW issues, type kwIssue()

        # Get args
        self.verbose = averbose
        self.url = aurl
        self.user = auser
        self.project = None
        # Get Klocwork MISRA details
        self.misracChecks = self.GetKWMisra(ataxonomy)

        self.ltoken = ""
        self.lastquery = ""

        self.PrintVerbose(" __init__ :: Created with url: " + str(self.url) + " and user: " + str(self.user) + ". Taxonomy file: " + ataxonomy)


    def GetProject(self):
        return self.project

    def GetKWMisra(self, f):
        self.PrintVerbose("  GetKWMisra :: Loading taxonomy file, which maps Klocwork Issue Codes to Misra Rules & Directives. Filepath: " + str(f))
        if not os.path.exists(f):
            print " ERROR: Klocwork MISRA checkers not installed: " + str(f)
        misraFile = open(f, 'r')
        errorAttr = {}
        for line in misraFile:
            if '<errorAttr ' in line:
                errorAttr[re.sub(r'\s*<errorAttr id="(.+?)" metainfo=".+?"/>\s*', r'\1', line)] \
                    = re.sub(r'\s*<errorAttr id=".+?" metainfo="((Dir. )?[^\s]+).*"/>\s*', r'\1', line)\
                        .split(', ') # Checker can be assigned multiple MISRA ID's
        if len(errorAttr) < 1:
            print " ERROR: No Klocwork checkers mapped (errorAttr): " + str(f)
        return errorAttr
   
    def GetKWCodesFromMISRA(self, misracode):
        returnvar = []
        misracode = misracode.replace("MISRA-C:2012 ","[\'")
        misracode = misracode.replace("Rule ", "")
        misracode = misracode + "\']"
        for k,v in self.misracChecks.iteritems():
            #print "Comparing " + str(misracode) + " to " + str(v)
            if str(misracode) == str(v):
                returnvar.append( k )
        return returnvar
 
    def PrintVerbose(self, string):
        if self.verbose == True:
            print " KWConnect :: " + string

    def GetKWIssues(self):
        # Setup api connection
        self.PrintVerbose("GetKWIssues :: Setting up api connection...")
        self.ApiConnection()  

        # list local Klocwork project
        self.PrintVerbose("GetKWIssues :: Fetching issues from server...")
        self.RunAnalysis()

        #return self.kwIssues
        #return self.GetIssues()
        self.PrintVerbose("GetKWIssues :: Complete! Returning with " + str(len(self.kwIssues)) + " MISRA issues.")
        return self.kwIssues

    def RunAnalysis(self):
        issues = self.GetIssues()
        if issues == None:
            self.PrintVerbose("RunAnalysis :: No issues returned in search, exiting.")
        else:
            for issue in issues:
                # Support for "Also there is one similar error on line x"
                # Support for "Also there are x similar errors on line(s) a, b, c, d."
                if re.search(r'Also there .* similar errors? on line.*', issue['message']):
                    extraLines = re.sub(r'.* on line[\(s\)]* ([\d\s,]*)\.$',r'\1', issue['message'])
                    extraLinesSplit = extraLines.split(', ')
                    #extraLinesSplit.insert(0, issue['line'])
                else:
                    extraLinesSplit = [issue['line']]
                
                for lineNo in extraLinesSplit:
                    issue['line'] = lineNo
                    # Add both C/C++ if present
                    if self.IsInMisra(issue['code'], self.misracChecks):
                        self.kwIssues.append(KWIssue(issue, "MISRA-C:2012", self.misracChecks))

    def IsInMisra(self, rule, misraArray):
        for misra in misraArray:
            if rule == misra:
                return True
        return False

    def ApiConnection(self):
        host = re.sub(r'^https?://([\w\.]*):\d*/.*$',r'\1',self.url)
        port = re.sub(r'^https?://[\w\.]*:(\d*)/.*$',r'\1',self.url)
        self.project = re.sub(r'^https?://[\w\.]*:\d*/(.*)$',r'\1',self.url)
        self.ssl = re.sub(r'^http(s?)://[\w\.]*:\d*/.*$',r'\1',self.url)
        if host == "localhost":
            host = socket.gethostname()
        http = "http"
        if (self.ssl != ""):
            http += 's'
        self.api = http + "://" + host + ':' + port + "/review/api"
        self.ltoken = self._getltoken(host, port)
        if not self.ltoken:
            print "No Klocwork token found please run \"kwauth --url " \
                    + str(self.url) + '"'

    def GetIssues(self):
        vals = {"action" : "search",
                "user" : self.user,
                "project" : self.project,
                "query" : 'grouping:off',
                "ltoken" : self.ltoken}
        return self._query(vals)

    def UpdateIssues(self, issueid, newstatus, newcomment):
        vals = {"action" : "update_status",
                "user" : self.user,
                "project" : self.project,
                "ids" : issueid,
                "status" : newstatus,
                "comment" : newcomment,
                "ltoken" : self.ltoken}
        return self._query(vals)

    def GetLastQuery(self):
        return self.lastquery


    def _query(self, vals):
        self.PrintVerbose("KWConnect:_query :: Executing following query: " + str(vals))
        data = urllib.urlencode(vals)
        request = urllib2.Request(self.api, data)
        self.lastquery = request.get_data()
        try:
            response = urllib2.urlopen(request)
            responseSplit = response.read().split('\n')
            rtn = []
            for line in responseSplit:
                if (line):
                    rtn.append(json.loads(line))
            return(rtn)
        except urllib2.HTTPError as e:
            print 'HTTP Connection Error code: ', str(e)
        except urllib2.URLError as e:
            print 'URL Error: ', str(e)

    def _getltoken(self, host, port):
        tokenFile = os.path.join(os.path.expanduser('~'), ".klocwork", "ltoken")
        if not os.path.exists(tokenFile):
            print "Klocwork ltoken does not exist please run 'kwauth':" + str(tokenFile)
        ptokenFile = open(tokenFile,'r')
        for line in ptokenFile:
            lineSplit = line.strip().split(';')
            if lineSplit[0] == host and lineSplit[1] == port:
                if lineSplit[2] == self.user or self.user == "":
                    self.user = lineSplit[2]
                    return lineSplit[3]
