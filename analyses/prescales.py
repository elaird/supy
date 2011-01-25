#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class prescales(analysis.analysis) :
    def parameters(self) :
        return {"jets" : ("ak5Jet","Pat"),
                "triggers": ("HLT_HT100U","HLT_HT120U","HLT_HT140U","HLT_HT150U_v1","HLT_HT150U_v3","HLT_HT160U_v1","HLT_HT160U_v3")
                }
    
    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[params["jets"]]) +\
               [calculables.jetIndices( params["jets"], ptMin = 50, etaMax = 3.0, flagName = "JetIDloose")]
    
    def listOfSteps(self,params) :
        return [
            steps.progressPrinter(),
            steps.jetPtSelector(params["jets"],100.0,0),
            steps.jetPtSelector(params["jets"],100.0,1),
            steps.jetEtaSelector(params["jets"],2.5,0),
            steps.lowestUnPrescaledTrigger(params["triggers"]),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            
            steps.hltPrescaleHistogrammer(params["triggers"]),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        return [
            specify(name = "Run2010B_MJ_skim4", color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_MJ_skim3", color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_MJ_skim2", color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_MJ_skim",  color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_J_skim2",  color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010B_J_skim",   color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JM_skim",  color = r.kBlack   , markerStyle = 20),
            specify(name = "Run2010A_JMT_skim", color = r.kBlack   , markerStyle = 20)
            ]
        
    
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            org=organizer.organizer( self.sampleSpecs(tag) )
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"]
                                 )
            pl.plotAll()

