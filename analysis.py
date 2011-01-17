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

        for item in ["baseOutputDirectory", "mainTree", "otherTreesToKeepWhenSkimming",
                     "leavesToBlackList", "printNodesUsed"] :
            setattr(self, "_"+item, getattr(self,item)() )
            
        self.sampleDict = samples.SampleHolder()
        map(self.sampleDict.update,self.listOfSampleDictionaries())

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
                fileNames[tuple].add(looper.inputFileListFileName())

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
            someFile = open(looper.inputFileListFileName())
            looper.inputFiles = cPickle.load(someFile)[job["iSlice"]::self._nSlices] #choose appropriate slice
            someFile.close()

            looper.name = childName(looper.name, job["iSlice"])
            looper.outputDir = self.outputDirectory(self._configurations[job["iConfig"]])

            looper.setQuietMode(self._loop)
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
                looper.setupSteps(minimal = True)
                listOfFileLists[index].append( looper.steps[0].outputFileName() )

        return [ dict(zip(["name","color","markerStyle"],sample[:3])+[("outputFileNames",fileList)]) \
                 for sample,fileList in zip(listOfSamples,listOfFileLists) ]


    def sampleLoopers(self, conf) :
        listOfCalculables = self.listOfCalculables(conf)
        listOfSteps = self.listOfSteps(conf)
        listOfSamples = self.listOfSamples(conf)

        selectors = filter(lambda s: hasattr(s,"select"), listOfSteps)
        assert len(selectors) == len(set(map(lambda s:(s.__class__.__name__,s.moreName,s.moreName2), selectors))),"Duplicate selectors are not allowed."
        names = [s.name for s in listOfSamples]
        assert len(names) == len(set(names)), "Duplicate sample names are not allowed."

        computeEntriesForReport = False #temporarily hard-coded

        def parseForEventNumber(ss,sampletuple) :
            if not ss.effectiveLumi :
                return ss.nFilesMax,ss.nEventsMax
            else :
                return ss.nFilesMax,ss.nEventsMax

        ptHatMinDict = {}
        outLoopers = []
        for sampleSpec in listOfSamples :
            sampleName = sampleSpec.name
            sampleTuple = self.sampleDict[sampleName]
            isMc = sampleTuple.lumi==None
            fileListCommand = sampleTuple.filesCommand
            nFilesMax,nEventsMax = parseForEventNumber(sampleSpec,sampleTuple)
                
            lumiWarn = False
            if (not isMc) and (nEventsMax!=-1 or nFilesMax!=-1) :
                print "Warning, not running over full data sample: wrong lumi?"
                lumiWarn = True

            if nFilesMax >= 0 : fileListCommand = "(%s)[:%d]"%(fileListCommand,nFilesMax)
            if sampleTuple.ptHatMin : ptHatMinDict[sampleName] = sampleTuple.ptHatMin
            adjustedListOfSteps = [steps.Master.master(xs = sampleTuple.xs,
                                                       lumi = sampleTuple.lumi,
                                                       lumiWarn = lumiWarn)
                                   ]+(steps.adjustStepsForMc(listOfSteps) if isMc else steps.adjustStepsForData(listOfSteps))
            
            outLoopers.append(analysisLooper(self.fileDirectory,
                                             self.treeName,
                                             self._otherTreesToKeepWhenSkimming,
                                             self._leavesToBlackList,
                                             self.outputDirectory(conf),
                                             adjustedListOfSteps,
                                             listOfCalculables,
                                             fileListCommand,
                                             computeEntriesForReport,
                                             self.printNodesUsed(),
                                             sampleName,
                                             nEventsMax,
                                             sampleSpec.color,
                                             sampleSpec.markerStyle
                                             )
                              )
            
        for thing in self.sampleDict.overlappingSamples :
            minPtHatsAndNames = []
            for sampleName in thing.samples :
                if sampleName not in ptHatMinDict : continue
                minPtHatsAndNames.append( (ptHatMinDict[sampleName],sampleName) )
            self.manageInclusiveSamples(minPtHatsAndNames, outLoopers)
        return outLoopers

    def manageInclusiveSamples(self, ptHatLowerThresholdsAndSampleNames = [], loopers = []) :
        def findLooper(ptHatLowerThreshold, sampleName) :
            out = None
            for iLooper,looper in enumerate(loopers) :
                if sampleName==looper.name :
                    out = iLooper
                for step in looper.steps :
                    if step.name()=="skimmer" :
                        print "WARNING: you are skimming inclusive samples.  The skims of all but the highest bin will be exclusive.  Use utils.printSkimResults()."
            return out
        
        looperIndexDict = {}
        for item in ptHatLowerThresholdsAndSampleNames :
            looperIndexDict[item[0]] = findLooper(*item)

        ptHatLowerThresholdsAndSampleNames.sort()
        for iItem in range(len(ptHatLowerThresholdsAndSampleNames)) :
            thisPtHatLowerThreshold = ptHatLowerThresholdsAndSampleNames[iItem][0]
            thisLooperIndex = looperIndexDict[thisPtHatLowerThreshold]

            #adjust cross sections and enable ptHatFilter in master step
            if iItem<len(ptHatLowerThresholdsAndSampleNames)-1 :
                nextPtHatLowerThreshold = ptHatLowerThresholdsAndSampleNames[iItem+1][0]
                nextLooperIndex = looperIndexDict[nextPtHatLowerThreshold]
                loopers[thisLooperIndex].steps[0].activatePtHatFilter(maxPtHat = nextPtHatLowerThreshold, lostXs = loopers[nextLooperIndex].steps[0].xs)

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
def mergeFunc(looper, listOfSlices) :
    def cleanUp(l) :
        for fileName in l :
            os.remove(fileName)
        
    def stuff(iSlice) :
        pDataFileName = looper.outputStepAndCalculableDataFileName().replace( looper.name, childName(looper.name,iSlice) )
        pDataFile = open(pDataFileName)
        dataList,calcsUsed,leavesUsed = cPickle.load(pDataFile)
        pDataFile.close()
        return dataList,calcsUsed,leavesUsed,pDataFileName

    def products() :
        prods = [[] for step in looper.steps]
        calcs = []
        leaves = []
        
        for iSlice in listOfSlices :
            dataList,calcsUsed,leavesUsed,pDataFileName = stuff(iSlice)
            cleanUpList.append(pDataFileName)

            for step,data,prod in zip(looper.steps, dataList, prods) :
                prod.append(data)
                if hasattr(step, "select") :
                    step.increment(True,  w = data["nPass"])
                    step.increment(False, w = data["nFail"])

            calcs.extend(calcsUsed)
            calcs = list(set(calcs))
            leaves.extend(leavesUsed)
            leaves = list(set(leaves))
        return prods,calcs,leaves

    cleanUpList = []
    looper.setupSteps(minimal = True)
    prods, looper.listOfCalculablesUsed, looper.listOfLeavesUsed = products()
    looper.printStats()
    print utils.hyphens
    for step,productList in zip(looper.steps, prods) :
        step.mergeFunc(productList, looper)

    cleanUp(cleanUpList)
