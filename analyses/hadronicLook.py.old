#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet,plotter
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
        steps.cleanJetPtHistogrammer(jets),
        steps.hbheNoiseFilter(),
        steps.cleanJetHtMhtHistogrammer(jets),
        
        steps.variableGreaterFilter(300.0,jets[0]+"SumPt"+jets[1]),
        steps.alphaHistogrammer(jets),

        #steps.eventPrinter(),
        #steps.htMhtPrinter(jets),       
        #steps.genParticlePrinter(minPt=10.0,minStatus=3),

        steps.variableGreaterFilter(0.55,jets[0]+"AlphaT"+jets[1]),
        steps.objectPtVetoer("muon","P4","Pat",20.0,0),

        steps.deltaPhiStarHistogrammer(jets),
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
    listOfCalculables += [ calculablesJet.indices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes[:2]]
    listOfCalculables += [ calculablesJet.pfIndicesByHand( collection = jetTypes[2], ptMin = 20., etaMax = 3.0,
                                                           fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0) ]
    listOfCalculables += [ calculablesJet.sumPt(   collection = jetType)                                                      for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.sumP4(   collection = jetType)                                                      for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.deltaPseudoJet( collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.alphaT(         collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.diJetAlpha(     collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.deltaPhiStar(   collection = jetType) for jetType in jetTypes ]    
    return listOfCalculables

#def dummy(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
#    return []
#utils.fileListFromSrmLs=dummy

a=analysis.analysis(name = "hadronicLook",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables()
                    )

a.addSample( sampleName="JetMETTau.Run2010A", nMaxFiles = -1, nEvents = -1, lumi = 0.012+0.120+0.1235,#/pb
             listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data/") )

##PY QCD SKIMS
#a.addSample( sampleName="qcd_py_pt80_skim", nMaxFiles = -1, nEvents = -1, xs = 0.894,#pb
#             listOfFileNames=utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt80/") )
#a.addSample( sampleName="qcd_py_pt170_skim", nMaxFiles = -1, nEvents = -1, xs = 0.377,#pb
#             listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt170/") )
#a.addSample( sampleName="qcd_py_pt300_skim", nMaxFiles = -1, nEvents = -1, xs = 0.0409,#pb
#             listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt300/") )
#a.addSample( sampleName="qcd_py_pt470_skim", nMaxFiles = -1, nEvents = -1, xs = 0.002362,#pb
#             listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt470/") )
#a.manageNonBinnedSamples(ptHatLowerThresholdsAndSampleNames=[(80,"qcd_py_pt80_skim"),
#                                                             (170,"qcd_py_pt170_skim"),
#                                                             (300,"qcd_py_pt300_skim"),
#                                                             (470,"qcd_py_pt470_skim"),
#                                                             ])

#PY QCD
a.addSample( sampleName="qcd_py_pt30", nMaxFiles = -1, nEvents = -1, xs = 6.041e+07,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/") )
a.addSample( sampleName="qcd_py_pt80", nMaxFiles = -1, nEvents = -1, xs = 9.238e+05,#pb
             listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_00_55_17/") )
a.addSample( sampleName="qcd_py_pt170", nMaxFiles = -1, nEvents = -1, xs = 2.547e+04,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_01_33_23/") )
a.addSample( sampleName="qcd_py_pt300", nMaxFiles = -1, nEvents = -1, xs = 1.256e+03,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_09_19_13_09/") )
a.addSample( sampleName="qcd_py_pt470", nMaxFiles = -1, nEvents = -1, xs = 8.798e+01,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_10_04_22_06/") )
a.addSample( sampleName="qcd_py_pt800", nMaxFiles = -1, nEvents = -1, xs = 2.186e+00,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_10_04_37_56/") )
a.addSample( sampleName="qcd_py_pt1400", nMaxFiles = -1, nEvents = -1, xs = 1.122e-02,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_10_04_47_48/") )
a.manageNonBinnedSamples(ptHatLowerThresholdsAndSampleNames=[(i,"qcd_py_pt%d"%i) for i in [30,80,170,300,470,800,1400] ])

#MG GAMMA + JETS
a.addSample( sampleName="gammajets_mg_pt40_100", nMaxFiles = -1, nEvents = -1, xs = 23620,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb//ICF/automated/2010_07_26_15_14_40//PhotonJets_Pt40to100-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))
a.addSample( sampleName="gammajets_mg_pt100_200", nMaxFiles = -1, nEvents = -1, xs = 3476,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt100to200-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))
a.addSample( sampleName="gammajets_mg_pt200", nMaxFiles = -1, nEvents = -1, xs = 485,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt200toInf-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

#OTHER
a.addSample( sampleName="tt_tauola_mg", nMaxFiles = -1, nEvents = -1, xs = 95.0,#pb
             listOfFileNames = utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n") )

a.addSample( sampleName="z_inv_mg", nMaxFiles = -1, nEvents = -1, xs=4500.0,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/zph04/ICF/automated/2010_07_14_11_52_58/",itemsToSkip=["14_3.root"]))

a.addSample( sampleName="z_jets_mg", nMaxFiles = -1, nEvents = -1, xs=2400.0,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_07_05_22_43_20/", pruneList=False) )

a.addSample( sampleName="w_jets_mg", nMaxFiles = -1, nEvents = -1, xs=24170.0,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_06_18_22_33_23/") )

a.addSample( sampleName="lm0", nMaxFiles = -1, nEvents = -1, xs = 38.93,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

a.addSample( sampleName="lm1", nMaxFiles = -1, nEvents = -1, xs = 4.888,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/") )

a.loop( nCores = 6 )

##plotting
a.mergeHistograms(target="g_jets_mg", source=["gammajets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
a.mergeHistograms(target="qcd_py",    source=["qcd_py_pt%d"%i         for i in [30,80,170,300,470,800,1400] ])
a.mergeAllHistogramsExceptSome(target="standard_model",dontMergeList=["JetMETTau.Run2010A","lm0","lm1"],keepSourceHistograms=True)

colorDict={}
colorDict["JetMETTau.Run2010A"]=r.kBlack
colorDict["standard_model"]=r.kGreen+3
colorDict["tt_tauola_mg"]=r.kOrange
colorDict["g_jets_mg"]=r.kGreen
colorDict["w_jets_mg"]=28
colorDict["z_jets_mg"]=r.kYellow-3
colorDict["z_inv_mg"]=r.kMagenta
colorDict["qcd_py"]=r.kBlue
colorDict["lm0"]=r.kRed
colorDict["lm1"]=r.kRed+1

markerStyleDict={}
markerStyleDict["JetMETTau.Run2010A"]=20

plotter.plotAll(a,colorDict,markerStyleDict)

#import statMan
#statMan.go(a.organizeHistograms(),
#           dataSampleName="JetMETTau.Run2010A",
#           mcSampleName="standard_model",
#           moneyPlotName="ak5JetPat_alphaT_vs_Ht_ge2jets",
#           xCut=0.51,yCut=330.0)
#
