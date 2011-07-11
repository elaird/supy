import os,analysis,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def listOfSteps(self,params) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-167913_7TeV_PromptReco_Collisions11_JSON.txt") #1078/pb

        out = []
        #out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Bryn",   weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1",   weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn2",   weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn3",   weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren1", weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren2", weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren3", weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren4", weights = jw)
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren5", weights = jw)

        #out += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Zoe_skim", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe1_skim", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe2_skim", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Zoe3_skim", weights = jw)
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob1",      weights = jw)
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob2",      weights = jw)
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob3",      weights = jw)
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob4",      weights = jw)
        out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Darren1",   weights = jw)
        
        #out += specify(names = [ "SingleMu.Run2011A-May10-v1.FJ.Burt",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt1",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt2",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt3",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt4",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt5",
        #                         ]) # no json filtering necessary, golden json used
        return out

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.photon, samples.electron]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
