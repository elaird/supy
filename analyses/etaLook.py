#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class etaLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        jets = ("ic5Jet","Pat")
        outList=[
            steps.progressPrinter(),
            steps.histogrammer("genpthat", 50, 0.0, 250.0,title=";#hat{p_{T}} (GeV);events / bin"),            
            steps.leadingUnCorrJetFilter(jets, 10.0, 10.0, extraHistos = True),
            steps.leadingUnCorrJetFilter(jets, 30.0, 10.0),
            steps.leadingUnCorrJetFilter(jets, 50.0, 10.0),
            steps.leadingUnCorrJetFilter(jets, 60.0, 10.0),
            steps.leadingUnCorrJetFilter(jets, 70.0, 10.0),

           #steps.leadingUnCorrJetFilter(jets, 80.0, 10.0),
           #steps.leadingUnCorrJetFilter(jets, 90.0, 10.0),
           #steps.leadingUnCorrJetFilter(jets,100.0, 10.0),
           #steps.leadingCorrJetFilter(jets, 110.0, 10.0),
           #steps.leadingCorrJetFilter(jets, 110.0,  3.0),

            steps.leadingUnCorrJetFilter(jets, 70.0,  3.0),
            steps.leadingUnCorrJetFilter(jets, 70.0,  2.8),
            steps.leadingUnCorrJetFilter(jets, 70.0,  2.6),
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        outList =[
            #specify(name = "qcd_py6_pt15",          nFilesMax = 3, nEventsMax = -1, color = r.kBlue    ),
            specify(name = "qcd_py6_pt30",          nFilesMax = 3, nEventsMax = -1, color = r.kBlue    ),
            #specify(name = "qcd_py6_pt80",          nFilesMax = 3, nEventsMax = -1, color = r.kBlue    ),
            #specify(name = "qcd_py6_pt170",         nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            #specify(name = "qcd_py6_pt300",         nFilesMax = 1, nEventsMax = 1000, color = r.kBlue    ),
            ]
        return outList

    def conclude(self) :
        org=organizer.organizer( self.sampleSpecs() )
        org.mergeSamples(targetSpec = {"name":"qcd_py6","color":r.kBlue}, sources = ["qcd_py6_pt%d"%i for i in [15,30,80] ])
        org.scale(100.0)

        pl = plotter.plotter(org,
                             psFileName = self.psFileName(""),
                             )
        pl.plotAll()
