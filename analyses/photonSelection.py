#!/usr/bin/env python

import os
import analysis,utils,steps,calculables,samples,plotter
import ROOT as r

jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]

def makeSteps() :
    jets = jetTypes[0]
    xcjets = ("xc"+jets[0],jets[1])
    
    listOfSteps=[
        steps.progressPrinter(),
        
        steps.hltFilter("HLT_Jet50U"),
        steps.leadingUnCorrJetPtSelector([jets],100.0),
        steps.techBitFilter([0],True),
        steps.physicsDeclared(),
        steps.vertexRequirementFilter(),
        steps.monsterEventFilter(),
        steps.hbheNoiseFilter(),
        
        steps.photonSelectionHistogrammer( nametag = "raw", matchDeltaRMax = 0.1),
        steps.jetPtSelector(jets,100.0,0),
        steps.jetPtSelector(jets,40.0,1),
        steps.maxNOtherJetEventFilter(jets,0),
        steps.minNCleanJetEventFilter(xcjets,2),
        steps.photonSelectionHistogrammer( nametag = "jets", matchDeltaRMax = 0.1),
        steps.alphaHistogrammer(xcjets),
        steps.variableGreaterFilter(300.0,"%sSumPt%s"%xcjets),
        steps.variableGreaterFilter(0.55,"%sAlphaT%s"%xcjets),
        steps.displayer(xcjets,"met","Calo","Pat","ak5Jet","Calo",recHitPtThreshold=1.0,#GeV
                        outputDir="/vols/cms02/%s/tmp/"%os.environ["USER"],scale=200.0),
        ]
    return listOfSteps

def makeCalculables() :
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += calculables.fromJetCollections(jetTypes)
    listOfCalculables += calculables.fromJetCollections([("xc"+jt[0],jt[1]) for jt in jetTypes])
    listOfCalculables += [ calculables.jetIndices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculables.jetIndicesOther( collection = jetType, ptMin = 20.0) for jetType in jetTypes]

    listOfCalculables += [ calculables.xcJetCorrectedP4(jetType, photons = ("photon","Pat"), photonDR = 0.5) for jetType in jetTypes ]
    listOfCalculables += [ calculables.xcJetIndices(("xc"+jt[0],jt[1])) for jt in jetTypes]

    listOfCalculables += [ calculables.genIndices( label = "Z",      pdgs = [23],     ptMin = 30, etaMax = 5),
                           calculables.genIndices( label = "Photon", pdgs = [22],     ptMin = 30, etaMax = 5),
                           calculables.photonIndicesPat( flagName="photonIDLoosePat", ptMin = 30, etaMax = 5) ]
    return listOfCalculables

def makeSamples() :
    from samples import specify
    return [#specify(name = "JetMETTau.Run2010A",    nFilesMax = 1, nEventsMax = 1000, color = r.kBlack   , markerStyle = 20),
            specify(name = "qcd_py_pt30",           nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt80",           nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt170",          nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt300",          nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt470",          nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt800",          nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "qcd_py_pt1400",         nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            specify(name = "gammajets_mg_pt40_100", nFilesMax = 1, nEventsMax = 1000, color = r.kGreen   ),
            specify(name = "gammajets_mg_pt100_200",nFilesMax = 1, nEventsMax = 1000, color = r.kGreen   ),
            specify(name = "gammajets_mg_pt200",    nFilesMax = 1, nEventsMax = 1000, color = r.kGreen   ),
            specify(name = "tt_tauola_mg",          nFilesMax = 1, nEventsMax = 1000, color = r.kOrange  ),
            specify(name = "z_inv_mg",              nFilesMax = 1, nEventsMax = 1000, color = r.kMagenta ),
            specify(name = "z_jets_mg",             nFilesMax = 1, nEventsMax = 1000, color = r.kYellow-3),
            specify(name = "w_jets_mg",             nFilesMax = 1, nEventsMax = 1000, color = 28         ),
            specify(name = "lm0",                   nFilesMax = 1, nEventsMax = 1000, color = r.kRed     ),
            specify(name = "lm1",                   nFilesMax = 1, nEventsMax = 1000, color = r.kRed+1   ),
            ]

a = analysis.analysis( name = "photonSelection",
                       outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                       listOfSteps = makeSteps(),
                       listOfCalculables = makeCalculables(),
                       listOfSamples = makeSamples(),
                       listOfSampleDictionaries = [samples.mc, samples.jetmet]
                       )
#a.loop( nCores = 6 )

##plotting
a.mergeHistograms(target="g_jets_mg", targetColor = r.kGreen, source=["gammajets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
a.mergeHistograms(target="qcd_py",    targetColor = r.kBlue, source=["qcd_py_pt%d"%i         for i in [30,80,170,300,470,800,1400] ])
a.mergeAllHistogramsExceptSome(target="standard_model",targetColor = r.kGreen, dontMergeList=["JetMETTau.Run2010A","lm0","lm1"],keepSourceHistograms=True)

plotter.plotAll(hyphens=a.hyphens,
                listOfPlotContainers=a.organizeHistograms(),
                psFileName=a.outputDir+"/"+a.name+".ps",
                samplesForRatios=("JetMETTau.Run2010A","qcd_py"),
                sampleLabelsForRatios=("data","sim"),
                )
