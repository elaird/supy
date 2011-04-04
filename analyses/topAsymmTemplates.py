#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils,math
import ROOT as r

class topAsymmTemplates(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                           [ "jet",              "met",           "sumP4",                "sumPt",                 "muon",       "electron",        "photon",        "muonsInJets"]
        objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),  "metP4AK5TypeII","xcSumP4",              "xcSumPt",               ("muon","Pat"),("electron","Pat"),("photon","Pat"), False]))
        #objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"),"metP4PF",       "xcak5JetPFRawSumP4Pat","xcak5JetPFRawSumPtPat", ("muon","Pat"),("electron","Pat"),("photon","Pat"),   True]))

        leptons = {}
        fieldsLepton    =                            ["name","ptMin",              "isoVar", "triggerList"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     20, "CombinedRelativeIso", ("HLT_Mu9","HLT_Mu15_v1")]))
        #leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,         "IsoCombined", ("FIX","ME")]))
        
        bVar = "TrkCountingHighEffBJetTags"
        bCut = {"normal"   : {"index":1, "min":2.0},
                "inverted" : {"index":0, "max":2.0}}
        lIso = {"normal":  {"nMaxIso":1, "indices":"Indices"},
                "inverted":{"nMaxIso":0, "indices":"IndicesNonIso"}}
        
        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  [{"min":3,"max":None}],
                 "bVar" : bVar,
                 "sample" : {"top" : {"bCut":bCut["normal"],  "lIso":lIso["normal"]},
                             #"Wlv" : {"bCut":bCut["inverted"],"lIso":lIso["normal"]},
                             #"QCD" : {"bCut":bCut["normal"],  "lIso":lIso["inverted"]}
                             }
                 }

    def listOfCalculables(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += calculables.fromCollections(calculables.Jet, [obj["jet"]])
        outList += [
            calculables.Jet.IndicesBtagged(obj["jet"],pars["bVar"]),
            calculables.Jet.Indices(      obj["jet"],      ptMin = 30, etaMax = 3.0, flagName = "JetIDloose"),
            calculables.Muon.Indices(     obj["muon"],     ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "80", useCombinedIso = True),
            calculables.Photon.photonIndicesPat(           ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),

            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.xcJet(obj["jet"], applyResidualCorrectionsToData = False,
                                     gamma    = obj["photon"],      gammaDR = 0.5,
                                     electron = obj["electron"], electronDR = 0.5,
                                     muon     = obj["muon"],         muonDR = 0.5, correctForMuons = not obj["muonsInJets"]),
            calculables.XClean.SumP4(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),
            calculables.XClean.SumPt(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),

            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            calculables.Other.lowestUnPrescaledTrigger(pars["lepton"]["triggerList"]),

            calculables.Top.mixedSumP4(transverse = obj["met"], longitudinal = obj["sumP4"]),
            calculables.Top.SemileptonicTopIndex(lepton),
            
            calculables.Top.NeutrinoPz(lepton,"mixedSumP4"),
            calculables.Top.NeutrinoP4P(lepton,"mixedSumP4"),
            calculables.Top.NeutrinoP4M(lepton,"mixedSumP4"),
            calculables.Top.TopReconstruction(lepton,obj["jet"]),
            calculables.Top.NeutrinoP4(lepton),
            calculables.Top.SumP4Nu(lepton,"mixedSumP4"),
            calculables.Top.SignedRapidity(lepton,"mixedSumP4Nu"),
            calculables.Top.RelativeRapidity(lepton,"mixedSumP4Nu"),
            
            calculables.Other.Mt(lepton,"%sNeutrinoP4%s"%lepton, allowNonIso=True),
            calculables.Muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"])
            ]
        return outList
    
    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])

        return [steps.Print.progressPrinter(),
                steps.Top.mcTruth(lepton),
                steps.Filter.multiplicity("%sIndices%s"%obj['jet'],min=3),
                steps.Top.mcTruthQDir(),
                steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
                steps.Top.mcTruthQDir(withNu = True),
                steps.Filter.label('cosThetaStar'),
                steps.Top.mcTruth(lepton),
                ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.muon, samples.electron]

    def listOfSamples(self,pars) :
        from samples import specify
        return specify( names = "tt_tauola_mg", effectiveLumi = None, color = r.kGreen+3)
    
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.scale(100)
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()

