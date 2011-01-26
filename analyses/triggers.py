#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggers(analysis.analysis) :
    def parameters(self) :
        return { "muon" : ("muon","Pat") }
    
    def listOfCalculables(self, params) :
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [params["muon"]])
        outList +=[calculables.Muon.Indices( params["muon"], ptMin = 5, combinedRelIsoMax = 0.15),
                   ]
        return outList
    
    def listOfSteps(self, params) :
        return (
            [steps.Print.progressPrinter()] +
            steps.Other.multiplicityPlotFilter("%sIndices%s"%params["muon"], nMin = 1, xlabel = "N muons") +
            [steps.Trigger.triggerScan( pattern = r"HLT_Mu\d*($|_v\d*|_HT\d*U|_Jet\d*U)", prescaleRequirement = "prescale==1", tag = "Mu"),
             steps.Trigger.triggerScan( pattern = r"HLT_Mu\d($|\d($|_v\d*))", prescaleRequirement = "True", tag = "MuAll"),
             steps.Trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
             steps.Trigger.triggerScan( pattern = r"HLT_IsoMu\d*", prescaleRequirement = "prescale==1", tag = "IsoMu"),
             steps.Trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
             steps.Trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
             steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%params["muon"], (50,0,25), "HLT_Mu9",["HLT_Mu%d"%d for d in [5,3]]),
             steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%params["muon"], (50,0,25), "HLT_Mu15_v1",["HLT_Mu%d"%d for d in [9,7,5,3]]),
             ])
    
    def listOfSampleDictionaries(self) :
        return [samples.muon,samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        data = specify(# nFilesMax = 32, nEventsMax = 40000,
                        names = ["Mu.Run2010A-Nov4ReReco.RECO.Jad",
                                 "Mu.Run2010B-Nov4ReReco.RECO.Jad",
                                 ])
        return data

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"Mu2010A", "color":r.kBlack}, allWithPrefix="Mu.Run2010A")
            org.mergeSamples(targetSpec = {"name":"Mu2010B", "color":r.kRed}, allWithPrefix="Mu.Run2010B")
            #org.scale()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 #samplesForRatios = ("2010 Data","standard_model"),
                                 #sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 #pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()
