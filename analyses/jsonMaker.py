#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        return [ steps.progressPrinter(2,300),
                 steps.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        return [samples.specify(name = "Jet.Run2010B-PromptReco-v2.RECO.Burt_skim")]
                

    def listOfSampleDictionaries(self) :
        return [samples.jetmet]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
