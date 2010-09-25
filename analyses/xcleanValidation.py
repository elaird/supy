#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class xcleanValidation(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        30.0]))
        #objects["jptAK5"]  = dict(zip(fields, [("xcak5JetJPT","Pat"),"metP4TC",     ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo",     True ,        30.0]))
        #objects["pfAK5"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        30.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] ),
                 "mcSoup" :           dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 "dR": 0.5,
                 "vetoPtMin": 20.0
                 }

    def listOfCalculables(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _electron = params["objects"]["electron"]
        _photon = params["objects"]["photon"]
        _jetPtMin = params["objects"]["jetPtMin"]
        _dR = params["dR"]
        _vPtMin = params["vetoPtMin"]
        
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ calculables.xcJet( _jet,  gamma = _photon, gammaDR = _dR, muon = _muon, muonDR = _dR, electron = _electron, electronDR = _dR,
                                    correctForMuons = not params["objects"]["muonsInJets"]),
                 calculables.jetIndices( _jet, _jetPtMin, etaMax = 3.0, flagName = params["jetId"]),
                 calculables.muonIndices( _muon, ptMin = _vPtMin, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = _vPtMin, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = _vPtMin, flagName = "photonIDLoosePat"),
                 calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = _dR),
                 calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = _dR)
                 ] \
                 + [calculables.deltaPseudoJet(_jet, True),
                    calculables.alphaT(_jet, True),
                    calculables.jetSumP4(_jet,1.0)]

    def listOfSteps(self,params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        
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

            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),

            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),

            steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),
            
            steps.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),

            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),
            
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.uniquelyMatchedNonisoMuons(_jet),
            steps.vetoCounts(params["objects"]),steps.jetModHistogrammer(_jet),steps.ecalDepositValidator(params["objects"],params["dR"]),

            
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

        #for i in range(len(outList)):
        #    o = outList[i]
        #    if o.name == "JetMET_skim": continue
        #    outList[i] = specify(name = o.name, color = o.color, nFilesMax = 1, nEventsMax=5000)
            
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


            def makeRate(hist,total,name) :
                if (not hist) or (not total): return 0
                hist.Scale(1./total)
                hist.SetMaximum(0.91)
                hist.GetXaxis().SetTitle("")
                if hist.GetYaxis().GetNbins()>1:
                    hist.GetYaxis().SetTitle("")
                    hist.GetZaxis().SetTitle("rate")
                else:
                    hist.GetYaxis().SetTitle("rate")
                    hist.SetTitle(name)
                return 1
                
            for iSel,selection in enumerate(org.selections) :
                if len(selection)>1 :
                    totals = tuple(map(lambda h: h.GetBinContent(2) if h else 0, selection["counts"]))
                    totals2 = tuple(map(lambda h: h.GetBinContent(1)+h.GetBinContent(2) if h else 0, org.selections[iSel+1]["counts"])) if \
                              iSel+1<len(org.selections) else [0]*len(totals)
                    totals = map(max,totals,totals2)
                    for name in selection:
                        if "VetoCounts" in name : 
                            result = map(makeRate, selection[name],totals, [name]*len(totals))

            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("JetMET_skim","standard_model"),
                                 sampleLabelsForRatios=("data","s.m."),
                                 #compactOutput=True
                                 )
            pl.plotAll()

