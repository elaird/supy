#!/usr/bin/env python
import os,sys,copy,cPickle
import utils
from analysisLooper import analysisLooper
import ROOT as r
#####################################
class analysis :
    """base class for an analysis"""
    
    def __init__(self,name="name",outputDir="/tmp/",listName="",calculables=[],moduleDefiningLists="lists",listOfSourceFiles=["pragmas.h","helpers.C"]) :
        for arg in ["name","outputDir","moduleDefiningLists","listOfSourceFiles"] :
            exec("self."+arg+"="+arg)

        self.globalSetup()
        self.makeListDictionary()
        self.listName=listName
        self.calculables=calculables
        self.looperList=[]
        self.needToSetup=True
        
    def setup(self) :
        if not self.needToSetup : return

        #prepare loopers
        self.makeParentDict(self.looperList)

        #prepare these for the plotter
        self.sampleNamesForPlotter=[]
        self.outputPlotFileNamesForPlotter=[]
        if len(self.parentDict)==0 :
            for looper in self.looperList :
                self.sampleNamesForPlotter.append(looper.name)
                self.outputPlotFileNamesForPlotter.append(looper.outputPlotFileName)
        else :
            for parent in self.parentDict :
                self.sampleNamesForPlotter.append(parent)
                iSomeLooper=self.parentDict[parent][0]
                someLooper=self.looperList[iSomeLooper]
                self.outputPlotFileNamesForPlotter.append(someLooper.outputPlotFileName.replace(someLooper.name,someLooper.parentName))
        self.needToSetup=False

    def splitJobsByInputFile(self) :
        self.splitUpLoopers()
        
    def loop(self,profile=False,nCores=1) :
        nCores=max(1,nCores)
        self.setup()
        #loop over samples and make TFiles containing histograms
        if not profile :
            self.loopOverSamples(nCores)
        else :
            self.profile(nCores) #profile the code while doing so

    def plot(self) :
        self.setup()        
        import plotter
        plotter.plotAll(self.name,self.sampleNamesForPlotter,self.outputPlotFileNamesForPlotter,self.outputDir)

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

    def checkXsAndLumi(self,xs,lumi) :
        if (xs==None and lumi==None) or (xs!=None and lumi!=None) :
            raise Exception("sample must have either a xs or a lumi specified")
        return lumi==None
        
    def addSample(self,sampleName,listOfFileNames=[],nEvents=-1,xs=None,lumi=None) :
        isMc=self.checkXsAndLumi(xs,lumi)
        
        listOfSteps=self.listHolder.getSteps(self.listName,isMc)
        self.looperList.append( analysisLooper(self.outputDir,listOfFileNames,sampleName,nEvents,self.name,listOfSteps,self.calculables,xs,lumi) )
        return

    def manageNonBinnedSamples(self,ptHatLowerThresholdsAndSampleNames=[]) :
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

            #inform relevant loopers of the ptHat thresholds
            for index in looperIndexDict.values() :
                self.looperList[index].ptHatThresholds.append(float(thisPtHatLowerThreshold))
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
