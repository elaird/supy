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
        return [samples.HT.ht]

    def listOfSamples(self,params) :
        from samples import specify
        out = []

        out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Darren1", )
        out += specify(names = "HT.Run2011A-05Aug2011-v1.AOD.Bryn1",     )
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1",    )
        out += specify(names = "HT.Run2011A-PromptReco-v6.AOD.Bryn1",    )
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn1",    )
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn2",    )
        out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.Bryn3",    )

        return out

    def conclude(self, conf) :
        org = self.organizer(conf)
        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag), blackList = ["lumiHisto","xsHisto","nJobsHisto"])
        pl.plotAll()
