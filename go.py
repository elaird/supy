#!/usr/bin/env python
import sys
import base,analyses,plotter

#choose the analysis
name="triggerSkim"
#name="jetAlgoComparison"
#name="example"
#name="jetKineLook"

#choose the output directory
outputDir="~"

#set up
base.globalSetup()
sampleSpecDict=analyses.buildAnalysisDictionary()
sampleSpecs=sampleSpecDict[name]

def loopOverSamples() :
    for sample in sampleSpecs :
        looper=base.analysisLooper(sample,outputDir)
        looper.go()

#loop over samples and make TFiles containing histograms
if (sys.argv.count("loop")>0 and sys.argv.count("prof")==0) :
    loopOverSamples()

#profile the code
if (sys.argv.count("prof")>0) :
    import cProfile
    cProfile.run("loopOverSamples()","resultProfile.out")

#make plots from the output histograms
if (sys.argv.count("plot")>0) :
    plotter.plotAll(name,sampleSpecs,outputDir)

