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

    def qcdPyNames(self) :
        l = ["80", "120", "170", "300", "470", "600", "800"]
        return ["qcd_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-2], l[1:-1])]

    def gJetPyNames(self) :
        l = ["80", "120", "170", "300", "470", "800"]
        return ["g_jets_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "Photon.Run2011A-PromptReco-v2.AOD.Ted2")

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
