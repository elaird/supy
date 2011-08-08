import os,sys,copy,cPickle,collections,tempfile
import utils,steps,samples,configuration,calculables,organizer,wrappedChain
from analysisLooper import analysisLooper
import ROOT as r
#####################################
class analysis(object) :
    """base class for an analysis

    Methods before __init__ can be overridden in inheriting class.
    """

    def listOfSteps(self,config) :       raise Exception("NotImplemented", "Implement a member function %s"%"listOfSteps(self,config)")
    def listOfCalculables(self,config) : raise Exception("NotImplemented", "Implement a member function %s"%"listOfCalculables(self,config)")
    def listOfSampleDictionaries(self) : raise Exception("NotImplemented", "Implement a member function %s"%"sampleDict(self)")
    def listOfSamples(self,config) :     raise Exception("NotImplemented", "Implement a member function %s"%"listOfSamples(self,config)")

    def mainTree(self) : return ("susyTree","tree")
    def otherTreesToKeepWhenSkimming(self) : return [("lumiTree","tree")]
    def useCachedFileLists(self) : return configuration.useCachedFileLists()
    def leavesToBlackList(self) : return []
    def parameters(self) : return {}
    def conclude(self, config) : return
    def concludeAll(self) : utils.operateOnListUsingQueue( configuration.nCoresDefault(), utils.qWorker(self.conclude), zip(self.readyConfs) )
    def organizer(self, config) : return organizer.organizer(config['tag'], self.sampleSpecs(config['tag']))

############
    def __init__(self, options) :
        self.__batch   = options.batch
        self.__loop    = int(options.loop)   if options.loop!=None else None
        self.__nSlices = int(options.slices) if options.slices!=None else 1
        self.__profile = options.profile
        self.__jobId   = options.jobId
        self.__tag     = options.tag
        self.__sample  = options.sample
        self.__site    = options.site if options.site!=None else configuration.sitePrefix()

        self.localStem  = "%s/%s"%(configuration.siteInfo(site = self.__site, key = "localOutputDir" ), self.name)
        self.globalStem = "%s/%s"%(configuration.siteInfo(site = self.__site, key = "globalOutputDir"), self.name)
    
        self.sampleDict = samples.SampleHolder()
        map(self.sampleDict.update,self.listOfSampleDictionaries())

        if self.__loop!=None :
            os.system("mkdir -p %s"%self.localStem)
            if self.__jobId==None :
                os.system("mkdir -p %s"%self.globalStem)
                self.makeInputFileLists()

        for conf in self.configurations :
            self.listsOfLoopers[conf['tag']] = self.sampleLoopers(conf)
            if self.__jobId==None and self.__loop!=None :
                for looper in self.listsOfLoopers[conf['tag']] :
                    utils.writePickle( self.jobsFile(conf['tag'],looper.name), self.__nSlices )

############
    @property
    def name(self) : return self.__class__.__name__
    @property
    def jobs(self) :
        if not hasattr(self,"_analysis__jobs") : self.__jobs = {}
        return self.__jobs
    @property
    def listsOfLoopers(self) :
        if not hasattr(self,"_analysis__listsOfLoopers") : self.__listsOfLoopers = {}
        return self.__listsOfLoopers
    @property
    def readyConfs(self) :
        def ready(conf) : return not any(os.path.exists(self.jobsFile(conf['tag'],looper.name)) for looper in self.listsOfLoopers[conf['tag']])
        return filter(ready,self.configurations)
    @property
    def configurations(self) :
        if not hasattr(self,"_analysis__configs") :
            parameters = self.parameters()
            for item in ['tag','sample','baseSample'] : assert item not in parameters
            self.__configs = [ dict( [("tag",[])] + [(key,val) for key,val in parameters.iteritems() if type(val)!=self.vary] ) ]
            for param,variations in parameters.iteritems() :
                if type(variations) is self.vary :
                    self.__configs = sum([[ dict( list(conf.iteritems()) + [ (param,val), ("tag",conf["tag"]+[str(key)]) ] )
                                            for key,val in variations.iteritems()] for conf in self.__configs],[])
            for conf in self.__configs : conf['tag'] = '_'.join(conf['tag'])
            if self.__tag!="" :
                self.__configs = [c for c in self.__configs if c['tag']==self.__tag]
                if not self.__configs : print "No such tag: %s"%self.__tag; sys.exit(0)
        return self.__configs
    class vary(dict) : pass

    def filteredSamples(self, conf) :
        samples = [s for s in self.listOfSamples(conf) if s.weightedName==self.__sample or self.__sample==None]
        if self.__sample and not samples : print "No such sample: %s"%self.__sample; sys.exit(0)
        return samples
