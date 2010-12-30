#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

def nameList(t, name)  : return list(set([obj[name] for obj in dict(t).values()]))

class hadronicSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                           [ "jet",                "muon",       "muonsInJets", "jetPtMin"]
        objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),   ("muon","Pat"),        False,      30.0 ]))
        objects["jpt"]  = dict(zip(fields, [("xcak5JetJPT","Pat"),("muon","Pat"),         True,      30.0 ]))
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"), ("muon","Pat"),         True,      30.0 ]))
        return {"recoAlgos": tuple(objects.iteritems())}

    def listOfSteps(self, params) :
        stepList = [
            steps.Print.progressPrinter(2,300),
            steps.Trigger.techBitFilter([0],True),
            steps.Trigger.physicsDeclared(),
            steps.Other.vertexRequirementFilter(),
            steps.Other.monsterEventFilter(),
            steps.Jet.htSelector(nameList(params["recoAlgos"], "jet"), 350.0),
            steps.Other.skimmer(),
            ]
        return stepList

    def calcListJet(self, obj) :
        outList = [
            calculables.XClean.xcJet(obj["jet"],
                                     applyResidualCorrectionsToData = True,
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
    
    def listOfSamples(self,params) :
        from samples import specify
        return [
            specify(name = "JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "JetMET.Run2010A-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "Jet.Run2010B-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "MultiJet.Run2010B-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "Jet.Run2010B-Nov4ReReco_v1.RECO.Henning"),
            specify(name = "JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Henning"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
