#!/usr/bin/env python

import analysis,utils,calculables,steps,os

def makeCalculables() :
    return calculables.zeroArgs()

a=analysis.analysis(name = "jsonMaker",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = [ steps.progressPrinter(2,300),
                                    steps.jsonMaker("/vols/cms02/%s/tmp/"%os.environ["USER"]),
                                    ],
                    listOfCalculables = makeCalculables(),
                    mainTree=("lumiTree","tree"),
                    otherTreesToKeepWhenSkimming=[],
                    )

a.addSample(sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.012,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/") )

a.addSample(sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.120,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/") )

a.addSample(sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.1235,#/pb
            listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/") )

a.loop( nCores = 6 )
#a.plot()
