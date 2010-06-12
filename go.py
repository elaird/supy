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
#name="MetPasSkim"
#name="MetPasSkim1"
#name="MetPasSkim2"
#name="MetPasSpeedTest"

#choose the output directory
outputDir="~"

def makeSampleSpecs(name) :
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

def mergeSplitOutput(looperList) :
    import os
    
    #make dictionary
    parentDict={}
    for iLooper in range(len(looperList)) :
        looper=looperList[iLooper]
        if looper.parentName!=None :
            if looper.parentName in parentDict :
                parentDict[looper.parentName].append(iLooper)
            else :
                parentDict[looper.parentName]=[iLooper]

    #combine output
    for parent in parentDict :
        #print parent,parentDict[parent]
        iSomeLooper=parentDict[parent][0]
        someLooper=looperList[iSomeLooper]
        outputPlotFileName=someLooper.outputPlotFileName.replace(someLooper.name,parent)
        inFileList=""

        for iLooper in parentDict[parent] :
            thisLooper=looperList[iLooper]
            plotFileName=thisLooper.outputPlotFileName
            inFileList+=" "+plotFileName
            for iStep in range(len(someLooper.steps)) :
                print iStep,someLooper.steps[iStep].nTotal,thisLooper.steps[iStep].nTotal
                someLooper.steps[iStep].nTotal+=thisLooper.steps[iStep].nTotal
                someLooper.steps[iStep].nPass +=thisLooper.steps[iStep].nPass
                someLooper.steps[iStep].nFail +=thisLooper.steps[iStep].nFail

        print someLooper.hyphens
        #print parent
        #someLooper.printStats()
                
        cmd="hadd -f "+outputPlotFileName+inFileList+" | grep -v 'Source file' | grep -v 'Target path'"
        #print "hadding",outputPlotFileName,"..."
        os.system(cmd)
        print someLooper.hyphens
        
def loopOverSamples() :
        looperList=[]
        for sample in sampleSpecs :
            looperList.append(base.analysisLooper(sample,outputDir))

        if ("multi" in sys.argv) :
            from multiprocessing import Pool
            pool=Pool(processes=6)
            #pool=Pool(processes=len(looperList))
            pool.map(goFunc,looperList)
        else :
            map(goFunc,looperList)

        mergeSplitOutput(looperList)
        
#set up
sampleSpecs=makeSampleSpecs(name)

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

