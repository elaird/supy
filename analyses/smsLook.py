#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class smsLook(analysis.analysis) :
    def parameters(self) :
        objects = self.vary()
        fields =                                                [ "jet",            "met",            "muon",        "electron",        "photon",
                                                                  "compJet",    "compMet",
                                                                  "rechit", "muonsInJets", "jetPtMin", "jetId"]

        objects["caloAK5JetMet_recoLepPhot"] = dict(zip(fields, [("xcak5Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"),
                                                                 ("xcak5JetPF","Pat"),"metP4PF",
                                                                 "Calo",     False,         50.0,      "JetIDloose"]))
        
        return { "objects": objects,
                 "nJetsMinMax" :      self.vary(dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]       [0:1] )),
                 "mcSoup" :           self.vary(dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] )),
                 "etRatherThanPt" : [True,False]        [0],
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "triggerList" : ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3"),#required to be a sorted tuple
                 }

    def calcListJet(self, obj, etRatherThanPt, lowPtThreshold, lowPtName) :
        def calcList(jet, met, photon, muon, electron, muonsInJets, jetPtMin, jetIdFlag) :
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
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.Photon.Indices(obj["photon"], ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            
            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
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
            #steps.Other.collector(["susyScanM0","susyScanM12"]),
            #steps.Other.orFilter([steps.Gen.ParticleCountFilter({"gluino":2}), steps.Gen.ParticleCountFilter({"squark":2})]),
            #steps.Other.smsMedianHistogrammer(_jet),
            ]+[
            steps.Histos.generic(("susyScanM0","susyScanM12"),(101,38),(i,i),(2020+i,760+i), title="%d;m_{0};m_{1/2};events/bin"%i) for i in range(20)]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc]

    def listOfSamples(self,params) :
        from samples import specify
        return specify( #nFilesMax = 4, nEventsMax = 10000,
                        names = ["scan_tanbeta10_burt1"])

    def conclude(self,pars) :
        org = self.organizer(pars)

        #plot
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
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
