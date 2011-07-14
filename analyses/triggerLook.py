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

        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob3_skim")
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Rob4_skim")
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Darren1_skim")
        
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren1")
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren2")
        #out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren3")
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren4")
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren5")
        out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren6")
        return out

    def conclude(self, conf) :
        org = self.organizer(conf)
        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag), blackList = ["lumiHisto","xsHisto","nJobsHisto"])
        pl.plotAll()
