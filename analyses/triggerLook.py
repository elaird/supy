#!/usr/bin/env python

from core import analysis,organizer,plotter
import steps,calculables,samples
import ROOT as r

class triggerLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        return [
            steps.Trigger.Counts(useCache = True),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.HT.ht, samples.Photon.photon, samples.DoubleMu.mumu]

    def listOfSamples(self,params) :
        from samples import specify
        out = []

        #out += specify(names = "Photon.Run2011A-05Aug2011-v1.AOD.job663")
        #out += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.job662")
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.job664")
        #out += specify(names = "Photon.Run2011A-PromptReco-v6.AOD.job667")
        #out += specify(names = "Photon.Run2011B-PromptReco-v1.AOD.job668")

        out += specify(names = "DoubleMu.Run2011A-05Aug2011-v1.AOD.job663",  )
        out += specify(names = "DoubleMu.Run2011A-May10ReReco-v1.AOD.job662",)
        out += specify(names = "DoubleMu.Run2011A-PromptReco-v4.AOD.job664", )
        out += specify(names = "DoubleMu.Run2011A-PromptReco-v6.AOD.job665", )
        out += specify(names = "DoubleMu.Run2011B-PromptReco-v1.AOD.job666", )

        return out

    def conclude(self, conf) :
        org = self.organizer(conf)
        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag), blackList = ["lumiHisto","xsHisto","nJobsHisto"])
        pl.plotAll()
