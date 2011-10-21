from core.analysis import analysis
import os,steps,samples,calculables

class jsonMaker(analysis) :
    def listOfSteps(self,params) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        jwPrompt = calculables.Other.jsonWeight("cert/Cert_160404-177515_7TeV_PromptReco_Collisions11_JSON.txt")
        jwMay = calculables.Other.jsonWeight("cert/Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON_v3.txt")
        jwAug = calculables.Other.jsonWeight("cert/Cert_170249-172619_7TeV_ReReco5Aug_Collisions11_JSON_v2.txt")

        out = []

        out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Darren1", weights = jwMay)
        out += specify(names = "HT.Run2011A-05Aug2011-v1.AOD.Bryn1",     weights = jwAug)
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1",    weights = jwPrompt)
        out += specify(names = "HT.Run2011A-PromptReco-v6.AOD.Bryn1",    weights = jwPrompt)
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn1",    weights = jwPrompt)
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn2",    weights = jwPrompt)
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn3",    weights = jwPrompt)

        #out += specify(names = [ "SingleMu.Run2011A-May10-v1.FJ.Burt",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt1",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt2",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt3",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt4",
        #                         "SingleMu.Run2011A-PR-v4.FJ.Burt5",
        #                         ]) # no json filtering necessary, golden json used
        return out

    def listOfSampleDictionaries(self) :
        return [samples.HT.ht, samples.Muon.muon, samples.Photon.photon, samples.Electron.electron]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
