#!/usr/bin/env python

import os,copy
import analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class photonLook(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                                             [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets"]
        objects["caloAK5Jet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,    ]))
        #objects["pfAK5Jet_recoLepPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","Pat"),("electron","Pat"),("photon","Pat"),  "PF"  ,    True ,    ]))
        #objects["pfAK5JetLep_recoPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,    ]))

        thresholds = {}
        fields =                                    ["jetPtMin","jet1PtMin","jet2PtMin","htLower","htUpper","mht","applyAlphaTCut","applyTrigger","photonPt","genPhotonPtMin"]
        thresholds["signal"]     = dict(zip(fields, [   50.0,       100.0,    100.0,      350.0,    None,   140.0,      True,           True,        100.0,         110.0    ]))
        #thresholds["relaxed"]    = dict(zip(fields, [   50.0,        50.0,     50.0,      250.0,   350.0,   140.0,      True,           True,        100.0,         110.0    ]))
        ##thresholds["HT_250_300"] = dict(zip(fields, [   35.9,        72.7,     72.7,      250.0,   300.0, , 100.0,      True,           True,         80.0,          90.0    ]))
        ##thresholds["HT_275_300"] = dict(zip(fields, [   39.3,        79.5,     79.5,      275.0,   300.0, , 110.0,      True,           True,         80.0,          90.0    ]))
        ##thresholds["HT_300_350"] = dict(zip(fields, [   42.9,        85.7,     85.7,      300.0,   350.0, , 120.0,      True,           True,         80.0,          90.0    ]))

        return { "objects": objects,
                 "thresholds": thresholds,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 "photonId" :         dict([ ("photonLoose","photonIDLooseFromTwikiPat"),             #0
                                             ("photonTight","photonIDTightFromTwikiPat"),             #1

                                             ("photonTrkIsoRelaxed","photonIDTrkIsoRelaxedPat"),      #2
                                             ("photonTrkIsoSideband","photonIDTrkIsoSideBandPat"),    #3

                                             ("photonIsoSideband","photonIDIsoSideBandPat"),          #4
                                             ("photonIsoRelaxed","photonIDIsoRelaxedPat"),            #5
                                             ("photonNoIsoReq","photonIDNoIsoReqPat"),                #6
                                             
                                             ("photonEGM-10-006-Loose","photonIDEGM_10_006_LoosePat"),#7
                                             ("photonEGM-10-006-Tight","photonIDEGM_10_006_TightPat"),#8

                                             ("photonAN-10-268",   "photonIDAnalysisNote_10_268Pat")]  [8:9] ),
                 "zMode" :            dict([ ("zMode",True), ("",False) ]                              [1:2] ),
                 "jetId" :  ["JetIDloose","JetIDtight"]            [0],
                 "etRatherThanPt" : [True,False]                   [0],
                 "lowPtThreshold": 30.0,
                 "lowPtName":"lowPt",
                 #required to be a sorted tuple with length>1
                 #"triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"), #2010
                 #"triggerList": ("HLT_HT160_v2","HLT_HT240_v2","HLT_HT260_v2","HLT_HT350_v2","HLT_HT360_v2"),#2011 epoch 0
                 "triggerList": ("HLT_Photon75_CaloIdVL_v1","HLT_Photon75_CaloIdVL_IsoL_v1","HLT_Photon75_CaloIdVL_v2","HLT_Photon75_CaloIdVL_IsoL_v2"),#2011 epoch 1
                 }

    def listOfCalculables(self, params) :
        obj = params["objects"]
        _etRatherThanPt = params["etRatherThanPt"]
        _jetPtMin = params["thresholds"]["jetPtMin"]

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
                 calculables.Jet.Indices( obj["jet"], _jetPtMin,      etaMax = 3.0, flagName = params["jetId"]),
                 calculables.Jet.Indices( obj["jet"], params["lowPtThreshold"], etaMax = 3.0, flagName = params["jetId"], extraName = params["lowPtName"]),
                 calculables.Muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
                 calculables.Photon.Indices(obj["photon"], ptMin = 25, flagName = params["photonId"]),

                 calculables.Gen.genIndices( pdgs = [22], label = "Status3Photon", status = [3]),
                 calculables.Gen.genMinDeltaRPhotonOther( label = "Status3Photon"),

                 calculables.Gen.genIndices( pdgs = [22], label = "Status1Photon", status = [1]),
                 calculables.Gen.genIsolations(label = "Status1Photon", coneSize = 0.4),
                 calculables.Gen.genPhotonCategory(label = "Status1Photon"),

                 calculables.Photon.minDeltaRToJet(obj["photon"], obj["jet"]),
                 
                 calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
                 calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5)
                 ] \
                 + [ calculables.Jet.SumP4(obj["jet"]),
                     calculables.Jet.SumP4(obj["jet"], extraName = params["lowPtName"]),
                     calculables.Jet.DeltaPhiStar(obj["jet"], extraName = ""),
                     calculables.Jet.DeltaPhiStar(obj["jet"], extraName = params["lowPtName"]),
                     calculables.Jet.DeltaPseudoJet(obj["jet"], _etRatherThanPt),
                     calculables.Jet.AlphaTWithPhoton1PtRatherThanMht(obj["jet"], photons = obj["photon"], etRatherThanPt = _etRatherThanPt),
                     calculables.Jet.AlphaT(obj["jet"], _etRatherThanPt),
                     calculables.Jet.AlphaTMet(obj["jet"], _etRatherThanPt, obj["met"]),
                     calculables.Jet.MhtOverMet(obj["jet"], met = "%sPlus%s%s"%(obj["met"], obj["photon"][0], obj["photon"][1])),
                     calculables.Photon.metPlusPhotons(met = obj["met"], photons = obj["photon"]),
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

        outList=[
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Jet.jetEtaSelector(_jet, 2.5, 0),
            ]

        if params["thresholds"]["jet1PtMin"]!=None : outList+=[steps.Jet.jetPtSelector(_jet, params["thresholds"]["jet1PtMin"], 0)]
        if params["thresholds"]["jet2PtMin"]!=None : outList+=[steps.Jet.jetPtSelector(_jet, params["thresholds"]["jet2PtMin"], 1)]
        if params["thresholds"]["applyTrigger"]    : outList+=[steps.Trigger.lowestUnPrescaledTrigger()]

        outList+=[
            steps.Other.vertexRequirementFilter(),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.Trigger.physicsDeclared(),
            steps.Other.monsterEventFilter(),
            steps.Other.hbheNoiseFilter(),
            steps.Trigger.hltPrescaleHistogrammer(params["triggerList"]),            
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            #steps.Other.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),
            ]

        if params["thresholds"]["htLower"]!=None : outList+=[steps.Other.variableGreaterFilter(params["thresholds"]["htLower"],"%sSumEt%s"%_jet, suffix = "GeV")]
        if params["thresholds"]["htUpper"]!=None : outList+=[steps.Other.variableLessFilter   (params["thresholds"]["htUpper"],"%sSumEt%s"%_jet, suffix = "GeV")]

        outList+=[
            #bad-jet, electron, muon, vetoes
            steps.Other.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.Other.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.Other.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            steps.Other.multiplicityFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0),
            steps.Jet.uniquelyMatchedNonisoMuons(_jet),
            steps.Other.multiplicityFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1]),
            #steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            ]
        if not params["zMode"] :
            outList+=[
                steps.Other.passFilter("photonEfficiencyPlots1"),
                steps.Gen.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                                                etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),
                
                steps.Photon.photonPtSelector(_photon, params["thresholds"]["photonPt"], 0),
                steps.Photon.photonEtaSelector(_photon, 1.45, 0),
                steps.Photon.photonDeltaRGreaterSelector(jets = _jet, photons = _photon, minDeltaR = 1.0, photonIndex = 0),
                
                steps.Other.multiplicityFilter("%sIndices%s"%_photon, nMin = 1, nMax = 1),

                steps.Other.passFilter("photonEfficiencyPlots2"),
                steps.Gen.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                                                etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),                                            
                ]
        else :
            outList+=[
                steps.Other.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
                ]

        outList+=[
            #many plots
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots1"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),
            #steps.Other.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            #steps.Other.vertexHistogrammer(),
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
            
            steps.Other.variablePtGreaterFilter(params["thresholds"]["mht"],"%sSumP4%s"%_jet,"GeV"),

            steps.Jet.alphaHistogrammer(_jet, deltaPhiStarExtraName = "", etRatherThanPt = _etRatherThanPt),            
            #steps.Other.histogrammer("%sAlphaTEt%s"%_jet, 4, 0.0, 0.55*4, title=";#alpha_{T};events / bin"),
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots2"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),
            ]
        if params["thresholds"]["applyAlphaTCut"] :
            outList+=[
                steps.Other.variableGreaterFilter(0.55,"%sAlphaTEt%s"%_jet),
            ]
        outList+=[
            steps.Jet.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),            
            steps.Other.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.Other.passFilter("singlePhotonPlots3"),
            steps.Photon.singlePhotonHistogrammer(_photon, _jet),

            steps.Other.passFilter("purityPlots2"),
            steps.Gen.photonPurityPlots("Status1Photon", _jet, _photon),
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),

            #steps.Other.histogrammer("%sSumEt%s"%_jet, 12, 250, 550, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),
            #steps.Other.variableGreaterFilter(450.0, "%sSumEt%s"%_jet, suffix = "GeV"),
        
            steps.Other.histogrammer("%sMht%sOver%s" %(_jet[0], _jet[1], _met+"Plus%s%s"%_photon), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0], _jet[1], _met+"Plus%s%s"%_photon)),
            steps.Other.variableLessFilter(1.25,"%sMht%sOver%s" %(_jet[0], _jet[1], _met+"Plus%s%s"%_photon)),
            steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
        
            #steps.Gen.genMotherHistogrammer("genIndicesPhoton", specialPtThreshold = 100.0),
            
            #steps.Other.skimmer(),
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
            #                          #deltaPhiStarExtraName = params["lowPtName"],
            #                          #deltaPhiStarExtraName = "%s%s"%("","PlusPhotons"),                            
            #                          ),
            
            ]

        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.photon]

    def listOfSamples(self,params) :
        from samples import specify

        #2010
        #data = specify(names = ["Nov4_MJ_noIsoReqSkim",
        #                        "Nov4_J_noIsoReqSkim",
        #                        "Nov4_J2_noIsoReqSkim",
        #                        "Nov4_JM_noIsoReqSkim",
        #                        "Nov4_JMT_noIsoReqSkim",
        #                        "Nov4_JMT2_noIsoReqSkim",
        #                        ])
        #
        #data = specify(names = ["Run2010A_JMT_skim_noIsoReqSkim",
        #                        "Run2010A_JM_skim_noIsoReqSkim",
        #                        "Run2010B_J_skim_noIsoReqSkim",
        #                        "Run2010B_J_skim2_noIsoReqSkim",
        #                        "Run2010B_MJ_skim_noIsoReqSkim",
        #                        "Run2010B_MJ_skim2_noIsoReqSkim",
        #                        "Run2010B_MJ_skim3_noIsoReqSkim",
        #                        "Run2010B_MJ_skim4_noIsoReqSkim",
        #                        #"Run2010B_MJ_skim5_noIsoReqSkim",
        #                        ])
        #
        #qcd_mg = specify(names = [#"v12_qcd_mg_ht_50_100_noIsoReqSkim",
        #                          "v12_qcd_mg_ht_100_250_noIsoReqSkim",
        #                          "v12_qcd_mg_ht_250_500_noIsoReqSkim",
        #                          "v12_qcd_mg_ht_500_1000_noIsoReqSkim",
        #                          "v12_qcd_mg_ht_1000_inf_noIsoReqSkim",
        #                          ])
        #
        #g_jets_mg = specify(names = ["v12_g_jets_mg_pt40_100_noIsoReqSkim",
        #                             "v12_g_jets_mg_pt100_200_noIsoReqSkim",
        #                             "v12_g_jets_mg_pt200_noIsoReqSkim"
        #                             ])

        #2011
        #data = specify(names = ["HT.Run2011A-PromptReco-v1.AOD.Henning_noIsoReqSkim", "HT.Run2011A-PromptReco-v1.AOD.Georgia_noIsoReqSkim"])
        data = specify(names = ["Photon.Run2011A-PromptReco-v1.AOD.Henning1_noIsoReqSkim", "Photon.Run2011A-PromptReco-v1.AOD.Henning2_noIsoReqSkim"])

        eL = 2000.0
        l = ["100", "250", "500", "1000", "inf"]
        qcd_mg = specify(effectiveLumi = eL, color = r.kBlue, names = ["qcd_mg_ht_%s_%s_noIsoReqSkim"%(a,b) for a,b in zip(l[:-1], l[1:])])
        l = ["40", "100", "200", "inf"]
        g_jets_mg = specify(effectiveLumi = eL, color = r.kGreen, names = ["g_jets_mg_ht_%s_%s_noIsoReqSkim"%(a,b) for a,b in zip(l[:-1], l[1:])])

        ttbar_mg = specify(effectiveLumi = eL, color = r.kOrange, names = ["tt_tauola_mg"])
        ewk_mg = specify(effectiveLumi = eL, color = r.kYellow-3, names = ["z_jets_mg"]) + specify(effectiveLumi = eL, color = 28, names = ["w_jets_mg"])
        zinv_mg = specify(effectiveLumi = eL, color = r.kMagenta, names = ["zinv_jets_mg"])

        outList = []

        if not params["zMode"] :
            outList += qcd_mg
            outList += g_jets_mg
            outList += data
            #outList += ewk_mg
            #outList += ttbar_mg
        else :
            outList += zinv_mg
            
        return outList

    def mergeSamples(self, org, tag) :
        def go(org, outName, inPrefix, color, markerStyle = 1) :
            org.mergeSamples(targetSpec = {"name":outName, "color":color, "markerStyle":markerStyle}, allWithPrefix = inPrefix)
            return [outName]

        smSources = []
        ewkSources = ["z_inv_mg", "z_jets_mg", "w_jets_mg"]
        #smSources += ewkSources

        smSources += go(org, outName = "qcd_mg",     inPrefix = "qcd_mg",     color = r.kBlue )
        smSources += go(org, outName = "g_jets_mg",  inPrefix = "g_jets_mg",  color = r.kGreen)
        
        #org.mergeSamples(targetSpec = {"name":"MG QCD+G", "color":r.kGreen}, sources = ["qcd_mg","g_jets_mg"])
        #org.mergeSamples(targetSpec = {"name":"MG TT+EWK", "color":r.kOrange}, sources = ewkSources])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3, "markerStyle":1}, sources = smSources, keepSources = True)
        org.mergeSamples(targetSpec = {"name":"2011 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "Photon.Run2011")
            
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            ##for skimming only
            #org = organizer.organizer( self.sampleSpecs(tag) )
            #utils.printSkimResults(org)            
            
            #organize
            org = organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)

            if "zMode" in tag :
                org.scale(34.7255)
                print "WARNING: HARD-CODED LUMI FOR Z MODE!"
            else :
                org.scale()
                
            self.makeStandardPlots(org, tag)
            #self.makeIndividualPlots(org, tag)
            #self.makePurityPlots(org, tag)
            #self.makeEfficiencyPlots(org, tag)
        #self.makeMultiModePlots(34.7255)

    def makeStandardPlots(self, org, tag) :
        #plot all
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(tag),
                             samplesForRatios = ("2011 Data","standard_model"),
                             sampleLabelsForRatios = ("data","s.m."),
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
                             doLog = False,
                             showStatBox = False,
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
        pl.individualPlots(plotSpecs = [{"plotName":"xcak5JetAlphaTFewBinsPat",
                                         "selName" :"variablePtGreaterFilter",
                                         "selDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                                         "newTitle":";#alpha_{T};events / bin / 35 pb^{-1}"},
                                        
                                        #{"plotName":"xcak5JetAlphaTRoughPat",
                                        # "selName" :"variablePtGreaterFilter",
                                        # "selDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                                        # "newTitle":";#alpha_{T};events / bin / 35 pb^{-1}"},
                                        
                                        {"plotName":"xcak5JetIndicesPat",
                                         "selName" :"variablePtGreaterFilter",
                                         "selDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                                         "newTitle":";N_{jets};events / bin / 35 pb^{-1}"},
                                        
                                        #{"plotName":"photonPat1MinDRToJet",
                                        # "selName" :"passFilter",
                                        # "selDesc" :"singlePhotonPlots2",
                                        # "newTitle":";#DeltaR(photon, nearest jet);events / bin / 35 pb^{-1}",
                                        # "reBinFactor":3},
                                        #
                                        #{"plotName":"photonPat1SeedTime",
                                        # "selName" :"passFilter",
                                        # "selDesc" :"singlePhotonPlots2",
                                        # "newTitle":";time of photon seed crystal hit (ns);events / bin / 35 pb^{-1}",
                                        # "sampleWhiteList": ["2010 Data"]},
                                        #
                                        #{"plotName":"photonPat1sigmaIetaIetaBarrel",
                                        # "selName" :"passFilter",
                                        # "selDesc" :"singlePhotonPlots2",
                                        # "newTitle":";#sigma_{i#eta i#eta};events / bin / 35 pb^{-1}"},
                                        
                                        #{"plotName":"photonPat1combinedIsolation",
                                        # "selName" :"passFilter",
                                        # "selDesc" :"singlePhotonPlots2",
                                        # "onlyDumpToFile":True},

                                        ],
                           newSampleNames = {"qcd_mg_v12": "Madgraph QCD",
                                             "g_jets_mg_v12": "Madgraph #gamma + jets",
                                             "2010 Data": "Data",
                                             "standard_model": "Standard Model",
                                             },
                           preliminary = False,
                           )

            
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
