#!/usr/bin/env python

import os,copy
from core import analysis,plotter,utils,organizer
import steps,calculables,samples
import ROOT as r

class photonLook(analysis.analysis) :
    def parameters(self) :
        objects = self.vary()
        fields =                                             [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets"]
        objects["caloAK5Jet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,    ]))
        #objects["pfAK5Jet_recoLepPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","Pat"),("electron","Pat"),("photon","Pat"),  "PF"  ,    True ,    ]))
        #objects["pfAK5JetLep_recoPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,    ]))

        return { "objects": objects,
                 "nJetsMinMax" :      self.vary(dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] )),
                 "photonId" :         self.vary(dict([ ("photonIsoRelaxed","photonIDIsoRelaxedPat"),            #0

                                                       ("photonLoose","photonIDLooseFromTwikiPat"),             #1
                                                       ("photonTight","photonIDTightFromTwikiPat"),             #2
                                                       
                                                       ("photonEGM-10-006-Loose","photonIDEGM_10_006_LoosePat"),#3
                                                       ("photonEGM-10-006-Tight","photonIDEGM_10_006_TightPat"),#4
                                                       
                                                       ("photonTrkIsoRelaxed","photonIDTrkIsoRelaxedPat"),      #5
                                                       ("photonTrkIsoSideband","photonIDTrkIsoSideBandPat"),    #6
                                                       ("photonIsoSideband","photonIDIsoSideBandPat"),          #7
                                                       ("photonNoIsoReq","photonIDNoIsoReqPat"),                #8
                                                       ("photonAN-10-268",   "photonIDAnalysisNote_10_268Pat")]  [2:3] )),
                 "zMode" :            self.vary(dict([ ("Z",True), ("g",False) ]                                  [:]  )),
                 "vertexMode" :       self.vary(dict([ ("vertexMode",True), ("",False) ]                         [1:2] )),
                 "subdet" :           self.vary(dict([ ("barrel", (0.0, 1.444)), ("endcap", (1.566, 2.5)) ]      [:1 ] )),
                 "jetId" :  ["JetIDloose","JetIDtight"]            [0],
                 "etRatherThanPt" : [True,False]                   [0],
                 "lowPtThreshold": 30.0,
                 "lowPtName":"lowPt",
                 "highPtThreshold" : 50.0,
                 "highPtName" : "highPt",
                 "thresholds": self.vary(dict( [("275",        (275.0, 325.0, 100.0, 50.0)),#0
                                                ("325",        (325.0, 375.0, 100.0, 50.0)),#1
                                                ("375",        (375.0, None,  100.0, 50.0)),#2
                                                ("275_scaled", (275.0, 325.0,  73.3, 36.7)),#3
                                                ("325_scaled", (325.0, 375.0,  86.7, 43.3)),#4
                                                ][2:3] )),
                 #required to be sorted
                 #"triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"), #2010
                 "triggerList": tuple(["HLT_Photon75_CaloIdVL_v%d"%i for i in range(1,8)]+
                                      ["HLT_Photon75_CaloIdVL_IsoL_v%d"%i for i in range(1,11)]+
                                      ["HLT_Photon90_CaloIdVL_v%d"%i for i in range(1,5)]+
                                      ["HLT_Photon90_CaloIdVL_IsoL_v%d"%i for i in range(1,8)]+
                                      ["HLT_Photon125_v%d"%i for i in range(1,3)]+
                                      ["HLT_Photon135_v%d"%i for i in range(1,3)]
                                      ),#2011
                 }

    def listOfCalculables(self, params) :
        if params["vertexMode"] :
            assert params["photonId"] in ["photonIDTightFromTwikiPat"],"In vertexMode but requested %s"%params["photonId"]

        obj = params["objects"]
        _etRatherThanPt = params["etRatherThanPt"]

        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.Jet,[obj["jet"]]) +\
               calculables.fromCollections(calculables.Muon,[obj["muon"]]) +\
               calculables.fromCollections(calculables.Electron,[obj["electron"]]) +\
               calculables.fromCollections(calculables.Photon,[obj["photon"]]) +\
               [ calculables.XClean.xcJet( obj["jet"],
                                           gamma = obj["photon"],
                                           gammaDR = 0.5,
                                           muon = obj["muon"],
                                           muonDR = 0.5,
                                           correctForMuons = not obj["muonsInJets"],
                                           electron = obj["electron"], electronDR = 0.5
                                           ),
                 calculables.Jet.Indices( obj["jet"], ptMin = params["thresholds"][3], etaMax = 3.0, flagName = params["jetId"]),
                 calculables.Jet.Indices( obj["jet"], ptMin = params["lowPtThreshold"], etaMax = 3.0, flagName = params["jetId"], extraName = params["lowPtName"]),
                 calculables.Jet.Indices( obj["jet"], ptMin = params["highPtThreshold"], etaMax = 3.0, flagName = params["jetId"], extraName = params["highPtName"]),
                 calculables.Muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
                 calculables.Photon.Indices(obj["photon"], ptMin = 25, flagName = params["photonId"]),

                 calculables.Gen.genIndices( pdgs = [22], label = "Status3Photon", status = [3]),
                 calculables.Gen.genMinDeltaRPhotonOther( label = "Status3Photon"),

                 calculables.Gen.genIndices( pdgs = [22], label = "Status1Photon", status = [1]),
                 calculables.Gen.genIsolations(label = "Status1Photon", coneSize = 0.4),
                 calculables.Gen.genPhotonCategory(label = "Status1Photon"),

                 calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
                 calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5)
                 ] \
                 + [ calculables.Jet.SumP4(obj["jet"]),
                     calculables.Jet.SumP4(obj["jet"], extraName = params["lowPtName"]),
                     calculables.Jet.SumP4(obj["jet"], extraName = params["highPtName"]),
                     calculables.Jet.DeltaPhiStar(obj["jet"], extraName = ""),
                     calculables.Jet.DeltaPhiStar(obj["jet"], extraName = params["lowPtName"]),
                     calculables.Jet.DeltaPseudoJet(obj["jet"], _etRatherThanPt),
                     calculables.Jet.AlphaTWithPhoton1PtRatherThanMht(obj["jet"], photons = obj["photon"], etRatherThanPt = _etRatherThanPt),
                     calculables.Jet.AlphaT(obj["jet"], _etRatherThanPt),
                     calculables.Jet.AlphaTMet(obj["jet"], _etRatherThanPt, obj["met"]),
                     calculables.Jet.MhtOverMet((obj["jet"][0], obj["jet"][1]+params["highPtName"]), met = obj["met"]),
                     calculables.Jet.MhtOverMet((obj["jet"][0], obj["jet"][1]+params["highPtName"]), met = "%sPlus%s%s"%(obj["met"], obj["photon"][0], obj["photon"][1])),
                     calculables.Other.metPlusParticles(met = obj["met"], particles = obj["photon"]),
                     calculables.Other.minDeltaRToJet(obj["photon"], obj["jet"]),
                     calculables.Other.SumP4(obj["photon"]),
                     calculables.Vertex.ID(),
                     calculables.Vertex.Indices(),
                     calculables.Jet.deadEcalDR(obj["jet"], extraName = params["lowPtName"], minNXtals = 10),
                     calculables.Other.lowestUnPrescaledTrigger(params["triggerList"]),
                     ]

    def listOfSteps(self,params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]
        _et = "Et" if _etRatherThanPt else "Pt"
        
        htUpper = [steps.Other.variableLessFilter(params["thresholds"][1],"%sSum%s%s"%(_jet[0], _et, _jet[1]), "GeV")] if params["thresholds"][1]!=None else []
        
        #event and trigger
        outList = [
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat", 200, 0, 1000, title = ";#hat{p_{T}} (GeV);events / bin"),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.Trigger.physicsDeclaredFilter(),
            steps.Other.monsterEventFilter(),
            steps.Other.hbheNoiseFilter(),
            steps.Trigger.hltPrescaleHistogrammer(params["triggerList"]),            
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            steps.Trigger.lowestUnPrescaledTriggerFilter(),
            ]

        if params["vertexMode"] :
            outList += [
                steps.Photon.photonPtSelector(_photon, 100.0, 0),
                steps.Photon.photonEtaSelector(_photon, 1.45, 0),
                steps.Other.passFilter("vertexDistribution1"),
                steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),                
                steps.Other.multiplicityFilter("%sIndices%s"%_jet, nMin = 1),
                steps.Photon.singlePhotonHistogrammer(_photon, _jet),
                ]

        #require vertex
        outList += steps.Other.multiplicityPlotFilter("vertexIndices", nMin = 1, xlabel = "N vertices")

        if params["vertexMode"] :
            return outList

        #HT bin and leading jets
        outList += [
            ##when using full scaling
            #steps.Jet.htBinFilter(_jet, min = params["htBin"], max = params["htBin"]),
            #steps.Jet.jetSelector(_jet, params["referenceThresholds"][0], 0),
            #steps.Jet.jetSelector(_jet, params["referenceThresholds"][0], 1),
            #steps.Jet.jetEtaSelector(_jet, 2.5, 0),

            #otherwise
            steps.Jet.jetPtSelector(_jet, params["thresholds"][2], 0),
            steps.Jet.jetPtSelector(_jet, params["thresholds"][2], 1),
            steps.Jet.jetEtaSelector(_jet,2.5,0),
            steps.Other.histogrammer("%sSum%s%s"%(_jet[0], _et, _jet[1]), 50, 0, 2500,
                                     title = ";H_{T} (GeV) from %s%s %ss;events / bin"%(_jet[0], _jet[1], _et)),
            steps.Other.variableGreaterFilter(params["thresholds"][0],"%sSum%s%s"%(_jet[0], _et, _jet[1]), "GeV"),
            ]
        outList += htUpper

        #one photon (zero in zMode)
        if not params["zMode"] :
            outList+=[
                #steps.Other.passFilter("photonEfficiencyPlots1"),
                #steps.Gen.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                #                                etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),

                steps.Filter.pt("%sP4%s"%_photon, min = 100.0, indices = "%sIndices%s"%_photon, index = 0),
                steps.Filter.absEta("%sP4%s"%_photon, min = params["subdet"][0], max = params["subdet"][1], indices = "%sIndices%s"%_photon, index = 0),
                steps.Filter.DeltaRGreaterSelector(jets = _jet, particles = _photon, minDeltaR = 1.0, particleIndex = 0),
                
                steps.Other.multiplicityFilter("%sIndices%s"%_photon, nMin = 1, nMax = 1),

                #steps.Other.passFilter("photonEfficiencyPlots2"),
                #steps.Gen.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                #                                etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),                                            
                ]
        else :
            outList+=[
                steps.Other.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
                ]
        
        #steps.Other.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),

        outList += [
            #bad-jet, electron, muon, vetoes
            steps.Other.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.Other.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.Other.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0),
            steps.Jet.uniquelyMatchedNonisoMuons(_jet),
            steps.Other.multiplicityFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1]),
            ]

        ##play with photon pT
        #outList += [
        #    steps.Filter.pt("%sP4%s"%_photon, min = params["thresholds"][2], indices = "%sIndices%s"%_photon, index = 0),
        #    steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
        #    steps.Filter.pt("%sP4%s"%_photon, min = 1.2*params["thresholds"][2], indices = "%sIndices%s"%_photon, index = 0),            
        #    steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
        #    steps.Filter.pt("%sP4%s"%_photon, min = 1.5*params["thresholds"][2], indices = "%sIndices%s"%_photon, index = 0),            
        #    steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
        #    steps.Filter.pt("%sP4%s"%_photon, min = 2.0*params["thresholds"][2], indices = "%sIndices%s"%_photon, index = 0),
        #    steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
        #    steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
        #
        #    steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 5*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 0, xtitle = "jet 1 p_{T} (GeV)"),
        #    steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 4*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 1, xtitle = "jet 2 p_{T} (GeV)"),
        #    steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 2*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 2, xtitle = "jet 3 p_{T} (GeV)"),
        #    ]
        
        outList+=[
            #many plots
            steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots1"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),
            steps.Other.passFilter("purityPlots1"),
            steps.Gen.photonPurityPlots("Status1Photon", _jet, _photon),
            
            steps.Other.passFilter("jetSumPlots"),
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.Other.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.Other.histogrammer("metP4PF",100,0.0,500.0,title=";metP4PF (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.Other.passFilter("kinematicPlots"),
            steps.Jet.alphaHistogrammer(_jet, deltaPhiStarExtraName = "", etRatherThanPt = _etRatherThanPt),
            steps.Other.histogrammer("%sAlphaTWithPhoton1PtRatherThanMht%s"%_jet, 4, 0.0, 4*0.55, title = ";#alpha_{T} using photon p_{T} rather than MHT;events / bin"),
            steps.Other.histogrammer(("%sAlphaTEt%s"%_jet, "%sAlphaTWithPhoton1PtRatherThanMht%s"%_jet),
                               (25, 25), (0.50, 0.50), (1.0, 1.0), title = ";#alpha_{T};#alpha_{T} using photon p_{T} rather than MHT;events / bin"),
            
            steps.Jet.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),
            
            steps.Filter.value("%sMhtOverHt%s"%_jet, min = 0.4),
            
            steps.Jet.alphaHistogrammer(_jet, deltaPhiStarExtraName = "", etRatherThanPt = _etRatherThanPt),            
            #steps.Other.histogrammer("%sAlphaTEt%s"%_jet, 4, 0.0, 0.55*4, title=";#alpha_{T};events / bin"),
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots2"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),
            
            steps.Other.variableGreaterFilter(0.55,"%sAlphaTEt%s"%_jet),
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            
            steps.Jet.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),            
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots3"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),
            
            steps.Other.passFilter("purityPlots2"),
            steps.Gen.photonPurityPlots("Status1Photon", _jet, _photon),
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            
            steps.Other.histogrammer("%sMht%sOver%s" %(_jet[0], _jet[1]+params["highPtName"], _met if params["zMode"] else _met+"Plus%s%s"%_photon), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0], _jet[1], _met if params["zMode"] else _met+"Plus%s%s"%_photon)),
            steps.Other.variableLessFilter(1.25,"%sMht%sOver%s" %(_jet[0], _jet[1]+params["highPtName"], _met if params["zMode"] else _met+"Plus%s%s"%_photon)),
            steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),

            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),

            steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 5*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 0, xtitle = "jet 1 p_{T} (GeV)"),
            steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 4*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 1, xtitle = "jet 2 p_{T} (GeV)"),
            steps.Histos.pt("%sCorrectedP4%s"%_jet, 20, 0.0, 2*params["thresholds"][2], indices = "%sIndices%s"%_jet, index = 2, xtitle = "jet 3 p_{T} (GeV)"),
            steps.Histos.eta("%sCorrectedP4%s"%_jet, 6, -3.0, 3.0, indices = "%sIndices%s"%_jet, index = 2, xtitle = "jet 3"),

            #steps.Other.skimmer(),
            
            #steps.Gen.genMotherHistogrammer("genIndicesPhoton", specialPtThreshold = 100.0),
            #steps.Print.eventPrinter(),
            #steps.Print.vertexPrinter(),
            #steps.Jet.jetPrinter(_jet),
            #steps.Jet.htMhtPrinter(_jet),
            #steps.Print.particleP4Printer(_photon),
            #steps.Print.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.Gen.genParticlePrinter(minPt = 10.0, minStatus = 3),
            #steps.Gen.genParticlePrinter(minPt = -1.0, minStatus = 3),
            #steps.Gen.genParticlePrinter(minPt=-10.0,minStatus=1),
            #
            #steps.Displayer.displayer(jets      = _jet,
            #                          muons     = _muon,
            #                          met       = params["objects"]["met"],
            #                          electrons = params["objects"]["electron"],
            #                          photons   = params["objects"]["photon"],                            
            #                          recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                          scale     = 400.0,#GeV
            #                          etRatherThanPt = _etRatherThanPt,
            #                          #doGenParticles = True,
            #                          deltaPhiStarExtraName = params["lowPtName"],
            #                          #deltaPhiStarExtraName = "%s%s"%("","PlusPhotons"),
            #                          mhtOverMetName = "%sMht%sOver%s"%(_jet[0], _jet[1]+params["highPtName"], _met if params["zMode"] else _met+"Plus%s%s"%_photon),
            #                          ),

            steps.Other.histogrammer("%sSumEt%s"%_jet, 40, 0, 1000, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),
            ] + [steps.Other.variableGreaterFilter(375.0+100*iBin, "%sSumEt%s"%_jet, suffix = "GeV") for iBin in range(1,6)]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.MC.mc, samples.JetMET.jetmet, samples.Photon.photon]

    def qcdMgNames2010(self) :
        return [#"v12_qcd_mg_ht_50_100_noIsoReqSkim",
            "v12_qcd_mg_ht_100_250_noIsoReqSkim",
            "v12_qcd_mg_ht_250_500_noIsoReqSkim",
            "v12_qcd_mg_ht_500_1000_noIsoReqSkim",
            "v12_qcd_mg_ht_1000_inf_noIsoReqSkim",
            ]

    def gJetsMgNames2010(self) :
        return ["v12_g_jets_mg_pt40_100_noIsoReqSkim",
                "v12_g_jets_mg_pt100_200_noIsoReqSkim",
                "v12_g_jets_mg_pt200_noIsoReqSkim"
                ]

    def qcdMgNames(self, era = "") :
        l = ["100", "250", "500", "1000", "inf"]
        return ["qcd_mg_ht_%s_%s_%s_skim"%(a, b, era) for a,b in zip(l[:-1], l[1:])]

    def gJetsMgNames(self, era = "") :
        l = ["40", "100", "200", "inf"]
        return ["g_jets_mg_ht_%s_%s_%s_skim"%(a, b, era) for a,b in zip(l[:-1], l[1:])]

    def zNunuMgNames(self, era = "summer11") :
        if era=="spring11" : return ["zinv_jets_mg"]
        l = ["50", "100", "200", "inf"]
        return ["znunu_jets_mg_ht_%s_%s_%s_skim"%(a, b, era) for a,b in zip(l[:-1], l[1:])]

    #def qcdPyNames(self) : #full samples
    #    l = ["15", "30", "50", "80", "120", "170", "300", "470", "600", "800", "1000", "1400", "1800"]
    #    return ["qcd_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-2], l[1:-1])]
    #
    #def gJetsPyNames(self) : #full samples
    #    l = ["0", "15", "30", "50", "80", "120", "170", "300", "470", "800", "1400", "1800", "inf"]
    #    return ["g_jets_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def qcdPyNames(self) :
        l = ["80", "120", "170", "300", "470", "600", "800"]
        return ["qcd_py6_pt_%s_%s_noIsoReqSkim"%(a,b) for a,b in zip(l[:-2], l[1:-1])]

    def gJetsPyNames(self) :
        l = ["80", "120", "170", "300", "470", "800"]
        return ["g_jets_py6_pt_%s_%s_noIsoReqSkim"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def listOfSamples(self,params) :
        from samples import specify

        #2010
        data_2010_nov4 = specify(names = ["Nov4_MJ_noIsoReqSkim","Nov4_J_noIsoReqSkim",
                                          "Nov4_J2_noIsoReqSkim","Nov4_JM_noIsoReqSkim",
                                          "Nov4_JMT_noIsoReqSkim","Nov4_JMT2_noIsoReqSkim",
                                          ])
        data_2010_prompt = specify(names = ["Run2010A_JMT_skim_noIsoReqSkim","Run2010A_JM_skim_noIsoReqSkim",
                                            "Run2010B_J_skim_noIsoReqSkim","Run2010B_J_skim2_noIsoReqSkim",
                                            "Run2010B_MJ_skim_noIsoReqSkim","Run2010B_MJ_skim2_noIsoReqSkim",
                                            "Run2010B_MJ_skim3_noIsoReqSkim","Run2010B_MJ_skim4_noIsoReqSkim",
                                            #"Run2010B_MJ_skim5_noIsoReqSkim",
                                            ])
        qcd_mg_2010    = specify(names = self.qcdMgNames2010())
        g_jets_mg_2010 = specify(names = self.gJetsMgNames2010())
        zinv_mg_2010   = specify(names = ["z_inv_mg_v12_skim"], color = r.kMagenta+3)

        ##2011 EPS
        #jw = calculables.Other.jsonWeight("cert/Cert_160404-167913_7TeV_PromptReco_Collisions11_JSON.txt") #1078/pb
        #data = []
        #data += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Zoe_skim",    weights = jw, overrideLumi = 188.9)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe1_skim",    weights = jw, overrideLumi =  70.0)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe2_skim",    weights = jw, overrideLumi = 151.1)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe3_skim",    weights = jw, overrideLumi =  74.4)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob1_skim",    weights = jw, overrideLumi = 167.1)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob2_skim",    weights = jw, overrideLumi = 119.7)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob3_skim",    weights = jw, overrideLumi = 180.2)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob4_skim",    weights = jw, overrideLumi =  69.3)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Darren1_skim", weights = jw, overrideLumi =  36.3)

        #2011
        data = []

        #jwPrompt = calculables.Other.jsonWeight("cert/Cert_160404-177515_7TeV_PromptReco_Collisions11_JSON.txt")
        #jwMay = calculables.Other.jsonWeight("cert/Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON_v3.txt")
        #jwAug = calculables.Other.jsonWeight("cert/Cert_170249-172619_7TeV_ReReco5Aug_Collisions11_JSON_v3.txt")
        #data += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Darren1", weights = jwMay   , overrideLumi = 202.7)
        #data += specify(names = "Photon.Run2011A-05Aug2011-v1.AOD.Bryn1",     weights = jwAug   , overrideLumi = 318.5)
        #data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Bryn1",    weights = jwPrompt, overrideLumi = 549.8)
        #data += specify(names = "Photon.Run2011A-PromptReco-v6.AOD.Bryn1",    weights = jwPrompt, overrideLumi = 382.6)
        #data += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn1",    weights = jwPrompt, overrideLumi = 221.2)
        #data += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn2",    weights = jwPrompt, overrideLumi = 280.5)
        #data += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn3",    weights = jwPrompt, overrideLumi = 374.1)

        data += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.job662_skim",color = r.kBlack)
        data += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.job664_skim", color = r.kRed)
        data += specify(names = "Photon.Run2011A-05Aug2011-v1.AOD.job663_skim",  color = r.kBlue)
        data += specify(names = "Photon.Run2011A-PromptReco-v6.AOD.job667_skim", color = r.kGreen)
        data += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.job668_skim", color = r.kCyan)
        
        eL = 20000.0

        phw = calculables.Photon.photonWeight(var = "vertexIndices")
        
        qcd_mg          = specify(effectiveLumi = eL, color = r.kBlue, names = self.qcdMgNames(era = "spring11"))
        g_jets_mg       = specify(effectiveLumi = eL, color = r.kGreen, names = self.gJetsMgNames(era = "summer11"))

        qcd_mg_weighted = specify(effectiveLumi = eL, color = r.kBlue, names = self.qcdMgNames(era = "spring11"), weights = phw)
        g_jets_mg_weighted = specify(effectiveLumi = eL, color = r.kGreen, names = self.gJetsMgNames(era = "summer11"), weights = phw)

        qcd_py6         = specify(effectiveLumi = eL, color = r.kBlue, names = self.qcdPyNames())
        g_jets_py6      = specify(effectiveLumi = eL, color = r.kGreen, names = self.gJetsPyNames())

        ttbar_mg = specify(effectiveLumi = eL, color = r.kOrange, names = ["tt_tauola_mg_noIsoReqSkim"])
        zjets_mg = specify(effectiveLumi = eL, color = r.kYellow-3, names = ["dyll_jets_mg_noIsoReqSkim"])
        wjets_mg = specify(effectiveLumi = eL, color = 28, names = ["w_jets_mg_noIsoReqSkim"])

        zinv_mg           = specify(effectiveLumi = eL, color = r.kMagenta, names = self.zNunuMgNames(era = "summer11"))
        zinv_mg_weighted  = specify(effectiveLumi = eL, color = r.kMagenta, names = self.zNunuMgNames(era = "summer11"), weights = phw)

        zinv_py6 = specify(effectiveLumi = eL, color = r.kMagenta, names = ["z_nunu"])
        
        outList = []

        if not params["zMode"] :
            #2010
            #outList += qcd_mg_2010
            #outList += g_jets_mg_2010
            #outList += data_2010_prompt
            ##outList += data_2010_nov4

            #2011
            #outList += qcd_py6
            #outList += g_jets_py6
            
            #outList += zjets_mg
            #outList += wjets_mg
            #outList += ttbar_mg

            outList += qcd_mg
            outList += g_jets_mg
            #outList += qcd_mg_weighted
            #outList += g_jets_mg_weighted
            
            outList += data

            #outList += freaks
            #outList += cands1
            #outList += cands2
            #outList += cands3
        else :
            #outList += zinv_mg_2010
            #outList += zinv_py6

            outList += zinv_mg
            #outList += zinv_mg_weighted
            
        return outList

    def mergeSamples(self, org) :
        smSources = []
        #ewkSources = ["z_inv_mg", "z_jets_mg", "w_jets_mg"]
        #smSources += ewkSources

        #org.mergeSamples(targetSpec = {"name":"qcd_py6",    "color":r.kBlue},  sources = self.qcdPyNames())
        #org.mergeSamples(targetSpec = {"name":"g_jets_py6", "color":r.kGreen}, sources = self.gJetsPyNames())
        #smSources += ["qcd_py6", "g_jets_py6"]
        #org.mergeSamples(targetSpec = {"name":"standard_model_py6",         "color":r.kRed,   "markerStyle":1}, sources = smSources, keepSources = True)

        names = [("_nVtx", ".photonWeight"), ("", "")][1]
        if "Z" in org.tag :
            org.mergeSamples(targetSpec = {"name":"znunu_mg%s"%names[0], "color":r.kMagenta}, sources = [item+names[1] for item in self.zNunuMgNames(era = "summer11")])
            return
        
        org.mergeSamples(targetSpec = {"name":"qcd_mg%s"%names[0],    "color":r.kBlue},  sources = [item+names[1] for item in self.qcdMgNames(era = "spring11")])
        org.mergeSamples(targetSpec = {"name":"g_jets_mg%s"%names[0], "color":r.kGreen}, sources = [item+names[1] for item in self.gJetsMgNames(era = "summer11")])

        smSources += ["qcd_mg%s"%names[0], "g_jets_mg%s"%names[0]]
        org.mergeSamples(targetSpec = {"name":"standard_model%s"%names[0], "color":r.kRed}, sources = smSources, keepSources = True)
        
        org.mergeSamples(targetSpec = {"name":"2011 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "Photon.Run2011")
            
        ##org.mergeSamples(targetSpec = {"name":"MG TT+EWK", "color":r.kOrange}, sources = ewkSources])
        #org.mergeSamples(targetSpec = {"name":"qcd_mg_2010",    "color":r.kBlue -3}, sources = self.qcdMgNames2010())
        #org.mergeSamples(targetSpec = {"name":"g_jets_mg_2010", "color":r.kGreen-3}, sources = self.gJetsMgNames2010())
        #smSources2010 += ["qcd_mg_2010", "g_jets_mg_2010"]
        #org.mergeSamples(targetSpec = {"name":"sm_2010", "color":r.kRed-3, "markerStyle":1}, sources = smSources2010, keepSources = True)

        ##org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "Nov4")
        #org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "Run2010")


    def concludeAll(self) :
        #super(photonLook,self).concludeAll()

        for item in ["275","325","375"][-1:] :
            organizers = [self.organizer(conf) for conf in self.readyConfs if (item in conf["tag"])]
            for org in organizers :
                self.mergeSamples(org)
                if "Z" in org.tag :
                    lumi = 4529.2
                    org.scale(lumi)
                    print "WARNING: HARD-CODED LUMI FOR Z MODE! (%g)"%lumi
                else :
                    org.scale()
            melded = organizer.organizer.meld(organizers = organizers)
            self.makeStandardPlots(melded)
            #self.makeIndividualPlots(melded)
                                 
    def conclude(self, conf) :
        org = self.organizer(conf)
        
        ##for skimming only
        #utils.printSkimResults(org)

        self.mergeSamples(org)
        if "Z" in org.tag :
            lumi = 4529.2
            org.scale(lumi)
            print "WARNING: HARD-CODED LUMI FOR Z MODE! (%g)"%lumi
        else :
            org.scale()
            
        self.makeStandardPlots(org)
        #self.makeIndividualPlots(org)
        #self.makePurityPlots(org, tag)
        #self.makeEfficiencyPlots(org, tag)
        #self.makeNVertexWeights(org, tag)
        #self.makeMultiModePlots(34.7255)

    def makeStandardPlots(self, org) :
        names = [ss["name"] for ss in org.samples]
        samplesForRatios = filter(lambda x: x[0] in names and x[1] in names,
                                  [("2011 Data","standard_model_nVtx"),
                                   (".2011 Data",".standard_model_nVtx"),
                                   ("g.2011 Data","g.standard_model_nVtx"),
                                   ("g.2011 Data","g.standard_model"),
                                   ("2011 Data","standard_model"),
                                   ("2011 Data","standard_model_py6"),
                                   ("2010 Data","sm_2010")])

        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             sampleLabelsForRatios = ("data","s.m."),
                             samplesForRatios = next(iter(samplesForRatios), ("","")),
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
                             doLog = False,
                             printRatios = True,
                             #latexYieldTable = True,
                             rowColors = [r.kBlack, r.kViolet+4],
                             #whiteList = ["xcak5JetIndicesPat",
                             #             #"photonPat1Pt",
                             #             #"photonPat1mhtVsPhotonPt",
                             #             "xcak5JetAlphaTFewBinsPat",
                             #             "xcak5JetAlphaTRoughPat",
                             #             "xcak5JetAlphaTWithPhoton1PtRatherThanMhtPat",
                             #             ],
                             )
        pl.plotAll()
            
    def makeIndividualPlots(self, org) :
        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             showStatBox = False,
                             doLog = False,
                             anMode = True,
                             )
        plots1 = [{"plotName":"xcak5JetAlphaTFewBinsPat",
                   "stepName" :"alphaHistogrammer",
                   "stepDesc" :"xcak5JetPat",
                   "newTitle":";#alpha_{T};events / bin"},
                  
                  {"plotName":"xcak5JetIndicesPat",
                   "stepName" :"histogrammer",
                   "stepDesc" :"(lambda x:len(x))(xcak5JetIndicesPat)",
                   "newTitle":";N_{jets};events / bin"},
                  
                  {"plotName":"photonPat1Pt",
                   "stepName":"singlePhotonHistogrammer",
                   "stepDesc":"photonPat through index 0",
                   "newTitle":";photon p_{T} (GeV);events / bin",
                   "legendCoords": (0.2, 0.60, 0.5, 0.90),
                   "stamp": False,
                   "index":-1,
                   "reBinFactor":5},
                  ]

        plots2 = [{"plotName":"photonPat1mhtVsPhotonPt",
                   "stepName":"singlePhotonHistogrammer",
                   "stepDesc":"photonPat through index 0",
                   "newTitle":";photon p_{T} (GeV);MHT (GeV);events / bin",
                   "stamp": False,
                   "sampleName":"2011 Data",
                   #"index":-1,
                   },
                  ]

        plots3 = [{"plotName":"xcak5JetAlphaTRoughPat",
                   "stepName" :"variablePtGreaterFilter",
                   "stepDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                   "newTitle":";#alpha_{T};events / bin / 35 pb^{-1}"},

                  {"plotName":"photonPat1MinDRToJet",
                   "stepName" :"passFilter",
                   "stepDesc" :"singlePhotonPlots2",
                   "newTitle":";#DeltaR(photon, nearest jet);events / bin / 35 pb^{-1}",
                   "reBinFactor":3},
                  
                  {"plotName":"photonPat1SeedTime",
                   "stepName" :"passFilter",
                   "stepDesc" :"singlePhotonPlots2",
                   "newTitle":";time of photon seed crystal hit (ns);events / bin / 35 pb^{-1}",
                   "sampleWhiteList": ["2010 Data"]},
                  
                  {"plotName":"photonPat1sigmaIetaIetaBarrel",
                   "stepName" :"passFilter",
                   "stepDesc" :"singlePhotonPlots2",
                   "newTitle":";#sigma_{i#eta i#eta};events / bin / 35 pb^{-1}"},
                  
                  {"plotName":"photonPat1combinedIsolation",
                   "stepName" :"passFilter",
                   "stepDesc" :"singlePhotonPlots2",
                   "onlyDumpToFile":True},
                  ]

        newSampleNames = {"qcd_mg_nVtx": "Madgraph QCD",
                          "g_jets_mg_nVtx": "Madgraph #gamma + jets",
                          "2011 Data": "Data",
                          "standard_model_nVtx": "Standard Model",
                          }

        pl.individualPlots(plotSpecs = plots2,
                           newSampleNames = newSampleNames,
                           preliminary = True,
                           tdrStyle = False,
                           )

        pl.individualPlots(plotSpecs = plots1,
                           newSampleNames = newSampleNames,
                           preliminary = True,
                           tdrStyle = True,
                           )

    def makeNVertexWeights(self, org, tag, chopToOne = False) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        def numerAndDenom(org, var) :
            d = {}
            for selection in org.selections :
                if selection.name != "passFilter" : continue
                if selection.title!="vertexDistribution1" : continue
                if var in selection :
                    sample = "2011 Data";      d["numer"] = selection[var][sampleIndex(org, sample)].Clone("%s_%s_clone"%(var, sample.replace(" ","_")))
                    sample = "standard_model"; d["denom"] = selection[var][sampleIndex(org, sample)].Clone("%s_%s_clone"%(var, sample.replace(" ","_")))
            return d

        def chop(h) :
            for iBin in range(1, 1 + h.GetNbinsX()) :
                if h.GetBinCenter(iBin)!=1.0 :
                    h.SetBinContent(iBin, 0.0)
            return
            
        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)
        canvas.SetTickx()
        canvas.SetTicky()
        psFileName = "%s.ps"%tag
        canvas.Print(psFileName+"[","Lanscape")
        for variable in ["vertexIndices"] :
            histos = numerAndDenom(org, variable)
            if "numer" not in histos or "denom" not in histos : continue

            #get relative bin heights
            result = histos["denom"].Clone("%s_oldDist"%variable)
            result.Reset()
            if chopToOne : chop(histos["numer"])
            result.Divide(histos["numer"], histos["denom"], 1.0/histos["numer"].Integral(), 1.0/histos["denom"].Integral())
            result.SetBinContent(1, 1.0); result.SetBinError(1, 0.0) #hack for zero vertex bin

            #leave MC yield unchanged
            newDist = histos["denom"].Clone("%s_newDist"%variable)
            newDist.Reset()
            newDist.Multiply(histos["denom"], result)
            result.Scale(histos["denom"].Integral()/newDist.Integral())

            #print results
            contents = []
            for iBin in range(1, 1+result.GetNbinsX()) :
                contents.append("%g:%g"%(result.GetBinCenter(iBin), result.GetBinContent(iBin)))
            print "self.weight = {%s}"%", ".join(contents)
            result.GetYaxis().SetTitle("weight to apply to MC")
            result.SetMarkerStyle(20)
            result.SetStats(False)
            result.Draw()
            canvas.Print(psFileName,"Lanscape")

        canvas.Print(psFileName+"]","Lanscape")                
        os.system("ps2pdf "+psFileName)
        os.remove(psFileName)

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

    def makeMultiModePlots(self, lumi) :
        def org(tag) :
            org = organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            if "Z" in tag : org.scale(1.0)
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

        plotName = ("xcak5JetAlphaTEtPat", "variablePtGreaterFilter", "xcak5JetSumP4Pat.pt()>=140.0 GeV")
        samples = ["z_inv_mg_v12_skim", "g_jets_mg_v12", "2010 Data"]
        sampleNames = ["Z -> #nu #bar{#nu}", " #gamma + jets", "Data"]
        styles  = [28,                   29,             20]
        d = histoDict(plotName, samples)

        canvas = r.TCanvas("canvas","canvas",500,500)
        canvas.SetTickx()
        canvas.SetTicky()

        legend = r.TLegend(0.65, 0.65, 0.85, 0.85)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)

        first = True
        for iSample,sample in enumerate(samples) :
            histo = d[sample]
            histo.SetMarkerStyle(styles[iSample])
            histo.SetStats(False)
            histo.Scale( 1.0/histo.Integral(0,histo.GetNbinsX()+1) )
            legend.AddEntry(histo,sampleNames[iSample],"pl")
            if first :
                histo.Draw()
                histo.GetYaxis().SetRangeUser(0.0,1.0)
                histo.GetYaxis().SetTitle("fraction of events / bin")
                histo.GetYaxis().SetTitleOffset(1.25)
            else :
                histo.Draw("same")
            first = False

        legend.Draw()

        utils.cmsStamp(lumi)
        
        eps = "alphaTCompare.eps"
        canvas.Print(eps)
        os.system("epstopdf "+eps)
        os.remove(eps)
