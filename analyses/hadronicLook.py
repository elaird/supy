#!/usr/bin/env python

import copy,os
import analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class hadronicLook(analysis.analysis) :
    def parameters(self) :
        objects = {}
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
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)),  ("3",(3,3)) ]       [0:1] ),
                 "mcSoup" :           dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] ),
                 "etRatherThanPt" : [True,False][0],
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "highPtThreshold" : 50.0,
                 "highPtName" : "highPt",
                 "tanBeta" : [None, 3, 10, 50][0],
                 "thresholds": dict( [("275",        (275.0, 325.0, 100.0, 50.0)),#0
                                      ("325",        (325.0, 375.0, 100.0, 50.0)),#1
                                      ("375",        (375.0, None,  100.0, 50.0)),#2
                                      ("275_scaled", (275.0, 325.0,  73.3, 36.7)),#3
                                      ("325_scaled", (325.0, 375.0,  86.7, 43.3)),#4
                                      ][2:3] ),
                 #required to be a sorted tuple with length>1
                 #"triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"), #2010
                 #"triggerList": ("HLT_HT150_v2","HLT_HT150_v3","HLT_HT160_v2","HLT_HT200_v2","HLT_HT200_v3","HLT_HT240_v2","HLT_HT250_v2","HLT_HT250_v3","HLT_HT260_v2",
                 #                "HLT_HT300_v2","HLT_HT300_v3","HLT_HT300_v4","HLT_HT350_v2","HLT_HT350_v3","HLT_HT360_v2","HLT_HT400_v2","HLT_HT400_v3","HLT_HT440_v2",
                 #                "HLT_HT450_v2","HLT_HT450_v3","HLT_HT500_v2","HLT_HT500_v3","HLT_HT520_v2","HLT_HT550_v2","HLT_HT550_v3")#2011 HT mania
                 "triggerList": ("HLT_HT250_MHT60_v2","HLT_HT250_MHT60_v3","HLT_HT260_MHT60_v2","HLT_HT300_MHT75_v2","HLT_HT300_MHT75_v3","HLT_HT300_MHT75_v4"),#2011 epoch 2
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
            steps.Trigger.lowestUnPrescaledTrigger(),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            
            steps.Trigger.physicsDeclared(),
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
            steps.Other.variablePtGreaterFilter(80.0,"%sSumP4%s"%_jet,"GeV"),
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
            steps.Other.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x["DeltaPhiStar"]'),
            steps.Other.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.Other.passFilter("kinematicPlots1"),
            
            steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            steps.Jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            steps.Jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),
            
            #signal selection
            #steps.Other.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.Other.variableGreaterFilter(0.55,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
            #]), #end cutSorter
            
            steps.Other.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            steps.Other.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.Other.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x["DeltaPhiStar"]'),
            steps.Other.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            #steps.Other.skimmer(),
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
            jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-163869_7TeV_PromptReco_Collisions11_JSON.txt", acceptFutureRuns = False) #193/pb
            out = []
            out += specify(names = "HT.Run2011A-PromptReco-v1.AOD.Arlo",     weights = jw, overrideLumi =  5.07)
            #out += specify(names = "HT.Run2011A-PromptReco-v1.AOD.Zoe",      weights = jw, overrideLumi =  0.0)
            out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Arlo",     weights = jw, overrideLumi = 10.6 )
            out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Arlo2",    weights = jw, overrideLumi = 84.6)
            out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Robin1",   weights = jw, overrideLumi = 80.7)
            out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Zoe1",     weights = jw, overrideLumi = 2.34)
            out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Zoe2",     weights = jw, overrideLumi = 5.78)

            #out += specify(names = "darrens_event")
            #out += specify(names = "calo_325_scaled")
            #w = calculables.Jet.nJetsWeight(jets = params["objects"]["jet"], nJets = [3])
            #out += specify(names = "calo_325_scaled", weights = w, color = r.kRed)

            #out += specify(names = "qcd_py6_275")
            #out += specify(names = "qcd_py6_325")
            #out += specify(names = "qcd_py6_375")
            
            #"HT250_skim_calo",
            #"HT300_skim_calo",
            #"bryn_skim_calo",
            #out += specify(names = "HT350_skim_calo")
            #out += specify(names = "hbhe_noise_skim_calo")
            
            #"Nov4_MJ_skim","Nov4_J_skim","Nov4_J_skim2","Nov4_JM_skim","Nov4_JMT_skim","Nov4_JMT_skim2",
            #, #nFilesMax = 4, nEventsMax = 2000)
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

    def mergeSamples(self, org, tag) :
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
        if "pythia8"  in tag : py8(org, smSources)
        if "madgraph" in tag : mg (org, smSources)
        if "pythia6"  in tag :
            if not self.ra1Cosmetics() :
                org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
                smSources.append("qcd_py6")
            else :
                org.mergeSamples(targetSpec = {"name":"QCD Multijet", "color":r.kGreen+3, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="qcd_py6")

        #org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Nov4")
        org.mergeSamples(targetSpec = {"name":"2011 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="HT.Run2011A")

        if not self.ra1Cosmetics() : 
            org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)        
        else : #Henning's requests
            org.mergeSamples(targetSpec = {"name":"t#bar{t}, W, Z + Jets", "color":r.kBlue, "lineWidth":lineWidth, "goptions":goptions}, sources = ewkSources)
            org.mergeSamples(targetSpec = {"name":"Standard Model ", "color":r.kCyan, "lineWidth":lineWidth, "goptions":goptions}, sources = ["QCD Multijet", "t#bar{t}, W, Z + Jets"], keepSources = True)
            org.mergeSamples(targetSpec = {"name":"LM1", "color":r.kMagenta, "lineStyle":2, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="lm1")
            org.mergeSamples(targetSpec = {"name":"LM6", "color":r.kRed, "lineStyle":10, "lineWidth":lineWidth, "goptions":goptions}, allWithPrefix="lm6")

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            ##for skimming only
            #org = organizer.organizer( self.sampleSpecs(tag) )
            #utils.printSkimResults(org)            
            
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            org.scale() if not self.parameters()["tanBeta"] else org.scale(100.0)
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
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

