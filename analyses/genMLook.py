#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class genMLook(analysis.analysis) :
    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSteps(self,params) :
        outList=[
            steps.Print.progressPrinter(),
            steps.Gen.genParticlePrinter(minPt = -1.0, minStatus = 3),
            #steps.Gen.genMassHistogrammer(),
            #steps.Gen.genSHatHistogrammer(),
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "t2", nFilesMax = 1, nEventsMax = 10, color = r.kYellow-3)

#    def conclude(self) :
#        org=organizer.organizer( self.sampleSpecs() )
#        org.scale(100.0)
#
#        pl = plotter.plotter(org,
#                             psFileName = self.psFileName(""),
#                             )
#        pl.plotAll()
