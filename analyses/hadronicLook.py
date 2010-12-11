#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class hadronicLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                                                [ "jet",            "met",            "muon",        "electron",        "photon",
                                                                  "compJet",    "compMet",
                                                                  "rechit", "muonsInJets", "jetPtMin", "jetId"]
        objects["caloAK5JetMet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"),
                                                                 ("xcak5JetPF","Pat"),"metP4PF",
                                                                 "Calo",     False,         50.0,      "JetIDloose"]))
        
        objects["pfAK5JetMet_recoLepPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",    ("muon","Pat"),("electron","Pat"),("photon","Pat"),
                                                                 ("xcak5Jet","Pat"),"metP4AK5TypeII",
                                                                 "PF",        True,         50.0,      "JetIDtight"]))

        #objects["pfAK5JetMetLep_recoPhot"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",    ("muon","PF"),("electron","PF"), ("photon","Pat"),
        #                                                         None, None,
        #                                                         "PF",        True,         50.0]))
        #objects["caloAK7JetMet_recoLepPhot"] = dict(zip(fields, [("xcak7Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"),
        #                                                         None, None,
        #                                                         "Calo" ,    False,         50.0]))
        #objects["jptAK5JetMet_recoLepPhot"]  = dict(zip(fields, [("xcak5JetJPT","Pat"), "metP4TC",   ("muon","Pat"),("electron","Pat"),("photon","Pat"),
        #                                                             None, None,
        #                                                             "Calo",      True,         50.0]))

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
                calculables.xclean.xcJet(jet,
                                         applyResidualCorrectionsToData = True,
                                         gamma = photon,
                                         gammaDR = 0.5,
                                         muon = muon,
                                         muonDR = 0.5,
                                         correctForMuons = not muonsInJets,
                                         electron = electron,
                                         electronDR = 0.5),
                calculables.jet.Indices( jet, jetPtMin, etaMax = 3.0, flagName = jetIdFlag),
                calculables.jet.Indices( jet, lowPtThreshold, etaMax = 3.0, flagName = jetIdFlag, extraName = lowPtName),
                
                calculables.jet.SumP4(jet),
                calculables.jet.SumP4(jet, extraName = lowPtName),
                calculables.jet.DeltaPhiStar(jet, extraName = lowPtName),
                calculables.jet.DeltaPseudoJet(jet, etRatherThanPt),
                calculables.jet.AlphaT(jet, etRatherThanPt),
                calculables.jet.AlphaTMet(jet, etRatherThanPt, met),
                calculables.jet.mhtOverMet(jet, met),
                calculables.jet.deadEcalDR(jet, extraName = lowPtName, minNXtals = 10),
                ]
            return outList+calculables.fromCollections(calculables.jet, [jet])

        outList = calcList(obj["jet"], obj["met"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetPtMin"], obj["jetId"])
        if obj["compJet"]!=None and obj["compMet"]!=None :
            outList += calcList(obj["compJet"], obj["compMet"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetPtMin"], obj["jetId"])
        return outList

    def calcListOther(self, obj, triggers) :
        return [
            calculables.xclean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.xclean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),

            calculables.muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.photon.photonIndicesPat(  ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            #calculables.photon.photonIndicesPat(  ptMin = 25, flagName = "photonIDTightFromTwikiPat"),
            
            calculables.other.vertexID(),
            calculables.other.vertexIndices(),
            calculables.other.lowestUnPrescaledTrigger(triggers),
            ]
    
    def listOfCalculables(self, params) :
        obj = params["objects"]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.photon, [obj["photon"]])
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

        return [
            steps.progressPrinter(),
            steps.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.jetPtSelector(_jet, 100.0, 0),
            steps.jetPtSelector(_jet, 100.0, 1),
            steps.jetEtaSelector(_jet,2.5,0),
            steps.lowestUnPrescaledTrigger(params["triggerList"]),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            #steps.cutSorter([
            steps.hbheNoiseFilter(),
            
            steps.hltPrescaleHistogrammer(params["triggerList"]),
            #steps.iterHistogrammer("ecalDeadTowerTrigPrimP4", 256, 0.0, 128.0, title=";E_{T} of ECAL TP in each dead region (GeV);TPs / bin", funcString="lambda x:x.Et()"),
            ]+(
            steps.multiplicityPlotFilter("%sIndices%s"%_electron,          nMax = 0, xlabel = "N electrons") +
            steps.multiplicityPlotFilter("%sIndices%s"%_muon,              nMax = 0, xlabel = "N muons") +
            steps.multiplicityPlotFilter("%sIndices%s"%_photon,            nMax = 0, xlabel = "N photons") +
            steps.multiplicityPlotFilter("%sIndicesOther%s"%_jet,          nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_jet) +
            steps.multiplicityPlotFilter("%sIndicesOther%s"%_muon,         nMax = 0, xlabel = "number of %s%s above p_{T}#semicolon failing ID or #eta"%_muon) +
            steps.multiplicityPlotFilter("%sIndicesUnmatched%s"%_electron, nMax = 0, xlabel = "N electrons unmatched") +
            steps.multiplicityPlotFilter("%sIndicesUnmatched%s"%_photon,   nMax = 0, xlabel = "N photons unmatched") +
            steps.multiplicityPlotFilter("%sIndices%s"%_jet, nMin=params["nJetsMinMax"][0], nMax=params["nJetsMinMax"][1], xlabel="number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts"%_jet)
            )+[
            steps.uniquelyMatchedNonisoMuons(_jet), 
               
            steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s %s_{T}s;events / bin"%(_jet[0],_jet[1],"p" if not _etRatherThanPt else "E")),
            steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            
            #many plots
            steps.lowestUnPrescaledTriggerHistogrammer(params["triggerList"]),
            steps.passFilter("singleJetPlots1"),
            steps.singleJetHistogrammer(_jet),
            steps.passFilter("jetSumPlots1"), 
            steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.passFilter("kinematicPlots1"), 
            steps.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            steps.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),
            
            #signal selection
            #steps.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.variableGreaterFilter(0.55,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
            #]), #end cutSorter
            steps.histogrammer("%sMht%s_Over_%s"%(_jet[0],_jet[1],_met), 100, 0.0, 3.0, title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1],_met)),
            steps.variableLessFilter(1.25,"%sMht%s_Over_%s"%(_jet[0],_jet[1],_met)),
            steps.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            #steps.skimmer(),
            #steps.cutBitHistogrammer(self.togglePfJet(_jet), self.togglePfMet(_met)),
            #steps.eventPrinter(),
            #steps.jetPrinter(_jet),
            #steps.particleP4Printer(_muon),
            #steps.particleP4Printer(_photon),
            #steps.recHitPrinter("clusterPF","Ecal"),
            #steps.htMhtPrinter(_jet),
            #steps.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),
            #       
            #steps.pickEventSpecMaker(),
            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 400.0,#GeV
            #                etRatherThanPt = _etRatherThanPt,
            #                deltaPhiStarExtraName = params["lowPtName"],
            #                deltaPhiStarCut = 0.5,
            #                deltaPhiStarDR = 0.3,
            #                printOtherJetAlgoQuantities = False,
            #                jetsOtherAlgo = params["objects"]["compJet"],
            #                metOtherAlgo  = params["objects"]["compMet"],
            #                markusMode = False,
            #                ),
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet, samples.signalSkim]

    def listOfSamples(self,params) :
        from samples import specify
        data = [
            specify(name = "Nov4_MJ_skim"  ),
            specify(name = "Nov4_J_skim"   ),
            specify(name = "Nov4_J_skim2"  ),
            specify(name = "Nov4_JM_skim"  ),
            specify(name = "Nov4_JMT_skim" ),
            specify(name = "Nov4_JMT_skim2"),
            
          ##specify(name = "2010_data_calo_skim",       nFilesMax = -1, color = r.kBlack   , markerStyle = 20),            
          ##specify(name = "2010_data_pf_skim",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
          ##specify(name = "test",                      nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            ]                                                       
        qcd_py6 = [                                                 
          ##specify(name = "v12_qcd_py6_pt30",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt170",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt300",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt470",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt800",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt1400",        nFilesMax = -1, color = r.kBlue    ),
            ]                                                       
        g_jets_py6 = [                                              
            specify(name = "v12_g_jets_py6_pt30",       nFilesMax = -1, nEventsMax = 1000000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt80",       nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt170",      nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            ]                                                       
        qcd_py8 = [                                                 
          ##specify(name = "qcd_py8_pt0to15",           nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt15to30",          nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt30to50",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt50to80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt80to120",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt120to170",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt170to300",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt300to470",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt470to600",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt600to800",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt800to1000",       nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1000to1400",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1400to1800",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1800",            nFilesMax = -1, color = r.kBlue    ),
            ]                                                       
        qcd_mg = [                                                  
            specify(name = "v12_qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
            ]                                                       
        g_jets_mg = [                                               
            specify(name = "v12_g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
            ]                                                       
        ttbar_mg = [                                                
            specify(name = "tt_tauola_mg_v12",          nFilesMax =  3, color = r.kOrange  ),
            ]                                                       
        ewk = [                                                     
            specify(name = "z_inv_mg_v12_skim",         nFilesMax = -1, color = r.kMagenta ),
            specify(name = "z_jets_mg_v12_skim",        nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12_skim",        nFilesMax = -1, color = 28         ),
            ]                                                       
        susy = [                                                    
            specify(name = "lm0_v12",                   nFilesMax = -1, color = r.kRed     ),
            specify(name = "lm1_v12",                   nFilesMax = -1, color = r.kRed+1   ),
            ]                                                   

        caloSkims = [
            specify(name = "2010_data_calo_skim",        nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "v12_qcd_py6_pt300_caloSkim", nFilesMax = -1, color = r.kBlue    ),
            specify(name = "tt_tauola_mg_v12_caloSkim",  nFilesMax =  3, color = r.kOrange  ),
            specify(name = "w_jets_mg_v12_skim_caloSkim",nFilesMax = -1, color = 28         ),
            specify(name = "z_inv_mg_v12_skim_caloSkim", nFilesMax = -1, color = r.kMagenta ),
            ]
        pfSkims = [
            specify(name = "2010_data_pf_skim",          nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "v12_qcd_py6_pt300_pfSkim",   nFilesMax = -1, color = r.kBlue    ),
            specify(name = "tt_tauola_mg_v12_pfSkim",    nFilesMax =  3, color = r.kOrange  ),
            specify(name = "w_jets_mg_v12_skim_pfSkim",  nFilesMax = -1, color = 28         ),
            specify(name = "z_inv_mg_v12_skim_pfSkim",   nFilesMax = -1, color = r.kMagenta ),
            ]

        outList = []
        #outList = caloSkims
        #self.skimString = "_caloSkim"

        #outList = pfSkims
        #self.skimString = "_pfSkim"

        self.skimString = ""
        if params["mcSoup"]=="py6" :
            outList+=qcd_py6
            outList+=g_jets_py6
            
        if params["mcSoup"]=="py8" :
            outList+=qcd_py8
            outList+=g_jets_py6#no py8 available
            
        if params["mcSoup"]=="mg":
            outList+=qcd_mg
            outList+=g_jets_mg
        
        outList+=data
        outList+=ttbar_mg
        outList+=ewk
        outList+=susy
        
        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 1000)

        return outList

    def mergeSamples(self, org, tag) :
        def py6(org, smSources) :
            org.mergeSamples(targetSpec = {"name":"qcd_py6_v12", "color":r.kBlue}, allWithPrefix="v12_qcd_py6")
            org.mergeSamples(targetSpec = {"name":"g_jets_py6_v12", "color":r.kGreen}, allWithPrefix="v12_g_jets_py6")
            smSources.append("qcd_py6_v12")
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
                                 samplesForRatios = ("2010 Data","standard_model"),
                                 sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 #doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()

            ##working on manipulation
            #dataIndex = org.indexOfSampleWithName("2010 Data")
            #csIndex = org.indicesOfSelectionsWithKey("cutSorterConfigurationCounts")[0]
            #csTriplet = [org.selections[csIndex][key][dataIndex] for key in ["cutSorterConfigurationCounts","cutSorterNames","cutSorterMoreNames"]]
            #cutSpecs = [(csTriplet[1].GetXaxis().GetBinLabel(i+1),csTriplet[2].GetXaxis().GetBinLabel(i+1)) for i in range(csTriplet[1].GetNbinsX())]

            
            
