#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

touch = [
    "triggered",
    #"prescaled",
    #"L1triggered",
    #"L1prescaled"
    #"ak5JetCorrectedP4Pat",
    #"ak5JetJPTCorrectedP4Pat",
    #"ak5JetPFCorrectedP4Pat",
    #"muonP4Pat",
    #"electronP4Pat",
    ]

a=analysis.analysis(name = "triggerSpeedTest",
                    outputDir = "./",
                    listOfCalculables = [],
                    listOfSteps = [ steps.touchstuff(touch) ]
                    )

a.addSample( sampleName="goodcol_v9", nMaxFiles = -1, nEvents = -1, lumi = 0.002, #/pb
             listOfFileNames = ["/d1/bbetchar/SusyCAF/2010_05_12/Skims/CaloJets/GOODCOL-v9_skim.root"] )

a.loop( nCores = 1 )

