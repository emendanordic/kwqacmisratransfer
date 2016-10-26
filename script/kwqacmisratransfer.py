#! /usr/bin/python -u

'''
Options:
-h             Print this help (optional)
-v             Verbose (optional)
-d             Dry-run (optional) - no updates made to Klocwork server

-k <klocwork-url>                       e.g. http(s)://klocworkserver:8080/projectname (REQUIRED)
-u <klocwork-user>                      The user name for the Klocwork server (used in kwauth command) (REQUIRED)
-x <prqa-deviation-xmls>                Comma-separated list of paths to PrqaDeviation.xmls (deviation approval files) (REQUIRED)
-m <qac-to-misra2004-map-file>          Path to file qac.usr.messages (REQUIRED)
-n <misra2004-to-misra2012-map-file>    Path to misra20042012 file (REQUIRED)
-t <klocwork-misra2012-taxonomy-file>   Path to .tconf for misra2012 Klocwork taxonomy (xml file) (REQUIRED)
-r <report>                             Path to report file (output) (optional)
-a <klocwork-src-prefix>                Klocwork source file prefix, to be removed from the file path during comparison (optional)
-b <project-src-prefix>                 Project source prefix, to be removed from the file path during comparison (optional)
'''

import sys
import os
import getopt
import re
from kwqacmisratransfer.Main import *


__doc__ = 'Usage: %s [<option> ...]\n' % (os.path.basename(sys.argv[0])) + \
  __doc__.strip()


def error(msg):
    sys.stderr.write('ERROR: %s\r\n' % (msg))
    sys.exit(1)

def warning(msg):
    sys.stderr.write('WARNING: %s\r\n' % (msg))

def usage():
    print __doc__

def shellcmd(cmd, withSts=False, stripped=False):
    f = os.popen(cmd)
    lines = f.readlines()
    sts = f.close()

    if stripped:
        sl = []
    for l in lines: 
        sl.append(l.rstrip())
        lines = sl

    if withSts:
        return (sts, lines)
    else:
        return lines

def main():

    optVerbose              = False # -v
    optInputFiles           = ""    # -x 
    optKWUrl                = ""    # -k
    optKWUser               = ""    # -u
    optQACMisra2004MapFile  = ""    # -m
    optMisra20042014MapFile = ""    # -n
    optKWMisraTaxonomy      = ""    # -t
    optReportFile           = ""    # -r
    optDryRun               = False # -d
    optKWPrefix             = ""    # -a
    optProjectPrefix        = ""    # -b

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hvdx:m:n:u:k:t:r:p:a:b:')
    except getopt.GetoptError, e:
        error(e.msg)

    for opt in opts:
        if opt[0] == '-h':
            usage()
            sys.exit(0)
        elif opt[0] == '-v':
            optVerbose = True
        elif opt[0] == '-x':
            optInputFiles = opt[1]
        elif opt[0] == '-m':
            optQACMisra2004MapFile = opt[1]
        elif opt[0] == '-n':
            optMisra20042012MapFile = opt[1]
        elif opt[0] == '-u':
            optKWUser = opt[1]
        elif opt[0] == '-k':
            optKWUrl = opt[1]
        elif opt[0] == '-t':
            optKWMisraTaxonomy = opt[1]
        elif opt[0] == '-r':
            optReportFile = opt[1]
        elif opt[0] == '-d':
            optDryRun = True
        elif opt[0] == '-a':
            optKWPrefix = opt[1]
        elif opt[0] == '-b':
            optProjectPrefix = opt[1]
        else:
            assert(False)

    if len(optInputFiles) == 0:
        error('-x is required (Comma-separated list of paths to PrqaDeviation.xmls)')
    if len(optQACMisra2004MapFile) == 0:
        error('-m is required (qac.usr.messages file path)')
    if len(optMisra20042012MapFile) == 0:
        error('-n is required (misra20042012 file path)')
    if len(optKWUser) == 0:
        error('-u is required (klocwork user name)')
    if len(optMisra20042012MapFile) == 0:
        error('-k is required (klocwork url, e.g. https://klocworkve.got.volvo.net:8080)')
    if len(optKWMisraTaxonomy) == 0:
        error('-t is required (klocwork misra taxonomy file path, e.g. /opt/klocwork/taxonomies/misra_c_2012_c99.tconf)')


    main = Main()
    main.SetFilePaths(optInputFiles)
    main.SetMISRAMapPaths(optQACMisra2004MapFile, optMisra20042012MapFile)
    main.SetFilePathPrefixes(optKWPrefix, optProjectPrefix)
    result = main.Runkwqacmisratransfer(optKWUrl, optKWUser, optVerbose, optKWMisraTaxonomy, optReportFile, optDryRun)
    exit(result)

if __name__ == '__main__':
    main()
