#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer,plotter

class checkHandles(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[steps.Print.progressPrinter(2,300),
                  #steps.Other.handleChecker(),
                  #steps.Jet.preIdJetPtSelector(("ak5Jet","Pat"), 100.0, 0),
                  steps.Other.iterHistogrammer("ak5JetCorrectedP4Pat", 100, 0.0, 100.0, title=";ak5 jet corrected p_{T} (GeV);jets / bin", funcString="lambda x:x.pt()"),
                  steps.Other.iterHistogrammer("genak5GenJetsP4", 100, 0.0, 100.0, title=";gen. ak5 jet corrected p_{T} (GeV);jets / bin", funcString="lambda x:x.pt()"),
                  steps.Other.iterHistogrammer("genStatus1P4", 100, 0.0, 100.0, title=";status 1 gen. particle p_{T} (GeV);jets / bin", funcString="lambda x:x.pt()"),
                  ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "41testMc")

    def listOfSampleDictionaries(self) :
        return [samples.jetmet]

    def conclude(self) :
        org = organizer.organizer(self.sampleSpecs())
        pl = plotter.plotter(org, psFileName = self.psFileName(), doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"])
        pl.plotAll()
