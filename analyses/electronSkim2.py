#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

electron = ("electron","Pat")

class electronSkim2(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(),
                   steps.Filter.pt("%sP4%s"%electron, min = 20, indices = "%sIndicesAnyIso%s"%electron, index = 0),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,pars) :
        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.Electron,[electron]) +\
               [calculables.Electron.Indices( electron, ptMin = 10, simpleEleID = "95", useCombinedIso = True)]
    
    def listOfSamples(self,params) :
        from samples import specify        
        return specify(names = [ "EG.Run2010A-Nov4ReReco_v1.RECO.Sparrow",
                                 "Electron.Run2010B-Nov4ReReco_v1.RECO.Sparrow",
                                 ])

    def listOfSampleDictionaries(self) :
        return [samples.electron]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
