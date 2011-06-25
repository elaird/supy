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
               [calculables.Photon.Indices(collection = params["photon"], ptMin = 100, flagName = "photonIDNoIsoReqPat")]

    def qcdPyNames(self) :
        l = ["80", "120", "170", "300", "470", "600", "800"]
        return ["qcd_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-2], l[1:-1])]

    def gJetPyNames(self) :
        l = ["80", "120", "170", "300", "470", "800"]
        return ["g_jets_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def listOfSamples(self,params) :
        from samples import specify
        out = []

        #out += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Henning.L1")
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Ted1.L1"    )
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Ted2.L1"    )

        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe2")
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob1")
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob2")
        
        #out += specify(names = "g_jets_mg_ht_40_100.L1" )
        #out += specify(names = "g_jets_mg_ht_100_200.L1")
        #out += specify(names = "g_jets_mg_ht_200_inf.L1")
        return out
    
        #return specify(names = "tt_tauola_mg") +\
        #       specify(names = "w_jets_mg") +\
        #       specify(names = "dyll_jets_mg")

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self, conf) :
        org = self.organizer(conf)
        utils.printSkimResults(org)
