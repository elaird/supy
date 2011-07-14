#!/usr/bin/env python

import copy,os
import analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class hadronicLook(analysis.analysis) :
    def parameters(self) :
        objects = self.vary()
        fields =                                                  [ "jet",                        "jetId",     "muonsInJets",           "met",
                                                                    "compJet",                "compJetId", "compMuonsInJets",        "compMet",
                                                                    "muon",                    "electron",          "photon",         "rechit"]

        objects["caloAK5JetMet_recoLepPhot"]   = dict(zip(fields, [("xcak5Jet","Pat"),       "JetIDloose",             False, "metP4AK5TypeII",
                                                                   ("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
                                                                   ("muon","Pat"),     ("electron","Pat"),  ("photon","Pat"),           "Calo",
                                                                   ]))
        
        #objects["pfAK5JetMet_recoLepPhot"]     = dict(zip(fields, [("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
        #                                                           ("xcak5Jet","Pat"),       "JetIDloose",             False, "metP4AK5TypeII",
        #                                                           ("muon","Pat"),     ("electron","Pat"),  ("photon","Pat"),             "PF",
        #                                                           ]))
        
        #objects["pf2patAK5JetMetLep_recoPhot"] = dict(zip(fields, [("xcak5JetPF2PAT","Pat"), "PFJetIDtight",            True,        "metP4PF",
        #                                                           ("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
        #                                                           ("muon","PF"),       ("electron","PF"),  ("photon","Pat"),             "PF",
        #                                                           ]))
        
        return { "objects": objects,
                 "nJetsMinMax" :      self.vary(dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)),  ("3",(3,3)) ]       [0:1] )),
                 "mcSoup" :           self.vary(dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] )),
                 "etRatherThanPt" : [True,False][0],
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "highPtThreshold" : 50.0,
                 "highPtName" : "highPt",
                 "tanBeta" : [None, 3, 10, 50][0],
                 "thresholds": self.vary(dict( [("275",        (275.0, 325.0, 100.0, 50.0)),#0
                                                ("325",        (325.0, 375.0, 100.0, 50.0)),#1
                                                ("375",        (375.0, None,  100.0, 50.0)),#2
                                                ("325_scaled", (325.0, 375.0,  86.7, 43.3)),#3
                                                ("275_scaled", (275.0, 325.0,  73.3, 36.7)),#4
                                                ][2:3] )),
                 #required to be sorted
                 #"triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"), #2010
                 #"triggerList": ("HLT_HT250_AlphaT0p55_v1","HLT_HT250_AlphaT0p55_v2","HLT_HT250_MHT60_v2","HLT_HT250_MHT60_v3","HLT_HT260_MHT60_v2","HLT_HT300_MHT75_v2","HLT_HT300_MHT75_v3","HLT_HT300_MHT75_v4"),#alphaT trigger test
                 "triggerList": tuple(["HLT_HT250_MHT60_v%d"%i for i in [2,3,4,6,7]   ]+
                                      ["HLT_HT250_MHT70_v%d"%i for i in [1,3,4]       ]+
                                      ["HLT_HT250_MHT80_v%d"%i for i in [3,4]         ]+
                                      ["HLT_HT250_MHT90_v%d"%i for i in [1]           ]+
                                      ["HLT_HT250_MHT100_v%d"%i for i in [1]          ]+
                                      ["HLT_HT260_MHT60_v%d"%i for i in [2]           ]

                                      #["HLT_HT300_MHT75_v%d"%i for i in [2,3,4,5,7,8] ]+
                                      #["HLT_HT300_MHT80_v%d"%i for i in [1]           ]+
                                      #["HLT_HT300_MHT90_v%d"%i for i in [1]           ]+
                                      #
                                      #["HLT_HT350_MHT70_v%d"%i for i in [1]           ]+
                                      #["HLT_HT350_MHT80_v%d"%i for i in [1]           ]+
                                      #
                                      #["HLT_HT250_MHT100_v%d"%i for i in [1]]
                                      )
                 }

    def ra1Cosmetics(self) : return True
    
    def calcListJet(self, obj, etRatherThanPt, ptMin, lowPtThreshold, lowPtName, highPtThreshold, highPtName) :
        def calcList(jet, met, photon, muon, electron, muonsInJets, jetIdFlag) :
            outList = [
                calculables.XClean.xcJet(jet,
                                         applyResidualCorrectionsToData = False,
                                         gamma = photon,
                                         gammaDR = 0.5,
                                         muon = muon,
                                         muonDR = 0.5,
                                         correctForMuons = not muonsInJets,
                                         electron = electron,
                                         electronDR = 0.5),
                calculables.Jet.Indices( jet, ptMin = ptMin,           etaMax = 3.0, flagName = jetIdFlag),
                calculables.Jet.Indices( jet, ptMin = lowPtThreshold,  etaMax = 3.0, flagName = jetIdFlag, extraName = lowPtName),
                calculables.Jet.Indices( jet, ptMin = highPtThreshold, etaMax = 3.0, flagName = jetIdFlag, extraName = highPtName),
                
                calculables.Jet.SumP4(jet),
                calculables.Jet.SumP4(jet, extraName = lowPtName),
                calculables.Jet.SumP4(jet, extraName = highPtName),
                calculables.Jet.DeltaPhiStar(jet, extraName = lowPtName),
                calculables.Jet.DeltaPhiStar(jet),
                calculables.Jet.DeltaPseudoJet(jet, etRatherThanPt),
                calculables.Jet.AlphaT(jet, etRatherThanPt),
                calculables.Jet.AlphaTMet(jet, etRatherThanPt, met),
                calculables.Jet.MhtOverMet((jet[0], jet[1]+highPtName), met),
                calculables.Jet.deadEcalDR(jet, extraName = lowPtName, minNXtals = 10),
                ]
            return outList+calculables.fromCollections(calculables.Jet, [jet])

        outList = calcList(obj["jet"], obj["met"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetId"])
        if all([("comp"+item in obj) for item in ["Jet", "Met","MuonsInJets","JetId"]]) :
            outList += calcList(obj["compJet"], obj["compMet"], obj["photon"], obj["muon"], obj["electron"], obj["compMuonsInJets"], obj["compJetId"])
        return outList

    def calcListOther(self, obj, triggers) :
        return [
            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),

            calculables.Muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.Photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            #calculables.Photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDTightFromTwikiPat"),

            calculables.Other.RecHitSumPt(obj["rechit"]),            
            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            calculables.Other.lowestUnPrescaledTrigger(triggers),
            ]
    
    def listOfCalculables(self, params) :
        obj = params["objects"]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += self.calcListOther(obj, params["triggerList"])
        outList += self.calcListJet(obj, params["etRatherThanPt"], params["thresholds"][3],
                                    params["lowPtThreshold"], params["lowPtName"], params["highPtThreshold"], params["highPtName"])
        return outList
    
    def listOfSteps(self, params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]
        _et = "Et" if _etRatherThanPt else "Pt"

        scanBefore = [steps.Other.passFilter("scanBefore"), steps.Gen.scanHistogrammer(tanBeta = params["tanBeta"])] if params["tanBeta"]!=None else []
        scanAfter = [steps.Other.passFilter("scanAfter"),
                     steps.Gen.scanHistogrammer(tanBeta = params["tanBeta"], htVar = "%sSum%s%s"%(_jet[0], _et, _jet[1]))] if params["tanBeta"]!=None else []
        htUpper = [steps.Other.variableLessFilter(params["thresholds"][1],"%sSum%s%s"%(_jet[0], _et, _jet[1]), "GeV")] if params["thresholds"][1]!=None else []
        return scanBefore + [
            steps.Print.progressPrinter(),
            steps.Trigger.lowestUnPrescaledTriggerFilter(),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            
            steps.Trigger.physicsDeclaredFilter(),
            steps.Other.monsterEventFilter(),
            steps.Other.hbheNoiseFilter(),

            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Trigger.hltPrescaleHistogrammer(params["triggerList"]),
            
            #steps.Other.cutSorter([

            ##when using full scaling
            #steps.Jet.htBinFilter(_jet, min = params["htBin"], max = params["htBin"]),
            #steps.Jet.jetSelector(_jet, params["thresholds"][2], 0),
            #steps.Jet.jetSelector(_jet, params["thresholds"][2], 1),

            #otherwise
            steps.Jet.jetPtSelector(_jet, params["thresholds"][2], 0),
            steps.Jet.jetPtSelector(_jet, params["thresholds"][2], 1),
            steps.Jet.jetEtaSelector(_jet,2.5,0),
            
            #steps.Other.iterHistogrammer("ecalDeadTowerTrigPrimP4", 256, 0.0, 128.0, title=";E_{T} of ECAL TP in each dead region (GeV);TPs / bin", funcString="lambda x:x.Et()"),
            ]+(
            steps.Other.multiplicityPlotFilter("vertexIndices",                  nMin = 1, xlabel = "N vertices") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_muon,              nMax = 0, xlabel = "N muons") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_electron,          nMax = 0, xlabel = "N electrons") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_photon,            nMax = 0, xlabel = "N photons") +
            steps.Other.multiplicityPlotFilter("%sIndicesOther%s"%_jet,          nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_jet) +
            steps.Other.multiplicityPlotFilter("%sIndicesOther%s"%_muon,         nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_muon) +
            steps.Other.multiplicityPlotFilter("%sIndicesUnmatched%s"%_electron, nMax = 0, xlabel = "N electrons unmatched") +
            steps.Other.multiplicityPlotFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0, xlabel = "N photons unmatched") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1], xlabel="number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts"%_jet)
            )+[
            steps.Jet.uniquelyMatchedNonisoMuons(_jet), 
            
            steps.Other.histogrammer("%sSum%s%s"%(_jet[0], _et, _jet[1]), 50, 0, 2500, title = ";H_{T} (GeV) from %s%s %ss;events / bin"%(_jet[0], _jet[1], _et)),
            steps.Other.variableGreaterFilter(params["thresholds"][0],"%sSum%s%s"%(_jet[0], _et, _jet[1]), "GeV"),
            ] + htUpper + [
            steps.Other.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            steps.Other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            
            steps.Other.histogrammer("%sSumP4%s"%_jet, 50, 0, 500, title = ";MHT from %s%s (GeV);events / bin"%_jet, funcString = "lambda x:x.pt()"),
            steps.Other.variablePtGreaterFilter(100.0,"%sSumP4%s"%_jet,"GeV"),
            steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            steps.Other.histogrammer("vertexSumPt", 100, 0.0, 1.0e3, title = ";SumPt of 2nd vertex (GeV);events / bin", funcString = "lambda x:([0.0,0.0]+sorted(x))[-2]"),
            #steps.Other.histogrammer("logErrorTooManySeeds",    2, 0.0, 1.0, title = ";logErrorTooManySeeds;events / bin"),
            #steps.Other.histogrammer("logErrorTooManyClusters", 2, 0.0, 1.0, title = ";logErrorTooManyClusters;events / bin"),
            
            #steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT350_v2", ["HLT_HT300_v3"]),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT350_v2", ["HLT_HT250_v2"]),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT350_v2", ["HLT_HT200_v2"]),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT350_v2", ["HLT_HT150_v2"]),
            #
            #steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 150.0, 450.0), "HLT_HT300_v3", ["HLT_HT250_v2"], permissive = True),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT300_v3", ["HLT_HT200_v2"]),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT300_v3", ["HLT_HT150_v2"]),
            #
            #steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 100.0, 400.0), "HLT_HT250_v2", ["HLT_HT200_v2"], permissive = True),
            ##steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60, 200.0, 500.0), "HLT_HT250_v2", ["HLT_HT150_v2"]),
            #
            #steps.Trigger.hltTurnOnHistogrammer( "%sSumEt%s"%_jet,    (60,  50.0, 350.0), "HLT_HT200_v2", ["HLT_HT150_v2"], permissive = True),
            #
            #steps.Other.variableGreaterFilter(150.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (70,   0.4,   0.75), "HLT_HT150_AlphaT0p60_v1", ["HLT_HT150_v2"]),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (70,   0.4,   0.75), "HLT_HT150_AlphaT0p70_v1", ["HLT_HT150_v2"]),
            #
            #steps.Other.variableGreaterFilter(200.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (60,   0.4,   0.7 ), "HLT_HT200_AlphaT0p60_v1", ["HLT_HT200_v2"]),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (60,   0.4,   0.7 ), "HLT_HT200_AlphaT0p65_v1", ["HLT_HT200_v2"]),
            #
            #steps.Other.variableGreaterFilter(250.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (60,   0.4,   0.7 ), "HLT_HT250_AlphaT0p55_v1", ["HLT_HT250_v2"]),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (60,   0.4,   0.7 ), "HLT_HT250_AlphaT0p62_v1", ["HLT_HT250_v2"]),
            #
            #steps.Other.variableGreaterFilter(300.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (80,   0.4,   0.6 ), "HLT_HT300_AlphaT0p52_v1", ["HLT_HT300_v3"]),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (80,   0.4,   0.6 ), "HLT_HT300_AlphaT0p54_v1", ["HLT_HT300_v3"]),
            #
            #steps.Other.variableGreaterFilter(350.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (80,   0.4,   0.6 ), "HLT_HT350_AlphaT0p51_v1", ["HLT_HT350_v2"]),
            #steps.Trigger.hltTurnOnHistogrammer( "%sAlphaTEt%s"%_jet, (80,   0.4,   0.6 ), "HLT_HT350_AlphaT0p53_v1", ["HLT_HT350_v2"]),
            
            #many plots
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            steps.Other.passFilter("singleJetPlots1"),
            steps.Jet.singleJetHistogrammer(_jet),
            steps.Other.passFilter("jetSumPlots1"), 
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.Other.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            steps.Other.histogrammer("%sDeltaPhiStar%s"%(_jet[0], _jet[1]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            steps.Other.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.Other.passFilter("kinematicPlots1"),

            steps.Jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            steps.Jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            #steps.Jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),

            #signal selection
            #steps.Other.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.Other.variableGreaterFilter(0.55,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
            #]), #end cutSorter

            #steps.Trigger.lowestUnPrescaledTriggerFilter(),
            #steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            #
            #steps.Trigger.physicsDeclaredFilter(),
            #steps.Other.monsterEventFilter(),
            #steps.Other.hbheNoiseFilter(),
            #
            #steps.Other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            #steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            
            steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.Other.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            steps.Other.histogrammer("%sDeltaPhiStar%s"%(_jet[0], _jet[1]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            steps.Other.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1]+params["highPtName"],_met)),

            #steps.Other.skimmer(),
            #steps.Other.duplicateEventCheck(),
            #steps.Other.cutBitHistogrammer(self.togglePfJet(_jet), self.togglePfMet(_met)),
            #steps.Print.eventPrinter(),
            #steps.Print.jetPrinter(_jet),

            #steps.Print.particleP4Printer(_muon),
            #steps.Print.particleP4Printer(_photon),
            #steps.Print.recHitPrinter("clusterPF","Ecal"),
            #steps.Print.htMhtPrinter(_jet),
            #steps.Print.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.Gen.genParticlePrinter(minPt = 10.0, minStatus = 3),
                   
            #steps.Other.pickEventSpecMaker(),
            #steps.Displayer.displayer(jets = _jet,
            #                          muons = _muon,
            #                          met       = params["objects"]["met"],
            #                          electrons = params["objects"]["electron"],
            #                          photons   = params["objects"]["photon"],                            
            #                          recHits   = params["objects"]["rechit"], recHitPtThreshold = 1.0,#GeV
            #                          scale = 400.0,#GeV
            #                          etRatherThanPt = _etRatherThanPt,
            #                          deltaPhiStarExtraName = params["lowPtName"],
            #                          deltaPhiStarCut = 0.5,
            #                          deltaPhiStarDR = 0.3,
            #                          mhtOverMetName = "%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met),
            #                          metOtherAlgo  = params["objects"]["compMet"],
            #                          jetsOtherAlgo = params["objects"]["compJet"],
            #                          #doGenJets = True,
            #                          markusMode = False,
            #                          ),
            ] + scanAfter + [steps.Other.variableGreaterFilter(bin, "%sSumEt%s"%_jet, suffix = "GeV") for bin in [475, 575, 675, 775, 875]] +\
            [ steps.Other.passFilter("final") ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.signalSkim]

    def listOfSamples(self,params) :
        from samples import specify

        def data() :
            out = []

            jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-167913_7TeV_PromptReco_Collisions11_JSON.txt") #1078/pb            

            out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Bryn",   weights = jw, overrideLumi = 183.0)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1",   weights = jw, overrideLumi =  70.2)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn2",   weights = jw, overrideLumi = 101.3)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn3",   weights = jw, overrideLumi =  74.8)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren1", weights = jw, overrideLumi = 181.2)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren2", weights = jw, overrideLumi = 122.8)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren3", weights = jw, overrideLumi =  36.4)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren4", weights = jw, overrideLumi =  50.5)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren5", weights = jw, overrideLumi = 130.6)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren6", weights = jw, overrideLumi = 116.0)

            #out += specify(names = "HT_skim")
            #out += specify(names = "MT2_events")
            #out += specify(names = "qcd_py6_375")
            return out

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q6.index(80)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py6_pt_%d_%d"%t)[:None if t[1] else -2] for t in zip(q6,q6[1:]+[0])[iCut:]] )

        def g_jets_py6(eL) :
            return specify( effectiveLumi = eL, color = r.kGreen,
                            names = ["v12_g_jets_py6_pt%d"%t for t in [30,80,170]] )

        def qcd_py8(eL) :
            q8 = [0,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q8.index(50)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("v14_qcd_py8_pt%dto%d"%t)[:None if t[1] else -3] for t in zip(q8,q8[1:]+[0])[iCut:]] )

        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])

        def g_jets_mg(eL) :
            gM = [40,100,200]
            return specify( effectiveLumi = eL, color = r.kGreen,
                            names = [("g_jets_mg_ht_%d_%d")[:None if t[1] else -2] for t in zip(gM,gM[1:]+["inf"])] )

        def ttbar_mg(eL) :
            return specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kOrange)
        
        def ewk(eL) :
            return ( specify(names = "zinv_jets_mg",  effectiveLumi = eL, color = r.kRed + 1) +
                     #specify(names = "z_jets_mg_v12_skim", effectiveLumi = eL, color = r.kYellow-3) +
                     specify(names = "w_jets_mg", effectiveLumi = eL, color = 28         ) )

        def susy(eL) :
            return ( specify(names = "lm1", effectiveLumi = eL, color = r.kMagenta) +
                     specify(names = "lm6", effectiveLumi = eL, color = r.kRed) )

        def scan(tanBeta) :
            return specify(names = "scan_tanbeta%d"%tanBeta, color = r.kMagenta, nFilesMax = 1)
                     
        qcd_func,g_jets_func = {"py6": (qcd_py6,g_jets_py6),
                                "py8": (qcd_py8,g_jets_py6), # no g_jets_py8 available
                                "mg" : (qcd_mg, g_jets_mg ) }[params["mcSoup"]]
        eL = 3000 # 1/pb
        susyEL = 10*eL
        #return data()
        return ( data() +
                 qcd_func(eL) + #g_jets_func(eL) +
                 ttbar_mg(eL) + ewk(eL) +
                 susy(susyEL)
                 ) if params["tanBeta"]==None else scan(params["tanBeta"])

    def mergeSamples(self, org) :
        def py8(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_py8", "color":r.kBlue}, allWithPrefix="qcd_py8")
            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen}, allWithPrefix="v12_g_jets_py6")
            smSources.append("qcd_py8")
            smSources.append("g_jets_py6_v12")

        def mg(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_mg", "color":r.kBlue}, allWithPrefix="v12_qcd_mg")
            org.mergeSamples(targetSpec = {"name":"g_jets_mg", "color":r.kGreen}, allWithPrefix="v12_g_jets_mg")
            smSources.append("qcd_mg_v12")
            smSources.append("g_jets_mg_v12")

        ewkSources = ["tt_tauola_mg", "zinv_jets_mg", "w_jets_mg"] #note: include DY samples
        smSources = copy.deepcopy(ewkSources)
        for i in range(len(smSources)) :
            smSources[i] = smSources[i]+(self.skimString if hasattr(self,"skimString") else "")

        lineWidth = 3
        goptions = "hist"
        if "pythia8"  in org.tag : py8(org, smSources)
        if "madgraph" in org.tag : mg (org, smSources)
        if "pythia6"  in org.tag :
            if not self.ra1Cosmetics() :
                org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
                smSources.append("qcd_py6")
            else :
                org.mergeSamples(targetSpec = {"name":"QCD Multijet", "color":r.kGreen+3, "markerStyle":1, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="qcd_py6")

        #org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Nov4")
        org.mergeSamples(targetSpec = {"name":"2011 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="HT.Run2011A")

        if not self.ra1Cosmetics() : 
            org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)        
        else : #Henning's requests
            org.mergeSamples(targetSpec = {"name":"t#bar{t}, W, Z + Jets", "color":r.kBlue, "markerStyle":1, "lineWidth":lineWidth, "goptions":goptions}, sources = ewkSources)
            org.mergeSamples(targetSpec = {"name":"Standard Model ", "color":r.kAzure+6, "markerStyle":1, "lineWidth":lineWidth, "goptions":goptions}, sources = ["QCD Multijet", "t#bar{t}, W, Z + Jets"], keepSources = True)
            org.mergeSamples(targetSpec = {"name":"LM1", "color":r.kRed,     "lineStyle":9, "markerStyle":1, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="lm1")
            org.mergeSamples(targetSpec = {"name":"LM6", "color":r.kMagenta, "lineStyle":2, "markerStyle":1, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="lm6")

    def conclude(self, conf) :
        org = self.organizer(conf)
        ##for skimming only
        #utils.printSkimResults(org)            

        self.mergeSamples(org)
        org.scale() if not self.parameters()["tanBeta"] else org.scale(100.0)
        
        #self.makeStandardPlots(org)
        self.makeIndividualPlots(org)

    def makeStandardPlots(self, org) :
        #plot
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             samplesForRatios = ("2011 Data","standard_model" if not self.ra1Cosmetics() else "Standard Model "),
                             sampleLabelsForRatios = ("data","s.m."),
                             #samplesForRatios = ("calo_325_scaled.xcak5JetnJetsWeightPat", "calo_325_scaled"),
                             #sampleLabelsForRatios = ("3jet","Njet"),
                             showStatBox = not self.ra1Cosmetics(),
                             #whiteList = ["lowestUnPrescaledTrigger"],
                             #doLog = False,
                             #compactOutput = True,
                             #noSci = True,
                             linYAfter = ("variableGreaterFilter", "xcak5JetAlphaTEtPat>=0.550 "),
                             pegMinimum = 0.1,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             )
        pl.plotAll()
        #self.makeEfficiencyPlots(org, tag, sampleName = "LM1")

    def makeIndividualPlots(self, org) :
        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             showStatBox = False,
                             doLog = True,
                             pegMinimum = 0.1,                             
                             anMode = True,
                             )
        pl.individualPlots(plotSpecs = [{"plotName":"xcak5JetAlphaTRoughPat",
                                         "stepName" :"alphaHistogrammer",
                                         "stepDesc" :"xcak5JetPat",
                                         "newTitle":";#alpha_{T};events / bin",
                                         "legendCoords": (0.55, 0.60, 0.85, 0.90),
                                         "stampCoords": (0.75, 0.55)
                                         },
                                        {"plotName":"jetMultiplicity",
                                         "stepName":"singleJetHistogrammer",
                                         "stepDesc":"xcak5JetPat through index 2",
                                         "newTitle":";N_{jets};events / bin",
                                         "legendCoords": (0.7, 0.7, 0.92, 0.92),
                                         "stampCoords": (0.5, 0.28),
                                         },
                                        {"plotName":"xcak5JetHtPat",
                                         "stepName":"cleanJetHtMhtHistogrammer",
                                         "stepDesc":"xcak5JetPat",
                                         "newTitle":";H_{T} (GeV);events / bin",
                                         "legendCoords": (0.6, 0.60, 0.92, 0.92),
                                         "stampCoords": (0.45, 0.88)
                                        },
                                        ],
                           newSampleNames = None,
                           #newSampleNames = {"qcd_mg_nVtx": "Madgraph QCD",
                           #                  "g_jets_mg_nVtx": "Madgraph #gamma + jets",
                           #                  "2011 Data": "Data",
                           #                  "standard_model_nVtx": "Standard Model",
                           #                  },
                           preliminary = True,
                           )


    def makeEfficiencyPlots(self, org, tag, sampleName) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        def numerAndDenom(org, var) :
            d = {}
            for selection in org.selections :
                if selection.name!= "passFilter" : continue
                if   "htLabel1" in selection.title : label = "before"
                elif "htLabel2" in selection.title : label = "after"
                else : continue
                if var in selection :
                    d[label] = selection[var][sampleIndex(org, sampleName)].Clone(label)
                
            return d

        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)
        canvas.SetTickx()
        canvas.SetTicky()
        psFileName = "%s.ps"%tag
        canvas.Print(psFileName+"[","Lanscape")

        assert len(self.parameters()["objects"])==1
        for key,value in self.parameters()["objects"].iteritems() :
            jet = value["jet"]

        for variable in ["%sSumEt%s"%jet] :
            histos = numerAndDenom(org, variable)
            if "before" not in histos or "after" not in histos : continue
            result = histos["after"].Clone(variable)
            result.Scale(1.0/histos["before"].Integral(0, histos["before"].GetNbinsX()+1))
            result.SetMarkerStyle(20)
            result.SetStats(False)
            if result.ClassName()[2]=="1" :
                #result.GetYaxis().SetRangeUser(0.0,1.0)
                result.GetYaxis().SetTitle("efficiency")
                result.Draw()
            else :
                #result.GetZaxis().SetRangeUser(0.0,1.0)
                result.GetZaxis().SetTitle("efficiency")
                result.Draw("colz")
            canvas.Print(psFileName,"Lanscape")

        canvas.Print(psFileName+"]","Lanscape")                
        os.system("ps2pdf "+psFileName)
        os.remove(psFileName)

