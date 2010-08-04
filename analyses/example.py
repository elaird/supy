#!/usr/bin/env python

import os
import analysis,utils,calculables,calculablesJet,steps

def makeSteps() :
    jetCollection="ak5Jet"
    jetSuffix="Pat"
    jetPtThreshold=10.0
    
    outSteps=[
        steps.progressPrinter(2,300),
        steps.techBitFilter([0],True),
        steps.physicsDeclared(),
        steps.vertexRequirementFilter(5.0,15.0),
        steps.monsterEventFilter(10,0.25),

        steps.jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
        steps.jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
        #steps.jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet
        steps.minNCleanJetEventFilter(jetCollection,jetSuffix,2),
        steps.maxNOtherJetEventFilter(jetCollection,jetSuffix,0),

        steps.cleanJetPtHistogrammer(jetCollection,jetSuffix),
        steps.cleanJetHtMhtHistogrammer(jetCollection,jetSuffix),
        #steps.variableGreaterFilter(25.0,jetCollection+"SumPt"+jetSuffix),

        steps.alphaHistogrammer(jetCollection,jetSuffix),
        #steps.skimmer("/tmp/%s/"%os.environ["USER"]),
        ]
    return outSteps

def makeCalculables() :
    jettypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += [ calculablesJet.indices(        collection = col, suffix = "Pat", ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for col in jettypes]
    listOfCalculables += [ calculablesJet.sumPt(          collection = col, suffix = "Pat") for col in jettypes ]
    listOfCalculables += [ calculablesJet.sumP4(          collection = col, suffix = "Pat") for col in jettypes ]
    listOfCalculables += [ calculablesJet.deltaPseudoJet( collection = col, suffix = "Pat") for col in jettypes ]
    listOfCalculables += [ calculablesJet.alphaT(         collection = col, suffix = "Pat") for col in jettypes ]
    listOfCalculables += [ calculablesJet.diJetAlpha(     collection = col, suffix = "Pat") for col in jettypes ]
    return listOfCalculables

a=analysis.analysis(name="example",
                    outputDir = "/tmp/%s/"%os.environ["USER"],
                    listOfSteps=makeSteps(),
                    listOfCalculables=makeCalculables(),
                    )

a.addSample(sampleName="Example_Skimmed_900_GeV_Data", nEvents = -1, lumi = 1.0e-5, #/pb
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"] )

a.addSample(sampleName="Example_Skimmed_900_GeV_MC", nEvents = -1, xs = 1.0e8, #pb
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"] )


#loop over events and make root files containing histograms
a.loop(profile=False,   #profile the code
       nCores=1,        #use multiple cores to process input files in parallel
       )

#make a pdf file with plots from the histograms created above
a.plot()
