#!/usr/bin/env python

import os,analysis,utils,steps,calculables

jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]

def makeSteps() :
    jets=jetTypes[0]
    
    listOfSteps=[
        steps.progressPrinter(),
        
        steps.hltFilter("HLT_Jet50U"),
        steps.leadingUnCorrJetPtSelector([jets],100.0),
        steps.techBitFilter([0],True),
        steps.physicsDeclared(),
        steps.vertexRequirementFilter(),
        steps.monsterEventFilter(),
        steps.hbheNoiseFilter(),

        steps.photonSelectionHistogrammer( nametag = "raw", deltaRMax = 0.1, zLike = True, zLikeEnergy = 20 ),
        steps.jetPtSelector(jets,100.0,0),
        steps.jetPtSelector(jets,40.0,1),
        steps.minNCleanJetEventFilter(jets,2),
        steps.maxNOtherJetEventFilter(jets,0),
        steps.photonSelectionHistogrammer( nametag = "jets", deltaRMax = 0.1, zLike = True, zLikeEnergy = 20 ),
        #steps.variableGreaterFilter(300.0,"%sSumPt%s"%jets),
        #steps.variableGreaterFilter(0.55,"%sAlphaT%s"%jets),
        ]
    return listOfSteps

def makeCalculables() :
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += [ calculables.jetIndices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculables.jetSumPt(   collection = jetType)     for jetType in jetTypes ]
    listOfCalculables += [ calculables.jetSumP4(   collection = jetType)     for jetType in jetTypes ]
    listOfCalculables += [ calculables.deltaPseudoJet( collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculables.alphaT(         collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculables.diJetAlpha(     collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculables.genIndices( label = "Photon", pdgs = [22], ptMin = 30, etaMax = 5),
                           calculables.photonIndicesPat( ptMin = 30, etaMax = 5, flagName = "photonIDLoosePat") ]
    return listOfCalculables

a = analysis.analysis( name = "photonSelection",
                       outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                       listOfSteps = makeSteps(),
                       listOfCalculables = makeCalculables()
                       )

# a.addSample( sampleName="JetMETTau.Run2010A", nMaxFiles = -1, nEvents = -1, lumi = 0.012+0.120+0.1235,#/pb
#              listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data/") )

# a.addSample( sampleName="qcd_py_pt30", nMaxFiles = 20, nEvents = -1, xs = 6.041e+07,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/") )

# a.addSample( sampleName="qcd_py_pt80", nMaxFiles = 6, nEvents = -1, xs = 9.238e+05,#pb
#              listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//bICF/automated/2010_07_06_00_55_17/") )

# a.addSample( sampleName="qcd_py_pt170", nMaxFiles = 1, nEvents = -1, xs = 2.547e+04,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_01_33_23/") )
# a.manageNonBinnedSamples(ptHatLowerThresholdsAndSampleNames=[(30,"qcd_py_pt30"),(80,"qcd_py_pt80"),(170,"qcd_py_pt170")],mergeIntoOneHistogramCalled="qcd_py")

# a.addSample( sampleName="tt_tauola_mg", nMaxFiles = 6, nEvents = -1, xs = 95.0,#pb
#              listOfFileNames = utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n") )

# a.addSample( sampleName="gammajets_mg_pt40_100", nMaxFiles = 1, nEvents = -1, xs = 23620,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb//ICF/automated/2010_07_26_15_14_40//PhotonJets_Pt40to100-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

a.addSample( sampleName="gammajets_mg_pt100_200", nMaxFiles = -1, nEvents = -1, xs = 3476,#pb
             listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt100to200-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="gammajets_mg_pt200", nMaxFiles = 1, nEvents = -1, xs = 485,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt200toInf-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))
# a.mergeHistogramsWhenPlotting(source=["gammajets_mg_pt40_100","gammajets_mg_pt100_200","gammajets_mg_pt200"],target="g_jets_mg")

# a.addSample( sampleName="z_inv_mg", nMaxFiles = 6, nEvents = -1, xs=4500.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/zph04/ICF/automated/2010_07_14_11_52_58/",
#                                                        itemsToSkip=["14_3.root"]))

# a.addSample( sampleName="z_jets_mg", nMaxFiles = 6, nEvents = -1, xs=2400.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_07_05_22_43_20/", pruneList=False) )

# a.addSample( sampleName="w_jets_mg", nMaxFiles = 6, nEvents = -1, xs=24170.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_06_18_22_33_23/") )

# a.addSample( sampleName="lm0", nMaxFiles = 1, nEvents = -1, xs = 38.93,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="lm1", nMaxFiles = 1, nEvents = -1, xs = 4.888,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/") )

a.loop( nCores = 8)
#a.plot( mergeAllStandardModelMc=False )
