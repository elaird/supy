#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify        
        return [
            specify(name = "Nov4_MJ_skim" ),
            specify(name = "Nov4_J_skim"  ),
            specify(name = "Nov4_J_skim2"),
            specify(name = "Nov4_JM_skim" ),
            specify(name = "Nov4_JMT_skim"),
            specify(name = "Nov4_JMT_skim2"),
            ]
                
    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.photon]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
