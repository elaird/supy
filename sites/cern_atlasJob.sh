#!/bin/bash

# This is very supy-d3pdtrig-specific
# Maybe we can allow the used to specify this script outside of supy?



export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup
cd /afs/cern.ch/work/g/gerbaudo/public/trigger/MyRootCoreDir/
source $AtlasSetup/scripts/asetup.sh AtlasP1HLT,17.1.4.5,here
source RootCore/scripts/setup.sh
export STAGE_SVCCLASS=atlcal
cd -

#INSERT_BATCH_SETUP
