#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class hadronicLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        objects["caloAK5"] = dict(zip(fields, [("ak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        30.0]))
        objects["jptAK5"]  = dict(zip(fields, [("ak5JetJPT","Pat"),"metP4TC",     ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo",     True ,        30.0]))
        objects["pfAK5"]   = dict(zip(fields, [("ak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        30.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [:] ),
                 "mcSoup" :           dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] ),
                 "mcMhtScaleFactor" : dict([ ("defaultMht",1.0), ("scaledMht",1.1) ]                   [0:1] ),
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
        
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ #calculables.xcJet( _jet,  gamma = _photon, gammaDR = 0.5, muon = _muon, muonDR = 0.5, electron = _electron, electronDR = 0.5),
                 calculables.jetIndices( _jet, _jetPtMin, etaMax = 3.0, flagName = params["jetId"]),
                 calculables.muonIndices( _muon, ptMin = 20, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = 20, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = 20, flagName = "photonIDLoosePat"),
                 #calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 #calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.jetSumP4(_jet, mcScaleFactor = params["mcMhtScaleFactor"]),
                     calculables.deltaPhiStar(_jet, ptMin = 50.0),
                     calculables.deltaPseudoJet(_jet, _etRatherThanPt),
                     calculables.alphaT(_jet, _etRatherThanPt) ]

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
            steps.preIdJetPtSelector(_jet, 80.0,1),
            
            steps.leadingUnCorrJetPtSelector( [_jet],100.0 ),
            steps.hltFilter("HLT_Jet50U"),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),

            steps.hltPrescaleHistogrammer(["HLT_Jet50U","HLT_HT100U","HLT_MET45"]),       
            
            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.histogrammer("%sIndicesOther%s"%_jet,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            
            #electron, muon, photon vetoes
            steps.histogrammer("%sIndices%s"%_electron,10,-0.5,9.5,title="; N electrons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.histogrammer("%sIndices%s"%_muon,10,-0.5,9.5,title="; N muons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            #steps.histogrammer("%sIndicesUnmatched%s"%_electron,10,-0.5,9.5,title="; N electrons unmatched;events / bin", funcString = "lambda x: len(x)"),
            #steps.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            #steps.histogrammer("%sIndicesUnmatched%s"%_photon,10,-0.5,9.5,title="; N photons unmatched;events / bin", funcString = "lambda x: len(x)"),
            #steps.multiplicityFilter("%sIndicesUnmatched%s"%_photon, nMax = 0),
            #steps.uniquelyMatchedNonisoMuons(_jet),

            steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s %s_{T}s;events / bin"%(_jet[0],_jet[1],"p" if not _etRatherThanPt else "E")),
            steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            
            #many plots
            steps.passFilter("singleJetPlots1"),
            steps.singleJetHistogrammer(_jet),
            steps.passFilter("jetSumPlots1"), 
            steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.passFilter("kinematicPlots1"), 
            steps.alphaHistogrammer(_jet, _etRatherThanPt),

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
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),

            #steps.skimmer(),
            #steps.eventPrinter(),
            #steps.jetPrinter(_jet),
            #steps.htMhtPrinter(_jet),
            #steps.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),

            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 200.0),#GeV
            
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify

        outList =[
            specify(name = "JetMET_skim",           nFilesMax = -1, color = r.kBlack   , markerStyle = 20)
            ]                                                   
        py6_list = [                                            
          ##specify(name = "qcd_py6_pt30",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py6_pt80",          nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py6_pt170",         nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py6_pt300",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py6_pt470",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py6_pt800",         nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py6_pt1400",        nFilesMax = -1, color = r.kBlue    ),
            ]                                                   
        py8_list = [                                            
          ##specify(name = "qcd_py8_pt0to15",       nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt15to20",      nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt20to30",      nFilesMax = -1, color = r.kBlue    ),
          ##specify(name = "qcd_py8_pt30to50",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt50to80",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt80to120",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt120to170",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt170to230",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt230to300",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt300to380",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt380to470",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt470to600",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt600to800",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt800to1000",   nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1000to1400",  nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1400to1800",  nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1800to2200",  nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt2200to2600",  nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt2600to3000",  nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt3000to3500",  nFilesMax = -1, color = r.kBlue    ),
            ]                                                   
        mg_list = [                                             
            specify(name = "qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
            specify(name = "qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
            ]                                                   
        default_list = [                                        
            specify(name = "tt_tauola_mg",          nFilesMax =  3, color = r.kOrange  ),
            specify(name = "g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
            specify(name = "g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
            specify(name = "g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
            specify(name = "z_inv_mg_skim",         nFilesMax = -1, color = r.kMagenta ),
            specify(name = "z_jets_mg_skim",        nFilesMax = -1, color = r.kYellow-3),
            specify(name = "w_jets_mg_skim",        nFilesMax = -1, color = 28         ),
            specify(name = "lm0",                   nFilesMax = -1, color = r.kRed     ),
            specify(name = "lm1",                   nFilesMax = -1, color = r.kRed+1   ),
            ]
        
        if params["mcSoup"]=="py6" : outList+=py6_list
        if params["mcSoup"]=="py8" : outList+=py8_list
        if params["mcSoup"]=="mg"  : outList+=mg_list
        outList+=default_list
        return outList

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"g_jets_mg",     "color":r.kGreen},   sources = ["g_jets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
            
            smSources = ["g_jets_mg","tt_tauola_mg","z_inv_mg_skim","z_jets_mg_skim","w_jets_mg_skim"]
            if "pythia6" in tag :
                org.mergeSamples(targetSpec = {"name":"qcd_py6",    "color":r.kBlue},    sources = ["qcd_py6_pt%d"%i      for i in [80,170,300] ])
                smSources.append("qcd_py6")
            if "pythia8" in tag :
                lowerPtList = [0,15,20,30,50,80,
                               120,170,230,300,380,470,600,800,
                               1000,1400,1800,2200,2600,3000,3500]
                org.mergeSamples(targetSpec = {"name":"qcd_py8","color":r.kBlue},
                                 sources = ["qcd_py8_pt%dto%d"%(lowerPtList[i],lowerPtList[i+1]) for i in range(len(lowerPtList)-1)] )
                smSources.append("qcd_py8")
            if "madgraph" in tag :
                org.mergeSamples(targetSpec = {"name":"qcd_mg",    "color":r.kBlue},
                                 sources = ["qcd_mg_ht_%s"%bin for bin in ["50_100","100_250","250_500","500_1000","1000_inf"] ])
                smSources.append("qcd_mg")
            
            org.mergeSamples(targetSpec = {"name":"standard_model","color":r.kGreen+3}, sources = smSources, keepSources = True)
            org.scale()


            ##other
            #import deltaPhiLook
            #numers = ["JetMET_skim","standard_model"]
            #if "pythia" in tag :   qcdLabel = "qcd_py"
            #if "madgraph" in tag : qcdLabel = "qcd_mg"
            #
            #for numer,denom in zip(numers,[qcdLabel]*len(numers)) :
            #    d = deltaPhiLook.deltaPhiLooker(org,tag,(numer,denom))
            #    d.makeSlicePlots()
            #    if numer==numers[0] :
            #        d.makeSliceComparisonPlots(qcdLabel)

            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("JetMET_skim","standard_model"),
                                 sampleLabelsForRatios=("data","s.m."),
                                 )
            pl.plotAll()

            #import statMan
            #statMan.go(a.organizeHistograms(),
            #           dataSampleName="JetMETTau.Run2010A",
            #           mcSampleName="standard_model",
            #           moneyPlotName="ak5JetPat_alphaT_vs_Ht_ge2jets",
            #           xCut=0.51,yCut=330.0)
