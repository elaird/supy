#!/usr/bin/env python
import sys,base
base.globalSetup()

#choose the analysis
#name="triggerSkim"
#name="jetAlgoComparison"
#name="metDistLook"
name="example"
#name="jetKineLook"
#name="deltaPhiLook"
#name="metGroupCleanupLook"
#name="Icf_Ra1_DiJet"
#name="Icf_Ra1_NJet"
#name="RecHitTest"
#name="Ra1_NJet"
#name="HcalTechTriggerCheck"
#name="mSugraLook"

#choose the output directory
outputDir="~"

def makeSampleSpecs() :
    import samples,lists,analyses
    #build dictionaries of files and xs
    sampleHolder=samples.sampleDictionaryHolder()
    sampleHolder.buildDictionaries()
    fileListDict=sampleHolder.getFileListDictionary()
    xsDict=sampleHolder.getXsDictionary()

    #build dictionary of lists
    listHolder=lists.listDictionaryHolder()
    listHolder.buildDictionary()
    listDict=listHolder.getDictionary()

    #build dictionary of analyses
    analysisHolder=analyses.analysisDictionaryHolder(fileListDict,xsDict,listDict)
    analysisHolder.buildDictionary()
    sampleSpecs=analysisHolder.getDictionary()[name]
    return sampleSpecs

def goFunc(x) :
    x.go()
    
def loopOverSamples() :
        looperList=[]
        for sample in sampleSpecs :
            looperList.append(base.analysisLooper(sample,outputDir))

        if ("multi" in sys.argv) :
            from multiprocessing import Pool
            pool=Pool(processes=4)
            #pool=Pool(processes=len(looperList))
            pool.map(goFunc,looperList)
        else :
            map(goFunc,looperList)

#set up
sampleSpecs=makeSampleSpecs()

#loop over samples and make TFiles containing histograms
if ("loop" in sys.argv and not "prof" in sys.argv) :
    loopOverSamples()

#profile the code
if ("prof" in sys.argv and not "multi" in sys.argv) :
    import cProfile
    cProfile.run("loopOverSamples()","resultProfile.out")

#make plots from the output histograms
if ("plot" in sys.argv) :
    import plotter
    plotter.plotAll(name,sampleSpecs,outputDir)

