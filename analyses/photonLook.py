#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

lowPtThreshold = 30.0
lowPtName = "lowPt"

class photonLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        #objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        50.0]))
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        36.0]))
        #objects["pfAK5"]   = dict(zip(fields, [("ak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        50.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 #"mcSoup" :           dict([ ("pythia6","py6"), ("madgraph","mg"), ("pythia8","py8") ] [1:2] ),
                 "photonId" :         dict([ ("photonLoose","photonIDLooseFromTwikiPat"),
                                             ("photonTight","photonIDTightFromTwikiPat"),

                                             ("photonTrkIsoRelaxed","photonIDTrkIsoRelaxedPat"),
                                             ("photonTrkIsoSideband","photonIDTrkIsoSideBandPat"),

                                             ("photonIsoSideband","photonIDIsoSideBandPat"),
                                             ("photonIsoRelaxed","photonIDIsoRelaxedPat"),
                                             ("photonEGM-10-006","photonIDEGM_10_006Pat"),
                                             ("photonAN",   "photonIDAnalysisNote_10_268Pat")]         [5:6] ),
                 "useSkims" :         dict([ ("fullSample",False), ("skimSample",True)]                [0:1] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 "etRatherThanPt" : [True,False]        [0],
                 }

    def listOfCalculables(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _electron = params["objects"]["electron"]
        _photon = params["objects"]["photon"]
        _jetPtMin = params["objects"]["jetPtMin"]
        _etRatherThanPt = params["etRatherThanPt"]
        _met = params["objects"]["met"]
        _correctForMuons = not params["objects"]["muonsInJets"]

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
                 calculables.genIndices( pdgs = [22], label = "Status1Photon", status = [1]),
                 calculables.genPhotonCategory(label = "Status1Photon"),
                 #calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 #calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.jetSumP4(_jet),
                     calculables.jetSumP4PlusPhotons(_jet, extraName = "", photon = _photon, photonIndices = [0]),
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

            steps.jetPtSelector(_jet,72.0,0),
            steps.jetPtSelector(_jet,72.0,1),
            #steps.jetPtSelector(_jet,100.0,0),
            #steps.jetPtSelector(_jet,100.0,1),
            steps.jetEtaSelector(_jet,2.5,0),
            steps.lowestUnPrescaledTrigger(["HLT_HT100U","HLT_HT120U","HLT_HT140U","HLT_HT150U"]),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            #steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s E_{T}s;events / bin"%_jet),

            #note leading jet cuts, single-jet threshold, eff. cuts
            steps.variableGreaterFilter(250.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            #steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),

            steps.passFilter("photonEfficiencyPlots1"),
            steps.photonEfficiencyPlots(label = "Status3Photon", ptCut = 90.0, etaCut = 1.4, jets = _jet),

            #note leading jet cuts and single-jet threshold
            steps.photonPtSelector(_photon, 80.0,0),
            #steps.photonPtSelector(_photon,100.0,0),
            steps.photonEtaSelector(_photon,1.45,0),

            steps.passFilter("photonEfficiencyPlots2"),
            steps.photonEfficiencyPlots(label = "Status3Photon", ptCut = 90.0, etaCut = 1.4, jets = _jet),
            
            #steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
            #                   funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            #steps.histogrammer("%sIndicesOther%s"%_jet,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_jet,
            #                   funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            
            #electron, muon, photon vetoes
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            #steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_photon, nMin = 1, nMax = 1),
            
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
            
            steps.variablePtGreaterFilter(100.0,"%sSumP4%s"%_jet,"GeV"),
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            
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
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),
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
        return [samples.mc, samples.jetmet, samples.ph]

    def listOfSamples(self,params) :
        skimString = "_phskim"
        
        from samples import specify
        data = [                                                
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
            ] if not params["useSkims"] else [
            specify(name = "Run2010B_MJ_skim2"+skimString,       color = r.kBlack),
            specify(name = "Run2010B_MJ_skim"+skimString,        color = r.kBlack),
            specify(name = "Run2010B_J_skim2"+skimString,        color = r.kBlack),
            specify(name = "Run2010B_J_skim"+skimString,         color = r.kBlack),
            specify(name = "Run2010A_JM_skim"+skimString,        color = r.kBlack),
            specify(name = "Run2010A_JMT_skim"+skimString,       color = r.kBlack),
            ]
        qcd_py6 = [                                                 
          ##specify(name = "v12_qcd_py6_pt30",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt170",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_py6_pt300",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt470",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt800",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "v12_qcd_py6_pt1400",        nFilesMax = -1, color = r.kBlue    ),
            ] if not params["useSkims"] else [
            specify(name = "v12_qcd_py6_pt80"+skimString, color = r.kBlue),
            specify(name = "v12_qcd_py6_pt170"+skimString,color = r.kBlue),
            specify(name = "v12_qcd_py6_pt300"+skimString,color = r.kBlue),
            ]
        g_jets_py6 = [                                              
            specify(name = "v12_g_jets_py6_pt30",       nFilesMax = -1, nEventsMax = 1000000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt80",       nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt170",      nFilesMax = -1, nEventsMax =  100000, color = r.kGreen),
            ] if not params["useSkims"] else [
            specify(name = "v12_g_jets_py6_pt80"+skimString,  color = r.kGreen),
            specify(name = "v12_g_jets_py6_pt170"+skimString, color = r.kGreen),
            ]
        qcd_mg = [                                                  
            specify(name = "v12_qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "v12_qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
            ] if not params["useSkims"] else [
            #specify(name = "v12_qcd_mg_ht_50_100"+skimString,    color = r.kBlue) ,
            #specify(name = "v12_qcd_mg_ht_100_250"+skimString,   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_250_500"+skimString,   color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_500_1000"+skimString,  color = r.kBlue) ,
            specify(name = "v12_qcd_mg_ht_1000_inf"+skimString,  color = r.kBlue) ,
            ]
        g_jets_mg = [                                               
            specify(name = "v12_g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
            specify(name = "v12_g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
            ] if not params["useSkims"] else [
            #specify(name = "v12_g_jets_mg_pt40_100"+skimString,  color = r.kGreen),
            #specify(name = "v12_g_jets_mg_pt100_200"+skimString, color = r.kGreen),
            specify(name = "v12_g_jets_mg_pt200"+skimString,     color = r.kGreen),
            ]
        ttbar_mg = [                                                
            specify(name = "tt_tauola_mg_v12",          nFilesMax =  3, color = r.kOrange  ),
            ] if not params["useSkims"] else [
            specify(name = "tt_tauola_mg_v12"+skimString,     nFilesMax = -1, color = r.kOrange  ),
            ]
        ewk = [                                                     
           #specify(name = "z_inv_mg_v12",              nFilesMax = -1, color = r.kMagenta ),
            specify(name = "z_jets_mg_v12",             nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12",             nFilesMax = -1, color = 28         ),
            ] if not params["useSkims"] else [
            specify(name = "z_jets_mg_v12"+skimString,  nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_v12"+skimString,  nFilesMax = -1, color = 28         ),
            ]
        susy = [                                                    
            specify(name = "lm0_v12",                   nFilesMax = -1, color = r.kRed     ),
            specify(name = "lm1_v12",                   nFilesMax = -1, color = r.kRed+1   ),
            ]                                                   

        outList = []

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

        #outList+=qcd_py6
        #outList+=g_jets_py6

        #outList+=qcd_mg
        outList+=g_jets_mg
        #
        #outList+=data
        #outList+=ewk
        #outList+=ttbar_mg

        #outList+=susy
        
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

        skimString = "_phskim" if "skimSample" in tag else ""

        smSources = ["z_inv_mg_v12", "z_jets_mg_v12", "w_jets_mg_v12"]
        #if "pythia6"  in tag : py6(org, smSources, skimString)
        #if "pythia8"  in tag : py8(org, smSources, skimString)
        #if "madgraph" in tag : mg (org, smSources, skimString)
        #py6(org, smSources, skimString)
        #py8(org, smSources, skimString)
        mg (org, smSources, skimString)

        #org.mergeSamples(targetSpec = {"name":"MG QCD+G", "color":r.kGreen}, sources = ["qcd_mg_v12","g_jets_mg_v12"])
        #org.mergeSamples(targetSpec = {"name":"PY6 QCD+G", "color":r.kBlue}, sources = ["qcd_py6_v12","g_jets_py6_v12"])
        org.mergeSamples(targetSpec = {"name":"MG TT+EWK", "color":r.kOrange}, sources = [item+skimString for item in ["z_jets_mg_v12", "w_jets_mg_v12", "tt_tauola_mg_v12"]])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3}, sources = smSources, keepSources = True)

        org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20},
                         sources = [item+skimString for item in ["Run2010B_MJ_skim","Run2010B_MJ_skim2","Run2010B_J_skim",
                                                                 "Run2010B_J_skim2","Run2010A_JM_skim","Run2010A_JMT_skim"]])
        
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            ##for skimming only
            #org = organizer.organizer( self.sampleSpecs(tag) )
            #utils.printSkimResults(org)            

            #organize
            org = organizer.organizer( self.sampleSpecs(tag) )
            self.mergeSamples(org, tag)
            #org.scale()
            
            ###plot all
            ##pl = plotter.plotter(org,
            ##                     psFileName = self.psFileName(tag),
            ##                     samplesForRatios = ("2010 Data","standard_model"),
            ##                     sampleLabelsForRatios = ("data","s.m."),
            ##                     #samplesForRatios = ("2010 Data","MG QCD+G"),
            ##                     #sampleLabelsForRatios = ("data","MG"),
            ##                     blackList = ["deltaRGenReco",
            ##                                  "photonMothergenPt",
            ##                                  "photonMotherrecoPt",
            ##                                  "photonMothermht",
            ##                                  "quarkMothergenPt",
            ##                                  "quarkMotherrecoPt",
            ##                                  "quarkMothermht",
            ##                                  "otherMothergenPt",
            ##                                  "otherMotherrecoPt",
            ##                                  "otherMothermht",
            ##                                  ],
            ##                     #whiteList = ["xcak5JetIndicesPat",
            ##                     #             #"photonPat1Pt",
            ##                     #             #"photonPat1mhtVsPhotonPt",
            ##                     #             "xcak5JetAlphaTFewBinsPat",
            ##                     #             "xcak5JetAlphaTRoughPat",
            ##                     #             "xcak5JetAlphaTWithPhoton1PtRatherThanMhtPat",
            ##                     #             ],
            ##                     
            ##                     )
            ##pl.plotAll()
            
            #self.makePurityPlots(org, tag)
            self.makeEfficiencyPlots(org, tag)
            
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
                key = var+"Status3Photon"
                if key in selection :
                    d[label] = selection[key][sampleIndex(org,"g_jets_mg_v12")].Clone(label)
                
            return d

        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)

        psFileName = "%s.ps"%tag
        canvas.Print(psFileName+"[","Lanscape")
        for variable in ["photonPt","photonEta","photonPhiVsEta","nJets","ht"] :
            histos = numerAndDenom(org, variable)
            if "numer" not in histos or "denom" not in histos : continue
            result = histos["numer"].Clone(variable)
            result.Reset()
            result.Divide(histos["numer"], histos["denom"], 1.0, 1.0, "b")
            result.SetMarkerStyle(20)
            result.SetStats(False)
            if result.ClassName()[2]=="1" :
                result.GetYaxis().SetTitle("efficiency")
                result.Draw()
            else :
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
