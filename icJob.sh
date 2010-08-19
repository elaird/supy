#!/bin/bash

. /vols/cms/grid/setup.sh
cd ~elaird1/03_SusyCAFmacro/CMSSW_3_6_1/src/ && eval `scram runtime -sh` && cd - >& /dev/null
cd ~elaird1/supy_dev2
export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
