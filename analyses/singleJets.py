#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,copy
import ROOT as r

class singleJets(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                              [ "jet",               "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        objects["caloAK7"] = dict(zip(fields, [("xcak7Jet","Pat"),   "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        30.0]))
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"),   "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        30.0]))
        objects["jptAK5"]  = dict(zip(fields, [("xcak5JetJPT","Pat"),"metP4TC",       ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo",     True ,        30.0]))
        objects["pfAK5"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",       ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        30.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [1:3] ),
                 "jetId" :  "JetIDloose",
                 "etRatherThanPt" : True,
                 }

    def listOfCalculables(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _electron = params["objects"]["electron"]
        _photon = params["objects"]["photon"]
        _jetPtMin = params["objects"]["jetPtMin"]
        _met = params["objects"]["met"]

        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ calculables.xcJet( _jet,  gamma = _photon, gammaDR = 0.5, muon = _muon, muonDR = 0.5, electron = _electron, electronDR = 0.5),
                 calculables.jetIndices( _jet, _jetPtMin, etaMax = 3.0, flagName = params["jetId"]),
                 calculables.muonIndices( _muon, ptMin = 20, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = 20, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = 20, flagName = "photonIDLoosePat"),
                 calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.deltaPhiStar(_jet, ptMin = 50.0),
                     calculables.deltaPseudoJet(_jet, params["etRatherThanPt"]),
                     calculables.alphaT(_jet, params["etRatherThanPt"]),
                     calculables.alphaTMet(_jet, params["etRatherThanPt"], _met),
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
            
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndicesUnmatched%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.uniquelyMatchedNonisoMuons(_jet),
            steps.singleJetHistogrammer(_jet),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.histogrammer("%sSumP4%s"%_jet,100,0.0,500.0,title=";MHT (GeV);events / bin", funcString = "lambda x: x.pt()"),

            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.jetPtSelector(_jet,100.0,0),
            steps.jetEtaSelector(_jet,2.5,0),
            steps.jetPtSelector(_jet,80.0,1),
            steps.singleJetHistogrammer(_jet),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.histogrammer("%sSumP4%s"%_jet,100,0.0,500.0,title=";MHT (GeV);events / bin", funcString = "lambda x: x.pt()"),
            
            steps.variableGreaterFilter(350.0,"%sSumEt%s"%_jet, suffix = "GeV"),
            steps.singleJetHistogrammer(_jet),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.histogrammer("%sSumP4%s"%_jet,100,0.0,500.0,title=";MHT (GeV);events / bin", funcString = "lambda x: x.pt()"),
            
            steps.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            steps.singleJetHistogrammer(_jet),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.histogrammer("%sSumP4%s"%_jet,100,0.0,500.0,title=";MHT (GeV);events / bin", funcString = "lambda x: x.pt()"),
            
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify

        data = [
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
            specify(name = "qcd_py8_pt1000to1400",  nFilesMax =  1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1400to1800",  nFilesMax =  1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt1800to2200",  nFilesMax =  1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt2200to2600",  nFilesMax =  1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt2600to3000",  nFilesMax =  1, color = r.kBlue    ),
            specify(name = "qcd_py8_pt3000to3500",  nFilesMax =  1, color = r.kBlue    ),
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
            #specify(name = "lm0",                   nFilesMax = -1, color = r.kRed     ),
            #specify(name = "lm1",                   nFilesMax = -1, color = r.kRed+1   ),
            ]
        
        outList = data
        outList += default_list

        outList += py6_list
        outList += py8_list
        outList += mg_list
        
        #for i in range(len(outList)):
        #    o = outList[i]
        #    if o.name == "JetMET_skim": continue
        #    outList[i] = specify(name = o.name, color = o.color, nFilesMax = 1, nEventsMax=10000)

        return outList

    def conclude(self) :
        smSources = ["g_jets_mg","tt_tauola_mg","z_inv_mg_skim","z_jets_mg_skim","w_jets_mg_skim"]

        for tag in self.sideBySideAnalysisTags() :

            org = organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"g_jets_mg", "color":r.kGreen}, allWithPrefix = "g_jets_mg")
            for color,qcd in zip([r.kRed,r.kBlue,r.kGreen],["qcd_py6", "qcd_py8", "qcd_mg"]) :
                org.mergeSamples(targetSpec = {"name":qcd, "color":r.kBlue}, allWithPrefix = qcd)
                if qcd in [sample["name"] for sample in org.samples]:
                    org.mergeSamples(targetSpec = {"name":"sm_w_"+qcd,"color":color}, sources = smSources+[qcd], keepSources = True)
                    org.drop(qcd)
            for sample in smSources: org.drop(sample)                    
            org.scale()

            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("JetMET_skim", filter(lambda name: "sm_w_qcd" in name, [sample["name"] for sample in org.samples])),
                                 sampleLabelsForRatios=("data","s.m.")
                                 )
            pl.plotAll()

