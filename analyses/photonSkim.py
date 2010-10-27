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
            specify(name = "EG.Run2010A-Sep17ReReco_v2.RECO"),
            specify(name = "Photon.Run2010B-PromptReco-v2.RECO.Alex"),
            specify(name = "Photon.Run2010B-PromptReco-v2.RECO.Martyn"),
            specify(name = "Photon.Run2010B-PromptReco-v2.RECO.Robin"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
