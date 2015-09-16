import copy,os,collections,math
import configuration
from supy import autoBook,wrappedChain,utils,keyTracer
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self, mainTree=None, otherTreesToKeepWhenSkimming=None,
                 leavesToBlackList=None, moveOutputFiles=None, localStem=None,
                 globalStem=None, subDir=None, steps=None, calculables=None,
                 inputFiles=None, name=None, nEventsMax=None, quietMode=None,
                 skip=None, nSlicesFixed=None, nEventsPerSlice=None, byEvents=None):

        for arg in ["mainTree", "otherTreesToKeepWhenSkimming",
                    "leavesToBlackList", "moveOutputFiles", "localStem",
                    "globalStem", "subDir", "steps", "calculables",
                    "inputFiles", "name", "nEventsMax", "quietMode",
                    "skip", "byEvents"]:
            setattr(self, arg, eval(arg))

        if nSlicesFixed is not None:
            assert nEventsPerSlice is None
            self.nSlices = nSlicesFixed
        if nEventsPerSlice is not None:
            assert nSlicesFixed is None
            self.byEvents = True  # until "by chunks" is implemented
            assert 1 <= nEventsPerSlice
            assert configuration.computeEntriesAtMakeFileList()
            self.nSlices = int(math.ceil((self.nExpect + 0.0) / nEventsPerSlice))

        self.trace = configuration.trace() and not any([step.requiresNoTrace() for step in self.steps])
        self.outputDir = self.globalDir #the value will be modified in self.prepareOutputDirectory()
        self.inputDir = self.globalDir 
        self.divisor = None
        self.remainder = None
        self.checkSteps()

    @property
    def globalDir(self) : return "%s/%s/"%(self.globalStem, self.subDir)
    @property
    def outputFileStem(self) :  return "%s/%s"%(self.outputDir, self.name)
    @property
    def inputFileStem(self) :  return "%s/%s"%(self.inputDir, self.name)
    @property
    def pickleFileName(self) : return "%s%s"%(self.outputFileStem, ".pickledData")

    def checkSteps(self) :
        for iStep,step in enumerate(self.steps) :
            if iStep : continue
            assert step.name=="master", "The master step must occur first."
            assert step.isSelector, "The master step must be a selector."
        selectors = [ (s.name,s.moreNames) for s in self.steps if s.isSelector ]
        for sel in selectors : assert 1==selectors.count(sel), "Duplicate selector (%s,%s) is not allowed."%sel
        inter = set(s.name for s in self.steps if not issubclass(type(s),wrappedChain.calculable)).intersection(set(c.name for c in self.calculables))
        if inter: print "Steps and calculables cannot share names { %s }"%', '.join(n for n in inter)
        
    def childName(self, iSlice) : return "%s_%d_%d"%(self.name, self.nSlices, iSlice)
    def slice(self, iSlice):
        nSlices = self.nSlices
        assert 0 <= iSlice < nSlices, "How did you do this?"
        out = copy.deepcopy(self)

        if self.byEvents:
            out.divisor = nSlices
            out.remainder = iSlice
        else:
            out.inputFiles = out.inputFiles[iSlice::nSlices]

        out.globalDir = "/".join([out.globalDir, out.name])

        out.name = out.childName(iSlice)
        out.outputDir = "/".join([out.outputDir, out.name])
        return out

    def __call__(self) :
        self.prepareOutputDirectory()
        self.setupChains()
        self.setupSteps()
        self.loop()
        self.endSteps()
        self.writeRoot()
        self.writePickle()
        self.deleteChains()
        if self.moveOutputFiles:
            self.moveFiles()
        if not self.quietMode : print utils.hyphens

    def loop(self) :
        if self.nEventsMax!=0 :
            chainWrapper = wrappedChain( self.chains[self.mainTree],
                                         calculables = self.calculables,
                                         useSetBranchAddress = not any([step.requiresNoSetBranchAddress() for step in self.steps]),
                                         leavesToBlackList = self.leavesToBlackList,
                                         maxArrayLength = configuration.maxArrayLength(),
                                         trace = self.trace,
                                         cacheSizeMB = configuration.ttreecacheMB(),
                                         )
            for step in filter(lambda s: (issubclass(type(s),wrappedChain.calculable) and
                                          hasattr(s,"source") and
                                          hasattr(s.source,"tracedKeys")), self.steps) :
                step.tracer = step.source
                step.source.tracedKeys |= step.priorFilters

            [ all(step(eventVars) for step in self.steps) for eventVars in chainWrapper.entries(self.nEventsMax, self.skip, self.divisor, self.remainder) ]

            for step in filter(lambda s: s.tracer and s.name in s.tracer.tracedKeys, self.steps) : step.tracer.tracedKeys.remove(step.name)
            self.recordLeavesAndCalcsUsed( chainWrapper.activeKeys(), chainWrapper.calcDependencies() )
        else : self.recordLeavesAndCalcsUsed([], {})

    def recordLeavesAndCalcsUsed(self, activeKeys, calculableDependencies) :
        calcs = dict([(calc.name,calc) for calc in self.calculables])
        def calcTitle(key) : return "%s%s%s"%(calcs[key].moreName, calcs[key].moreName2, configuration.fakeString() if calcs[key].isFake() else "")
        self.calculablesUsed = set([ (key,calcTitle(key)) for key,isLeaf,keyType in activeKeys if not isLeaf ])
        self.leavesUsed      = set([ (key,       keyType) for key,isLeaf,keyType in activeKeys if isLeaf ])
        self.calculableDependencies = collections.defaultdict(set)
        for key,val in calculableDependencies.iteritems() :
            self.calculableDependencies[key] = set(map(lambda c: c if type(c)==tuple else (c,c),val))
        
    def prepareOutputDirectory(self):
        utils.mkdir(self.localStem)
        self.outputDir = self.outputDir.replace(self.globalStem, self.localStem)
        os.system("rm -rf %s" % self.outputDir)
        utils.mkdir(self.outputDir)

    def moveFiles(self):
        utils.mkdir(self.globalDir)
        os.system("mv %s/* %s/" % (self.outputDir, self.globalDir))
        os.system("rm -rf %s" % self.outputDir)

    @property
    def nExpect(self):
        if not configuration.computeEntriesAtMakeFileList(): return None
        if not len(self.inputFiles): return 0
        nExpect = sum(zip(*self.inputFiles)[1])
        return nExpect if self.nEventsMax==None else min(nExpect, self.nEventsMax)

    def setupChains(self) :
        assert self.mainTree not in self.otherTreesToKeepWhenSkimming
        self.chains = dict( [(item,r.TChain("%s/%s"%item)) for item in [self.mainTree]+self.otherTreesToKeepWhenSkimming])
        for (dirName,treeName),chain in self.chains.iteritems() :
            for infile in self.inputFiles : chain.Add(infile[0])
            r.SetOwnership(chain, False)

        if self.inputFiles and not self.quietMode:
            nFiles = len(self.inputFiles)
            nEventsString = ( str(self.chains[self.mainTree].GetEntries()) if configuration.computeEntriesForReport() else
                              "%d (expected)"%self.nExpect if configuration.computeEntriesAtMakeFileList() else
                              "(number not computed)" )
            filesLines = ( '\n'.join(zip(*self.inputFiles)[0]) if len(self.inputFiles) < 5 else
                           '\n'.join(zip(*self.inputFiles[:2])[0]+("...",)[:len(self.inputFiles)-1]+zip(*self.inputFiles[2:][-2:])[0]) )
            plural = nFiles>1
            print utils.hyphens
            print "The %d \"%s\" input file%s:"%(nFiles, self.name, ['','s'][plural])
            print filesLines
            print "contain%s %s events."%(['s',''][plural], nEventsString)
            if self.skip :
                print "Skipping first %d events"%self.skip
            print utils.hyphens

    def deleteChains(self) : #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
        for chain in self.chains.values() : utils.delete(chain)
        for step in self.steps :
            for name,hist in list(step.book.iteritems()) :
                utils.delete(hist)
                #del step.book[name]
        
    def setupSteps(self, withBook = True, minimal = False) :
        r.gROOT.cd()
        current = r.gDirectory
        priorFilters = []

        for step in self.steps :
            step.setOutputFileStem(self.outputFileStem)
            step.setInputFileStem(self.inputFileStem)
            step.priorFilters = set(priorFilters)
            if step.isSelector and step.name not in ['master','label'] : priorFilters.append((step.name,step.moreNames))
            if self.quietMode : step.makeQuiet()

            if withBook : 
                current = current.mkdir(step.name)
                step.book = autoBook(current)

            if minimal : continue
            step.tracer = keyTracer(None) if self.trace and (step.isSelector or issubclass(type(step),wrappedChain.calculable)) else None
            assert step.isSelector ^ hasattr(step,"uponAcceptance"), "Step %s must implement 1 and only 1 of {select,uponAcceptance}"%step.name
            if step.disabled : continue
            step.setup(self.chains[self.mainTree], self.mainTree[0])

    def endSteps(self) : [ step.endFunc(self.chains) for step in self.steps ]
        
    def writeRoot(self) :
        def writeFromSteps() :
            while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
            for step in self.steps :
                r.gDirectory.mkdir(step.name, step.moreNames).cd()
                for hist in [step.book[name] for name in step.book.fillOrder] : hist.Write()
                if self.trace and step.isSelector :
                    r.gDirectory.mkdir("Calculables").cd()
                    for key in step.tracer.tracedKeys : r.gDirectory.mkdir(key)
                    r.gDirectory.GetMother().cd()
    
        def writeNodesUsed() :
            while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
            r.gDirectory.mkdir("Leaves",".").cd()
            for leaf in self.leavesUsed: r.gDirectory.mkdir(*leaf)
            r.gDirectory.GetMother().cd()
            r.gDirectory.mkdir("Calculables",".").cd()
            for calc in self.calculablesUsed :
                r.gDirectory.mkdir(*calc).cd()
                for dep in self.calculableDependencies[calc[0]] : r.gDirectory.mkdir(dep[0]+dep[1],dep[1])
                r.gDirectory.GetMother().cd()
            r.gDirectory.GetMother().cd()

        outputFile = r.TFile(self.steps[0].outputFileName, "RECREATE")
        writeNodesUsed()
        writeFromSteps()
        outputFile.Close()

    def writePickle(self) :
        def pickleJar(step) :
            if step.name=='master' and configuration.computeEntriesAtMakeFileList() and not self.byEvents:
                msg = "Expect: %d, Actual: %d"%(self.nExpect,step.nPass+step.nFail)
                assert abs(step.nPass + step.nFail - self.nExpect) < 1 , msg
            inter = set(step.varsToPickle()).intersection(set(['nPass','nFail','outputFileName']))
            assert not inter, "%s is trying to pickle %s, which %s reserved for use by analysisStep."%(step.name, str(inter), ["is","are"][len(inter)>1])
            return dict([ (item, getattr(step,item)) for item in step.varsToPickle()+['nPass','nFail']] +
                        [('outputFileName', getattr(step,'outputFileName').replace(self.outputDir, self.globalDir))])

        utils.writePickle( self.pickleFileName,
                           [ [pickleJar(step) for step in self.steps], self.calculablesUsed, self.leavesUsed] )

    def incompleteSlices(self):
        out = []
        for iSlice in range(self.nSlices):
            pickleFileBlocks = self.pickleFileName.split('/')
            pickleFileBlocks.insert(-1,self.name)
            pickleFileBlocks[-1] = pickleFileBlocks[-1].replace(self.name,
                                                                self.childName(iSlice),
                                                                1)
            pickleFileName = '/'.join(pickleFileBlocks)
            if not os.path.exists(pickleFileName) :
                fields = pickleFileName.split('/')
                script = '/'.join(fields[:-1] + ["job%s.sh"%fields[-1].replace('.pickledData','').split('_')[-1]])
                out.append(script)
        return out

    def mergeFunc(self):
        cleanUpList = []
        self.setupSteps(minimal = True)
        self.calculablesUsed = set()
        self.leavesUsed = set()
        products = [collections.defaultdict(list) for step in self.steps]
        
        for iSlice in range(self.nSlices):
            pickleFileBlocks = self.pickleFileName.split('/')
            pickleFileBlocks.insert(-1,self.name)
            pickleFileBlocks[-1] = pickleFileBlocks[-1].replace(self.name,
                                                                self.childName(iSlice),
                                                                1)
            cleanUpList.append( '/'.join(pickleFileBlocks[:-1]) )
            dataByStep,calcsUsed,leavesUsed = utils.readPickle( '/'.join(pickleFileBlocks) )
            self.calculablesUsed |= calcsUsed
            self.leavesUsed |= leavesUsed
            for stepDict,data in zip(products, dataByStep) :
                for key,val in data.iteritems() : stepDict[key].append(val)
    
        for step,stepDict in filter(lambda s: s[0].isSelector, zip(self.steps, products)) :
            step.increment(True, sum(stepDict["nPass"]))
            step.increment(False,sum(stepDict["nFail"]))

        self.printStats()
        for iStep,step,stepDict in zip(range(len(self.steps)),self.steps,products) :
            if iStep : rootFile.cd('/'.join(step.name for step in self.steps[:iStep+1] ))
            step.mergeFunc(stepDict)
            if not iStep: rootFile = r.TFile.Open(self.steps[0].outputFileName, "UPDATE")
        rootFile.Close()
        for dirName in cleanUpList : os.system("rm -fr %s"%dirName)

    def printStats(self) :
        if self.quietMode : return
        print utils.hyphens
        print self.name
        
        if configuration.printNodesUsed() :
            print utils.hyphens
            print "Leaves accessed:"
            print str([x[0] for x in self.leavesUsed]).replace("'","")
            print utils.hyphens
            print "Calculables accessed:"
            print str([x[0] for x in self.calculablesUsed]).replace("'","")

        print utils.hyphens
        print "Calculables' configuration:"
        print '\n'.join("%s\t\t%s"%calc for calc in self.calculablesUsed if calc[1])
                
        #print step statistics
        if not len(self.steps) : return
        print utils.hyphens
        width = self.steps[0].integerWidth
        print "Steps:%s" % ("nPass ".rjust(width) + "(nFail)".rjust(width+2)).rjust(len(utils.hyphens)-len("Steps:"))
        for step in self.steps :
            step.printStatistics()
        print utils.hyphens
        print utils.hyphens

#####################################
