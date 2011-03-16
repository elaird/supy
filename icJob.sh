#!/bin/bash

export X509_USER_PROXY=/home/hep/$USER/.MyProxy
export SCRAM_ARCH=slc5_amd64_gcc434
CMSSW=/vols/sl5_exp_software/cms/slc5_amd64_gcc434/cms/cmssw/CMSSW_4_1_2/src
. /vols/cms/grid/setup.sh
cd $CMSSW && eval `scram runtime -sh` && cd - >& /dev/null
#export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
