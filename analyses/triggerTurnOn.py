#!/usr/bin/env python
import os,analysis,utils,steps,calculables

jetTypes = [ (col,"Pat") for col in ["ak5Jet","ak5JetJPT","ak5JetPF"]]

def makeSteps() :
    stepList = [ steps.progressPrinter(),
                 steps.techBitFilter([0],True),
                 steps.physicsDeclared(),
                 steps.vertexRequirementFilter(),
                 steps.monsterEventFilter(),
                 steps.hbheNoiseFilter() ]
    stepList+= [ steps.maxNOtherJetEventFilter(col,0) for col in jetTypes ]
    stepList+= [ steps.hltTurnOnHistogrammer(probeTrig = "HLT_Jet50U", var = "%sLeadingPt%s"%col, tagTrigs = ["HLT_Jet30U"], binsMinMax = (240,0,120) ) \
                 for col in jetTypes ]
    return stepList

def makeCalculables() :
    calcs =  calculables.zeroArgs()
    calcs += [ calculables.leadingJetPt( collection = col) for col in jetTypes] 
    calcs += [ calculables.jetIndices( collection = col, ptMin = 20., etaMax = 3.0, flagName = "JetIDloose") for col in jetTypes ]
    calcs += [ calculables.PFJetIDloose( collection = jetTypes[2],
                                         fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    return calcs

a=analysis.analysis( name = "triggerTurnOn",
                     outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                     listOfSteps = makeSteps(),
                     listOfCalculables = makeCalculables()
                    )

def dummy(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
    return []
utils.fileListFromSrmLs=dummy

a.addSample( sampleName = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.012,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_16_52_06/"))

a.addSample( sampleName = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.120,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_17_20_35/"))

a.addSample( sampleName = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn", nMaxFiles = -1, nEvents = -1, lumi = 0.1235,#/pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bm409//ICF/automated/2010_07_20_15_40_06/"))

#a.loop( nCores = 6 )

#########################################################

targetName = "JetMETTau.Run2010A"
a.mergeAllHistogramsExceptSome( target=targetName,
                                dontMergeList=[],
                                keepSourceHistograms = False)
organizedHists = a.organizeHistograms( multipleDisjointDataSamples = True)
histograms = dict([(spec["plotName"],spec['histoDict'][targetName]) for spec in organizedHists])

import ROOT as r
import re

hists = 3*[None]
vars = ["ak5JetLeadingPtPat", "ak5JetJPTLeadingPtPat","ak5JetPFLeadingPtPat"]
labels = ["Calo","JetPlusTracks","Particle Flow"]
colors = [r.kRed, r.kGreen, r.kBlue]

for var,tag,probe in filter( lambda Tuple: len(Tuple)==3, \
                             [ tuple(re.split(r"(\w*)_given_(\w*)_and_(\w*)",name)[1:-1]) for name in histograms ] ) :
    numerator = histograms["%s_given_%s_and_%s" % (var,tag,probe)]
    denomenator = histograms["%s_given_%s" % (var,tag)]
    name = "efficiencyBy_%s_of_%s_given_%s"%(var,probe,tag)
    hist = numerator.Clone(name)
    hist.Divide(numerator,denomenator,1,1,"B") #binomial errors
    hist.GetYaxis().SetTitle("efficiency")
    hist.SetTitle("Probability of %s given %s" % (probe,tag))

    if var in vars :
        hists[vars.index(var)] = hist
        hist.GetXaxis().SetTitle("Leading Jet p_{T}  (GeV)")
        hist.GetXaxis().SetLimits(20,120)
        hist.SetMaximum(1)

r.gROOT.SetStyle("Plain")
r.gStyle.SetOptStat(0)
leg = r.TLegend(0.15,0.6,0.4,0.87)
c = r.TCanvas("c","",800,600)
c.SetGridx()
c.SetGridy()

same = ""
for i in range(3) :
    hists[i].SetLineColor(colors[i])
    leg.AddEntry(hists[i],labels[i])
    hists[i].Draw(same)
    same = "same"
leg.Draw()

c.Print("triggerTurnOn.eps")
