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
        jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-163869_7TeV_PromptReco_Collisions11_JSON.txt", acceptFutureRuns = False) #193/pb
        
        out = []
        #out += specify(names = "Photon.Run2011A-PromptReco-v1.AOD.Henning1", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v1.AOD.Henning2", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v2.AOD.Ted1",     weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v2.AOD.Ted2",     weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v2.AOD.Ted3",     weights = jw)
        
        out += specify(names = "HT.Run2011A-PromptReco-v1.AOD.Arlo",     weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v1.AOD.Zoe",      weights = jw)
        out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Arlo",     weights = jw)
        out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Arlo2",    weights = jw)
        out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Robin1",   weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Zoe1",     weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v2.AOD.Zoe2",     weights = jw)

        # out += specify(names = "SingleMu.Run2011A-PR-v2.Robin1", weights = jw )
        # out += specify(names = "SingleMu.Run2011A-PR-v2.Robin2", weights = jw )
        # out += specify(names = "SingleMu.Run2011A-PR-v2.Alex", weights = jw )
        # #out += specify(names = "SingleMu.Run2011A-PR-v2.Burt", weights = jw )

        return out

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.photon, samples.electron]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
