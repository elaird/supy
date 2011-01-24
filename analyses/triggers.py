#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggers(analysis.analysis) :
    def parameters(self) :
        return { }
    
    def listOfCalculables(self, params) :
        outList  = calculables.zeroArgs()
        return outList
    
    def listOfSteps(self, params) :
        return [
            steps.Print.progressPrinter(),
            steps.Trigger.triggerScan( pattern = r"HLT_Mu\d*($|_v\d*|_HT\d*U|_Jet\d*U)", prescaleRequirement = "prescale==1", tag = "Mu"),
            steps.Trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
            steps.Trigger.triggerScan( pattern = r"HLT_IsoMu\d*", prescaleRequirement = "prescale==1", tag = "IsoMu"),
            steps.Trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
            steps.Trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.muon]

    def listOfSamples(self,params) :
        from samples import specify
        data = specify( names = ["Mu.Run2010A-Nov4ReReco.RECO.Jad",
                                 "Mu.Run2010B-Nov4ReReco.RECO.Jad",
                                 ])#, nFilesMax = 3, nEventsMax = 1000)
        return data

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"Mu2010", "color":r.kBlack}, allWithPrefix="Mu.Run2010")
            org.scale()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 #samplesForRatios = ("2010 Data","standard_model"),
                                 #sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 #doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 #pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()
