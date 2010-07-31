#!/usr/bin/env python

import analysis,utils,calculables,steps

def makeSteps() :
    jetCollection="ak5Jet"
    jetSuffix="Pat"
    jetPtThreshold=10.0
    nCleanJets=2
    jetEtaMax=3.0
    
    outSteps=[
        steps.progressPrinter(2,300),
        steps.techBitFilter([0],True),
        steps.physicsDeclared(),
        steps.vertexRequirementFilter(5.0,15.0),
        steps.monsterEventFilter(10,0.25),

        steps.jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
        steps.jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
        #steps.jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet

        steps.nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
        steps.nOtherJetEventFilter(jetCollection,jetSuffix,1),
        steps.cleanJetPtHistogrammer(jetCollection,jetSuffix),

        steps.cleanJetHtMhtProducer(jetCollection,jetSuffix),
        steps.cleanJetHtMhtHistogrammer(jetCollection,jetSuffix,True),
        #steps.variableGreaterFilter(25.0,jetCollection+"SumPt"+jetSuffix),

        steps.cleanDiJetAlphaProducer(jetCollection,jetSuffix),
        steps.cleanNJetAlphaProducer(jetCollection,jetSuffix),
        steps.alphaHistogrammer(jetCollection,jetSuffix),

        #steps.skimmer("/tmp/"),
        ]
    return outSteps
    
a=analysis.analysis(name="example",
                    outputDir="/tmp/",
                    listOfSteps=makeSteps(),
                    calculables=calculables.allDefaultCalculables()                    
                    )

a.addSample(sampleName="Example_Skimmed_900_GeV_Data",
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"],
            lumi=1.0e-5, #/pb
            nEvents=-1)

a.addSample(sampleName="Example_Skimmed_900_GeV_MC",
            listOfFileNames=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"],
            xs=1.0e3, #pb
            nEvents=100)

#loop over events and make root files containing histograms
a.loop(profile=False,              #profile the code
       nCores=1,                   #use multiple cores to process samples in parallel
       splitJobsByInputFile=False  #process all input files (rather than just samples) in parallel
       )

#make a pdf file with plots from the histograms created above
a.plot()
