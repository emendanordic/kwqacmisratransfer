# kwqacmisratransfer
# **************************************************************************************************
#  Created by: Emenda
#
#  $LastChangedBy: Andreas Lärfors
#  $LastChangedDate: 2016-09-20
#  $Version: 1.0
#
# Disclaimer: Please note that this software or software component is released by Emenda on a 
# non-proprietary basis for commercial or non-commercial use with no warranty. Emenda will not be 
# liable for any damage or loss caused by the use of this software. Redistribution is only allowed 
# with prior consent.
#
# **************************************************************************************************


INTRODUCTION

kwqacmisratransfer runs through a list of QAC MISRA deviations and attempts to find matching issues
from a list of Klocwork issues. The QAC MISRA deviations are gathered from a deviation file
(usually PrqaDeviation.xml) and cross referenced with the entries in the source code for verification.
The Klocwork issues are fetched directly from the Klocwork server. Matching is done by comparing the 
MISRA 2012 rule that the QAC and Klocwork issues represent, and also by comparing the location of 
the reported issue (including the scope of the QAC MISRA deviation).


REQUIREMENTS

*Script files required:
kwqacmisratransfer/Cfile.py
kwqacmisratransfer/Common.py
kwqacmisratransfer/Deviationfile.py
kwqacmisratransfer/KWConnect.py
kwqacmisratransfer/MISRAMap.py
kwqacmisratransfer/MISRAMap20042012.py
kwqacmisratransfer/MISRAMapQAC2004.py
kwqacmisratransfer/Main.py
kwqacmisratransfer/MessageIndex.py
kwqacmisratransfer/ProjectReport.py
kwqacmisratransfer.py

*Input files required:
misra20042012
qac.usr.messages
PrqaDeviation.xml
misra_c_2012_c99.tconf (found in the "taxonomies" directory of the Klocwork installation)
Source code files containing QAC Deviation comments (/* PRQA ...)

*Other requirements:
Klocwork server with compliance license (enables fetching of line numbers)


EXECUTION

Example execution, simple:
python kwqacmisratransfer.py -x/home/steve/source-code/ -m./qac.usr.messages -n./misra20042012 -usteve -khttp://localhost:8080/klocworkproject -t/opt/klocwork11/taxonomies/misra_c_2012_c99.tconf -r./reportfile.out

Example execution, verbose into output log file:
python kwqacmisratransfer.py -v -x/home/steve/source-code/ -m./qac.usr.messages -n./misra20042012 -usteve -khttp://localhost:8080/klocworkproject -t/opt/klocwork11/taxonomies/misra_c_2012_c99.tconf -r./reportfile.out > debuglog.out

*Arguments:
-h             Print this help (optional)
-v             Verbose (optional)

-x <file>      input file(s) or directories (REQUIRED)

-k <klocwork-url>                       e.g. http(s)://klocworkserver:8080/projectname (REQUIRED)
-u <klocwork-user>                      The user name for the Klocwork server (used in kwauth command) (REQUIRED)
-m <qac-to-misra2004-map-file>          Path to file qac.usr.messages (REQUIRED)
-n <misra2004-to-misra2012-map-file>    Path to misra20042012 file (REQUIRED)
-t <klocwork-misra2012-taxonomy-file>   Path to .tconf for misra2012 Klocwork taxonomy (xml file) (REQUIRED)
-r <report>                             Path to report file (output) (optional)
-p <prqa-deviation-xml>                 Path to deviation approval XML file (PrqaDeviation.xml) (REQUIRED)

TROUBLESHOOTING

For any support queries, please contact support@emenda.eu


FAQ



MAINTAINERS

Andreas Lärfors (andreas.larfors@emenda.eu)

