#!/bin/bash

source /uscmst1/prod/sw/cms/shrc prod
export SCRAM_ARCH=slc5_amd64_gcc462

cd /cvmfs/cms.cern.ch/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_2_5/src && eval \`scram runtime -sh\` && cd - >& /dev/null

#INSERT_BATCH_SETUP

if [ -e `pwd`/local.sh ]; then
    source `pwd`/local.sh
fi
