#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class triggers(analysis.analysis) :
    def parameters(self) :
        return { "muon" : ("muon","PF"),
                 "electron":("electron","PF") }
    
    def listOfCalculables(self, pars) :
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [pars["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [pars["electron"]])
        outList +=[calculables.Muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                   calculables.Muon.IndicesAnyIsoIsoOrder(pars['muon'], "CombinedRelativeIso"),
                   calculables.Muon.LeadingIsoAny(pars['muon'], ptMin = 18, iso = "CombinedRelativeIso"),
                   calculables.Electron.Indices( pars["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True)
                   ]
        return outList
    
    def listOfSteps(self, pars) :
        return (
            [steps.Print.progressPrinter(),
             #steps.Filter.absEta("%sP4%s"%pars['muon'], max = 2.1, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             steps.Trigger.triggerScan( pattern = r"HLT_Mu\d*_v\d", prescaleRequirement = "prescale==1", tag = "Mu"),
             steps.Trigger.triggerScan( pattern = r"HLT_Mu\d*_v\d", prescaleRequirement = "True", tag = "MuAll"),
             #steps.Trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
             #steps.Trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
             #steps.Trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
             steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (100,0,50), "HLT_Mu30_v3",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (80,0,40), "HLT_Mu30_v4",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #steps.Filter.pt("%sP4%s"%pars['muon'], min = 18, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v10",["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v9" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v8" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (50,0,25), "HLT_Mu15_v1",["HLT_Mu%d"%d for d in [9,7,5,3]]),
             ])
    
    def listOfSampleDictionaries(self) :
        return [samples.muon,samples.jetmet,samples.electron]

    def listOfSamples(self,pars) :
        return ( samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt4", color = r.kBlue) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt3", color = r.kBlue) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt2", color = r.kGreen) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt1", color = r.kBlack) +
                 samples.specify(names = "SingleMu.Run2011A-May10-v1.FJ.Burt", color = r.kRed ) +
                 [])
        

    def conclude(self,conf) :
        org = self.organizer(conf)
        #org.mergeSamples(targetSpec = {"name":"SingleMu", "color":r.kBlack}, allWithPrefix="SingleMu")
        #org.scale()
        
        #plot
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
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
