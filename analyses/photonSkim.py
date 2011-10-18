#!/usr/bin/env python

from core import analysis,utils,organizer
import calculables,steps,samples

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
               [calculables.Photon.Indices(collection = params["photon"], ptMin = 100, flagName = "photonIDLooseFromTwikiPat")]

    def qcdPyNames(self) :
        l = ["80", "120", "170", "300", "470", "600", "800"]
        return ["qcd_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-2], l[1:-1])]

    def gJetPyNames(self) :
        l = ["80", "120", "170", "300", "470", "800"]
        return ["g_jets_py6_pt_%s_%s"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def qcdMgNames(self) :
        l = ["100", "250", "500", "1000", "inf"]
        return ["qcd_mg_ht_%s_%s"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def gJetsMgNames(self) :
        l = ["40", "100", "200", "inf"]
        return ["g_jets_mg_ht_%s_%s_summer11"%(a,b) for a,b in zip(l[:-1], l[1:])]

    def listOfSamples(self,params) :
        from samples import specify
        out = []

        #out += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Darren1")
        #out += specify(names = "Photon.Run2011A-05Aug2011-v1.AOD.Bryn1"    )
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Bryn1"   )
        #out += specify(names = "Photon.Run2011A-PromptReco-v6.AOD.Bryn1"   )
        #out += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn1"   )
        #out += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn2"   )
        #out += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.Bryn3"   )

        #out += specify(names = self.qcdMgNames())
        out += specify(names = self.gJetsMgNames())

        return out
    
        #return specify(names = "tt_tauola_mg") +\
        #       specify(names = "w_jets_mg") +\
        #       specify(names = "dyll_jets_mg")

    def listOfSampleDictionaries(self) :
        return [samples.JetMET.jetmet, samples.Photon.photon, samples.MC.mc]

    def conclude(self, conf) :
        org = self.organizer(conf)
        utils.printSkimResults(org)
