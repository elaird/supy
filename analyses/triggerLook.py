#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggerLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        return [
            #steps.triggerCounts(["HLT_HT"]),
            steps.hltPrescaleHistogrammer(["HLT_HT100U","HLT_HT120U","HLT_HT140U","HLT_HT150U_v1","HLT_HT150U_v3","HLT_HT160U_v1","HLT_HT160U_v3"]),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        outList = [
            #specify(name = "MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Bryn"),
            specify(name = "Run2010B_MJ_skim3"),
            ]

        ##uncomment for short tests
        #for i in range(len(outList)):
        #    o = outList[i]
        #    outList[i] = specify(name = o.name, color = o.color, markerStyle = o.markerStyle, nFilesMax = 1, nEventsMax = 1000)
        
        return outList
        
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.scale()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"]
                                 )
            pl.plotAll()
