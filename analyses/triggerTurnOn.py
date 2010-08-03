#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

def makeSteps() :
    jetTypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    stepList=[ steps.progressPrinter(2,300),
               steps.techBitFilter([0],True),
               steps.physicsDeclared(),
               steps.vertexRequirementFilter(5.0,15.0),
               steps.monsterEventFilter(10,0.25)
               ] + [ steps.hltTurnOnHistogrammer(probeTrig = "HLT_Jet50U", var = "%sLeadingPtPat"%col, tagTrigs = ["HLT_Jet30U"], binsMinMax = (75,0,150) ) \
                     for col in jetTypes ]
    return stepList

def makeCalculables() :
    jetTypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    return calculables.zeroArgs() \
           + [ calculablesJet.leadingPt(collection=col,suffix="Pat") for col in jetTypes] \
           + [ calculablesJet.indices(collection=col,suffix="Pat",ptMin=20., etaMax=3.0,flagName="JetIDloose") for col in jetTypes[:-1] ] \
           + [ calculablesJet.indices(collection="ak5JetPF",suffix="Pat",ptMin=20., etaMax=3.0,) ]

a=analysis.analysis( name = "triggerTurnOn",
                     outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                     listOfSteps = makeSteps(),
                     listOfCalculables = makeCalculables()
                    )

a.addSample( sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.012,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/"))

a.addSample( sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.120,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/"))

a.addSample( sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.1235,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/"))

a.loop( nCores = 6 )
#a.plot()
