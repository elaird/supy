#!/usr/bin/env python
import os,sys,copy,cPickle,collections
import utils,steps,samples
from analysisLooper import analysisLooper
import ROOT as r
#####################################
def listOfConfigurationsAndTags(paramsIn) :
    def maxLength(d) :
        lengths = []
        for key,value in d.iteritems() :
            if   (type(value) is list) or (type(value) is dict) : lengths.append(len(value))
            else : lengths.append(1)
        return max(lengths) if len(lengths) else 0

    def listOfCodes(nOps,nItems) :
        return [ utils.makeCodes(i,nOps,nItems) for i in range(nOps**nItems) ]

    configurationCodes = listOfCodes(maxLength(paramsIn),len(paramsIn))

    configsOut     = []
    tagsOut        = []
    codeStringsOut = []
    paramKeys = paramsIn.keys()
    paramKeys.sort()
    for codeList in configurationCodes :
        config = {}
        tag = ""
        codeString = ""
        insert = True
        for iParamKey,paramKey in enumerate(paramKeys) :
            variations = paramsIn[paramKey]
            #make list from singletons
            if (not (type(variations) is list)) and (not (type(variations) is dict)) : variations = [variations]
            code = codeList[iParamKey]

            #skip this code list if it is not valid
            if code>=len(variations) :
                insert = False
                continue

            #add to this config
            if type(variations) is list :
                config[paramKey] = variations[code]
                codeString+=str(code)
            if type(variations) is dict :
                variationKey = variations.keys()[code]
                variation = variations[variationKey]
                config[paramKey] = variation
                #add to this tag
                if tag!="" : tag+="_"
                tag+=variationKey

        #append to the lists
        if insert :
            configsOut.append(config)
            tagsOut.append(tag)
            codeStringsOut.append(codeString)
    return configsOut,tagsOut,codeStringsOut
