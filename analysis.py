#!/usr/bin/env python
import os,sys,copy,cPickle
import utils,steps
from analysisLooper import analysisLooper
import ROOT as r
#####################################
def globalSetup(listOfSourceFiles=[]) :
    for sourceFile in listOfSourceFiles :
        r.gROOT.LoadMacro(sourceFile+"+")
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.TH1.SetDefaultSumw2(True)
    r.gErrorIgnoreLevel=2000
    r.gROOT.SetBatch(True)
#####################################
globalSetup(listOfSourceFiles=["pragmas.h","helpers.C"])
#####################################
class analysis :
    """base class for an analysis"""
    
    def __init__(self,name="name",outputDir="/tmp/",listOfSteps=[],calculables=[]) :
        for arg in ["name","outputDir"] :
            exec("self."+arg+"="+arg)

        self.listOfSteps=listOfSteps
        self.calculables=calculables
        self.looperList=[]
        
    def loop(self,profile=False,nCores=1,splitJobsByInputFile=False) :
        nCores=max(1,nCores)

        if splitJobsByInputFile : self.splitUpLoopers()

        #prepare loopers
        self.makeParentDict(self.looperList)

        #loop over samples and make TFiles containing histograms
        if not profile :
            self.loopOverSamples(nCores)
        else :
            self.profile(nCores) #profile the code while doing so

    def plot(self) :
        sampleNamesForPlotter=[]
        outputPlotFileNamesForPlotter=[]
        if (not hasattr(self,"parentDict")) or len(self.parentDict)==0 :
            for looper in self.looperList :
                sampleNamesForPlotter.append(looper.name)
                outputPlotFileNamesForPlotter.append(looper.outputPlotFileName)
        else :
            for parent in self.parentDict :
                sampleNamesForPlotter.append(parent)
                iSomeLooper=self.parentDict[parent][0]
                someLooper=self.looperList[iSomeLooper]
                outputPlotFileNamesForPlotter.append(someLooper.outputPlotFileName.replace(someLooper.name,someLooper.parentName))
        
        import plotter
        plotter.plotAll(self.name,sampleNamesForPlotter,outputPlotFileNamesForPlotter,self.outputDir)

    def checkXsAndLumi(self,xs,lumi) :
        if (xs==None and lumi==None) or (xs!=None and lumi!=None) :
            raise Exception("sample must have either a xs or a lumi specified")
        return lumi==None
        
    def addSample(self,sampleName,listOfFileNames=[],nEvents=-1,xs=None,lumi=None) :
        isMc=self.checkXsAndLumi(xs,lumi)

        listOfSteps=[]
        if isMc : listOfSteps=steps.removeStepsForMc(self.listOfSteps)
        else :    listOfSteps=steps.removeStepsForData(self.listOfSteps)

        self.looperList.append( analysisLooper(self.outputDir,listOfFileNames,sampleName,nEvents,self.name,listOfSteps,self.calculables,xs,lumi) )
        return

    def manageNonBinnedSamples(self,ptHatLowerThresholdsAndSampleNames=[],useRejectionMethod=True) :
        if not useRejectionMethod :
            raise Exception("the other method of combining non-binned samples is not yet implemented")
        looperIndexDict={}
        for item in ptHatLowerThresholdsAndSampleNames :
            ptHatLowerThreshold=item[0]
            sampleName=item[1]
            for iLooper in range(len(self.looperList)) :
                looper=self.looperList[iLooper]
                if sampleName==looper.name :
                    looperIndexDict[ptHatLowerThreshold]=iLooper

        ptHatLowerThresholdsAndSampleNames.sort()
        for iItem in range(len(ptHatLowerThresholdsAndSampleNames)) :

            thisPtHatLowerThreshold=ptHatLowerThresholdsAndSampleNames[iItem][0]
            thisLooperIndex=looperIndexDict[thisPtHatLowerThreshold]

            #adjust cross sections
            if iItem<len(ptHatLowerThresholdsAndSampleNames)-1 :
                nextPtHatLowerThreshold=ptHatLowerThresholdsAndSampleNames[iItem+1][0]
                nextLooperIndex=looperIndexDict[nextPtHatLowerThreshold]
                self.looperList[thisLooperIndex].xs-=self.looperList[nextLooperIndex].xs

                if useRejectionMethod :
                    self.looperList[thisLooperIndex].needToConsiderPtHatThresholds=False
                    steps.insertPtHatFilter(self.looperList[thisLooperIndex].steps,nextPtHatLowerThreshold)

            #inform relevant loopers of the ptHat thresholds
            for index in looperIndexDict.values() :
                self.looperList[index].ptHatThresholds.append(float(thisPtHatLowerThreshold))
                if not useRejectionMethod :
                    self.looperList[index].needToConsiderPtHatThresholds=True
        return
    
    def splitUpLoopers(self) :
        outListOfLoopers=[]
        for looper in self.looperList :
            fileIndex=0
            for iFileName in range(len(looper.inputFiles)) :
                outListOfLoopers.append(analysisLooper(looper.outputDir,
                                                       [looper.inputFiles[iFileName]],
                                                       looper.name+"_"+str(iFileName),
                                                       looper.nEvents,
                                                       looper.outputPrefix,
                                                       copy.deepcopy(looper.steps),
                                                       self.calculables,
                                                       looper.xs,
                                                       looper.lumi
                                                       )
                                        )
                outListOfLoopers[-1].doSplitMode(looper.name)
        self.looperList=outListOfLoopers

    def makeParentDict(self,looperList) :
        self.parentDict={}
        for iLooper in range(len(looperList)) :
            looper=looperList[iLooper]
            if looper.splitMode :
                if looper.parentName in self.parentDict :
                    self.parentDict[looper.parentName].append(iLooper)
                else :
                    self.parentDict[looper.parentName]=[iLooper]

    def looperPrint(self,parent,looper) :
        print looper.hyphens
        print parent
        looper.quietMode=False
        looper.printStats()
        print looper.hyphens

    def mergeSplitOutput(self,looperList) :
        #combine output
        for parent in self.parentDict :
            #print parent,parentDict[parent]
            iSomeLooper=self.parentDict[parent][0]
            someLooper=looperList[iSomeLooper]
            outputPlotFileName=someLooper.outputPlotFileName.replace(someLooper.name,parent)
            inFileList=[]
            displayFileList=[]
        
            isFirstLooper=True
            for iLooper in self.parentDict[parent] :
                #add the root file to hadd command
                inFileList.append(looperList[iLooper].outputPlotFileName)

                #read in the step data
                stepDataFileName=os.path.expanduser(looperList[iLooper].outputStepDataFileName)
                stepDataFile=open(stepDataFileName)
                stepDataList=cPickle.load(stepDataFile)
                stepDataFile.close()

                #add stats to those of someLooper
                for i in range(len(someLooper.steps)) :
                    #need to zero in case sample is split but not run in multi mode
                    if isFirstLooper :
                        someLooper.steps[i].nTotal=0
                        someLooper.steps[i].nPass =0
                        someLooper.steps[i].nFail =0
                    someLooper.steps[i].nTotal+=stepDataList[i]["nTotal"]
                    someLooper.steps[i].nPass +=stepDataList[i]["nPass" ]
                    someLooper.steps[i].nFail +=stepDataList[i]["nFail" ]

                    if someLooper.steps[i].__doc__==someLooper.steps[i].displayerStepName :
                        displayFileList.append(stepDataList[i]["outputFileName"])
                isFirstLooper=False

            self.looperPrint(parent,someLooper)
            inFiles=" ".join(inFileList)
            cmd="hadd -f "+outputPlotFileName+" "+inFiles+" | grep -v 'Source file' | grep -v 'Target path'"
            #print cmd
            hAddOut=utils.getCommandOutput2(cmd)
            print hAddOut[:-1]
            print someLooper.hyphens
            if len(displayFileList)>0 :
                outputFileName=displayFileList[0].replace(someLooper.name,someLooper.parentName).replace(".root",".ps")
                utils.psFromRoot(displayFileList,outputFileName,beQuiet=False)
                print someLooper.hyphens

    def profile(self,nCores) :
        if nCores>1 : raise ValueError("to profile, nCores must equal one")
        global runFunc
        runFunc=self.loopOverSamples
        import cProfile
        cProfile.run("analysis.runFunc(1)","resultProfile.out")

    def loopOverSamples(self,nCores) :
        if nCores>1 :
            from multiprocessing import Pool
            pool=Pool(processes=nCores)
            pool.map(utils.goFunc,self.looperList)
        else :
            map(utils.goFunc,self.looperList)
        self.mergeSplitOutput(self.looperList)