############
    def jobsFile(self,tag,sample) :
        if self.__loop : os.system("mkdir -p %s/%s/%s"%(self.globalStem,tag,sample))
        return "/".join([self.globalStem, tag, sample,"jobs"])
    def psFileName(self,tag = "") : return "%s/%s%s.ps"%(self.globalStem, self.name, "_"+tag if len(tag) else "")

    def sampleSpecs(self, tag = "") :
        confSamples = self.filteredSamples(next(conf for conf in self.configurations if conf['tag']==tag))
        def sampleSpecDict(looper) :
            looper.setupSteps(minimal = True)
            sampleSpec = next( s for s in confSamples if s.weightedName == looper.name ) 
            return {"name":looper.name, "outputFileName":looper.steps[0].outputFileName,
                    "color":sampleSpec.color, "markerStyle":sampleSpec.markerStyle }
        return [ sampleSpecDict(looper) for looper in self.listsOfLoopers[tag] ]
    
############
    def inputFilesListFile(self, sampleName) : return "%s/%s.inputFiles"%(self.globalStem, sampleName)

    def globalToLocal(self, globalFileName) :
        tmpDir = tempfile.mkdtemp(dir = self.localStem)
        localFileName = globalFileName.replace(self.globalStem, tmpDir)
        return tmpDir,localFileName,globalFileName

    def localToGlobal(self, tmpDir, localFileName, globalFileName) :
        os.system(configuration.mvCommand(site = self.__site, src = localFileName, dest = globalFileName))
        os.system("rm -r %s"%tmpDir)

    def makeInputFileLists(self) :
        def makeFileList(name) :
            if os.path.exists(self.inputFilesListFile(name)) and self.useCachedFileLists() : return
            fileNames = eval(self.sampleDict[name].filesCommand)
            assert fileNames, "The command '%s' produced an empty list of files"%self.sampleDict[name].filesCommand
            tmpDir,localFileName,globalFileName = self.globalToLocal(self.inputFilesListFile(name))
            utils.writePickle(localFileName, fileNames)
            self.localToGlobal(tmpDir, localFileName, globalFileName)

        sampleNames = set(sum([[sampleSpec.name for sampleSpec in self.filteredSamples(conf)] for conf in self.configurations],[]))
        utils.operateOnListUsingQueue(self.__loop, utils.qWorker(makeFileList), [(name,) for name in sampleNames] )

############
    def workList(self) :
        out = []
        for looper in sum(self.listsOfLoopers.values(), []) :
            for iSlice in (range(self.__nSlices) if self.__jobId==None else [int(self.__jobId)]) :
                out.append( (looper, iSlice) )
        return out
############
    def func(self, looper, iSlice) :
        looper.slice(self.__nSlices, iSlice)()
############
    def loop(self) :
        wl = self.workList()
        
        if self.__jobId!=None : self.func(*(wl[0]))
        elif not self.__profile : utils.operateOnListUsingQueue(self.__loop, utils.qWorker(self.func), wl)
        else :
            import cProfile
            self.listOfLoopersForProf = wl
            cProfile.run("someInstance.profileLoop()","resultProfile.out")

    def profileLoop(self) :
        for looper,iSlice in self.listOfLoopersForProf :
            self.func(looper, iSlice)
