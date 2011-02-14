#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

muon = ("muon","Pat")

class muonSkim2(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(),
                   steps.Filter.pt("%sP4%s"%muon, min = 15, indices = "%sIndicesAnyIso%s"%muon, index = 0),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.Muon,[muon]) +\
               [calculables.Muon.Indices( muon, ptMin = 10, combinedRelIsoMax = 0.15)]
    
    def listOfSamples(self,params) :
        from samples import specify        
        #return specify(names = "Mu.Run2010B-Nov4ReReco.RECO.Jad")
        return specify(names = "Mu.Run2010A-Nov4ReReco.RECO.Jad")

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
