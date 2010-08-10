#!/usr/bin/env python

import os,analysis,utils,steps,calculables

touch = [
    #"triggered",
    #"prescaled",
    #"L1triggered",
    #"L1prescaled"
    "ak5JetCorrectedP4Pat",
    "ak5JetJPTCorrectedP4Pat",
    "ak5JetPFCorrectedP4Pat",
    "muonP4Pat",
    "electronP4Pat",
    ]

a=analysis.analysis(name = "triggerSpeedTest",
                    outputDir = "./",
                    listOfCalculables = [],
                    listOfSteps = [ steps.touchstuff(touch) ]
                    )

a.addSample( sampleName="JetMETTau.Run2010A.Jul16thReReco", nMaxFiles = -1, nEvents = -1, lumi = 0.120, #/pb
             listOfFileNames = utils.fileListFromDisk("/vols/cms02/elaird1/05_skims/JetMETTau.Run2010A-Jul6thReReco_v1.RECO/") )

a.loop( nCores = 1 )

