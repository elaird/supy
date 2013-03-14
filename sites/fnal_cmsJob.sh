#!/bin/bash

source /uscmst1/prod/sw/cms/shrc prod
export SCRAM_ARCH=slc5_amd64_gcc462
#cd /uscmst1/prod/sw/cms/slc5_amd64_gcc462/cms/cmssw-patch/CMSSW_5_2_4_patch1/src && eval \`scram runtime -sh\` && cd - >& /dev/null
cd /uscms/home/elaird/CMSSW_5_2_5/src && eval `scram runtime -sh` && cd - >& /dev/null