############
    def sampleLoopers(self, conf) :

        def parseForNumberEvents(spec,tup,nFiles,nSlices) :
            if not spec.effectiveLumi : return (spec.nEventsMax,nFiles)
            if spec.nEventsMax>=0: print "Warning: %s nEventsMax ignored in favor of effectiveLumi."%spec.weightedName
            assert not tup.lumi, "Cannot calculate effectiveLumi for _data_ sample %s"%spec.weightedName
            nJobs = min(nFiles, nSlices)
            nEventsTotal = spec.effectiveLumi * tup.xs
            if nEventsTotal < nJobs : return (1,int(nEventsTotal+0.9))
            return (1+int(nEventsTotal/nJobs), nFiles)

        def lumiWarn(isData, nEventsMax, nFilesMax) :
            invalid = isData and (nEventsMax>=0 or nFilesMax>=0)
            if invalid : print "Warning: Not running over full data sample: wrong lumi?"
            return invalid

        def allCalculables(calcs,weights,adjustedSteps) :
            secondaries = [ s for s in adjustedSteps if self.isSecondary(s) ]
            weightsAlready = [next(c for c in secondaries+calcs if c.name==w) for w in weights if type(w)==str ]
            weightsAdditional = [ w for w in weights if type(w)!=str ]
            def check(As,Bs) :
                intersect = set([a.name for a in As]).intersection(set([b.name for b in Bs]))
                assert not intersect, "Warning: { %s } are already listed in listOfCalculables."%','.join(intersect)
            check(calcs,weightsAdditional)
            check(calcs,secondaries)
            check(weightsAdditional,secondaries)
            return calcs + [calculables.weight(weightsAdditional+weightsAlready)] + weightsAdditional + secondaries

        def looper(spec) :
            assert spec.weightedName not in sampleNames,"Duplicate sample name %s is not allowed."%spec.weightedName ; sampleNames.add(spec.weightedName)
            pars = dict( list(conf.iteritems()) + [("baseSample",spec.name), ("sample",spec.weightedName) ] )
            tup = self.sampleDict[spec.name]
            inputFiles = utils.readPickle(self.inputFilesListFile(spec.name))[:spec.nFilesMax]
            nEventsMax,nFilesMax = parseForNumberEvents(spec, tup, len(inputFiles), self.__nSlices)
            inputFiles = inputFiles[:nFilesMax]

            adjustedSteps = [ steps.Master.Master(xs = tup.xs, xsPostWeights = spec.xsPostWeights,
                                                  lumi = spec.overrideLumi if spec.overrideLumi!=None else tup.lumi,
                                                  lumiWarn = lumiWarn(tup.lumi, nEventsMax, spec.nFilesMax) )
                              ] + steps.adjustSteps(self.listOfSteps(pars), "Data" if tup.lumi else "Mc")

            return analysisLooper( mainTree = self.mainTree(),   otherTreesToKeepWhenSkimming = self.otherTreesToKeepWhenSkimming(),
                                   nEventsMax = nEventsMax,      leavesToBlackList = self.leavesToBlackList(),
                                   steps = adjustedSteps,        calculables = allCalculables( self.listOfCalculables(pars), spec.weights, adjustedSteps ),
                                   inputFiles = inputFiles,      name = pars["sample"],
                                   localStem  = self.localStem,  subDir = "%(tag)s"%conf,
                                   globalStem = self.globalStem, quietMode = self.__loop>1 )
        sampleNames = set()
        return [ looper(sampleSpec) for sampleSpec in self.filteredSamples(conf) ]
    
############
    def mergeAllOutput(self) :
        args = sum([[(conf['tag'],looper) for looper in self.listsOfLoopers[conf['tag']]] for conf in self.configurations],[])
        utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(self.mergeOutput), args)
        #for arg in args : self.mergeOutput(*arg)
    
    def mergeOutput(self,tag,looper) :
        if not os.path.exists(self.jobsFile(tag,looper.name)) : return
        nSlices = utils.readPickle(self.jobsFile(tag,looper.name))
        if looper.readyMerge(nSlices) : looper.mergeFunc(nSlices)

############
    def manageSecondaries(self,update) :
        for conf in self.readyConfs :
            loopers = self.listsOfLoopers[conf['tag']]
            for secondary in filter(self.isSecondary, loopers[0].steps) :
                org = self.organizer(conf)
                index = next(org.indicesOfStep(secondary.name,secondary.moreNames), next(org.indicesOfStep(secondary.name),None))
                if index==None :
                    print " !! Not found: %s    %s"%(secondary.name,secondary.moreNames)
                    continue
                org.dropSteps( allButIndices = [index])
                if update==True or (type(update)==str and secondary.name in update.split(',')) :
                    secondary.doCache(org)
                else : secondary.checkCache(org)

    def isSecondary(self,step) : return issubclass(type(step),wrappedChain.wrappedChain.calculable)
