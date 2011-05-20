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
        outList +=[calculables.Muon.Indices( pars["muon"], ptMin = 5, combinedRelIsoMax = 0.15),
                   calculables.Electron.Indices( pars["electron"], ptMin = 5, simpleEleID = "95", useCombinedIso = True)
                   ]
        return outList
    
    def listOfSteps(self, pars) :
        return (
            [steps.Print.progressPrinter(),
             steps.Filter.multiplicity("%sIndices%s"%pars["muon"], min = 1),
             steps.Trigger.triggerScan( pattern = r"HLT_Mu\d*($|_v\d*|_HT\d*U|_Jet\d*U)", prescaleRequirement = "prescale==1", tag = "Mu"),
             steps.Trigger.triggerScan( pattern = r"HLT_IsoMu\d*", prescaleRequirement = "prescale==1", tag = "IsoMu"),
             steps.Trigger.triggerScan( pattern = r"HLT_Mu\d($|\d($|_v\d*))", prescaleRequirement = "True", tag = "MuAll"),
             #steps.Trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
             #steps.Trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
             #steps.Trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
             steps.Filter.label("mu24_v1"), steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (80,0,40), "HLT_Mu24_v1",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(15,3),(15,2)]]),
             steps.Filter.label("mu24_v2"), steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (80,0,40), "HLT_Mu24_v2",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(15,3),(15,2)]]),
             #steps.Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (50,0,25), "HLT_Mu15_v1",["HLT_Mu%d"%d for d in [9,7,5,3]]),
             ])
    
    def listOfSampleDictionaries(self) :
        return [samples.muon,samples.jetmet,samples.electron]

    def listOfSamples(self,pars) :
        from samples import specify
        jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-163869_7TeV_PromptReco_Collisions11_JSON.txt", acceptFutureRuns = False) #193/pb
        return ( specify(names="SingleMu.Run2011A-PR-v2.Robin1", weights = jw, overrideLumi = 87.31, color = r.kBlack) +
                 specify(names="SingleMu.Run2011A-PR-v2.Robin2", weights = jw, overrideLumi = 79.34, color = r.kRed) +
                 specify(names="SingleMu.Run2011A-PR-v2.Alex", weights = jw,   overrideLumi = 12.27, color = r.kBlue) +
                 #specify(names="SingleMu.Run2011A-PR-v2.Burt", weights = jw) +
                 [])
        
        

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            org=organizer.organizer( self.sampleSpecs(tag) )
            #org.mergeSamples(targetSpec = {"name":"SingleMu", "color":r.kBlack}, allWithPrefix="SingleMu")
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
