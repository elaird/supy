#!/usr/bin/env python
import os,sys,copy,cPickle
import utils
from analysisLooper import analysisLooper
import ROOT as r
#####################################
class analysis :
    """base class for an analysis"""
    
    def __init__(self,name="name",outputDir="/tmp/",moduleDefiningLists="lists",listOfSourceFiles=["pragmas.h","helpers.C"]) :
        for arg in ["name","outputDir","moduleDefiningLists","listOfSourceFiles"] :
            exec("self."+arg+"="+arg)

        self.globalSetup()
        self.makeListDictionary()
        self.looperList=[]
        
    def go(self,loop=False,plot=False,profile=False,nCores=1,splitJobsByInputFile=False) :
        if nCores<1 : nCores=1
        
        #possibly parallelize
        if splitJobsByInputFile : self.splitUpLoopers()

        #set up loopers
        self.makeParentDict(self.looperList)

        #loop over samples and make TFiles containing histograms
        if loop and not profile : self.loopOverSamples(nCores)

        #profile the code
        if profile : self.profile(nCores)

        #make plots from the output histograms
        if plot : self.plot()
        
    def globalSetup(self) :
        for sourceFile in self.listOfSourceFiles :
            r.gROOT.LoadMacro(sourceFile+"+")
        r.gROOT.SetStyle("Plain")
        r.gStyle.SetPalette(1)
        r.TH1.SetDefaultSumw2(True)
        r.gErrorIgnoreLevel=2000
        r.gROOT.SetBatch(True)

    def makeListDictionary(self) :
        exec("import "+self.moduleDefiningLists+" as lists")
        #build dictionary of lists
        self.listHolder=lists.listDictionaryHolder()
        self.listHolder.buildDictionary()

    def addSampleSpec(self,listName,sampleName,listOfFileNames=[],isMc=False,nEvents=-1,xs=1.0) :
        listOfSteps=self.listHolder.getSteps(listName,isMc)
        self.looperList.append( analysisLooper(self.outputDir,listOfFileNames,sampleName,nEvents,self.name,listOfSteps,xs) )
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
                                                       looper.xs
                                                       )
                                        )
                outListOfLoopers[-1].doSplitMode(looper.name)
        self.looperList=outListOfLoopers

    def makeParentDict(self,looperList) :
        parentDict={}
        for iLooper in range(len(looperList)) :
            looper=looperList[iLooper]
            if looper.splitMode :
                if looper.parentName in parentDict :
                    parentDict[looper.parentName].append(iLooper)
                else :
                    parentDict[looper.parentName]=[iLooper]
        self.parentDict=parentDict

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
        
    def plot(self) :
        sampleNames=[]
        outputPlotFileNames=[]
        if len(self.parentDict)==0 :
            for looper in self.looperList :
                sampleNames.append(looper.name)
                outputPlotFileNames.append(looper.outputPlotFileName)
        else :
            for parent in self.parentDict :
                sampleNames.append(parent)
                iSomeLooper=self.parentDict[parent][0]
                someLooper=self.looperList[iSomeLooper]
                outputPlotFileNames.append(someLooper.outputPlotFileName.replace(someLooper.name,someLooper.parentName))

        import plotter
        plotter.plotAll(self.name,sampleNames,outputPlotFileNames,self.outputDir)

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
