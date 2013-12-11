#!/bin/bash

export SCRAM_ARCH=slc5_amd64_gcc462
cd /afs/cern.ch/cms/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_3_7/src/ && eval `scram runtime -sh` && cd - > /dev/null