#####################################
def childName(looperName,iSlice) : return looperName+"_%d"%iSlice
#####################################
class analysis(object) :
    """base class for an analysis"""

    def __init__(self, options) :
        self.name = self.__class__.__name__

        for item in ["baseOutputDirectory","listOfSampleDictionaries",
                     "mainTree","otherTreesToKeepWhenSkimming","printNodesUsed"] :
            setattr(self, "_"+item, getattr(self,item)() )

        self.fileDirectory=self._mainTree[0]
        self.treeName=self._mainTree[1]

        self._configurations,self._tags,self._codeStrings = listOfConfigurationsAndTags(self.parameters())
        self._sideBySideAnalysisTags = sorted(list(set(self._tags)))

        self._batch   = options.batch
        self._loop    = int(options.loop)   if options.loop!=None else None
        self._nSlices = int(options.slices) if options.slices!=None else 1
        self._profile = options.profile
        self._jobId   = options.jobId

        self._listsOfLoopers = []
        self._jobs = []
        for iConfiguration,configuration in enumerate(self._configurations) :
            listOfSteps = self.listOfSteps(configuration)
            listOfSamples = self.listOfSamples(configuration)
            selectors = filter(lambda s: hasattr(s,"select"), listOfSteps)
            assert len(selectors) == len(set(map(lambda s: (s.__doc__,s.moreName,s.moreName2), selectors))), "Duplicate selectors are not allowed."
            assert len(listOfSamples) == len(set(map(lambda s: s.name,listOfSamples))), "Duplicate sample names are not allowed."

            listOfCalculables = self.listOfCalculables(configuration)
            listOfLoopers = self.listOfLoopers(listOfSamples, listOfSteps, listOfCalculables, iConfiguration)
            #add to list of loopers
            self._listsOfLoopers.append( listOfLoopers )

            #add to list of jobs
            for iLooper in range(len(listOfLoopers)) :
                for iSlice in range(self._nSlices) :
                    d = {}
                    d["iConfig"]=iConfiguration
                    d["iSample"]=iLooper
                    d["iSlice" ]=iSlice
                    self._jobs.append(d)

        #make lists of input files
        if self._jobId==None and self._loop!=None :
            self.makeInputFileLists()
            self.pickleJobs()
            
    def sideBySideAnalysisTags(self) : return self._sideBySideAnalysisTags
    def configurations(self) :         return self._configurations
    def jobs(self) :                   return self._jobs
    def jobsFile(self) :               return self.namedOutputDirectory()+"/"+self.name+".jobs"
    def namedOutputDirectory(self) :   return os.path.expanduser(self.baseOutputDirectory())+"/"+self.name

    def outputDirectory(self, iConfig) :
        tag  = self._tags[iConfig]
        code = self._codeStrings[iConfig]
        return self.namedOutputDirectory()+"/"+tag+"/config"+str(code)+"/"

    def makeOutputPlotFileName(self,configurationId,sampleName) :
        return self.outputDirectory(configurationId)+"/"+sampleName+"_plots.root"

    def psFileName(self,tag="") :
        base = self.namedOutputDirectory()+"/"+self.name
        if tag!="" : base+="_"+tag
        return base+".ps"
    
    def baseOutputDirectory(self) :          raise Exception("NotImplemented","Implement a member function baseOutputDirectory()")
    def listOfSteps(self,config) :           raise Exception("NotImplemented","Implement a member function listOfSteps(self,config)")
    def listOfCalculables(self,config) :     raise Exception("NotImplemented","Implement a member function listOfCalculables(self,config)")
                                             
    def listOfSampleDictionaries(self) :     raise Exception("NotImplemented","Implement a member function sampleDict()")
    def listOfSamples(self,config) :         raise Exception("NotImplemented","Implement a member function listOfSamples(self,config)")

    def printNodesUsed(self) :               return False
    def mainTree(self) :                     return ("susyTree","tree")
    def otherTreesToKeepWhenSkimming(self) : return [("lumiTree","tree")]

    def parameters(self) :                   return {}
    def conclude(self) :                     return

    def pickleJobs(self) :
        outFile=open(self.jobsFile(),"w")
        cPickle.dump( (self._loop,self._jobs), outFile )
        outFile.close()
        
    def makeInputFileLists(self) :
        #define a helper function
        def inputFilesEvalWorker(q):
            while True:
                key,value = q.get()
                #write file list to disk
                fileListCommand = key[1]
                fileList = eval(fileListCommand)
                for fileName in value :
                    outFile=open(os.path.expanduser(fileName),"w")
                    cPickle.dump(fileList,outFile)
                    outFile.close()
                #notify queue
                q.task_done()

        #make output directories; compile a dict of commands and file names
        fileNames = collections.defaultdict(set)
        for job in self._jobs :
            os.system("mkdir -p "+self.outputDirectory(job["iConfig"]))
            for looper in self._listsOfLoopers[job["iConfig"]] :
                tuple = (looper.name, looper.fileListCommand)
                fileNames[tuple].add(looper.inputFileListFileName)

        #make lists from the sets
        for key,value in fileNames.iteritems() :
            fileNames[key]=list(value)

        #execute in parallel commands to make file lists
        utils.operateOnListUsingQueue(self._loop,inputFilesEvalWorker,fileNames.iteritems())

    def loop(self) :
        listOfLoopers = []
        for iJob,job in enumerate(self._jobs) :
            if self._jobId!=None and int(self._jobId)!=iJob : continue
            #make sure output directory exists (perhaps not necessary-- to be checked)
            os.system("mkdir -p "+self.outputDirectory(job["iConfig"]))
            #associate the file list
            looper = copy.deepcopy(self._listsOfLoopers[job["iConfig"]][job["iSample"]])
            someFile = open(looper.inputFileListFileName)
            looper.inputFiles = cPickle.load(someFile)[job["iSlice"]::self._nSlices] #choose appropriate slice
            someFile.close()

            oldName = looper.name
            looper.name = childName(looper.name,job["iSlice"])
            looper.outputPlotFileName=self.makeOutputPlotFileName(job["iConfig"],looper.name)
            looper.setOutputFileNames()
            looper.doSplitMode(oldName,self._loop)
            listOfLoopers.append(looper)

        if self._jobId!=None :
            listOfLoopers[0].go()
        else :
            ##for looper in listOfLoopers : looper.go()
            utils.operateOnListUsingQueue(self._loop,utils.goWorker,listOfLoopers)

    def sampleSpecs(self, tag = None) :
        condition = tag!=None or (len(self.sideBySideAnalysisTags())==1 and self.sideBySideAnalysisTags()[0]=="")
        assert condition,"There are side-by-side analyses specified, but sampleSpecs() was not passed a tag."
        if tag==None : tag = ""

        listOfSamples   = []
        listOfFileLists = []
        for iConfig,listOfLoopers in enumerate(self._listsOfLoopers) :
            if self._tags[iConfig]!=tag : continue
            for looper in listOfLoopers :
                tuple = (looper.name, looper.color, looper.markerStyle)
                if tuple not in listOfSamples :
                    listOfSamples.append(tuple)
                    listOfFileLists.append([])
                index = listOfSamples.index(tuple)
                listOfFileLists[index].append( self.makeOutputPlotFileName(iConfig,looper.name) )

        outList = []
        for sample,fileList in zip(listOfSamples,listOfFileLists) :
            d = {}
            d["name"]            = sample[0]
            d["color"]           = sample[1]
            d["markerStyle"]     = sample[2]
            d["outputFileNames"] = fileList
            outList.append(d)
        return outList

    def listOfLoopers(self, listOfSamples = [], listOfSteps = [], listOfCalculables = [], iConfiguration = None) :
        computeEntriesForReport = False #temporarily hard-coded
        mergedDict = samples.SampleHolder()
        map(mergedDict.update,self._listOfSampleDictionaries)

        outLoopers = []
        #print mergedDict
        ptHatMinDict={}
        for sampleSpec in listOfSamples :
            sampleName = sampleSpec.name
            sampleTuple = mergedDict[sampleName]
            isMc = sampleTuple.lumi==None
            fileListCommand=sampleTuple.filesCommand
            nFilesMax=sampleSpec.nFilesMax
            nEventsMax=sampleSpec.nEventsMax

            lumiWarn = False
            if (not isMc) and (nEventsMax!=-1 or nFilesMax!=-1) :
                print "Warning, not running over full data sample: wrong lumi?"
                lumiWarn = True
                
            if nFilesMax >= 0 :
                fileListCommand = "(%s)[:%d]"%(fileListCommand,nFilesMax)
                
            adjustedListOfSteps = []
            if isMc : adjustedListOfSteps = steps.adjustStepsForMc(listOfSteps)
            else :    adjustedListOfSteps = steps.adjustStepsForData(listOfSteps)

            if sampleTuple.ptHatMin :
                ptHatMinDict[sampleName]=sampleTuple.ptHatMin

            outLoopers.append(analysisLooper(self.fileDirectory,
                                             self.treeName,
                                             self._otherTreesToKeepWhenSkimming,
                                             self.outputDirectory(iConfiguration),
                                             self.makeOutputPlotFileName(iConfiguration,sampleName),
                                             adjustedListOfSteps,
                                             listOfCalculables,
                                             sampleSpec,
                                             fileListCommand,
                                             sampleTuple.xs,
                                             sampleTuple.lumi,
                                             lumiWarn,
                                             computeEntriesForReport,
                                             self.printNodesUsed(),
                                             )
                              )
        for thing in mergedDict.overlappingSamples :
            minPtHatsAndNames=[]
            for sampleName in thing.samples :
                if sampleName not in ptHatMinDict : continue
                minPtHatsAndNames.append( (ptHatMinDict[sampleName],sampleName) )
            self.manageNonBinnedSamples(minPtHatsAndNames, thing.useRejectionMethod, outLoopers)
        return outLoopers

    def manageNonBinnedSamples(self, ptHatLowerThresholdsAndSampleNames = [], useRejectionMethod = True, loopers = []) :
        if not useRejectionMethod :
            raise Exception("the other method of combining non-binned samples is not yet implemented")
        looperIndexDict={}
        for item in ptHatLowerThresholdsAndSampleNames :
            ptHatLowerThreshold=item[0]
            sampleName=item[1]

            #find the associated looper
            for iLooper,looper in enumerate(loopers) :
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
                loopers[thisLooperIndex].xs-=loopers[nextLooperIndex].xs

                if useRejectionMethod :
                    loopers[thisLooperIndex].needToConsiderPtHatThresholds=False
                    steps.insertPtHatFilter(loopers[thisLooperIndex].steps,nextPtHatLowerThreshold)

            #inform relevant loopers of the ptHat thresholds
            for index in looperIndexDict.values() :
                loopers[index].ptHatThresholds.append(float(thisPtHatLowerThreshold))
                if not useRejectionMethod :
                    loopers[index].needToConsiderPtHatThresholds=True
        return
    
    def mergeOutput(self) :
        if not os.path.exists(self.jobsFile()) : return

        def mergeWorker(q):
            while True:
                mergeFunc(*q.get())
                q.task_done()
        
        inFile=open(self.jobsFile())
        nCores,jobs = cPickle.load(inFile)
        inFile.close()

        mergeDict = collections.defaultdict(list)
        for job in jobs : mergeDict[(job["iConfig"],job["iSample"])].append(job["iSlice"])

        workList = []
        for key,listOfSlices in mergeDict.iteritems() :
            iConfig = key[0]
            iSample = key[1]
            looper = self._listsOfLoopers[iConfig][iSample]
            workList.append( (looper,listOfSlices) )

        ##for item in workList : mergeFunc(*item)
        utils.operateOnListUsingQueue(nCores,mergeWorker,workList)
        os.remove(self.jobsFile())
                
    def profile(self) :
        global runFunc
        runFunc=self.loopOverSamples
        import cProfile
        cProfile.run("analysis.runFunc()","resultProfile.out")
