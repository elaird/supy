#!/bin/bash

source /uscmst1/prod/sw/cms/shrc prod
export SCRAM_ARCH=slc5_amd64_gcc462

if [[ "$HOSTNAME" == *cmslpc*.fnal.gov ]]; then
    cd /uscms/home/elaird/CMSSW_5_2_5/src && eval `scram runtime -sh` && cd - >& /dev/null
else
    cd /uscmst1/prod/sw/cms/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_2_5/src && eval \`scram runtime -sh\` && cd - >& /dev/null
fi

#INSERT_BATCH_SETUP

if [ -e `pwd`/local.sh ]; then
    source `pwd`/local.sh
fi
