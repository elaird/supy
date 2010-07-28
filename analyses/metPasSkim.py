#!/usr/bin/env python

import analysis,utils

a=analysis.analysis(name="metPasSkim",
                    outputDir="/vols/cms02/elaird1/tmp/"
                    )

a.addSampleSpec(sampleName="JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/",nMaxFiles=-1),
                listName="metPasFilter",
                isMc=False,
                nEvents=-1)

a.addSampleSpec(sampleName="JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/",nMaxFiles=-1),
                listName="metPasFilter",
                isMc=False,
                nEvents=-1)

a.go(loop=True,
     plot=False,
     profile=False,
     nCores=6,
     splitJobsByInputFile=True
     )
