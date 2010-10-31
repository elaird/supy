#!/usr/bin/env python

import os,copy
import analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

lowPtThreshold = 30.0
lowPtName = "lowPt"

class photonLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets"]
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,    ]))
        #objects["pfAK5"]   = dict(zip(fields, [("ak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,     ]))

        thresholds = {}
        fields =                                 ["jetPtMin","jet1PtMin","jet2PtMin", "ht","mhtJustBeforeAlphaT","applyAlphaTCut","applyTrigger","photonPt","genPhotonPtMin"] 
        thresholds["signal"]  = dict(zip(fields, [   50.0,       100.0,    100.0,    350.0,       140.0,                     True,          True,   100.0,         110.0    ]))
       #thresholds["relaxed"] = dict(zip(fields, [   36.0,        72.0,     72.0,    250.0,       100.0,                     True,          True,    80.0,          90.0    ]))
       #thresholds["markus"]  = dict(zip(fields, [   30.0,        30.0,     None,     None,       140.0,                    False,         False,    80.0,          90.0    ]))

        return { "objects": objects,
                 "thresholds": thresholds,
                #"nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 "photonId" :         dict([ ("photonLoose","photonIDLooseFromTwikiPat"),             #0
                                             ("photonTight","photonIDTightFromTwikiPat"),             #1

                                             ("photonTrkIsoRelaxed","photonIDTrkIsoRelaxedPat"),      #2
                                             ("photonTrkIsoSideband","photonIDTrkIsoSideBandPat"),    #3

                                             ("photonIsoSideband","photonIDIsoSideBandPat"),          #4
                                             ("photonIsoRelaxed","photonIDIsoRelaxedPat"),            #5
                                             
                                             ("photonEGM-10-006-Loose","photonIDEGM_10_006_LoosePat"),#6
                                             ("photonEGM-10-006-Tight","photonIDEGM_10_006_TightPat"),#7

                                             ("photonAN-10-268",   "photonIDAnalysisNote_10_268Pat")]  [7:8] ),
                 "zMode" :            dict([ ("zMode",True), ("",False) ]                              [:] ),
                 "skimString" : ["","_phskim","_markusSkim"] [1],
                 "jetId" :  ["JetIDloose","JetIDtight"]      [0],
                 "etRatherThanPt" : [True,False]             [0],
                 }

    def listOfCalculables(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _electron = params["objects"]["electron"]
        _photon = params["objects"]["photon"]
        _etRatherThanPt = params["etRatherThanPt"]
        _met = params["objects"]["met"]
        _correctForMuons = not params["objects"]["muonsInJets"]

        _jetPtMin = params["thresholds"]["jetPtMin"]

        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ calculables.xcJet( _jet,
                                    gamma = _photon,
                                    gammaDR = 0.5,
                                    muon = _muon,
                                    muonDR = 0.5,
                                    correctForMuons = _correctForMuons,
                                    electron = _electron, electronDR = 0.5
                                    ),
                 calculables.jetIndices( _jet, _jetPtMin,      etaMax = 3.0, flagName = params["jetId"]),
                 #calculables.jetIndices( _jet, lowPtThreshold, etaMax = 3.0, flagName = params["jetId"], extraName = lowPtName),
                 calculables.muonIndices( _muon, ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = 20, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = 25, flagName = params["photonId"]),

                 calculables.genIndices( pdgs = [22], label = "Status3Photon", status = [3]),
                 calculables.genMinDeltaRPhotonOther( label = "Status3Photon"),

                 calculables.genIndices( pdgs = [22], label = "Status1Photon", status = [1]),
                 calculables.genIsolations(label = "Status1Photon", coneSize = 0.4),
                 calculables.genPhotonCategory(label = "Status1Photon"),

                 calculables.minDeltaRToJet(_photon, _jet),
                 
                 #calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 #calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.jetSumP4(_jet),
                     calculables.jetSumP4PlusPhotons(_jet, extraName = "", photon = _photon),
                     calculables.deltaPhiStar(_jet, extraName = ""),
                     calculables.deltaPhiStarIncludingPhotons(_jet, photons = _photon, extraName = ""),
                     calculables.deltaPseudoJet(_jet, _etRatherThanPt),
                     calculables.alphaTWithPhoton1PtRatherThanMht(_jet, photons = _photon, etRatherThanPt = _etRatherThanPt),
                     calculables.alphaT(_jet, _etRatherThanPt),
                     calculables.alphaTMet(_jet, _etRatherThanPt, _met),
                     calculables.metPlusPhoton(met = "metP4PF", photons = _photon, photonIndex = 0),
                     calculables.mhtMinusMetOverMeff(_jet, "metPlusPhoton", _etRatherThanPt),
                     calculables.mhtIncludingPhotonsOverMet(_jet, "metP4PF", _etRatherThanPt),
                     calculables.vertexID(),
                     calculables.vertexIndices(),
                     ]

    def listOfSteps(self,params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]

        outList=[
            steps.progressPrinter(),
            steps.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.jetEtaSelector(_jet, 2.5, 0),
            ]

        if params["thresholds"]["jet1PtMin"]!=None : outList+=[steps.jetPtSelector(_jet, params["thresholds"]["jet1PtMin"], 0)]
        if params["thresholds"]["jet2PtMin"]!=None : outList+=[steps.jetPtSelector(_jet, params["thresholds"]["jet2PtMin"], 1)]
        if params["thresholds"]["applyTrigger"]    : outList+=[steps.lowestUnPrescaledTrigger(["HLT_HT100U","HLT_HT120U","HLT_HT140U","HLT_HT150U"])]

        outList+=[
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            #steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),
            ]

        if params["thresholds"]["ht"]!=None : outList+=[steps.variableGreaterFilter(params["thresholds"]["ht"],"%sSumEt%s"%_jet, suffix = "GeV")]

        outList+=[
            #bad jet, electron, muon, vetoes
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            #steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            ]
        if not params["zMode"] :
            outList+=[
                steps.passFilter("photonEfficiencyPlots1"),
                steps.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"], etaCut = 1.4, isoCut = 5.0, jets = _jet, photons = _photon),
                
                steps.photonPtSelector(_photon, params["thresholds"]["photonPt"], 0),
                steps.photonEtaSelector(_photon, 1.45, 0),
                steps.multiplicityFilter("%sIndices%s"%_photon, nMin = 1, nMax = 1),

                steps.passFilter("photonEfficiencyPlots2"),
                steps.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"], etaCut = 1.4, isoCut = 5.0, jets = _jet, photons = _photon),
                ]
        else :
            outList+=[
                steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),                
                ]

        outList+=[
            #many plots
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.passFilter("singlePhotonPlots1"),
            steps.singlePhotonHistogrammer(_photon, _jet),
            #steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            #steps.vertexHistogrammer(),
            steps.passFilter("purityPlots1"),
            steps.photonPurityPlots("Status1Photon", _jet, _photon),
            
            steps.passFilter("jetSumPlots"),
            steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.histogrammer("metP4PF",100,0.0,500.0,title=";metP4PF (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.passFilter("kinematicPlots"),
            steps.alphaHistogrammer(_jet, deltaPhiStarExtraName = "", etRatherThanPt = _etRatherThanPt),
            steps.histogrammer("%sAlphaTWithPhoton1PtRatherThanMht%s"%_jet, 4, 0.0, 4*0.55, title = ";#alpha_{T} using photon p_{T} rather than MHT;events / bin"),
            steps.histogrammer(("%sAlphaT%s"%_jet, "%sAlphaTWithPhoton1PtRatherThanMht%s"%_jet),
                               (25, 25), (0.50, 0.50), (1.0, 1.0), title = ";#alpha_{T};#alpha_{T} using photon p_{T} rather than MHT;events / bin"),
            
            steps.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),
            
            steps.variablePtGreaterFilter(params["thresholds"]["mhtJustBeforeAlphaT"],"%sSumP4%s"%_jet,"GeV"),
            steps.histogrammer("%sAlphaT%s"%_jet, 4, 0.0, 0.55*4, title=";#alpha_{T};events / bin"),
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            ]
        if params["thresholds"]["applyAlphaTCut"] :
            outList+=[
                steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            ]
        outList+=[
            steps.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),            
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.passFilter("singlePhotonPlots2"),
            steps.singlePhotonHistogrammer(_photon, _jet),

            steps.passFilter("purityPlots2"),
            steps.photonPurityPlots("Status1Photon", _jet, _photon),
            
            #steps.histogrammer("mhtMinusMetOverMeff", 100, -1.0, 1.0, title = ";(MHT - [PFMET+photon])/(MHT+HT);events / bin"),
            steps.histogrammer("mhtIncludingPhotonsOverMet", 100, 0.0, 2.0, title = ";MHT [including photon] / PFMET;events / bin"),
            #steps.variableLessFilter(0.15,"mhtMinusMetOverMeff"),
            steps.deadEcalFilterIncludingPhotons(jets = _jet, extraName = "", photons = _photon, dR = 0.3, dPhiStarCut = 0.5, nXtalThreshold = 5),
            
            #steps.genMotherHistogrammer("genIndicesPhoton", specialPtThreshold = 100.0),
            
            #steps.skimmer(),
            #steps.eventPrinter(),
            #steps.vertexPrinter(),
            #steps.jetPrinter(_jet),
            #steps.htMhtPrinter(_jet),
            #steps.particleP4Printer(_photon),
            #steps.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.genParticlePrinter(minPt = 10.0, minStatus = 3),
            #steps.genParticlePrinter(minPt = -1.0, minStatus = 3),
            #steps.genParticlePrinter(minPt=-10.0,minStatus=1),
            #
            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 400.0,#GeV
            #                etRatherThanPt = _etRatherThanPt,
            #                #doGenParticles = True,
            #                #deltaPhiStarExtraName = lowPtName,
            #                #deltaPhiStarExtraName = "%s%s"%("","PlusPhotons"),                            
            #                ),
            
            ]

        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.photon]

    def listOfSamples(self,params) :
        from samples import specify

        #horrible hack
        self.skimStringHack = params["skimString"]
        
        data = {}
        data[""] = [
            specify(name = "Run2010B_MJ_skim2",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_MJ_skim",          nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_J_skim2",          nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_J_skim",           nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JM_skim",          nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JMT_skim",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "2010_data_skim_calo",       nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "2010_data_skim_pf",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "test",                      nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "2010_data_photons_high_met",nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            ]
        data["_phskim"] = [
            specify(name = "Run2010B_MJ_skim2_phskim",                  color = r.kBlack),
            specify(name = "Run2010B_MJ_skim_phskim",                   color = r.kBlack),
            specify(name = "Run2010B_J_skim2_phskim",                   color = r.kBlack),
            specify(name = "Run2010B_J_skim_phskim",                    color = r.kBlack),
            specify(name = "Run2010A_JM_skim_phskim",                   color = r.kBlack),
            specify(name = "Run2010A_JMT_skim_phskim",                  color = r.kBlack),
            ]
        data["_markusSkim"] = [
            specify(name = "Ph.Data_markusSkim",        nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            ]

        qcd_py6 = {}
        qcd_py6[""] = [                                                 
          ##specify(name = "v12_qcd_py6_pt30",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt170",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt300",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt470",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt800",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt1400",        nFilesMax = -1, color = r.kBlue    ),
            ]
        qcd_py6["_phskim"] = [
            specify(name = "v12_qcd_py6_pt80_phskim", color = r.kBlue),
            specify(name = "v12_qcd_py6_pt170_phskim",color = r.kBlue),
            specify(name = "v12_qcd_py6_pt300_phskim",color = r.kBlue),
            ]

        g_jets_py6 = {}
        g_jets_py6[""] = [                                              
            specify(name = "v12_g_jets_py6_pt30",       nFilesMax = -1, nEventsMax = 1000000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt80",       nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt170",      nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            ]
        g_jets_py6["_phskim"] = [
            specify(name = "v12_g_jets_py6_pt80_phskim",  color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt170_phskim", color = r.kGreen),
            ]

        qcd_mg = {}
        qcd_mg[""] = [                                                  
            specify(name = "v12_qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
            ]
        qcd_mg["_phskim"] = [
           #specify(name = "v12_qcd_mg_ht_50_100_phskim",    color = r.kBlue) ,
           #specify(name = "v12_qcd_mg_ht_100_250_phskim",   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_250_500_phskim",   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_500_1000_phskim",  color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_1000_inf_phskim",  color = r.kBlue) ,
            ]
        qcd_mg["_markusSkim"] = [
           #specify(name = "v12_qcd_mg_ht_50_100_markusSkim",    color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_100_250_markusSkim",   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_250_500_markusSkim",   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_500_1000_markusSkim",  color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_1000_inf_markusSkim",  color = r.kBlue) ,
            ]

        g_jets_mg = {}
        g_jets_mg[""] = [                                               
            specify(name = "v12_g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
            ]
        g_jets_mg["_phskim"] = [
            #specify(name = "v12_g_jets_mg_pt40_100_phskim",  color = r.kGreen),
            #specify(name = "v12_g_jets_mg_pt100_200_phskim", color = r.kGreen),
            specify(name = "v12_g_jets_mg_pt200_phskim",     color = r.kGreen),
            ]
        g_jets_mg["_markusSkim"] = [
            specify(name = "v12_g_jets_mg_pt40_100_markusSkim",  color = r.kGreen),
            specify(name = "v12_g_jets_mg_pt100_200_markusSkim", color = r.kGreen),
            specify(name = "v12_g_jets_mg_pt200_markusSkim",     color = r.kGreen),
            ]

        ttbar_mg = {}
        ttbar_mg[""] = [                                                
            specify(name = "tt_tauola_mg_v12",          nFilesMax =  3, color = r.kOrange  ),
            ]
        ttbar_mg["_phskim"] = [
            specify(name = "tt_tauola_mg_v12_phskim",   nFilesMax = -1, color = r.kOrange  ),
            ]

        ewk_mg = {}
        ewk_mg[""] = [                                                     
            #specify(name = "z_inv_mg_v12",              nFilesMax = -1, color = r.kMagenta ),
            specify(name = "z_jets_mg_v12",             nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12",             nFilesMax = -1, color = 28         ),
            ]
        ewk_mg["_phskim"] = [
            specify(name = "z_jets_mg_v12_phskim",      nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12_phskim",      nFilesMax = -1, color = 28         ),
            ]

        zinv_mg = {}
        for item in ["","_phskim"] :
            zinv_mg[item] = [specify(name = "z_inv_mg_v12_skim", nFilesMax = -1, color = r.kMagenta )]

        outList = []

        if not params["zMode"] :
            #outList+=qcd_py6[params["skimString"]]
            #outList+=g_jets_py6[params["skimString"]]
        
            outList += qcd_mg    [params["skimString"]]
            outList += g_jets_mg [params["skimString"]]
            
            outList += data      [params["skimString"]]
            outList += ewk_mg    [params["skimString"]]
            outList += ttbar_mg  [params["skimString"]]
        else :
            outList += zinv_mg   [params["skimString"]]
            
        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    #if "2010" in o.name: continue
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 1000)
        
        return outList

    def mergeSamples(self, org, tag) :
        def py6(org, smSources, skimString) :
            org.mergeSamples(targetSpec = {"name":"qcd_py6_v12", "color":r.kBlue},
                             sources = ["v12_qcd_py6_pt%d%s"%(i,skimString) for i in [80,170,300] ])
            smSources.append("qcd_py6_v12")

            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen},
                             sources = ["v12_g_jets_py6_pt%d%s"%(i,skimString) for i in [30,80,170] ])
            smSources.append("g_jets_py6_v12")

        def py8(org, smSources, skimString) :
            lowerPtList = [0,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            sources = ["qcd_py8_pt%dto%d"%(lowerPtList[i],lowerPtList[i+1]) for i in range(len(lowerPtList)-1)]
            sources.append("qcd_py8_pt%d"%lowerPtList[-1])
            org.mergeSamples(targetSpec = {"name":"qcd_py8", "color":r.kBlue}, sources = sources)
            smSources.append("qcd_py8")

            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen},
                             sources = ["v12_g_jets_py6_pt%d"%i      for i in [30,80,170] ])
            smSources.append("g_jets_py6_v12")

        def mg(org, smSources, skimString) :
            org.mergeSamples(targetSpec = {"name":"qcd_mg_v12", "color":r.kBlue},
                             sources = ["v12_qcd_mg_ht_%s%s"%(bin,skimString) for bin in ["50_100","100_250","250_500","500_1000","1000_inf"] ])
            smSources.append("qcd_mg_v12")
            
            org.mergeSamples(targetSpec = {"name":"g_jets_mg_v12", "color":r.kGreen},
                             sources = ["v12_g_jets_mg_pt%s%s"%(bin,skimString) for bin in ["40_100","100_200","200"] ])
            smSources.append("g_jets_mg_v12")

        smSources = [item+self.skimStringHack for item in ["z_inv_mg_v12", "z_jets_mg_v12", "w_jets_mg_v12"]]
        #if "pythia6"  in tag : py6(org, smSources, skimString)
        #if "pythia8"  in tag : py8(org, smSources, skimString)
        #if "madgraph" in tag : mg (org, smSources, skimString)
        #py6(org, smSources, skimString)
        #py8(org, smSources, skimString)
        mg (org, smSources, self.skimStringHack)

        #org.mergeSamples(targetSpec = {"name":"MG QCD+G", "color":r.kGreen}, sources = ["qcd_mg_v12","g_jets_mg_v12"])
        #org.mergeSamples(targetSpec = {"name":"PY6 QCD+G", "color":r.kBlue}, sources = ["qcd_py6_v12","g_jets_py6_v12"])
        org.mergeSamples(targetSpec = {"name":"MG TT+EWK", "color":r.kOrange}, sources = [item+self.skimStringHack for item in ["z_jets_mg_v12", "w_jets_mg_v12", "tt_tauola_mg_v12"]])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)

        if self.skimStringHack=="_markusSkim" :
            org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, sources = ["Ph.Data_markusSkim"])
        else :
            org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20},
                             sources = [item+self.skimStringHack for item in ["Run2010B_MJ_skim","Run2010B_MJ_skim2","Run2010B_J_skim",
                                                                              "Run2010B_J_skim2","Run2010A_JM_skim","Run2010A_JMT_skim"]])
            
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            ##for skimming only
            #org = organizer.organizer( self.sampleSpecs(tag) )
            #utils.printSkimResults(org)            

            #organize
            org = organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            if "zMode" in tag :
                org.scale(1.0)
            else :
                org.scale()

            #self.makeStandardPlots(org, tag)
            self.makeIndividualPlots(org, tag)
            #self.makePurityPlots(org, tag)
            #self.makeEfficiencyPlots(org, tag)
        #self.makeMultiModePlots()

    def makeStandardPlots(self, org, tag) :
        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(tag),
                             #samplesForRatios = ("2010 Data","standard_model"),
                             #sampleLabelsForRatios = ("data","s.m."),
                             #samplesForRatios = ("2010 Data","MG QCD+G"),
                             #sampleLabelsForRatios = ("data","MG"),
                             blackList = ["lumiHisto","xsHisto","nJobsHisto",
                                          "deltaRGenReco",
                                          "photonMothergenPt", "photonMotherrecoPt", "photonMothermht",
                                          "quarkMothergenPt",  "quarkMotherrecoPt",  "quarkMothermht",
                                          "otherMothergenPt",  "otherMotherrecoPt",  "otherMothermht",
                                          "nGenPhotonsStatus1Photon","photonEtaStatus1Photon","photonPtStatus1Photon",
                                          "photonPhiVsEtaStatus1Photon", "photonIsoStatus1Photon",
                                          "nJetsStatus1Photon", "jetHtStatus1Photon",
                                          "nJetsPlusnPhotonsStatus1Photon", "jetHtPlusPhotonHtStatus1Photon",
                                          ],
                             #whiteList = ["xcak5JetIndicesPat",
                             #             #"photonPat1Pt",
                             #             #"photonPat1mhtVsPhotonPt",
                             #             "xcak5JetAlphaTFewBinsPat",
                             #             "xcak5JetAlphaTRoughPat",
                             #             "xcak5JetAlphaTWithPhoton1PtRatherThanMhtPat",
                             #             ],
                             )
        pl.plotAll()
            
    def makeIndividualPlots(self, org, tag) :
        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(tag),
                             showStatBox = False,
                             doLog = False,
                             anMode = True,
                             )
        pl.individualPlots([("xcak5JetAlphaTPat",  "variablePtGreaterFilter", "xcak5JetSumP4Pat.pt()>=140.0 GeV"),
                            ("xcak5JetIndicesPat", "variablePtGreaterFilter", "xcak5JetSumP4Pat.pt()>=140.0 GeV"),
                            ])

            
    def makeEfficiencyPlots(self, org, tag) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        def numerAndDenom(org, var) :
            d = {}
            for selection in org.selections :
                if selection.name != "passFilter" : continue
                if   "photonEfficiencyPlots1" in selection.title : label = "denom"
                elif "photonEfficiencyPlots2" in selection.title : label = "numer"
                else : continue
                key = var+"Status1Photon"
                if key in selection :
                    d[label] = selection[key][sampleIndex(org,"g_jets_mg_v12")].Clone(label)
                
            return d

        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)
        canvas.SetTickx()
        canvas.SetTicky()
        psFileName = "%s.ps"%tag
        canvas.Print(psFileName+"[","Lanscape")
        for variable in ["photonPt","photonEta","photonIso",
                         "nJets","jetHt","nJetsPlusnPhotons","jetHtPlusPhotonHt","getMinDeltaRPhotonOtherStatus3Photon"] :
            histos = numerAndDenom(org, variable)
            if "numer" not in histos or "denom" not in histos : continue
            result = histos["numer"].Clone(variable)
            result.Reset()
            result.Divide(histos["numer"], histos["denom"], 1.0, 1.0, "b")
            result.SetMarkerStyle(20)
            result.SetStats(False)
            if result.ClassName()[2]=="1" :
                result.GetYaxis().SetRangeUser(0.0,1.0)
                result.GetYaxis().SetTitle("efficiency")
                result.Draw()
            else :
                result.GetZaxis().SetRangeUser(0.0,1.0)
                result.GetZaxis().SetTitle("efficiency")
                result.Draw("colz")
            canvas.Print(psFileName,"Lanscape")

        canvas.Print(psFileName+"]","Lanscape")                
        os.system("ps2pdf "+psFileName)
        os.remove(psFileName)

    def makePurityPlots(self, org, tag) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        for selection in org.selections :
            if selection.name != "passFilter" : continue
            if "purityPlots3" not in selection.title : continue

            variables = ["genPt"]
            #variables = ["genPt","recoPt","mht"]
            for variable in variables :
                sum = None
                categories = ["photonMother","quarkMother","otherMother"]
                colors = {"photonMother":r.kBlack, "quarkMother":r.kBlue, "otherMother":r.kMagenta}
                labels = {"photonMother":"mother is photon", "quarkMother":"mother is quark", "otherMother":"mother is other"}
                histos = {}
                reBinFactor = 10
                for category in categories :
                    histoOrig = selection[category+variable][sampleIndex(org,"standard_model")]
                    histos[category] = histoOrig.Clone(histoOrig.GetName()+"clone")
                    histos[category].Rebin(reBinFactor)
                    if sum==None :
                        sum = histos[category].Clone()
                    else :
                        sum.Add(histos[category])

                canvas = r.TCanvas()
                canvas.SetRightMargin(0.2)
                null = histos[categories[0]].Clone()
                null.Reset()
                null.SetStats(False)
                null.GetYaxis().SetTitle("fraction of events")
                null.Draw()
                keep = []
                e = 0.02
                legend = r.TLegend(0.80+e, 0.60-e, 0.95+e, 0.90-e)
                for category in categories :
                    result = histos[category].Clone("result"+category)
                    result.Reset()
                    result.Divide(histos[category], sum, 1.0, 1.0, "b")
                    result.SetLineColor(colors[category])
                    result.SetMarkerColor(colors[category])
                    result.SetMarkerStyle(20)
                    result.Draw("same")
                    legend.AddEntry(result,labels[category],"p")
                    keep.append(result)

                legend.Draw()
                eps = "%s_%s_%s.eps"%(tag,variable,selection.title)
                pdf = eps.replace(".eps",".pdf")
                canvas.Print(eps)
                os.system("epstopdf "+eps)
                os.remove(eps)

    def makeMultiModePlots(self) :
        def org(tag) :
            org = organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            if "zMode" in tag : org.scale(1.0)
            else :              org.scale()
            return org

        def fetchPlots(someOrg, plotName) :
            outList = []
            for selection in someOrg.selections :
                if selection.name != plotName[1] : continue
                if plotName[2] not in selection.title : continue
                if plotName[0] not in selection : continue

                histos = selection[plotName[0]]
                for sample,histo in zip(someOrg.samples, histos) :
                    if "color" in sample :
                        histo.SetLineColor(sample["color"])
                        histo.SetMarkerColor(sample["color"])
                    if "markerStyle" in sample :
                        histo.SetMarkerStyle(sample["markerStyle"])
                    outList.append( (sample["name"], histo) )
            return copy.deepcopy(outList)

        def histoDict(plotName, samples) :
            l = []
            for tag in self.sideBySideAnalysisTags() :
                l += fetchPlots(org(tag), plotName)

            d = {}
            names = [item[0] for item in l]
            for item in l :
                name = item[0]
                assert names.count(name)==1, "found %d instances of sample %s"%(names.count(name),name)
                if name in samples :
                    d[name] = item[1]
            return d

        plotName = ("xcak5JetAlphaTPat", "variablePtGreaterFilter", "xcak5JetSumP4Pat.pt()>=140.0 GeV")
        samples = ["z_inv_mg_v12_skim", "g_jets_mg_v12", "2010 Data"]
        styles  = [28,                   29,             20]
        d = histoDict(plotName, samples)

        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        
        first = True
        for iSample,sample in enumerate(samples) :
            histo = d[sample]
            histo.SetMarkerStyle(styles[iSample])
            histo.SetStats(False)
            histo.Scale( 1.0/histo.Integral(0,histo.GetNbinsX()+1) )
            if first :
                histo.Draw()
                histo.GetYaxis().SetRangeUser(0.0,1.0)
                histo.GetYaxis().SetTitle("fraction of events / bin")
            else :
                histo.Draw("same")
            first = False

        eps = "alphaTCompare.eps"
        canvas.Print(eps)
        os.system("epstopdf "+eps)
        os.remove(eps)
