#!/usr/bin/env python

import os,copy
import analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class photonLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                                             [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets"]
        objects["caloAK5Jet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,    ]))
        #objects["pfAK5Jet_recoLepPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","Pat"),("electron","Pat"),("photon","Pat"),  "PF"  ,    True ,    ]))
        #objects["pfAK5JetLep_recoPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,    ]))

        thresholds = {}
        fields =                                    ["jetPtMin","jet1PtMin","jet2PtMin","htLower","htUpper","mht","applyAlphaTCut","applyTrigger","photonPt","genPhotonPtMin"]
        #thresholds["signal"]     = dict(zip(fields, [   50.0,       100.0,    100.0,      350.0,    None,   140.0,      True,           True,        100.0,         110.0    ]))
        thresholds["relaxed"]    = dict(zip(fields, [   50.0,        50.0,     50.0,      250.0,   350.0,   140.0,      True,           True,        100.0,         110.0    ]))
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

                                             ("photonAN-10-268",   "photonIDAnalysisNote_10_268Pat")]  [6:7] ),
                 "zMode" :            dict([ ("zMode",True), ("",False) ]                              [1:2] ),
                 "jetId" :  ["JetIDloose","JetIDtight"]            [0],
                 "etRatherThanPt" : [True,False]                   [0],
                 "lowPtThreshold": 30.0,
                 "lowPtName":"lowPt",
                 "triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"),#required to be a sorted tuple                 
                 }

    def listOfCalculables(self, params) :
        obj = params["objects"]
        _etRatherThanPt = params["etRatherThanPt"]
        _jetPtMin = params["thresholds"]["jetPtMin"]

        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.jet,[obj["jet"]]) +\
               calculables.fromCollections(calculables.muon,[obj["muon"]]) +\
               calculables.fromCollections(calculables.electron,[obj["electron"]]) +\
               calculables.fromCollections(calculables.photon,[obj["photon"]]) +\
               [ calculables.xclean.xcJet( obj["jet"],
                                           gamma = obj["photon"],
                                           gammaDR = 0.5,
                                           muon = obj["muon"],
                                           muonDR = 0.5,
                                           correctForMuons = not obj["muonsInJets"],
                                           electron = obj["electron"], electronDR = 0.5
                                           ),
                 calculables.jet.Indices( obj["jet"], _jetPtMin,      etaMax = 3.0, flagName = params["jetId"]),
                 calculables.jet.Indices( obj["jet"], params["lowPtThreshold"], etaMax = 3.0, flagName = params["jetId"], extraName = params["lowPtName"]),
                 calculables.muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
                 calculables.photon.photonIndicesPat(  ptMin = 25, flagName = params["photonId"]),

                 calculables.gen.genIndices( pdgs = [22], label = "Status3Photon", status = [3]),
                 calculables.gen.genMinDeltaRPhotonOther( label = "Status3Photon"),

                 calculables.gen.genIndices( pdgs = [22], label = "Status1Photon", status = [1]),
                 calculables.gen.genIsolations(label = "Status1Photon", coneSize = 0.4),
                 calculables.gen.genPhotonCategory(label = "Status1Photon"),

                 calculables.photon.minDeltaRToJet(obj["photon"], obj["jet"]),
                 
                 calculables.xclean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
                 calculables.xclean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5)
                 ] \
                 + [ calculables.jet.SumP4(obj["jet"]),
                     calculables.jet.SumP4(obj["jet"], extraName = params["lowPtName"]),
                     #calculables.jet.SumP4PlusPhotons(obj["jet"], extraName = "", photon = obj["photon"]),
                     calculables.jet.DeltaPhiStar(obj["jet"], extraName = ""),
                     calculables.jet.DeltaPhiStar(obj["jet"], extraName = params["lowPtName"]),
                     #calculables.jet.DeltaPhiStarIncludingPhotons(obj["jet"], photons = obj["photon"], extraName = ""),
                     calculables.jet.DeltaPseudoJet(obj["jet"], _etRatherThanPt),
                     calculables.jet.AlphaTWithPhoton1PtRatherThanMht(obj["jet"], photons = obj["photon"], etRatherThanPt = _etRatherThanPt),
                     calculables.jet.AlphaT(obj["jet"], _etRatherThanPt),
                     calculables.jet.AlphaTMet(obj["jet"], _etRatherThanPt, obj["met"]),
                     calculables.jet.metPlusPhoton(met = "metP4PF", photons = obj["photon"], photonIndex = 0),
                     calculables.jet.mhtIncludingPhotonsOverMet(obj["jet"], "metP4PF", _etRatherThanPt),
                     calculables.other.vertexID(),
                     calculables.other.vertexIndices(),
                     calculables.jet.deadEcalDR(obj["jet"], extraName = params["lowPtName"], minNXtals = 10),
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
        if params["thresholds"]["applyTrigger"]    : outList+=[steps.lowestUnPrescaledTrigger(params["triggerList"])]

        outList+=[
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            #steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),
            ]

        if params["thresholds"]["htLower"]!=None : outList+=[steps.variableGreaterFilter(params["thresholds"]["htLower"],"%sSumEt%s"%_jet, suffix = "GeV")]
        if params["thresholds"]["htUpper"]!=None : outList+=[steps.variableLessFilter   (params["thresholds"]["htUpper"],"%sSumEt%s"%_jet, suffix = "GeV")]

        outList+=[
            #bad-jet, electron, muon, vetoes
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0),
            steps.uniquelyMatchedNonisoMuons(_jet),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1]),
            #steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            ]
        if not params["zMode"] :
            outList+=[
                steps.passFilter("photonEfficiencyPlots1"),
                steps.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                                            etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),
                
                steps.photonPtSelector(_photon, params["thresholds"]["photonPt"], 0),
                steps.photonEtaSelector(_photon, 1.45, 0),
                steps.photonDeltaRGreaterSelector(jets = _jet, photons = _photon, minDeltaR = 1.0, photonIndex = 0),
                
                steps.multiplicityFilter("%sIndices%s"%_photon, nMin = 1, nMax = 1),

                steps.passFilter("photonEfficiencyPlots2"),
                steps.photonEfficiencyPlots(label = "Status1Photon", ptCut = params["thresholds"]["genPhotonPtMin"],
                                            etaCut = 1.4, isoCut = 5.0, deltaRCut = 1.1, jets = _jet, photons = _photon),                                            
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
            steps.histogrammer(("%sAlphaTEt%s"%_jet, "%sAlphaTWithPhoton1PtRatherThanMht%s"%_jet),
                               (25, 25), (0.50, 0.50), (1.0, 1.0), title = ";#alpha_{T};#alpha_{T} using photon p_{T} rather than MHT;events / bin"),
            
            steps.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),
            
            steps.variablePtGreaterFilter(params["thresholds"]["mht"],"%sSumP4%s"%_jet,"GeV"),
            steps.histogrammer("%sAlphaTEt%s"%_jet, 4, 0.0, 0.55*4, title=";#alpha_{T};events / bin"),
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.passFilter("singlePhotonPlots2"),
            steps.singlePhotonHistogrammer(_photon, _jet),
            ]
        if params["thresholds"]["applyAlphaTCut"] :
            outList+=[
                steps.variableGreaterFilter(0.55,"%sAlphaTEt%s"%_jet),
            ]
        outList+=[
            steps.photon1PtOverHtHistogrammer(jets = _jet, photons = _photon, etRatherThanPt = _etRatherThanPt),            
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.passFilter("singlePhotonPlots3"),
            steps.singlePhotonHistogrammer(_photon, _jet),

            steps.passFilter("purityPlots2"),
            steps.photonPurityPlots("Status1Photon", _jet, _photon),
            steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            
            #steps.histogrammer("mhtOverMet", 100, 0.0, 3.0, title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1],_met)),
            #steps.variableLessFilter(1.25,"mhtOverMet"),
            steps.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
        
            ##steps.histogrammer("mhtIncludingPhotonsOverMet", 100, 0.0, 2.0, title = ";MHT [including photon] / PFMET;events / bin"),
            ##steps.deadEcalFilterIncludingPhotons(jets = _jet, extraName = "", photons = _photon, dR = 0.3, dPhiStarCut = 0.5, nXtalThreshold = 5),
            
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
            #                #deltaPhiStarExtraName = params["lowPtName"],
            #                #deltaPhiStarExtraName = "%s%s"%("","PlusPhotons"),                            
            #                ),
            
            ]

        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.photon]

    def listOfSamples(self,params) :
        from samples import specify

        data = [
            specify(name = "Run2010A_JMT_skim_noIsoReqSkim"),
            specify(name = "Run2010A_JM_skim_noIsoReqSkim"),
            specify(name = "Run2010B_J_skim_noIsoReqSkim"),
            specify(name = "Run2010B_J_skim2_noIsoReqSkim"),
            specify(name = "Run2010B_MJ_skim_noIsoReqSkim"),
            specify(name = "Run2010B_MJ_skim2_noIsoReqSkim"),
            specify(name = "Run2010B_MJ_skim3_noIsoReqSkim"),
            specify(name = "Run2010B_MJ_skim4_noIsoReqSkim"),
            specify(name = "Run2010B_MJ_skim5_noIsoReqSkim"),
            
            #specify(name = "Nov4_MJ_noIsoReqSkim"),
            #specify(name = "Nov4_J_noIsoReqSkim"),
            #specify(name = "Nov4_JM_noIsoReqSkim"),
            #specify(name = "Nov4_JMT_noIsoReqSkim"),
            ]

        qcd_mg = [
            #specify(name = "v12_qcd_mg_ht_50_100_noIsoReqSkim"),
            specify(name = "v12_qcd_mg_ht_100_250_noIsoReqSkim"),
            specify(name = "v12_qcd_mg_ht_250_500_noIsoReqSkim"),
            specify(name = "v12_qcd_mg_ht_500_1000_noIsoReqSkim"),
            specify(name = "v12_qcd_mg_ht_1000_inf_noIsoReqSkim"),
            ]

        g_jets_mg = [
            specify(name = "v12_g_jets_mg_pt40_100_noIsoReqSkim"),
            specify(name = "v12_g_jets_mg_pt100_200_noIsoReqSkim"),
            specify(name = "v12_g_jets_mg_pt200_noIsoReqSkim"),
            ]

        qcd_mg_full = [
            specify(name = "v12_qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
            ]

        g_jets_mg_full = [                                               
            specify(name = "v12_g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
            ]

        ttbar_mg_full = [                                                
            specify(name = "tt_tauola_mg_v12",          nFilesMax =  3, color = r.kOrange  ),
            ]

        ewk_mg_full = [                                                     
            specify(name = "z_jets_mg_v12",             nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12",             nFilesMax = -1, color = 28         ),
            ]

        zinv_mg = [specify(name = "z_inv_mg_v12_skim", nFilesMax = -1, color = r.kMagenta )]

        outList = []

        if not params["zMode"] :
            outList += qcd_mg
            outList += g_jets_mg
            outList += data
            #outList += ewk_mg
            #outList += ttbar_mg
        else :
            outList += zinv_mg
            
        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 1000)
        
        return outList

    def mergeSamples(self, org, tag) :
        def go(org, outName, inPrefix, color) :
            org.mergeSamples(targetSpec = {"name":outName, "color":color}, allWithPrefix = inPrefix)
            return [outName]

        smSources = [item for item in ["z_inv_mg_v12", "z_jets_mg_v12", "w_jets_mg_v12"]]

        smSources += go(org, outName = "qcd_mg_v12",     inPrefix = "v12_qcd_mg",     color = r.kBlue )
        smSources += go(org, outName = "g_jets_mg_v12",  inPrefix = "v12_g_jets_mg",  color = r.kGreen)
        
        #org.mergeSamples(targetSpec = {"name":"MG QCD+G", "color":r.kGreen}, sources = ["qcd_mg_v12","g_jets_mg_v12"])
        #org.mergeSamples(targetSpec = {"name":"MG TT+EWK", "color":r.kOrange}, sources = [item for item in ["z_jets_mg_v12", "w_jets_mg_v12", "tt_tauola_mg_v12"]])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)
        org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "Run2010")
            
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
                             samplesForRatios = ("2010 Data","standard_model"),
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
        pl.individualPlots(plotSpecs = [#{"plotName":"xcak5JetAlphaTEtPat",
                                        # "selName" :"variablePtGreaterFilter",
                                        # "selDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                                        # "newTitle":";#alpha_{T};events / bin / 35 pb^{-1}"},
                                        #
                                        #{"plotName":"xcak5JetIndicesPat",
                                        # "selName" :"variablePtGreaterFilter",
                                        # "selDesc" :"xcak5JetSumP4Pat.pt()>=140.0 GeV",
                                        # "newTitle":";N_{jets};events / bin / 35 pb^{-1}"},
                                        #
                                        ##{"plotName":"photonPat1MinDRToJet",
                                        ## "selName" :"passFilter",
                                        ## "selDesc" :"singlePhotonPlots2",
                                        ## "newTitle":";#DeltaR(photon, nearest jet);events / bin / 35 pb^{-1}",
                                        ## "reBinFactor":3},
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
                                        
                                        {"plotName":"photonPat1combinedIsolation",
                                         "selName" :"passFilter",
                                         "selDesc" :"singlePhotonPlots2",
                                         "onlyDumpToFile":True},

                                        ],
                           newSampleNames = {"qcd_mg_v12": "Madgraph QCD",
                                             "g_jets_mg_v12": "Madgraph #gamma + jets",
                                             "2010 Data": "Data",
                                             "standard_model": "Standard Model",
                                             },
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
