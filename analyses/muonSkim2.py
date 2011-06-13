#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

muon = ("muon","PF")

class muonSkim2(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(),
                   steps.Filter.pt("%sP4%s"%muon, min = 24, indices = "%sIndicesAnyIso%s"%muon, index = 0),
                   steps.Filter.absEta("%sP4%s"%muon, max = 2.2, indices = "%sIndicesAnyIso%s"%muon, index = 0),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return (calculables.zeroArgs() +
                calculables.fromCollections(calculables.Muon,[muon]) +
                [calculables.Muon.Indices( muon, ptMin = 10, combinedRelIsoMax = 0.15)] )
    
    def listOfSamples(self,params) :
        return samples.specify(names = ["SingleMu.Run2011A-PR-v4.FJ.Burt",
                                        "SingleMu.Run2011A-May10-v1.FJ.Burt"])

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.mc]

    def conclude(self,conf) :
        org = self.organizer(conf)
        utils.printSkimResults(org)
