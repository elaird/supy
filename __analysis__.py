import os,sys,tempfile,re
import utils,steps,samples,configuration,calculables,sites,batch
from __organizer__ import organizer
from __analysisLooper__ import analysisLooper
from __analysisStep__ import analysisStep
from supy import wrappedChain, whereami
#####################################
class analysis(object) :
    """base class for an analysis

    Methods before __init__ can be overridden in inheriting class.
    """

    def listOfSteps(self,config) :       raise Exception("NotImplemented", "Implement a member function %s"%"listOfSteps(self,config)")
    def listOfCalculables(self,config) : raise Exception("NotImplemented", "Implement a member function %s"%"listOfCalculables(self,config)")
    def listOfSampleDictionaries(self) : raise Exception("NotImplemented", "Implement a member function %s"%"sampleDict(self)")
    def listOfSamples(self,config) :     raise Exception("NotImplemented", "Implement a member function %s"%"listOfSamples(self,config)")

    def mainTree(self) : return configuration.mainTree()
    def otherTreesToKeepWhenSkimming(self) : return configuration.otherTreesToKeepWhenSkimming()
    def useCachedFileLists(self) : return configuration.useCachedFileLists()
    def leavesToBlackList(self) : return configuration.leavesToBlackList()
    def parameters(self) : return {}
    def conclude(self, config) : return
    def concludeAll(self) : utils.operateOnListUsingQueue( configuration.nCoresDefault(), utils.qWorker(self.conclude), zip(self.readyConfs) )
    def organizer(self, config, verbose = True, prefixesNoScale=[]) :
        return organizer(config['tag'], self.sampleSpecs(config['tag']), verbose=verbose, prefixesNoScale=prefixesNoScale)

############
    def __init__(self, options) :
        self.__batch   = options.batch
        self.__resubmit= options.resubmit
        self.__loop    = options.loop
        self.__nSlices = options.slices
        self.__byEvents= options.byEvents
        self.__profile = options.profile
        self.__jobId   = options.jobId
        self.__tag     = options.tag
        self.__sample  = options.sample
        self.__site    = options.site if options.site!=None else sites.prefix()
        self.__tags    = options.tags.split(',') if type(options.tags)==str else options.tags
        self.__samples = options.samples.split(',') if type(options.samples)==str else options.samples
        self.__omit    = options.omit.split(',')
        self.__nocheck = options.nocheck
        self.__quiet   = options.quiet
        self.__skip    = options.skip

        self.moveOutputFiles = (self.__jobId is None) or sites.info(site = self.__site, key = "moveOutputFilesBatch")
        self.localStem  = "%s/%s"%(sites.info(site = self.__site, key = "localOutputDir" ), self.name)
        self.globalStem = "%s/%s"%(sites.info(site = self.__site, key = "globalOutputDir"), self.name)
    
        self.sampleDict = samples.SampleHolder()
        map(self.sampleDict.update,self.listOfSampleDictionaries())

        if self.__tags is True or self.__samples is True :
            for conf in self.configurations :
                print conf['tag']
                if self.__samples is True :
                    print '\n'.join('  '+sample.weightedName for sample in self.filteredSamples(conf))
            sys.exit(0)
                
        if self.__loop:
            os.system("mkdir -p %s"%self.localStem)
            if self.__jobId==None :
                os.system("mkdir -p %s"%self.globalStem)
                self.makeInputFileLists()

        for conf in self.configurations :
            self.listsOfLoopers[conf['tag']] = self.sampleLoopers(conf)
            if self.__jobId==None and self.__loop:
                for looper in self.listsOfLoopers[conf['tag']] :
                    utils.writePickle( self.jobsFile(conf['tag'],looper.name,clean=True), self.__nSlices )

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
            if 'vary' not in parameters : parameters['vary'] = []
            order = parameters['vary'] + [p for p in parameters if p not in parameters['vary']]
            for item in ['tag','sample','baseSample'] : assert item not in parameters
            self.__configs = [ dict( [("tag",[])] + [(key,val) for key,val in parameters.iteritems() if type(val)!=self.vary] ) ]
            for param,variations in sorted(parameters.iteritems(), key = lambda x: order.index(x[0])) :
                if type(variations) is self.vary :
                    assert len(variations), "Empty <vary> for parameter '%s'"%param
                    self.__configs = sum([[ dict( list(conf.iteritems()) + [ (param,val), ("tag",conf["tag"]+[str(key)]) ] )
                                            for key,val in variations.iteritems()] for conf in self.__configs],[])
            if 'nullvary' in parameters :
                self.__configs = [c for c in self.__configs if not any( pair[0] in c['tag'] and pair[1] in c['tag'] for pair in parameters['nullvary']) ]
            for conf in self.__configs : conf['tag'] = '_'.join(conf['tag'])
            if type(self.__tags) is list :
                for tag in self.__tags :
                    if not [c['tag'] for c in self.__configs].count(tag) : print "No such tag: %s"%tag; sys.exit(0)
                self.__configs = [c for c in self.__configs if c['tag'] in self.__tags]
            if self.__tag!="" :
                self.__configs = [c for c in self.__configs if c['tag']==self.__tag]
                if not self.__configs : print "No such tag: %s"%self.__tag; sys.exit(0)
        return self.__configs
    class vary(dict) : pass

    def filteredSamples(self, conf) :
        def use(ss) :
            name = ss.weightedName
            return name not in self.__omit and ( name==self.__sample or 
                                                 self.__sample==None and ( type(self.__samples)!=list or 
                                                                           name in self.__samples ) )
        samples = filter(use, self.listOfSamples(conf))
        if not samples : print "No such sample: %s"%self.__sample if self.__sample else "No samples!"; sys.exit(0)
        return samples
