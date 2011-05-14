#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class xsLook(analysis.analysis) :
    def listOfCalculables(self, params) :
        outList  = calculables.zeroArgs()
        return outList
    
    def listOfSteps(self, params) :
        return [
            steps.Print.progressPrinter(),
            steps.Gen.xsHistogrammer(tanBeta = 10.0),
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc]

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "scan_tanbeta10_tanja1", color = r.kRed)

    def conclude(self) :
        #organize
        org = organizer.organizer( self.sampleSpecs() )
        #org.scale()
            
        ##plot
        #pl = plotter.plotter(org,
        #                     psFileName = self.psFileName(),
        #                     doLog = False,
        #                     #compactOutput = True,
        #                     #noSci = True,
        #                     #pegMinimum = 0.1,
        #                     blackList = ["lumiHisto","xsHisto","nJobsHisto"],
        #                     )
        #pl.plotAll()
        
        self.makeXsPlot(org, "", "scan_tanbeta10_tanja1")

    def makeXsPlot(self, org, tag, sampleName) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        def numerAndDenom(org) :
            d = {}
            for selection in org.selections :
                if "nEvents" not in selection : continue
                if "XS" not in selection : continue
                for var in ["nEvents", "XS"] :
                    d[var] = selection[var][sampleIndex(org, sampleName)]
            return d

        histos = numerAndDenom(org)
        result = histos["XS"].Clone("xs")
        result.Divide(histos["nEvents"])

        f = r.TFile("xs_%s.root"%sampleName, "RECREATE")
        result.Write()
        f.Close()
