#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

muon = ("muon","Pat")

class muonSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(),
                   steps.multiplicityFilter("%sIndices%s"%muon, nMin = 1),
                  #steps.objectEtaSelector(muon, etaThreshold = 2.5, index = 0, p4String = "P4"),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesMuon",[muon]) +\
               [calculables.muonIndices( muon, ptMin = 10, combinedRelIsoMax = 0.50)]
    
    def listOfSamples(self,params) :
        from samples import specify        
        return [
            #specify(name = "Mu.Run2010A-Sep17ReReco_v2.RECO.Robin"),
            #specify(name = "Mu.Run2010B-PromptReco-v2.RECO.Arlo1"),
            #specify(name = "Mu.Run2010B-PromptReco-v2.RECO.Arlo2"),
            #specify(name = "Mu.Run2010B-PromptReco-v2.RECO.Martyn"),
            #specify(name = "v12_qcd_py6_pt30"),
            #specify(name = "v12_qcd_py6_pt80"),
            #specify(name = "v12_qcd_py6_pt170"),
            #specify(name = "v12_qcd_py6_pt300"),
            #specify(name = "Run2010B_MJ_skim3"),
            #specify(name = "Run2010B_MJ_skim4"),
            specify(name ="MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Robin"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