############
    def jobsFile(self,tag,sample,clean=False) :
        if self.__loop :
            path = "%s/%s/%s"%(self.globalStem,tag,sample)
            if clean: os.system("rm -fr %s"%path)
            os.system("mkdir -p %s"%path)
        return "/".join([self.globalStem, tag, sample,"jobs"])
    def pdfFileName(self,tag = "") : return "%s/%s%s.pdf"%(self.globalStem, self.name, "_"+tag if len(tag) else "")

    def sampleSpecs(self, tag = "") :
        confSamples = self.filteredSamples(next(conf for conf in self.configurations if conf['tag']==tag))
        def sampleSpecDict(looper) :
            looper.setupSteps(minimal = True)
            sampleSpec = next( s for s in confSamples if s.weightedName == looper.name ) 
            return {"name":looper.name, "outputFileName":looper.steps[0].outputFileName,
                    "color":sampleSpec.color, "markerStyle":sampleSpec.markerStyle, "nCheck":self.sampleDict[sampleSpec.name].nCheck }
        return [ sampleSpecDict(looper) for looper in self.listsOfLoopers[tag] ]
############
    def inputFilesListFile(self, sampleName):
        return "%s/inputFileLists/%s/%s.inputFiles" % (whereami(), self.name, sampleName)

    def makeInputFileLists(self) :
        def nEventsFile(fileName):
            if not configuration.computeEntriesAtMakeFileList(): return None
            return utils.nEventsFile(fileName,'/'.join(self.mainTree()))
        def makeFileList(name) :
            fName = self.inputFilesListFile(name)
            if os.path.exists(fName) and self.useCachedFileLists() : return
            fileNames = eval(self.sampleDict[name].filesCommand)
            assert fileNames, "The command '%s' produced an empty list of files"%self.sampleDict[name].filesCommand
            utils.mkdir(os.path.dirname(fName))
            utils.writePickle(fName, zip(fileNames,map(nEventsFile, fileNames)))

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
        looper.slice(self.__nSlices, iSlice, self.__byEvents)()
