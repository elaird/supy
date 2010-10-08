#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]

class hadronicSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(2,300),
                   steps.hltFilterList(["HLT_HT100U","HLT_HT120U","HLT_HT140U"]),
                   steps.techBitFilter([0],True),
                   steps.physicsDeclared(),
                   steps.vertexRequirementFilter(),
                   steps.monsterEventFilter(),
                   steps.htSelector(jetAlgoList,250.0),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",jetAlgoList) +\
               [calculables.jetIndices( jet, 30.0, etaMax = 3.0, flagName = "JetIDloose") for jet in jetAlgoList]
    
    def listOfSamples(self,params) :
        return [
            #samples.specify(name = "Jet.Run2010B-PromptReco-v2.RECO.Burt"),
            #samples.specify(name = "JetMET.Run2010A-Sep17ReReco_v2.RECO.Burt"),
            samples.specify(name = "JetMETTau.Run2010A-Sep17ReReco_v2.RECO.Burt"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
