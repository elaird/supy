from core.analysis import analysis
import steps,calculables,samples
import copy,os,ROOT as r
from calculables import *

class ra1Displays(analysis) :
    def useCachedFileLists(self) : return False
    
    def parameters(self) :
        objects = self.vary()
        fields =                                                  [ "jet",                        "jetId",     "muonsInJets",           "met",
                                                                    "compJet",                "compJetId", "compMuonsInJets",        "compMet",
                                                                    "muon",                    "electron",          "photon",         "rechit"]

        objects["caloAK5JetMet_recoLepPhot"]   = dict(zip(fields, [("xcak5Jet","Pat"),       "JetIDloose",             False, "metP4AK5TypeII",
                                                                   ("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
                                                                   ("muon","Pat"),     ("electron","Pat"),  ("photon","Pat"),           "Calo",
                                                                   ]))
        
        return { "objects": objects,
                 "etRatherThanPt" : True,
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "highPtThreshold" : 50.0,
                 "highPtName" : "highPt",
                 "thresholds": self.vary(dict( [("375",        (375.0, None,  100.0, 50.0)),#0
                                                ("325_scaled", (325.0, 375.0,  86.7, 43.3)),#1
                                                ("275_scaled", (275.0, 325.0,  73.3, 36.7)),#2
                                                ][0:1] )),
                 }

    def calcListJet(self, obj, etRatherThanPt, ptMin, lowPtThreshold, lowPtName, highPtThreshold, highPtName, htThreshold) :
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
                calculables.Other.FixedValue("%sFixedHtBin%s"%jet, htThreshold),
                ]
            return outList+calculables.fromCollections(calculables.Jet, [jet])

        outList = calcList(obj["jet"], obj["met"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetId"])
        if all([("comp"+item in obj) for item in ["Jet", "Met","MuonsInJets","JetId"]]) :
            outList += calcList(obj["compJet"], obj["compMet"], obj["photon"], obj["muon"], obj["electron"], obj["compMuonsInJets"], obj["compJetId"])
        return outList

    def calcListOther(self, obj) :
        return [
            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),

            calculables.Muon.Indices(obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices(obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.Photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            #calculables.Photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDTightFromTwikiPat"),

            calculables.Other.RecHitSumPt(obj["rechit"]),
            calculables.Other.RecHitSumP4(obj["rechit"]),
            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            ]
    
    def listOfCalculables(self, params) :
        obj = params["objects"]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += self.calcListOther(obj)
        outList += self.calcListJet(obj, params["etRatherThanPt"], params["thresholds"][3],
                                    params["lowPtThreshold"], params["lowPtName"], params["highPtThreshold"], params["highPtName"], params["thresholds"][0])
        return outList
    
    def listOfSteps(self, params) :
        from steps import Print,Displayer,Other
        return [
            Print.progressPrinter(),
            #Other.variableGreaterFilter(675, "%sSumEt%s"%params["objects"]["jet"], suffix = "GeV"),
            Displayer.displayer(jets      = params["objects"]["jet"],
                                muons     = params["objects"]["muon"],
                                met       = params["objects"]["met"],
                                electrons = params["objects"]["electron"],
                                photons   = params["objects"]["photon"],                            
                                recHits   = params["objects"]["rechit"], recHitPtThreshold = 1.0,#GeV
                                scale = 400.0,#GeV
                                etRatherThanPt = params["etRatherThanPt"],
                                deltaPhiStarExtraName = params["lowPtName"],
                                deltaPhiStarCut = 0.5,
                                deltaPhiStarDR = 0.3,
                                j2Factor = params["thresholds"][2]/params["thresholds"][0],
                                mhtOverMetName = "%sMht%sOver%s"%(params["objects"]["jet"][0], params["objects"]["jet"][1]+params["highPtName"], params["objects"]["met"]),
                                metOtherAlgo  = params["objects"]["compMet"],
                                jetsOtherAlgo = params["objects"]["compJet"],
                                #doGenJets = True,
                                #prettyMode = True,
                                ),
            ]
    
    def listOfSampleDictionaries(self) :
        sampleDict = samples.SampleHolder()
        sampleDict.add("MT2_events", '["/home/hep/bm409/public_html/MT2Skim.root"]', lumi = 600)
        sampleDict.add("Data_375", '["/home/hep/elaird1/73_candidates/v8/375.root"]', lumi = 1.1e3)
        sampleDict.add("T2_skim", '["/home/hep/db1110/public_html/Simplified_Models/T2_testpoint_results/T2_skims/T2_testpoint_200_175.root"]', xs = 1.0)
        sampleDict.add("Data_275", '["/home/hep/db1110/public_html/AnalysisSkims/DefaultAnalysisSkims/275-325/Dataskims/275data.root"]', lumi = 602.) #/pb
        sampleDict.add("MG_QCD", '["/home/hep/db1110/public_html/AnalysisSkims/DefaultAnalysisSkims/275-325/MCskims/275madgraph.root"]', xs = 1.0) #dummy xs
        sampleDict.add("PY_QCD", '["/home/hep/db1110/public_html/AnalysisSkims/DefaultAnalysisSkims/275-325/AlphaT54MCSkims/275Pythia.root"]', xs = 1.0) #dummy xs
        sampleDict.add("py_qcd_375", '["/home/hep/elaird1/87_qcd_hunt/02_ht375/py6/skims_alphaT.gt.0.55/all.root"]', xs = 1.0) #dummy xs
        return [sampleDict]
    
    def listOfSamples(self,params) :
        return samples.specify(names = "Data_375")
