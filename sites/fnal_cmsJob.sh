#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc5_amd64_gcc462

cd /cvmfs/cms.cern.ch/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_2_5/src && eval `scram runtime -sh` && cd - >& /dev/null

#INSERT_BATCH_SETUP

if [ -e `pwd`/local.sh ]; then
    source `pwd`/local.sh
fi
