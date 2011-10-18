#!/usr/bin/env python

import os
from core import analysis,utils
import calculables,steps,samples

def nameList(t, name)  : return list(set([obj[name] for obj in dict(t).values()]))

class hadronicSkim(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                           [ "jet",                "muon",       "muonsInJets", "jetPtMin"]
        objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),   ("muon","Pat"),        False,      30.0 ]))
        #objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"), ("muon","Pat"),         True,      30.0 ]))
        return {"recoAlgos": tuple(objects.iteritems())}

    def listOfSteps(self, params) :
        stepList = [
            steps.Print.progressPrinter(2,300),
            steps.Jet.htSelector(nameList(params["recoAlgos"], "jet"), 250.0),
            steps.Other.skimmer(),
            ]
        return stepList

    def calcListJet(self, obj) :
        outList = [
            calculables.XClean.xcJet(obj["jet"],
                                     gamma = None,
                                     gammaDR = 0.5,
                                     muon = obj["muon"],
                                     muonDR = 0.5,
                                     correctForMuons = not obj["muonsInJets"],
                                     electron = None,
                                     electronDR = 0.5),
            calculables.Jet.Indices( obj["jet"], obj["jetPtMin"], etaMax = 3.0, flagName = "JetIDloose"),
            ]
        return outList+calculables.fromCollections(calculables.Jet, [obj["jet"]])
    
    def listOfCalculables(self, params) :
        outList = calculables.zeroArgs()

        for muon in nameList(params["recoAlgos"],"muon") :
            outList += calculables.fromCollections(calculables.Muon, [muon])
            outList += [calculables.Muon.Indices(muon, ptMin = 10, combinedRelIsoMax = 0.15)]
            
        for obj in dict(params["recoAlgos"]).values() :
            outList += self.calcListJet(obj)

        return outList
    
    def listOfSamples(self, params) :
        from samples import specify
        out = []
        out += specify(names = "znunu_jets_mg_ht_50_100")
        out += specify(names = "znunu_jets_mg_ht_100_200")
        out += specify(names = "znunu_jets_mg_ht_200_inf")
        return out

    def listOfSampleDictionaries(self) :
        return [samples.MC.mc]

    def conclude(self, config) :
        utils.printSkimResults(self.organizer(config))
