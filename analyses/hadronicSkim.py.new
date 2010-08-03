#!/usr/bin/env python

import analysis,utils,calculables,steps,os

def makeSteps() :
    jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]
    stepList=[ steps.progressPrinter(2,300),
               steps.hltFilter("HLT_Jet50U"),
               steps.leadingUnCorrJetPtSelector(jetAlgoList,80.0),
               steps.techBitFilter([0],True),
               steps.physicsDeclared(),
               steps.vertexRequirementFilter(5.0,15.0),
               steps.monsterEventFilter(10,0.25),
               steps.skimmer("/vols/cms02/%s/"%os.environ["USER"]),
               ]
    return stepList

def makeCalculables() :
    return calculables.zeroArgs()

a=analysis.analysis(name = "hadronicSkim",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables()
                    )

a.addSample(sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.012,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/") )

a.addSample(sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.120,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/") )

a.addSample(sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.1235,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/") )

a.loop( nCores = 6 )
#a.plot()
