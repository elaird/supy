#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

def makeSteps() :
    jetTypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    stepList = [ steps.progressPrinter(2,300),
                 steps.techBitFilter([0],True),
                 steps.physicsDeclared(),
                 steps.vertexRequirementFilter(5.0,15.0),
                 steps.monsterEventFilter(10,0.25) ]
    stepList+= [ steps.hltTurnOnHistogrammer(probeTrig = "HLT_Jet50U", var = "%sLeadingPtPat"%col, tagTrigs = ["HLT_Jet30U"], binsMinMax = (75,0,150) ) \
                 for col in jetTypes ]
    return stepList

def makeCalculables() :
    jetTypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    calcs =  calculables.zeroArgs()
    calcs += [ calculablesJet.leadingPt( collection = col, suffix="Pat") for col in jetTypes] 
    calcs += [ calculablesJet.indices( collection = col, suffix = "Pat", ptMin = 20., etaMax = 3.0, flagName = "JetIDloose") for col in jetTypes[:-1] ]
    calcs += [ calculablesJet.pfIndicesByHand( collection = "ak5JetPF", suffix = "Pat", ptMin = 20., etaMax = 3.0,
                                               fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    return calcs

a=analysis.analysis( name = "triggerTurnOn",
                     outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                     listOfSteps = makeSteps(),
                     listOfCalculables = makeCalculables()
                    )

a.addSample( sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", nMaxFiles = 1, nEvents = -1, lumi = 0.012,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/"))

a.addSample( sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", nMaxFiles = 1, nEvents = -1, lumi = 0.120,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/"))

a.addSample( sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn", nMaxFiles = 1, nEvents = -1, lumi = 0.1235,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/"))

a.loop( nCores = 3 )


#########################################################

import ROOT as r
outFiles = a.listOfOutputPlotFileNames

fileName = "triggerTurnOn_plots.root"
os.system("rm %s >& /dev/null" % fileName)
os.system('hadd %s %s | grep "Target file:"' % (fileName, ' '.join(outFiles)))
file = r.TFile.Open(fileName)
r.gDirectory.ls()
