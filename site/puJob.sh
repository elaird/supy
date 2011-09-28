#!/bin/bash

export SCRAM_ARCH=slc5_ia32_gcc434
source /tigress-hsm/cmssoft/base5/cmsset_default.sh
cd /tigress-hsm/cmssoft/base5/slc5_ia32_gcc434/cms/cmssw/CMSSW_3_8_5/src && eval `scram runtime -sh` && cd - >& /dev/null
