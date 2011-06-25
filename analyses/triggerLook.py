#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggerLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        return [
            steps.Trigger.Counts(),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.muon]

    def listOfSamples(self,params) :
        from samples import specify
        out = []
        #out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Bryn")
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1")
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn2")

        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn3"  )
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren1")
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren2")
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren3")

        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob1_skim")
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob2_skim")
        
        return out

    def conclude(self, conf) :
        org = self.organizer(conf)
        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag), blackList = ["lumiHisto","xsHisto","nJobsHisto"])
        pl.plotAll()
