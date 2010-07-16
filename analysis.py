#!/usr/bin/env python
import os,sys,copy,cPickle
import base,utils
import ROOT as r
#####################################
class analysis :
    """base class for an analysis"""
    
    def __init__(self,name="name",outputDir="/tmp/",moduleDefiningSamples="samples",moduleDefiningLists="lists",listOfSourceFiles=["SusyCAFpragmas.h","helpers.C"]) :
        for arg in ["name","outputDir","moduleDefiningSamples","moduleDefiningLists","listOfSourceFiles"] :
            exec("self."+arg+"="+arg)

        self.globalSetup()
        self.makeSampleAndListDictionaries()
        self.sampleSpecs=[]
        
    def go(self,loop=False,plot=False,profile=False,nCores=1,splitJobsByInputFile=False) :
        if nCores<1 : nCores=1
        
        #possibly parallelize
        if splitJobsByInputFile : self.splitUpSpecs()

        #set up loopers
        self.makeLooperList()

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

    def makeSampleAndListDictionaries(self) :
        exec("import "+self.moduleDefiningSamples+" as samples")
        exec("import "+self.moduleDefiningLists+" as lists")

        #build dictionaries of files and xs
        sampleHolder=samples.sampleDictionaryHolder()
        sampleHolder.buildDictionaries()
        self.fileListDict=sampleHolder.getFileListDictionary()
        self.xsDict=sampleHolder.getXsDictionary()

        #build dictionary of lists
        self.listHolder=lists.listDictionaryHolder()
        self.listHolder.buildDictionary()

    def addSampleSpec(self,sampleName="",listName="",isMc=False,nEvents=-1) :
        outputPrefix=sampleName
        listOfSteps=self.listHolder.getSteps(listName,isMc)
        self.sampleSpecs.append( base.sampleSpecification(self.fileListDict,outputPrefix,nEvents,self.name,listOfSteps) )
        return

    def splitUpSpecs(self) :
        outListOfSpecs=[]
        for spec in self.sampleSpecs :
            fileIndex=0
            for iFileName in range(len(self.fileListDict[spec.name])) :
                suffix="_"+str(iFileName)
                newName=spec.name+suffix
                if newName in self.fileListDict :
                    raise NameError(newName," already in fileListDict")
                self.fileListDict[newName]=[self.fileListDict[spec.name][iFileName]]
                outListOfSpecs.append(base.sampleSpecification(self.fileListDict,
                                                               newName,
                                                               spec.nEvents,
                                                               spec.outputPrefix,
                                                               copy.deepcopy(spec.steps),
                                                               spec.xs
                                                               )
                                      )
                outListOfSpecs[-1].doSplitMode(spec.name)
        self.sampleSpecs=outListOfSpecs

    def makeLooperList(self) :
        self.looperList=[base.analysisLooper(sample,self.outputDir) for sample in self.sampleSpecs]
        self.makeParentDict(self.looperList)

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
