#!/usr/bin/env python

import os,copy
import analysis,steps,calculables,samples,plotter
import ROOT as r

def makeSteps() :
    jets=("ak5Jet","Pat")
    #jets=("ak5JetJPT","Pat")
    #jets=("ak5JetPF","Pat")
    
    metCollection="met"
    metSuffix="Calo"
    metSuffix=jets[0][:3].upper()
    metSuffix+="TypeII"
    #metSuffix="PF"
    
    leptonSuffix="Pat"
    #leptonSuffix="PF"

    #for displayer only
    recHitType="Calo"
    genJetCollection="ak5Jet"
    
    listOfSteps=[
        steps.progressPrinter(),
        
        steps.ptHatHistogrammer(),
        steps.jetPtSelector(jets,100.0,0),
        #steps.jetPtSelector(jets,40.0,1),
        steps.leadingUnCorrJetPtSelector( [jets],100.0 ),

        steps.hltFilter("HLT_Jet50U"),
        steps.hltPrescaleHistogrammer(["HLT_ZeroBias","HLT_Jet50U","HLT_MET45"]),

        steps.minNCleanJetEventFilter(jets,2),
        steps.maxNOtherJetEventFilter(jets,0),
        steps.hbheNoiseFilter(),
        
        steps.variableGreaterFilter(300.0,jets[0]+"SumPt"+jets[1]),
        steps.cleanJetPtHistogrammer(jets),
        steps.cleanJetHtMhtHistogrammer(jets),
        steps.alphaHistogrammer(jets),

        #steps.eventPrinter(),
        #steps.htMhtPrinter(jets),       
        #steps.genParticlePrinter(minPt=10.0,minStatus=3),
        
        steps.variableGreaterFilter(0.55,jets[0]+"AlphaT"+jets[1]),
        steps.objectPtVetoer("muon","P4","Pat",20.0,0),

        #steps.deltaPhiStarHistogrammer(jets),
        #steps.skimmer("/vols/cms02/%s/"%os.environ["USER"]),
        #steps.displayer(jets,metCollection,metSuffix,leptonSuffix,genJetCollection,recHitType,recHitPtThreshold=1.0,#GeV
        #                outputDir="/vols/cms02/%s/tmp/"%os.environ["USER"],scale=200.0),

        #steps.eventPrinter(),
        #steps.jetPrinter(jets),
        #steps.htMhtPrinter(jets),
        #steps.nJetAlphaTPrinter(jets)
        ]
    return listOfSteps

def makeCalculables() :
    jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += calculables.fromJetCollections(jetTypes)
    listOfCalculables += [ calculables.jetIndices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculables.jetIndicesOther( collection = jetType, ptMin = 20.0) for jetType in jetTypes]
    listOfCalculables += [ calculables.PFJetIDloose( collection = jetTypes[2],
                                                     fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    return listOfCalculables

def makeSamples() :
    from samples import specify
    return [specify(name = "JetMET.Run2010A",        color = r.kBlack   , markerStyle = 20),
            specify(name = "qcd_py_pt30",            color = r.kBlue    ),
            specify(name = "qcd_py_pt80",            color = r.kBlue    ),
            specify(name = "qcd_py_pt170",           color = r.kBlue    ),
            specify(name = "qcd_py_pt300",           color = r.kBlue    ),
            specify(name = "qcd_py_pt470",           color = r.kBlue    ),
            specify(name = "qcd_py_pt800",           color = r.kBlue    ),
            specify(name = "qcd_py_pt1400",          color = r.kBlue    ),
            specify(name = "gammajets_mg_pt40_100",  color = r.kGreen   ),
            specify(name = "gammajets_mg_pt100_200", color = r.kGreen   ),
            specify(name = "gammajets_mg_pt200",     color = r.kGreen   ),
            specify(name = "tt_tauola_mg",           color = r.kOrange  ),
            specify(name = "z_inv_mg",               color = r.kMagenta ),
            specify(name = "z_jets_mg",              color = r.kYellow-3),
            specify(name = "w_jets_mg",              color = 28         ),
            specify(name = "lm0",                    color = r.kRed     ),
            specify(name = "lm1",                    color = r.kRed+1   ),
            ]
    
a=analysis.analysis(name = "hadronicLook",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables(),
                    listOfSamples = makeSamples(),
                    listOfSampleDictionaries = [samples.mc, samples.jetmet]
                    )

a.loop( nCores = 8 )

#plotting
a.mergeHistograms(target = "g_jets_mg",      targetColor = r.kGreen,   source = ["gammajets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
a.mergeHistograms(target = "qcd_py",         targetColor = r.kBlue,    source = ["qcd_py_pt%d"%i         for i in [30,80,170,300,470,800,1400] ])
a.mergeHistograms(target = "standard_model", targetColor = r.kGreen+3, source = ["g_jets_mg","qcd_py","tt_tauola_mg",
                                                                                 "z_inv_mg","z_jets_mg","w_jets_mg"], keepSourceHistograms = True)
listOfPlotContainers=a.organizeHistograms()

plotter.plotAll(listOfPlotContainers=listOfPlotContainers,
                psFileName=a.outputDir+"/"+a.name+".ps",
                #samplesForRatios=("JetMET.Run2010A","qcd_py"),
                #sampleLabelsForRatios=("data","qcd"),
                samplesForRatios=("JetMET.Run2010A","standard_model"),
                sampleLabelsForRatios=("data","sm"),
                )

#import statMan
#statMan.go(a.organizeHistograms(),
#           dataSampleName="JetMETTau.Run2010A",
#           mcSampleName="standard_model",
#           moneyPlotName="ak5JetPat_alphaT_vs_Ht_ge2jets",
#           xCut=0.51,yCut=330.0)
#