#############################################
def looperPrint(looper) :
    print utils.hyphens
    print looper.name
    looper.quietMode=False
    looper.printStats()
    print utils.hyphens
#############################################
def reportEffectiveXs(skimmerFileDict,someLooper) :
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
            print utils.hyphens
#############################################
def mergeDisplays(displayFileDict,someLooper) :
    if len(displayFileDict)>0 :
        outputFileName=displayFileDict.values()[0][0].replace(someLooper.name,someLooper.parentName).replace(".root",".ps")
        utils.psFromRoot(displayFileDict.values()[0],outputFileName,beQuiet=False)
        print utils.hyphens
#############################################
def mergeFunc(looper,listOfSlices) :

    #these map step index to list of output file names
    displayFileDict = collections.defaultdict(list)
    skimmerFileDict = collections.defaultdict(list)
    jsonFileDict    = collections.defaultdict(list)
    #these map step index to list of run-ls dicts
    runLsDict       = collections.defaultdict(list)

    plotFileNameList = []
    stepAndCalculableDataFileNameList = []

    #zero counts for this looper
    for i in range(len(looper.steps)) :
        looper.steps[i].nTotal = 0
        looper.steps[i].nPass  = 0
        looper.steps[i].nFail  = 0
    #empty lists for this looper
    looper.listOfCalculablesUsed = []
    looper.listOfLeavesUsed      = []
    
    for iSlice in listOfSlices :
        plotFileNameList.append( looper.outputPlotFileName.replace( looper.name, childName(looper.name,iSlice) ) )

        #read in the step and calculable data
        stepAndCalculableDataFileName = looper.outputStepAndCalculableDataFileName.replace( looper.name, childName(looper.name,iSlice) )
        stepAndCalculableDataFile=open(stepAndCalculableDataFileName)
        stepDataList,listOfCalculablesUsed,listOfLeavesUsed=cPickle.load(stepAndCalculableDataFile)
        stepAndCalculableDataFile.close()
        stepAndCalculableDataFileNameList.append(stepAndCalculableDataFileName)

        for i in range(len(looper.steps)) :
            looper.steps[i].nTotal+=stepDataList[i]["nTotal"]
            looper.steps[i].nPass +=stepDataList[i]["nPass" ]
            looper.steps[i].nFail +=stepDataList[i]["nFail" ]

            if looper.steps[i].__doc__==looper.steps[i].displayerStepName :
                displayFileDict[i].append(stepDataList[i]["outputFileName"])
            if looper.steps[i].__doc__==looper.steps[i].skimmerStepName :
                skimmerFileDict[i].append(stepDataList[i]["outputFileName"])
            if looper.steps[i].__doc__==looper.steps[i].jsonMakerStepName :
                runLsDict[i].append(stepDataList[i]["runLsDict"])
                jsonFileDict[i].append(stepDataList[i]["outputFileName"])

        looper.listOfCalculablesUsed.extend(listOfCalculablesUsed)
        looper.listOfCalculablesUsed = list(set(looper.listOfCalculablesUsed))
        looper.listOfLeavesUsed.extend(listOfLeavesUsed)
        looper.listOfLeavesUsed = list(set(looper.listOfLeavesUsed))

    looperPrint(looper)

    cmd = "hadd -f "+looper.outputPlotFileName+" "+" ".join(plotFileNameList)
    cmd+= " | grep -v 'Source file' | grep -v 'Target path' | grep -v 'Found subdirectory'"
    #print cmd
    hAddOut = utils.getCommandOutput2(cmd)
            
    print hAddOut[:-1].replace("Target","The output")+" has been written."
    print utils.hyphens

    mergeDisplays(displayFileDict, looper)
    reportEffectiveXs(skimmerFileDict, looper)

    if len(jsonFileDict.values())>0 and len(jsonFileDict.values()[0])>0 :
        utils.mergeRunLsDicts(runLsDict, jsonFileDict.values()[0][0], printHyphens = True)

    #clean up
    for fileName in plotFileNameList :
        os.remove(fileName)
    for fileName in stepAndCalculableDataFileNameList :
        os.remove(fileName)
