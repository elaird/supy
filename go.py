#!/usr/bin/env python
import sys
import base,analyses,plotter

#choose the analysis
name="triggerSkim"
#name="jetAlgoComparison"
#name="metDistLook"
#name="example"
#name="jetKineLook"
#name="deltaPhiLook"
#name="metGroupCleanupLook"
#name="RA1_DiJet"
#name="RA1_NJet"

#choose the output directory
outputDir="~"

#set up
base.globalSetup()
sampleSpecDict=analyses.buildAnalysisDictionary()
sampleSpecs=sampleSpecDict[name]

def goFunc(x) :
    x.go()
    
def loopOverSamples() :
        looperList=[]
        for sample in sampleSpecs :
            looperList.append(base.analysisLooper(sample,outputDir))

        if ("multi" in sys.argv) :
            from multiprocessing import Pool
            #pool=Pool(processes=4)
            pool=Pool(processes=len(looperList))
            pool.map(goFunc,looperList)
        else :
            map(goFunc,looperList)

#loop over samples and make TFiles containing histograms
if ("loop" in sys.argv and not "prof" in sys.argv) :
    loopOverSamples()

#profile the code
if ("prof" in sys.argv and not "multi" in sys.argv) :
    import cProfile
    cProfile.run("loopOverSamples()","resultProfile.out")

#make plots from the output histograms
if ("plot" in sys.argv) :
    plotter.plotAll(name,sampleSpecs,outputDir)

