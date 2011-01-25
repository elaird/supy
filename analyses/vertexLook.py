#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class vertexLook(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        #objects["caloAK5_pfMET"] = dict(zip(fields, [("ak5Jet","Pat"), "metP4PF", ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        50.0]))
        objects["caloAK5_30"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        30.0]))
        objects["caloAK5_35"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        35.0]))
        objects["caloAK5_40"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        40.0]))
        objects["caloAK5_45"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        45.0]))
        objects["caloAK5_50"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        50.0]))
        #objects["caloAK7"] = dict(zip(fields, [("xcak7Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        50.0]))
        #objects["jptAK5"]  = dict(zip(fields, [("xcak5JetJPT","Pat"),"metP4TC",     ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo",     True ,        50.0]))
        #objects["pfAK5"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        50.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 "mcSoup" :           dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [1:2] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 "etRatherThanPt" : [True,False]        [0],
                 #"jesAbs":  [1.0,1.1,0.9]               [:],
                 #"jesRel":  0,
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

        lowPtThreshold = 30.0
        lowPtName = "lowPt"
        
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ calculables.xcJet(_jet,
                                   gamma = _photon,
                                   gammaDR = 0.5,
                                   muon = _muon,
                                   muonDR = 0.5,
                                   correctForMuons = _correctForMuons,
                                   electron = _electron,
                                   electronDR = 0.5),
                 calculables.jetIndices( _jet, _jetPtMin,      etaMax = 3.0, flagName = params["jetId"]),
                 calculables.jetIndices( _jet, lowPtThreshold, etaMax = 3.0, flagName = params["jetId"], extraName = lowPtName),
                 calculables.muonIndices( _muon, ptMin = 20, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = 20, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = 20, flagName = "photonIDLooseFromTwikiPat"),
                 calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.jetSumP4(_jet, mcScaleFactor = 1.0),
                     calculables.deltaPhiStar(_jet, ptMin = lowPtThreshold, extraName = lowPtName),
                     calculables.deltaPseudoJet(_jet, _etRatherThanPt),
                     calculables.alphaT(_jet, _etRatherThanPt),
                     calculables.alphaTMet(_jet, _etRatherThanPt, _met),
                    #calculables.mhtMinusMetOverMeff(_jet, _met, _etRatherThanPt),
                     calculables.mhtMinusMetOverMeff(_jet, "metP4PF", _etRatherThanPt),
                     calculables.vertexID(),
                     calculables.vertexIndices(sumPtMin=20),
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
            
            steps.preIdJetPtSelector(_jet,100.0,0),
            steps.preIdJetPtSelector(_jet,100.0,1),
            steps.jetEtaSelector(_jet,2.5,0),
            steps.hltFilter("HLT_HT100U"),
            #steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            
            steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            steps.multiplicityFilter("vertexIndices", nMin = 1),
            steps.histogrammer("vertexIndicesOther", 10,-0.5,9.5, title = ";N bad vertices;events / bin", funcString="lambda x:len(x)"),
            steps.multiplicityFilter("vertexIndicesOther", nMax = 0),

            steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            steps.vertexHistogrammer(),
            #steps.hltPrescaleHistogrammer(["HLT_Jet50U","HLT_Jet70U","HLT_Jet100U","HLT_HT100U","HLT_HT120U","HLT_HT140U"]),
            #steps.iterHistogrammer("ecalDeadTowerTrigPrimP4", 256, 0.0, 128.0, title=";E_{T} of ECAL TP in each dead region (GeV);TPs / bin",
            #                       funcString="lambda x:x.Et()"),
            
            #steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,       funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            #steps.histogrammer("%sIndicesOther%s"%_jet,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_jet,                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            
            #electron, muon, photon vetoes
            #steps.histogrammer("%sIndices%s"%_electron,10,-0.5,9.5,title="; N electrons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            #steps.histogrammer("%sIndices%s"%_muon,10,-0.5,9.5,title="; N muons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            #steps.histogrammer("%sIndicesOther%s"%_muon,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_muon,funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            #steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),

            #steps.histogrammer("%sIndicesUnmatched%s"%_electron,10,-0.5,9.5,title="; N electrons unmatched;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            #steps.histogrammer("%sIndicesUnmatched%s"%_photon,10,-0.5,9.5,title="; N photons unmatched;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_photon, nMax = 0),
            steps.uniquelyMatchedNonisoMuons(_jet),
            
            steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s %s_{T}s;events / bin"%(_jet[0],_jet[1],"p" if not _etRatherThanPt else "E")),
            steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            
            steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            steps.vertexHistogrammer(),
            #many plots
            #steps.passFilter("singleJetPlots1"),
            #steps.singleJetHistogrammer(_jet),
            #steps.passFilter("jetSumPlots1"), 
            #steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            #steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            #steps.passFilter("kinematicPlots1"), 
            #steps.alphaHistogrammer(_jet, _etRatherThanPt),
            #steps.alphaMetHistogrammer(_jet, _etRatherThanPt, _met),
            
            ###extrapolation region
            ##steps.variableGreaterFilter(0.50,"%sAlphaT%s"%_jet),
            ##
            ###many plots (again)
            ##steps.passFilter("singleJetPlots2"),
            ##steps.cleanJetPtHistogrammer(_jet),
            ##steps.passFilter("jetSumPlots2"), 
            ##steps.cleanJetHtMhtHistogrammer(_jet),
            ###steps.passFilter("kinematicPlots2"), 
            ###steps.alphaHistogrammer(_jet),
            
            #signal selection
            steps.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.variableGreaterFilter(0.5,"%sAlphaT%s"%_jet),
            steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            steps.vertexHistogrammer(),
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            steps.histogrammer("vertexIndices", 10,-0.5,9.5, title = ";N good vertices;events / bin", funcString="lambda x:len(x)"),
            steps.vertexHistogrammer(),
            #steps.histogrammer("mhtMinusMetOverMeff", 100, -1.0, 1.0, title = ";(MHT - PFMET)/(MHT+HT);events / bin"),
            #steps.variableLessFilter(0.15,"mhtMinusMetOverMeff"),
            #steps.deadEcalFilter(jets = _jet, dR = 0.3, dPhiStarCut = 0.5, nXtalThreshold = 5),
            ##steps.variableGreaterFilter(0.53,"%sAlphaTMet%s"%_jet),
            
            #steps.skimmer(),
            #steps.eventPrinter(),
            #steps.jetPrinter(_jet),
            #steps.particleP4Printer(_muon),
            #steps.particleP4Printer(_photon),
            #steps.recHitPrinter("clusterPF","Ecal"),
            #steps.htMhtPrinter(_jet),
            #steps.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),
            #
            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 400.0,#GeV
            #                etRatherThanPt = _etRatherThanPt,
            #                ),
            
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        data = [                                                
            specify(name = "Run2010B_J_skim",           nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JM_skim",          nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JMT_skim",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "2010_data_skim_calo",       nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "2010_data_skim_pf",         nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
           #specify(name = "test",                      nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
            ]                                                       
        qcd_py8 = [                                                 
          ##specify(name = "qcd_py8_pt0to15",           nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt15to30",          nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt30to50",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt50to80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt80to120",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt120to170",        nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt170to300",        nFilesMax = -1, nEventsMax=10000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt300to470",        nFilesMax = 20, nEventsMax=10000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt470to600",        nFilesMax = 20, nEventsMax=5000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt600to800",        nFilesMax = 20, nEventsMax=5000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt800to1000",       nFilesMax = 10, nEventsMax=5000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1000to1400",      nFilesMax = 1, nEventsMax=5000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1400to1800",      nFilesMax = 1, nEventsMax=5000, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1800",            nFilesMax = 1, nEventsMax=5000, color = r.kBlue    ),
            ]                                                       

        outList = []
        if params["mcSoup"]=="py8" :
            outList+=qcd_py8
            pass

        outList+=data

        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    #if "2010" in o.name: continue
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 10, nEventsMax = 5000)
        
        return outList

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :

            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"qcd_py8", "color":r.kBlue}, allWithPrefix="qcd_py8")
            org.mergeSamples(targetSpec = {"name":"2010 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Run2010")
            org.scale()

            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("2010 Data","qcd_py8"),
                                 sampleLabelsForRatios=("data","qcd"),
                                 )
            pl.plotAll()

