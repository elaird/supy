#!/bin/bash

source /uscmst1/prod/sw/cms/shrc prod
cd /uscmst1/prod/sw/cms/slc5_ia32_gcc434/cms/cmssw/CMSSW_3_8_5/src && eval `scram runtime -sh` && cd - >& /dev/null
