#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class muonLook(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                                                [ "jet",            "met",            "muon",        "electron",        "photon",
                                                                  "compJet",    "compMet",
                                                                  "rechit", "muonsInJets", "jetPtMin", "jetId"]
        objects["caloAK5JetMet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"),
                                                                 ("xcak5JetPF","Pat"),"metP4PF",
                                                                 "Calo",     False,         50.0,      "JetIDloose"]))
        
        #objects["pfAK5JetMet_recoLepPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",    ("muon","Pat"),("electron","Pat"),("photon","Pat"),
        #                                                         ("xcak5Jet","Pat"),"metP4AK5TypeII",
        #                                                         "PF",        True,         50.0,      "JetIDtight"]))

        #objects["pfAK5JetMetLep_recoPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",    ("muon","PF"),("electron","PF"), ("photon","Pat"),
        #                                                         None, None,
        #                                                         "PF",        True,         50.0]))
        #objects["caloAK7JetMet_recoLepPhot"] = dict(zip(fields, [("xcak7Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"),
        #                                                         None, None,
        #                                                         "Calo" ,    False,         50.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 "mcSoup" :           dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] ),
                 "etRatherThanPt" : [True,False]        [0],
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"),#required to be a sorted tuple
                 }

    def calcListJet(self, obj, etRatherThanPt, lowPtThreshold, lowPtName) :
        def calcList(jet, met, photon, muon, electron, muonsInJets, jetPtMin, jetIdFlag) :
            outList = [
                calculables.XClean.xcJet(jet,
                                         applyResidualCorrectionsToData = True,
                                         gamma = photon,
                                         gammaDR = 0.5,
                                         muon = muon,
                                         muonDR = 0.5,
                                         correctForMuons = not muonsInJets,
                                         electron = electron,
                                         electronDR = 0.5),
                calculables.Jet.Indices( jet, jetPtMin, etaMax = 3.0, flagName = jetIdFlag),
                calculables.Jet.Indices( jet, lowPtThreshold, etaMax = 3.0, flagName = jetIdFlag, extraName = lowPtName),
                
                calculables.Jet.SumP4(jet),
                calculables.Jet.SumP4(jet, extraName = lowPtName),
                calculables.Jet.DeltaPhiStar(jet, extraName = lowPtName),
                calculables.Jet.DeltaPseudoJet(jet, etRatherThanPt),
                calculables.Jet.AlphaT(jet, etRatherThanPt),
                calculables.Jet.AlphaTMet(jet, etRatherThanPt, met),
                calculables.Jet.MhtOverMet(jet, met),
                calculables.Jet.deadEcalDR(jet, extraName = lowPtName, minNXtals = 10),
                ]
            return outList+calculables.fromCollections(calculables.Jet, [jet])

        outList = calcList(obj["jet"], obj["met"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetPtMin"], obj["jetId"])
        if obj["compJet"]!=None and obj["compMet"]!=None :
            outList += calcList(obj["compJet"], obj["compMet"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetPtMin"], obj["jetId"])
        return outList

    def calcListOther(self, obj, triggers) :
        return [
            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),

            calculables.Muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Other.Mt( obj["muon"], obj["met"]),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.Photon.photonIndicesPat(  ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            #calculables.Photon.photonIndicesPat(  ptMin = 25, flagName = "photonIDTightFromTwikiPat"),
            
            calculables.Vertex.vertexID(),
            calculables.Vertex.vertexIndices(),
            calculables.Other.lowestUnPrescaledTrigger(triggers),
            ]
    
    def listOfCalculables(self, params) :
        obj = params["objects"]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += self.calcListOther(obj, params["triggerList"])
        outList += self.calcListJet(obj, params["etRatherThanPt"], params["lowPtThreshold"], params["lowPtName"])
        return outList
    
    def listOfSteps(self, params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]
        _et = "Et" if _etRatherThanPt else "Pt"

        return [
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Jet.jetPtSelector(_jet, 100.0, 0),
            steps.Jet.jetPtSelector(_jet, 100.0, 1),
            steps.Jet.jetEtaSelector(_jet,2.5,0),
            steps.Trigger.lowestUnPrescaledTrigger(params["triggerList"]),
            steps.Other.vertexRequirementFilter(),
            steps.Trigger.techBitFilter([0],True),
            steps.Trigger.physicsDeclared(),
            steps.Other.monsterEventFilter(),
            #steps.Other.cutSorter([
            steps.Other.hbheNoiseFilter(),
            steps.Trigger.hltPrescaleHistogrammer(params["triggerList"]),
            ]+(
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_electron,          nMax = 0, xlabel = "N electrons") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_muon,              nMin = 1, nMax = 1, xlabel = "N muons") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_photon,            nMax = 0, xlabel = "N photons") +
            steps.Other.multiplicityPlotFilter("%sIndicesOther%s"%_jet,          nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_jet) +
            steps.Other.multiplicityPlotFilter("%sIndicesOther%s"%_muon,         nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_muon) +
            steps.Other.multiplicityPlotFilter("%sIndicesUnmatched%s"%_electron, nMax = 0, xlabel = "N electrons unmatched") +
            steps.Other.multiplicityPlotFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0, xlabel = "N photons unmatched") +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1], xlabel="number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts"%_jet)
            )+[
            #steps.Jet.uniquelyMatchedNonisoMuons(_jet), 
               
            steps.Other.histogrammer("%sSum%s%s"%(_jet[0], _et, _jet[1]), 50, 0, 1500, title = ";H_{T} (GeV) from %s%s %ss;events / bin"%(_jet[0], _jet[1], _et)),
            steps.Other.variableGreaterFilter(350.0,"%sSum%s%s"%(_jet[0], _et, _jet[1]), suffix = "GeV"),
            steps.Other.histogrammer("%sMt%s%s"%(_muon[0],_muon[1],_met), 50, 0, 200, title = ";M_{T} (GeV) of %s%s,%s;events / bin"%(_muon[0],_muon[1],_met)),
            #many plots
            #steps.Trigger.lowestUnPrescaledTriggerHistogrammer(params["triggerList"]),
            steps.Other.passFilter("singleJetPlots1"),
            steps.Jet.singleJetHistogrammer(_jet),
            steps.Other.passFilter("jetSumPlots1"), 
            steps.Jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.Other.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.Other.passFilter("kinematicPlots1"), 
            steps.Jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            steps.Jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),
            
            #signal selection
            steps.Other.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.Other.variableGreaterFilter(0.55,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
            ##]), #end cutSorter
            #steps.Other.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1],_met), 100, 0.0, 3.0, title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1],_met)),
            #steps.Other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1],_met)),
            #steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            #steps.Other.skimmer(),
            #steps.Other.cutBitHistogrammer(self.togglePfJet(_jet), self.togglePfMet(_met)),
            #steps.Print.eventPrinter(),
            #steps.Print.jetPrinter(_jet),
            #steps.Print.particleP4Printer(_muon),
            #steps.Print.particleP4Printer(_photon),
            #steps.Print.recHitPrinter("clusterPF","Ecal"),
            #steps.Print.htMhtPrinter(_jet),
            #steps.Print.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.Gen.genParticlePrinter(minPt=10.0,minStatus=3),
            #       
            #steps.Other.pickEventSpecMaker(),
            #steps.Displayer.displayer(jets = _jet,
            #                          muons = _muon,
            #                          met       = params["objects"]["met"],
            #                          electrons = params["objects"]["electron"],
            #                          photons   = params["objects"]["photon"],                            
            #                          recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                          scale = 400.0,#GeV
            #                          etRatherThanPt = _etRatherThanPt,
            #                          deltaPhiStarExtraName = params["lowPtName"],
            #                          deltaPhiStarCut = 0.5,
            #                          deltaPhiStarDR = 0.3,
            #                          printOtherJetAlgoQuantities = False,
            #                          jetsOtherAlgo = params["objects"]["compJet"],
            #                          metOtherAlgo  = params["objects"]["compMet"],
            #                          markusMode = False,
            #                          ),
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.signalSkim, samples.muon]

    def listOfSamples(self,params) :
        from samples import specify
        data = specify(names = ["Run2010_muonSkim"], markerStyle = 20)
        #qcd_py6 = [
        #    #specify(name = "qcd_py6_pt_0to5"      ),
        #    #specify(name = "qcd_py6_pt_5to15"     ),
        #    #specify(name = "qcd_py6_pt_15to30"    ),
        #    #specify(name = "qcd_py6_pt_30to50"    ),
        #    #specify(name = "qcd_py6_pt_50to80"    ),
        #    specify(name = "qcd_py6_pt_80to120"   ),
        #    specify(name = "qcd_py6_pt_120to170"  ),
        #    specify(name = "qcd_py6_pt_170to300"  ),
        #    specify(name = "qcd_py6_pt_300to470"  ),
        #    specify(name = "qcd_py6_pt_470to600"  ),
        #    specify(name = "qcd_py6_pt_600to800"  ),
        #    specify(name = "qcd_py6_pt_800to1000" ),
        #    specify(name = "qcd_py6_pt_1000to1400"),
        #    specify(name = "qcd_py6_pt_1400to1800"),
        #    specify(name = "qcd_py6_pt_1800"      ),
        #    ]
        #g_jets_py6 = [                                              
        #    specify(name = "v12_g_jets_py6_pt30",       nFilesMax = -1, nEventsMax = 1000000, color = r.kGreen),
        #    specify(name = "v12_g_jets_py6_pt80",       nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
        #    specify(name = "v12_g_jets_py6_pt170",      nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
        #    ]                                                       
        #qcd_py8 = [                                                 
        #  ##specify(name = "qcd_py8_pt0to15",           nFilesMax = -1, color = r.kBlue    ),
        #  ##specify(name = "qcd_py8_pt15to30",          nFilesMax = -1, color = r.kBlue    ),
        #  ##specify(name = "qcd_py8_pt30to50",          nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt50to80",          nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt80to120",         nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt120to170",        nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt170to300",        nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt300to470",        nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt470to600",        nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt600to800",        nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt800to1000",       nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt1000to1400",      nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt1400to1800",      nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "qcd_py8_pt1800",            nFilesMax = -1, color = r.kBlue    ),
        #    ]                                                       
        #qcd_mg = [                                                  
        #    specify(name = "v12_qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "v12_qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "v12_qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "v12_qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
        #    specify(name = "v12_qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
        #    ]                                                       
        #g_jets_mg = [                                               
        #    specify(name = "v12_g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
        #    specify(name = "v12_g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
        #    specify(name = "v12_g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
        #    ]                                                       
        ttbar_mg = specify(names = ["tt_tauola_mg_v12"],          nFilesMax =  3, color = r.kOrange  )
        
        ewk = specify(names = ["w_jets_mg_v12_skim"],        nFilesMax = -1, color = 28)
        #    specify(name = "z_inv_mg_v12_skim",         nFilesMax = -1, color = r.kMagenta ),
        #    specify(name = "z_jets_mg_v12_skim",        nFilesMax = -1, color = r.kYellow-3),
        
        #susy = [                                                    
        #    specify(name = "lm0_v12",                   nFilesMax = -1, color = r.kRed     ),
        #    specify(name = "lm1_v12",                   nFilesMax = -1, color = r.kRed+1   ),
        #    ]                                                   

        outList = []

        self.skimString = ""
        #if params["mcSoup"]=="py6" :
        #    outList+=qcd_py6
        #    outList+=g_jets_py6
        #    
        #if params["mcSoup"]=="py8" :
        #    outList+=qcd_py8
        #    outList+=g_jets_py6#no py8 available
        #    
        #if params["mcSoup"]=="mg":
        #    outList+=qcd_mg
        #    outList+=g_jets_mg
        #
        outList+=data
        outList+=ttbar_mg
        outList+=ewk
        #outList+=susy
        
        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    outList[i] = specify(names = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 3000)[0]

        return outList

    def mergeSamples(self, org, tag) :
        def py6(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen}, allWithPrefix="v12_g_jets_py6")
            smSources.append("qcd_py6")
            smSources.append("g_jets_py6_v12")

        def py8(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_py8", "color":r.kBlue}, allWithPrefix="qcd_py8")
            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen}, allWithPrefix="v12_g_jets_py6")
            smSources.append("qcd_py8")
            smSources.append("g_jets_py6_v12")

        def mg(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_mg_v12", "color":r.kBlue}, allWithPrefix="v12_qcd_mg")
            org.mergeSamples(targetSpec = {"name":"g_jets_mg_v12", "color":r.kGreen}, allWithPrefix="v12_g_jets_mg")
            smSources.append("qcd_mg_v12")
            smSources.append("g_jets_mg_v12")

        smSources = ["tt_tauola_mg_v12", "z_inv_mg_v12_skim", "z_jets_mg_v12_skim", "w_jets_mg_v12_skim"]
        for i in range(len(smSources)) :
            smSources[i] = smSources[i]+self.skimString
            
        if "pythia6"  in tag : py6(org, smSources)
        if "pythia8"  in tag : py8(org, smSources)
        if "madgraph" in tag : mg (org, smSources)
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)
        org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Nov4")

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            ##for skimming only
            #org = organizer.organizer( self.sampleSpecs(tag) )
            #utils.printSkimResults(org)            
            
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            org.scale()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 #samplesForRatios = ("2010 Data","standard_model"),
                                 #sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 #pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()
