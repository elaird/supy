#!/usr/bin/env python
import os,sys,copy,cPickle,collections
import utils,steps,samples
from analysisLooper import analysisLooper
import ROOT as r
#####################################
def listOfConfigurations(params) :
    configs = [{"tag":"","codeString":""}]
    
    for key in sorted(params.keys()) :
        variations = params[key]
        if type(variations) not in [list, dict] : variations = [variations]
        isDict = type(variations) is dict

        baseLen = len(configs)
        configs = sum([copy.deepcopy(configs) for i in range(len( variations.keys() if isDict else variations ))],[])

        for iConf in range(baseLen) :
            for iVar,kval in enumerate(sorted(variations.keys()) if isDict else variations) :
                i = iVar*baseLen + iConf
                conf = configs[i]
                conf[key] = variations[kval] if isDict else kval
                if isDict : conf["tag"] += ("%s"+kval) % ("_" if len(conf["tag"]) else "")
                else : conf["codeString"] += str(iVar)
    return configs
#####################################
def childName(looperName,iSlice) : return looperName+"_%d"%iSlice
#####################################
class analysis(object) :
    """base class for an analysis"""

    def __init__(self, options) :
        self.name = self.__class__.__name__

        for item in ["baseOutputDirectory","listOfSampleDictionaries",
                     "mainTree","otherTreesToKeepWhenSkimming","leavesToBlackList","printNodesUsed"] :
            setattr(self, "_"+item, getattr(self,item)() )

        self.fileDirectory,self.treeName = self._mainTree
        self._configurations = listOfConfigurations(self.parameters())

        self._batch   = options.batch
        self._loop    = int(options.loop)   if options.loop!=None else None
        self._nSlices = int(options.slices) if options.slices!=None else 1
        self._profile = options.profile
        self._jobId   = options.jobId

        self._listsOfLoopers = []
        self._jobs = []
        for iConf,conf in enumerate(self._configurations) :
            self._listsOfLoopers.append( self.sampleLoopers(conf) )
            for iSample in range(len(self._listsOfLoopers[-1])) :
                for iSlice in range(self._nSlices) :
                    self._jobs.append({"iConfig":iConf,"iSample":iSample,"iSlice":iSlice})

        if self._jobId==None and self._loop!=None :
            self.makeInputFileLists()
            self.pickleJobs()

    def sideBySideAnalysisTags(self) : return sorted(list(set([conf["tag"] for conf in self._configurations])))
    def configurations(self) : return self._configurations
    def jobs(self) : return self._jobs

    def namedOutputDirectory(self) : return os.path.expanduser(self.baseOutputDirectory())+"/"+self.name
    def jobsFile(self) : return "%s/%s.jobs" % (self.namedOutputDirectory(),self.name)
    def outputDirectory(self, conf) : return "%s/%s/config%s" % (self.namedOutputDirectory(), conf["tag"], conf["codeString"])
    def outputPlotFileName(self,conf,sampleName) : return "%s/%s_plots.root" % ( self.outputDirectory(conf), sampleName )
    def psFileName(self,tag="") : return "%s/%s%s.ps" % (self.namedOutputDirectory(), self.name, "_"+tag if len(tag) else "")

    def baseOutputDirectory(self) :      raise Exception("NotImplemented", "Implement a member function %s"%"baseOutputDirectory(self)")
    def listOfSteps(self,config) :       raise Exception("NotImplemented", "Implement a member function %s"%"listOfSteps(self,config)")
    def listOfCalculables(self,config) : raise Exception("NotImplemented", "Implement a member function %s"%"listOfCalculables(self,config)")
    def listOfSampleDictionaries(self) : raise Exception("NotImplemented", "Implement a member function %s"%"sampleDict(self)")
    def listOfSamples(self,config) :     raise Exception("NotImplemented", "Implement a member function %s"%"listOfSamples(self,config)")

    def printNodesUsed(self) : return False
    def mainTree(self) : return ("susyTree","tree")
    def otherTreesToKeepWhenSkimming(self) : return [("lumiTree","tree")]
    def leavesToBlackList(self) : return ["hltL1Seeds"]
    def parameters(self) : return {}
    def conclude(self) : return

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
                assert len(fileList), "The command '%s' produced an empty list of files"%fileListCommand
                for fileName in value :
                    outFile=open(os.path.expanduser(fileName),"w")
                    cPickle.dump(fileList,outFile)
                    outFile.close()
                #notify queue
                q.task_done()

        #make output directories; compile a dict of commands and file names
        fileNames = collections.defaultdict(set)
        for job in self._jobs :
            os.system("mkdir -p "+self.outputDirectory(self._configurations[job["iConfig"]]))
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
            os.system("mkdir -p "+self.outputDirectory(self._configurations[job["iConfig"]]))
            #associate the file list
            looper = copy.deepcopy(self._listsOfLoopers[job["iConfig"]][job["iSample"]])
            someFile = open(looper.inputFileListFileName)
            looper.inputFiles = cPickle.load(someFile)[job["iSlice"]::self._nSlices] #choose appropriate slice
            someFile.close()

            oldName = looper.name
            looper.name = childName(looper.name,job["iSlice"])
            looper.outputPlotFileName=self.outputPlotFileName(self._configurations[job["iConfig"]],looper.name)
            looper.setOutputFileNames()
            looper.doSplitMode(oldName,self._loop)
            listOfLoopers.append(looper)

        if self._jobId!=None :
            listOfLoopers[0].go()

        elif self._profile :
            self.listOfLoopersForProf = listOfLoopers
            import cProfile
            cProfile.run("someInstance.goLoop()","resultProfile.out")

        else :
            utils.operateOnListUsingQueue(self._loop,utils.goWorker,listOfLoopers)

    def goLoop(self) :
        for looper in self.listOfLoopersForProf : looper.go()
        
    def sampleSpecs(self, tag = None) :
        condition = tag or (len(self.sideBySideAnalysisTags())==1 and self.sideBySideAnalysisTags()[0]=="")
        assert condition,"There are side-by-side analyses specified, but sampleSpecs() was not passed a tag."
        if not tag : tag = ""

        listOfSamples   = []
        listOfFileLists = []
        for iConfig,listOfLoopers in enumerate(self._listsOfLoopers) :
            conf = self._configurations[iConfig]
            if conf["tag"]!=tag : continue
            for looper in listOfLoopers :
                triplet = (looper.name, looper.color, looper.markerStyle)
                if triplet not in listOfSamples :
                    listOfSamples.append(triplet)
                    listOfFileLists.append([])
                index = listOfSamples.index(triplet)
                listOfFileLists[index].append( self.outputPlotFileName(conf,looper.name) )

        return [ dict(zip(["name","color","markerStyle"],sample[:3])+[("outputFileNames",fileList)]) \
                 for sample,fileList in zip(listOfSamples,listOfFileLists) ]


    def sampleLoopers(self, conf) :
        listOfCalculables = self.listOfCalculables(conf)
        listOfSteps = self.listOfSteps(conf)
        listOfSamples = self.listOfSamples(conf)

        selectors = filter(lambda s: hasattr(s,"select"), listOfSteps)
        assert len(selectors) == len(set(map(lambda s:(s.__class__.__name__,s.moreName,s.moreName2), selectors))),"Duplicate selectors are not allowed."
        assert len(listOfSamples) == len(set(map(lambda s: s.name,listOfSamples))), "Duplicate sample names are not allowed."

        computeEntriesForReport = False #temporarily hard-coded
        mergedDict = samples.SampleHolder()
        map(mergedDict.update,self._listOfSampleDictionaries)

        ptHatMinDict={}
        sampleLoopers = []
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
                
            if nFilesMax >= 0 : fileListCommand = "(%s)[:%d]"%(fileListCommand,nFilesMax)
            if sampleTuple.ptHatMin : ptHatMinDict[sampleName] = sampleTuple.ptHatMin
            adjustedListOfSteps = steps.adjustStepsForMc(listOfSteps) if isMc else \
                                  steps.adjustStepsForData(listOfSteps)

            sampleLoopers.append(analysisLooper(self.fileDirectory,
                                                self.treeName,
                                                self._otherTreesToKeepWhenSkimming,
                                                self._leavesToBlackList,
                                                self.outputDirectory(conf),
                                                self.outputPlotFileName(conf,sampleName),
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
            self.manageInclusiveSamples(minPtHatsAndNames, thing.useRejectionMethod, sampleLoopers)
        return sampleLoopers

    def manageInclusiveSamples(self, ptHatLowerThresholdsAndSampleNames = [], useRejectionMethod = True, loopers = []) :
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
                    if step.name() == "skimmer" :
                        print "WARNING: you are skimming inclusive samples.  The skims of all but the highest bin will be exclusive.  Use utils.printSkimResults()."

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
#############################################
def looperPrint(looper) :
    print utils.hyphens
    print looper.name
    looper.quietMode=False
    looper.printStats()
    print utils.hyphens
#############################################
def reportSkimFiles(skimmerFileDict,someLooper) :
    for skimmerIndex,skimFileNames in skimmerFileDict.iteritems() :
        print "The",len(skimFileNames),"skim files have been written."
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

            if looper.steps[i].name() == "displayer" :
                displayFileDict[i].append(stepDataList[i]["outputFileName"])
            if looper.steps[i].name() == "skimmer" :
                skimmerFileDict[i].append(stepDataList[i]["outputFileName"])
            if looper.steps[i].name() == "jsonMaker" : 
                runLsDict[i].append(stepDataList[i]["runLsDict"])
                jsonFileDict[i].append(stepDataList[i]["outputFileName"])

        looper.listOfCalculablesUsed.extend(listOfCalculablesUsed)
        looper.listOfCalculablesUsed = list(set(looper.listOfCalculablesUsed))
        looper.listOfLeavesUsed.extend(listOfLeavesUsed)
        looper.listOfLeavesUsed = list(set(looper.listOfLeavesUsed))

    looperPrint(looper)

    cmd = "hadd -f "+looper.outputPlotFileName+" "+" ".join(plotFileNameList)
    hAddOut = utils.getCommandOutput(cmd)

    for line in hAddOut.split("\n") :
        if 'Source file' in line or \
           'Target path' in line or \
           'Found subdirectory' in line : continue
        print line.replace("Target","The output")+" has been written."
        break
            
    print utils.hyphens

    mergeDisplays(displayFileDict, looper)
    reportSkimFiles(skimmerFileDict, looper)

    if len(jsonFileDict.values())>0 and len(jsonFileDict.values()[0])>0 :
        utils.mergeRunLsDicts(runLsDict, jsonFileDict.values()[0][0], printHyphens = True)

    #clean up
    for fileName in plotFileNameList :
        os.remove(fileName)
    for fileName in stepAndCalculableDataFileNameList :
        os.remove(fileName)
