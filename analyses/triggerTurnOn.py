#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

def makeSteps() :
    jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]
    stepList=[ steps.progressPrinter(2,300),
               steps.techBitFilter([0],True),
               steps.physicsDeclared(),
               steps.vertexRequirementFilter(5.0,15.0),
               steps.monsterEventFilter(10,0.25),
               steps.hltTurnOnHistogrammer(probeTrigger = "HLT_Jet50U", var = "ak5JetLeadingPtPat", tagTriggers = ["HLT_Jet30U"], )
               ]
    return stepList

def makeCalculables() :
    return calculables.zeroArgs() + [ \
           calculablesJet.leadingPt(collection="ak5Jet",suffix="Pat"), \
           calculablesJet.indices(collection="ak5Jet",suffix="Pat",ptMin=20., etaMax=3.0,flagName="JetIDLoose") ]

a=analysis.analysis(name = "triggerTurnOn",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables()
                    )

a.addSample(sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn",
            lumi = 0.012,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/"),
            nMaxFiles = 1,
            nEvents = -1)

# a.addSample(sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",
#             lumi = 0.120,#/pb
#             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/"),
#             nMaxFiles = -1,
#             nEvents = -1)

# a.addSample(sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn",
#             lumi = 0.1235,#/pb
#             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/"),
#             nMaxFiles = -1,
#             nEvents = -1)


a.loop( nCores = 1, splitJobsByInputFile = False)
#a.plot()
