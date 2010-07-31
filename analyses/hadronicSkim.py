#!/usr/bin/env python

import analysis,utils,calculables,steps

def makeSteps() :
    jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]
    stepList=[ steps.progressPrinter(2,300),
               steps.hltFilter("HLT_Jet50U"),
               steps.leadingUnCorrJetPtSelector(jetAlgoList,80.0),
               steps.techBitFilter([0],True),
               steps.physicsDeclared(),
               steps.vertexRequirementFilter(5.0,15.0),
               steps.monsterEventFilter(10,0.25),
               steps.skimmer("/vols/cms02/elaird1/"),
               ]
    return stepList

a=analysis.analysis(name="hadronicSkim",
                    outputDir="/vols/cms02/elaird1/tmp/",
                    listOfSteps=makeSteps(),
                    calculables=calculables.allDefaultCalculables()                    
                    )

a.addSample(sampleName="JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn",
            listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/",nMaxFiles=-1),
            lumi=0.012,                
            nEvents=-1)

a.addSample(sampleName="JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",
            listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/",
                                                    itemsToSkip=["123_5_062","79_1_034"],
                                                    nMaxFiles=-1),
            lumi=0.120,
            nEvents=-1)

a.loop(nCores=6,splitJobsByInputFile=True)
#a.plot()
