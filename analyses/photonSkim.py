#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

class photonSkim(analysis.analysis) :
    def parameters(self) :
        return {"photon": ("photon", "Pat")}

    def listOfSteps(self, params) :
        stepList=[ steps.Print.progressPrinter(),
                   steps.Other.multiplicityFilter("%sIndices%s"%params["photon"], nMin = 1),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.Photon,[params["photon"]]) +\
               [calculables.Photon.Indices(collection = params["photon"], ptMin = 80, flagName = "photonIDNoIsoReqPat")]

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = ["Photon.Run2011A-PromptReco-v2.AOD.Ted"])# +\
               #specify(names = ["HT.Run2011A-PromptReco-v1.AOD.Henning"]) +\
               #specify(names = ["HT.Run2011A-PromptReco-v1.AOD.Georgia"]) +\
               #specify(names = ["qcd_mg_ht_100_250", "qcd_mg_ht_250_500", "qcd_mg_ht_500_1000", "qcd_mg_ht_1000_inf"]) +\
               #specify(names = ["g_jets_mg_ht_40_100", "g_jets_mg_ht_100_200", "g_jets_mg_ht_200_inf"])

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
