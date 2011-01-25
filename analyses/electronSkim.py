#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

class electronSkim(analysis.analysis) :
    def parameters(self) :
        return { "useCombinedIso": dict([ ("combinedIso", True), ("relativeIso", False) ]  [:] ),
                 "electrons" : ("electron","Pat"),
                 }

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(),
                   steps.multiplicityFilter("%sIndices%s"%params["electrons"], nMin = 1),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesElectron",[params["electrons"]]) +\
               [calculables.electronIndices( params["electrons"], ptMin = 20, simpleEleID = "80", useCombinedIso = params["useCombinedIso"])]
    
    def listOfSamples(self,params) :
        from samples import specify        
        return [
            specify(name = "Run2010B_MJ_skim2"),
            specify(name = "Run2010B_MJ_skim"),
            specify(name = "Run2010B_J_skim2"),
            specify(name = "Run2010B_J_skim"),
            specify(name = "Run2010A_JM_skim"),
            specify(name = "Run2010A_JMT_skim"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            org = organizer.organizer( self.sampleSpecs(tag) )
            utils.printSkimResults(org)
