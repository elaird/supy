#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

photon = ("photon","Pat")

class photonSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(),
                   steps.multiplicityFilter("%sIndices%s"%photon, nMin = 1),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesPhoton",[photon]) +\
               [calculables.photonIndicesPat(ptMin = 80, flagName = "photonIDIsoRelaxedPat")]

    def listOfSamples(self,params) :
        from samples import specify        
        return [
            specify(name = "Run2010B_MJ_skim3"),
            specify(name = "Run2010B_MJ_skim2"),
            specify(name = "Run2010B_MJ_skim"),
            specify(name = "Run2010B_J_skim2"),
            specify(name = "Run2010B_J_skim"),
            specify(name = "Run2010A_JM_skim"),
            specify(name = "Run2010A_JMT_skim"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