############
    def loop(self) :
        wl = self.workList()
        
        if self.__jobId!=None : self.func(*(wl[0]))
        elif not self.__profile : utils.operateOnListUsingQueue(self.__loop, utils.qWorker(self.func), wl)
        else :
            import cProfile
            self.listOfLoopersForProf = wl
            cProfile.run("anInstance.profileLoop()","resultProfile.out")

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
                nonCalcs = [c for c in As + Bs if not issubclass(type(c), wrappedChain.calculable)]
                assert not nonCalcs, "\n\nWarning, the following items from listOfCalculables() are not calculables:\n"+('\n'.join(' '+str(c) for c in nonCalcs))
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
            inputFiles = utils.readPickle(self.inputFilesListFile(spec.name), "Have you looped?")[:spec.nFilesMax]
            nEventsMax,nFilesMax = parseForNumberEvents(spec, tup, len(inputFiles), self.__nSlices)
            inputFiles = inputFiles[:nFilesMax]

            adjustedSteps = ([steps.master(xs = tup.xs, xsPostWeights = spec.xsPostWeights,
                                           lumi = spec.overrideLumi if spec.overrideLumi!=None else tup.lumi,
                                           lumiWarn = lumiWarn(tup.lumi, nEventsMax, spec.nFilesMax) )] +
                             self.listOfSteps(pars) )
            nonSteps = [s for s in adjustedSteps if not issubclass(type(s), analysisStep)]
            assert not nonSteps, "\n\nWarning, the following items from listOfSteps() are not analysisSteps:\n"+('\n'.join(' '+str(s) for s in nonSteps))
            for step in filter(lambda s: s.only not in ['','data' if tup.lumi else 'sim'], adjustedSteps) : step.disabled = True

            return analysisLooper(mainTree=self.mainTree(),
                                  otherTreesToKeepWhenSkimming=self.otherTreesToKeepWhenSkimming(),
                                  nEventsMax=nEventsMax,
                                  leavesToBlackList=self.leavesToBlackList(),
                                  steps=adjustedSteps,
                                  calculables=allCalculables(self.listOfCalculables(pars),
                                                             spec.weights,
                                                             adjustedSteps),
                                  inputFiles=inputFiles,
                                  name=pars["sample"],
                                  moveOutputFiles=self.moveOutputFiles,
                                  localStem=self.localStem,
                                  subDir="%(tag)s" % conf,
                                  globalStem=self.globalStem,
                                  quietMode=(self.__loop > 1) or self.__quiet,
                                  skip=self.__skip,
                                  )
        sampleNames = set()
        return [ looper(sampleSpec) for sampleSpec in self.filteredSamples(conf) ]


    def mergeAllOutput(self) :
        args = sum([[(conf['tag'],looper) for looper in self.listsOfLoopers[conf['tag']]] for conf in self.configurations],[])
        utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(self.mergeOutput), args, False)


    def mergeOutput(self,tag,looper) :
        if not os.path.exists(self.jobsFile(tag,looper.name)) : return
        nSlices = utils.readPickle(self.jobsFile(tag,looper.name))
        incompleteSlices = looper.incompleteSlices(nSlices)

        if not incompleteSlices:
            looper.mergeFunc(nSlices)

        for item in incompleteSlices:
            if self.__resubmit:
                batch.submitJob(item)
            else:
                print item


    def manageSecondaries(self,updates,reportAll,reports) :
        def doUpdate(name) : return updates==True or type(updates)==str and name in updates.split(',')
        def doReport(name) : return reportAll==True or type(reports)==str and name in reports.split(',')

        def manage(conf,secondary) :
            if self.__nocheck and not doUpdate(secondary.name) : return
            org = organizer(conf['tag'], [ss for ss in self.sampleSpecs(conf['tag'])
                                          if ss['name'] in secondary.baseSamples() or not secondary.baseSamples()])
            index = next(org.indicesOfStep(secondary.name,secondary.moreNames), next(org.indicesOfStep(secondary.name),None))
            if index==None :
                print " !! Not found: %s    %s"%(secondary.name,secondary.moreNames)
                print org
                return
            org.dropSteps( allButIndices = [index])
            if doUpdate(secondary.name) : secondary.doCache(org)
            else : secondary.checkCache(org)

        def report(conf,secondary) :
            secondary.allSamples = [ss.weightedName for ss in self.filteredSamples(conf)]
            if doReport(secondary.name) : secondary.reportCache()
            
        confLoopers = [(conf,self.listsOfLoopers[conf['tag']][0]) for conf in self.readyConfs]
        for _,looper in confLoopers : looper.setupSteps(minimal = True, withBook = False)
        args = sum([[(conf,secondary) for secondary in filter(self.isSecondary, looper.steps[:self.indexOfInvertedLabel(looper.steps)])] for conf,looper in confLoopers],[])
        if reports==True :
            print '\n'.join(sorted(set(s.name for c,s in args)))
            sys.exit(0)
        utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(manage), args)
        utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(report), args)

    @staticmethod
    def isSecondary(step) : return issubclass(type(step),calculables.secondary)
    @staticmethod
    def indexOfInvertedLabel(loopersteps) : return next((i for i,step in enumerate(loopersteps) if type(step)==steps.filters.label and step.inverted()),None)
