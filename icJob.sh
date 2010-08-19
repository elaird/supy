#!/bin/bash

USERTMP="/vols/cms02/$USER/tmp"
CMSSW=/vols/sl5_exp_software/cms/slc5_ia32_gcc434/cms/cmssw/CMSSW_3_7_0/src
mkdir -p $USERTMP >& /dev/null
. /vols/cms/grid/setup.sh
cd $CMSSW && eval `scram runtime -sh` && cd - >& /dev/null
export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
