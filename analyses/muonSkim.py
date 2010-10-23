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
            specify(name = "Run2010B_MJ_skim2"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
