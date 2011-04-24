#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggerLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        return [
            steps.Trigger.Counts(),
            #steps.Filter.label("150"),
            #steps.Trigger.hltPrescaleHistogrammer(["HLT_HT150_v2","HLT_HT150_AlphaT0p60_v1","HLT_HT150_AlphaT0p70_v1"]),
            #steps.Filter.label("200"),            
            #steps.Trigger.hltPrescaleHistogrammer(["HLT_HT200_v2","HLT_HT200_AlphaT0p60_v1","HLT_HT200_AlphaT0p65_v1"]),
            #steps.Filter.label("250"),
            #steps.Trigger.hltPrescaleHistogrammer(["HLT_HT250_v2","HLT_HT250_AlphaT0p55_v1","HLT_HT250_AlphaT0p62_v1"]),
            #steps.Filter.label("300"),
            #steps.Trigger.hltPrescaleHistogrammer(["HLT_HT300_v3","HLT_HT300_AlphaT0p52_v1","HLT_HT300_AlphaT0p54_v1"]),
            #steps.Filter.label("350"),
            #steps.Trigger.hltPrescaleHistogrammer(["HLT_HT350_v2","HLT_HT350_AlphaT0p51_v1","HLT_HT350_AlphaT0p53_v1"]),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon]

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = ["Photon.Run2011A-PromptReco-v1.AOD.Henning1","Photon.Run2011A-PromptReco-v1.AOD.Henning2"])
        
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"]
                                 )
            pl.plotAll()
