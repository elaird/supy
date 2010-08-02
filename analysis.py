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
    
    def __init__(self,name="name",outputDir="/tmp/",listOfSteps=[],listOfCalculables=[],fileDirectory="susyTree",treeName="tree") :
        for arg in ["name","outputDir"] :
            exec("self."+arg+"="+arg)

        self.hyphens="".ljust(95,"-")
        self.fileDirectory=fileDirectory
        self.treeName=treeName
        
        self.listOfSteps=listOfSteps
        self.listOfCalculables=listOfCalculables
        self.listOfLoopers=[]
        self.mergeRequestForPlotter={}
        
    def loop(self,profile=False,nCores=1,splitJobsByInputFile=False) :
        nCores=max(1,nCores)

        if splitJobsByInputFile : self.splitLoopers()

        #prepare loopers
        self.makeParentDict(self.listOfLoopers)

        #loop over samples and make TFiles containing histograms
        if not profile :
            self.loopOverSamples(nCores)
        else :
            self.profile(nCores) #profile the code while doing so

    def plot(self) :
        sampleNamesForPlotter=[]
        outputPlotFileNamesForPlotter=[]
        if (not hasattr(self,"parentDict")) or len(self.parentDict)==0 :
            for looper in self.listOfLoopers :
                sampleNamesForPlotter.append(looper.name)
                outputPlotFileNamesForPlotter.append(looper.outputPlotFileName)
        else :
            for parent in self.parentDict :
                sampleNamesForPlotter.append(parent)
                iSomeLooper=self.parentDict[parent][0]
                someLooper=self.listOfLoopers[iSomeLooper]
                outputPlotFileNamesForPlotter.append(someLooper.outputPlotFileName.replace(someLooper.name,someLooper.parentName))
        
        import plotter
        plotter.plotAll(self.name,sampleNamesForPlotter,outputPlotFileNamesForPlotter,self.mergeRequestForPlotter,self.outputDir,self.hyphens)

    def checkXsAndLumi(self,xs,lumi) :
        if (xs==None and lumi==None) or (xs!=None and lumi!=None) :
            raise Exception("sample must have either a xs or a lumi specified")
        return lumi==None
        
    def addSample(self,sampleName,listOfFileNames=[],nEvents=-1,xs=None,lumi=None) :
        isMc=self.checkXsAndLumi(xs,lumi)

        listOfSteps=[]
        if isMc : listOfSteps=steps.removeStepsForMc(self.listOfSteps)
        else :    listOfSteps=steps.removeStepsForData(self.listOfSteps)

        self.listOfLoopers.append(analysisLooper(self.fileDirectory,
                                              self.treeName,
                                              self.hyphens,
                                              self.outputDir,
                                              listOfFileNames,
                                              sampleName,
                                              nEvents,
                                              self.name,
                                              listOfSteps,
                                              self.listOfCalculables,
                                              xs,
                                              lumi)
                               )
        return

    def manageNonBinnedSamples(self,ptHatLowerThresholdsAndSampleNames=[],mergeIntoOnePlot=False,mergeName="",useRejectionMethod=True) :
        if not useRejectionMethod :
            raise Exception("the other method of combining non-binned samples is not yet implemented")
        looperIndexDict={}
        mergeDict={}
        for item in ptHatLowerThresholdsAndSampleNames :
            ptHatLowerThreshold=item[0]
            sampleName=item[1]

            #find the associated looper
            for iLooper in range(len(self.listOfLoopers)) :
                looper=self.listOfLoopers[iLooper]
                if sampleName==looper.name :
                    looperIndexDict[ptHatLowerThreshold]=iLooper

            mergeDict[sampleName]=mergeName
        #inform the plotter of the merge request
        if mergeIntoOnePlot : self.mergeRequestForPlotter=mergeDict

        ptHatLowerThresholdsAndSampleNames.sort()
        for iItem in range(len(ptHatLowerThresholdsAndSampleNames)) :

            thisPtHatLowerThreshold=ptHatLowerThresholdsAndSampleNames[iItem][0]
            thisLooperIndex=looperIndexDict[thisPtHatLowerThreshold]

            #adjust cross sections
            if iItem<len(ptHatLowerThresholdsAndSampleNames)-1 :
                nextPtHatLowerThreshold=ptHatLowerThresholdsAndSampleNames[iItem+1][0]
                nextLooperIndex=looperIndexDict[nextPtHatLowerThreshold]
                self.listOfLoopers[thisLooperIndex].xs-=self.listOfLoopers[nextLooperIndex].xs

                if useRejectionMethod :
                    self.listOfLoopers[thisLooperIndex].needToConsiderPtHatThresholds=False
                    steps.insertPtHatFilter(self.listOfLoopers[thisLooperIndex].steps,nextPtHatLowerThreshold)

            #inform relevant loopers of the ptHat thresholds
            for index in looperIndexDict.values() :
                self.listOfLoopers[index].ptHatThresholds.append(float(thisPtHatLowerThreshold))
                if not useRejectionMethod :
                    self.listOfLoopers[index].needToConsiderPtHatThresholds=True
        return
    
    def splitLoopers(self) :
        outListOfLoopers=[]
        for looper in self.listOfLoopers :
            fileIndex=0
            for iFileName in range(len(looper.inputFiles)) :
                outListOfLoopers.append(analysisLooper(self.fileDirectory,
                                                       self.treeName,
                                                       self.hyphens,
                                                       looper.outputDir,
                                                       [looper.inputFiles[iFileName]],
                                                       looper.name+"_"+str(iFileName),
                                                       looper.nEvents,
                                                       looper.outputPrefix,
                                                       copy.deepcopy(looper.steps),
                                                       self.listOfCalculables,
                                                       looper.xs,
                                                       looper.lumi
                                                       )
                                        )
                outListOfLoopers[-1].doSplitMode(looper.name)
        self.listOfLoopers=outListOfLoopers

    def makeParentDict(self,listOfLoopers) :
        self.parentDict={}
        for iLooper in range(len(listOfLoopers)) :
            looper=listOfLoopers[iLooper]
            if looper.splitMode :
                if looper.parentName in self.parentDict :
                    self.parentDict[looper.parentName].append(iLooper)
                else :
                    self.parentDict[looper.parentName]=[iLooper]

    def looperPrint(self,parent,looper) :
        print self.hyphens
        print parent
        looper.quietMode=False
        looper.printStats()
        print self.hyphens

    def mergeSplitOutput(self,listOfLoopers) :
        #combine output
        for parent in self.parentDict :
            #print parent,parentDict[parent]
            iSomeLooper=self.parentDict[parent][0]
            someLooper=listOfLoopers[iSomeLooper]
            outputPlotFileName=someLooper.outputPlotFileName.replace(someLooper.name,parent)
            inFileList=[]
            displayFileList=[]
        
            isFirstLooper=True
            for iLooper in self.parentDict[parent] :
                #add the root file to hadd command
                inFileList.append(listOfLoopers[iLooper].outputPlotFileName)

                #read in the step data
                stepDataFileName=os.path.expanduser(listOfLoopers[iLooper].outputStepDataFileName)
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
            print self.hyphens
            if len(displayFileList)>0 :
                outputFileName=displayFileList[0].replace(someLooper.name,someLooper.parentName).replace(".root",".ps")
                utils.psFromRoot(displayFileList,outputFileName,beQuiet=False)
                print self.hyphens

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
            pool.map(utils.goFunc,self.listOfLoopers)
        else :
            map(utils.goFunc,self.listOfLoopers)
        self.mergeSplitOutput(self.listOfLoopers)
