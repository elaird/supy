#!/usr/bin/env python
import os,sys,copy,cPickle,collections
sys.argv.append("-b")#set batch mode before importing ROOT
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
    
    def __init__(self,name="name",outputDir="/tmp/",listOfSteps=[],listOfCalculables=[],
                 mainTree=("susyTree","tree"),
                 otherTreesToKeepWhenSkimming=[("lumiTree","tree")],
                 printNodesUsed=False) :
        for arg in ["name","outputDir"] :
            exec("self."+arg+"="+arg)

        self.hyphens="".ljust(95,"-")
        self.fileDirectory=mainTree[0]
        self.treeName=mainTree[1]
        self.otherTreesToKeepWhenSkimming=otherTreesToKeepWhenSkimming
        self.printNodesUsed=printNodesUsed
        
        self.listOfSteps=listOfSteps
        self.listOfCalculables=listOfCalculables
        self.listOfLoopers=[]
        self.listOfOutputPlotFileNames=[]

        self.histogramMergeRequests=[]
        self.histogramMergeKeepSources=[]

        self.hasLooped=False
        
    def loop(self, profile = False, nCores = 1, splitJobsByInputFile = None) :
        nCores = max(1,nCores)
        if splitJobsByInputFile!=False and (splitJobsByInputFile or nCores>1) :
            self.splitLoopers()

        #prepare loopers
        self.makeParentDict(self.listOfLoopers)

        #loop over samples and make TFiles containing histograms
        if not profile :
            self.loopOverSamples(nCores)
        else :
            self.profile(nCores) #profile the code while doing so
        self.hasLooped=True            

    def producePlotFileNamesDict(self) :
        outDict={}
        if (not hasattr(self,"parentDict")) or len(self.parentDict)==0 :
            for looper in self.listOfLoopers :
                outDict[looper.name]=looper.outputPlotFileName
        else :
            for parent in self.parentDict :
                iSomeLooper=self.parentDict[parent][0]
                someLooper=self.listOfLoopers[iSomeLooper]
                outDict[parent]=someLooper.outputPlotFileName.replace(someLooper.name,someLooper.parentName)
        return outDict

    def organizeHistograms(self,
                           scaleHistograms=True,
                           scaleByAreaRatherThanByXs=False,
                           multipleDisjointDataSamples=False,                           
                           lumiToUseInAbsenceOfData=100,#/pb
                           ) :
        import histogramOrganizer
        return histogramOrganizer.go(self.producePlotFileNamesDict(),
                                     scaleHistograms,
                                     scaleByAreaRatherThanByXs,
                                     multipleDisjointDataSamples,
                                     lumiToUseInAbsenceOfData,
                                     self.histogramMergeRequests,
                                     self.histogramMergeKeepSources,
                                     )

    def checkXsAndLumi(self,xs,lumi) :
        if (xs==None and lumi==None) or (xs!=None and lumi!=None) :
            raise Exception("sample must have either a xs or a lumi specified")
        return lumi==None

    def makeOutputPlotFileName(self,sampleName,isChild=False) :
        answer=self.outputDir+"/"+self.name+"_"+sampleName+"_plots.root"
        if not isChild :
            self.listOfOutputPlotFileNames.append(answer)
        return answer
        
    def addSample(self, sampleName, listOfFileNames = [], nEvents = -1, nMaxFiles = -1, xs = None, lumi = None, computeEntriesForReport = False) :
        isMc = self.checkXsAndLumi(xs,lumi)
        if (not isMc) and (nEvents!=-1 or nMaxFiles!=-1) :
            print "Warning, not running over full data sample: wrong lumi?"

        if nMaxFiles >= 0 :
            listOfFileNames = listOfFileNames[:nMaxFiles]

        listOfSteps = []
        if isMc : listOfSteps = steps.removeStepsForMc(self.listOfSteps)
        else :    listOfSteps = steps.removeStepsForData(self.listOfSteps)

        self.listOfLoopers.append(analysisLooper(self.fileDirectory,
                                                 self.treeName,
                                                 self.otherTreesToKeepWhenSkimming,
                                                 self.hyphens,
                                                 self.outputDir,
                                                 listOfFileNames,
                                                 sampleName,
                                                 nEvents,
                                                 self.makeOutputPlotFileName(sampleName),
                                                 listOfSteps,
                                                 self.listOfCalculables,
                                                 xs,
                                                 lumi,
                                                 computeEntriesForReport,
                                                 self.printNodesUsed
                                                 )
                               )
        return

    def mergeHistograms(self,source=[],target="", keepSourceHistograms=False) :
        outDict={}
        for item in source :
            outDict[item]=target
        self.histogramMergeRequests.append(outDict)
        self.histogramMergeKeepSources.append(keepSourceHistograms)

    def mergeAllHistogramsExceptSome(self,dontMergeList=[],target="",keepSourceHistograms=True) :
        fileNameDict=self.producePlotFileNamesDict()
        sources=[]
        for sampleName in fileNameDict.keys() :
            if sampleName in dontMergeList : continue
            sources.append(sampleName)
        self.mergeHistograms(sources,target,keepSourceHistograms)
        
    def manageNonBinnedSamples(self,ptHatLowerThresholdsAndSampleNames=[],useRejectionMethod=True) :
        if not useRejectionMethod :
            raise Exception("the other method of combining non-binned samples is not yet implemented")
        looperIndexDict={}
        for item in ptHatLowerThresholdsAndSampleNames :
            ptHatLowerThreshold=item[0]
            sampleName=item[1]

            #find the associated looper
            for iLooper in range(len(self.listOfLoopers)) :
                looper=self.listOfLoopers[iLooper]
                if sampleName==looper.name :
                    looperIndexDict[ptHatLowerThreshold]=iLooper
                for step in looper.steps :
                    if step.__doc__==step.skimmerStepName :
                        raise Exception("do not manage non-binned samples when skimming")


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
                sampleName=looper.name+"_"+str(iFileName)
                outListOfLoopers.append(analysisLooper(self.fileDirectory,
                                                       self.treeName,
                                                       self.otherTreesToKeepWhenSkimming,                                                       
                                                       self.hyphens,
                                                       looper.outputDir,
                                                       [looper.inputFiles[iFileName]],
                                                       sampleName,
                                                       looper.nEvents,
                                                       self.makeOutputPlotFileName(sampleName,isChild=True),
                                                       copy.deepcopy(looper.steps),
                                                       self.listOfCalculables,
                                                       looper.xs,
                                                       looper.lumi,
                                                       looper.computeEntriesForReport,
                                                       looper.printNodesUsed
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
            displayFileDict=collections.defaultdict(list)
            skimmerFileDict=collections.defaultdict(list)
            runLsDict=collections.defaultdict(list)
            jsonFileDict=collections.defaultdict(list)
            
            isFirstLooper=True
            for iLooper in self.parentDict[parent] :
                #add the root file to hadd command
                inFileList.append(listOfLoopers[iLooper].outputPlotFileName)

                #read in the step and calculable data
                stepAndCalculableDataFileName=os.path.expanduser(listOfLoopers[iLooper].outputStepAndCalculableDataFileName)
                stepAndCalculableDataFile=open(stepAndCalculableDataFileName)
                stepDataList,calculableConfigDict,listOfLeavesUsed=cPickle.load(stepAndCalculableDataFile)
                stepAndCalculableDataFile.close()

                #clean up
                os.remove(stepAndCalculableDataFileName)

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
                        displayFileDict[i].append(stepDataList[i]["outputFileName"])
                    if someLooper.steps[i].__doc__==someLooper.steps[i].skimmerStepName :
                        skimmerFileDict[i].append(stepDataList[i]["outputFileName"])
                    if someLooper.steps[i].__doc__==someLooper.steps[i].jsonMakerStepName :
                        runLsDict[i].append(stepDataList[i]["runLsDict"])
                        jsonFileDict[i].append(stepDataList[i]["outputFileName"])

                if isFirstLooper :
                    someLooper.calculableConfigDict={}
                    someLooper.listOfLeavesUsed=[]
                for item in calculableConfigDict :
                    someLooper.calculableConfigDict[item]=calculableConfigDict[item]
                someLooper.listOfLeavesUsed.extend(listOfLeavesUsed)
                isFirstLooper=False

            self.looperPrint(parent,someLooper)
            inFiles=" ".join(inFileList)
            cmd="hadd -f "+outputPlotFileName+" "+inFiles+" | grep -v 'Source file' | grep -v 'Target path'"
            #print cmd
            hAddOut=utils.getCommandOutput2(cmd)
            #clean up
            for fileName in inFileList :
                os.remove(fileName)
            
            print hAddOut[:-1].replace("Target","The output")+" has been written."
            print self.hyphens

            self.mergeDisplays(displayFileDict,someLooper)
            self.reportEffectiveXs(skimmerFileDict,someLooper)

            if len(jsonFileDict.values())>0 and len(jsonFileDict.values()[0])>0 :
                utils.mergeRunLsDicts(runLsDict,jsonFileDict.values()[0][0],self.hyphens,printHyphens=True)
            
    def reportEffectiveXs(self,skimmerFileDict,someLooper) :
        if len(skimmerFileDict)>0 :
            for skimmerIndex,skimFileNames in skimmerFileDict.iteritems() :
                if someLooper.xs==None :
                    print "The",len(skimFileNames),"skim files have been written."
                else :
                    effXs=0.0
                    nEvents=someLooper.steps[0].nTotal
                    nPass=someLooper.steps[skimmerIndex].nPass
                    if nEvents>0 : effXs=(someLooper.xs+0.0)*nPass/nEvents
                    print "The",len(skimFileNames),"skim files have effective XS =",someLooper.xs,"*",nPass,"/",nEvents,"=",effXs
                print "( e.g.",skimFileNames[0],")"
                print self.hyphens

    def mergeDisplays(self,displayFileDict,someLooper) :
        if len(displayFileDict)>0 :
            outputFileName=displayFileDict.values()[0][0].replace(someLooper.name,someLooper.parentName).replace(".root",".ps")
            utils.psFromRoot(displayFileDict.values()[0],outputFileName,beQuiet=False)
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
