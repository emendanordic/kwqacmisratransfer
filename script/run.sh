#/bin/bash
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

ROOTDIR='NOT_SET'
LIBDIR=$ROOTDIR'/lib'

DEVFILEPATHS='../sample-code/PrqaDeviation.xml'

KWURL='http://localhost:8080/samplecode'
KWINSTALLDIR='/opt/klocwork11'
KWMISRATAXONOMY=$KWINSTALLDIR'/taxonomies/misra_c_2012_c99.tconf'

KWFILEPATHPREFIX='C:\J\Klocwork-Analysis\'
PROJECTFILEPATHPREFIX='/cygwin/test/test/'

DRYRUN='-d'

python kwqacmisratransfer.py -v $DRYRUN -x$DEVFILEPATHS -a$KWFILEPATHPREFIX -b$PROJECTFILEPATHPREFIX -m$LIBDIR/qac.usr.messages -n$LIBDIR/misra20042012 -uNOT_SET -k$KWURL -t$KWMISRATAXONOMY -r./reportfile.out > verboseoutput.out

