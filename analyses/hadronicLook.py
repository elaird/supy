#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

def makeSteps() :
    jetCollection="ak5Jet"
    #jetCollection="ak5JetJPT"
    #jetCollection="ak5JetPF"
    jetSuffix="Pat"
    
    metCollection="met"
    metSuffix="Calo"
    metSuffix=jetCollection[:3].upper()
    metSuffix+="TypeII"
    #metSuffix="PF"
    
    leptonSuffix="Pat"
    #leptonSuffix="PF"
    
    nCleanJets=2
    
    listOfSteps=[
        steps.progressPrinter(2,300),
        
        steps.ptHatHistogrammer(),
        steps.jetPtSelector(jetCollection,jetSuffix,80.0,0),
        #steps.jetPtSelector(jetCollection,jetSuffix,40.0,1),            
        steps.leadingUnCorrJetPtSelector( [(jetCollection,jetSuffix)],80.0 ),
        steps.hltFilter("HLT_Jet50U"),            
        steps.hltPrescaleHistogrammer(["HLT_ZeroBias","HLT_Jet15U","HLT_Jet30U","HLT_Jet50U","HLT_MET45"]),
        
        steps.nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
        steps.nOtherJetEventFilter(jetCollection,jetSuffix,1),
        steps.cleanJetPtHistogrammer(jetCollection,jetSuffix),
        steps.hbheNoiseFilter(),
        steps.cleanJetHtMhtProducer(jetCollection,jetSuffix),
        steps.cleanJetHtMhtHistogrammer(jetCollection,jetSuffix),
        #steps.crockVariablePtGreaterFilter(100.0,jetCollection+"Mht"+jetSuffix),
        
        steps.variableGreaterFilter(300.0,jetCollection+"SumPt"+jetSuffix),
        steps.cleanDiJetAlphaProducer(jetCollection,jetSuffix),
        steps.cleanNJetAlphaProducer(jetCollection,jetSuffix),
        steps.alphaHistogrammer(jetCollection,jetSuffix),
        
        steps.crockVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
        steps.displayer(jetCollection,jetSuffix,metCollection,metSuffix,leptonSuffix,genJetCollection="ak5Jet",outputDir="/vols/cms02/%s/tmp/"%os.environ["USER"],scale=200.0),
        steps.eventPrinter(),
        steps.jetPrinter(jetCollection,jetSuffix),
        steps.htMhtPrinter(jetCollection,jetSuffix),
        steps.nJetAlphaTPrinter(jetCollection,jetSuffix),
        ]
    return listOfSteps

def makeCalculables() :
    jettypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += [ calculablesJet.indices( collection = col, suffix = "Pat", ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for col in jettypes]
    listOfCalculables += [ calculablesJet.sumPt( collection = col, suffix = "Pat")                                                        for col in jettypes]

    return listOfCalculables

#def dummy(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
#    return []
#utils.fileListFromSrmLs=dummy

a=analysis.analysis(name="hadronicLook",
                    outputDir="/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables()
                    )

a.addSample(sampleName="JetMETTau.Run2010A",
                listOfFileNames=utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/take2/JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",pruneList=False,nMaxFiles=-1),
                nEvents=-1,
                lumi=0.120,#/pb
                )

a.addSample(sampleName="qcd_py_pt30",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/",
                                                        nMaxFiles=1),
                nEvents=-1,
                xs=6.041e+07#pb
                )

a.addSample(sampleName="qcd_py_pt80",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_00_55_17/",
                                                        nMaxFiles=1),
                nEvents=-1,
                xs=9.238e+05#pb
                )

a.addSample(sampleName="qcd_py_pt170",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_01_33_23/",
                                                        nMaxFiles=1),
                nEvents=-1,
                xs=2.547e+04#pb
                )

a.manageNonBinnedSamples(ptHatLowerThresholdsAndSampleNames=[(30,"qcd_py_pt30"),(80,"qcd_py_pt80"),(170,"qcd_py_pt170")])#,mergeIntoOnePlot=True,mergeName="qcd_py")

a.addSample(sampleName="tt_tauola_mg",
                listOfFileNames=utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n")[:1],
                nEvents=-1,
                xs=95.0#pb
                )

a.addSample(sampleName="z_inv_mg",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/zph04/ICF/automated/2010_07_14_11_52_58/",
                                                        itemsToSkip=["14_3.root"],
                                                        nMaxFiles=-1),
                nEvents=-1,
                xs=4500.0#pb
                )

a.addSample(sampleName="z_jets_mg",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_07_05_22_43_20/",
                                                        nMaxFiles=1),
                nEvents=100,
                xs=2400.0#pb
                )

a.addSample(sampleName="w_jets_mg",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_06_18_22_33_23/",
                                                        nMaxFiles=-1),
                nEvents=-1,
                xs=24170.0#pb
                )

a.addSample(sampleName="lm0",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
                                                        nMaxFiles=1),
                nEvents=-1,
                xs=38.93#pb
                )

a.addSample(sampleName="lm1",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
                                                        nMaxFiles=1),
                nEvents=-1,
                xs=4.888#pb
                )

a.loop( nCores = 1,
        splitJobsByInputFile = False
        )

a.plot()
