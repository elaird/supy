#!/usr/bin/env python

import analysis
        
a=analysis.analysis(name="metPasLook",
                    outputDir="/vols/cms02/elaird1/tmp/"
                    )

a.addSampleSpec(sampleName="JetMETTau.Run2010A-Jul6thReReco_v1.RECO_cleanEvent",
                listName="metPasLook",
                isMc=False,
                nEvents=-1)

a.go(loop=True,
     plot=True,
     profile=False,
     nCores=6,
     splitJobsByInputFile=True
     )
