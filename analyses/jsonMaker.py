#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def listOfSteps(self,params) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify        
        return specify(names = [#"Nov4_MJ_skim",
                                #"Nov4_J_skim",
                                #"Nov4_J_skim2",
                                #"Nov4_JM_skim",
                                #"Nov4_JMT_skim",
                                #"Nov4_JMT_skim2",
                                #"EG.2010A_skim",
                                #"Electron.Run2010B_skim"
                                ] )
                
    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.photon, samples.electron]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
