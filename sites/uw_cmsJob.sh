#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc491
export PATH=${PATH}:/cvmfs/cms.cern.ch/common
cd /cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/CMSSW_7_4_7/src && eval `scram runtime -sh` && cd - >& /dev/null

#INSERT_BATCH_SETUP
