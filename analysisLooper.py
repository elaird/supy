import copy,array,os,cPickle,tempfile,sys,collections
import wrappedChain,utils,steps,configuration
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self, mainTree = None, otherTreesToKeepWhenSkimming = None, leavesToBlackList = None,
                 localStem = None, globalStem = None, subDir = None, steps = None, calculables = None, inputFiles = None, name = None,
                 nEventsMax = None, quietMode = None) :

        for arg in ["mainTree", "otherTreesToKeepWhenSkimming", "leavesToBlackList",
                    "steps", "calculables",
                    "localStem", "globalStem", "subDir", "inputFiles", "name", "nEventsMax", "quietMode"] :
            setattr(self, arg, eval(arg))

        self.outputDir = self.globalDir #the value will be modified in self.prepareOutputDirectory()
        self.checkSteps()

    @property
    def globalDir(self) : return "%s/%s/"%(self.globalStem, self.subDir)
    @property
    def outputFileStem(self) :  return "%s/%s"%(self.outputDir, self.name)
    @property
    def pickleFileName(self) : return "%s%s"%(self.outputFileStem, ".pickledData")

    def checkSteps(self) :
        for iStep,step in enumerate(self.steps) :
            if iStep : continue
            assert step.name=="Master", "The master step must occur first."
            assert step.isSelector, "The master step must be a selector."
        selectors = [ (s.name,s.moreName,s.moreName2) for s in filter(lambda s: s.isSelector, self.steps) ]
        for sel in selectors : assert 1==selectors.count(sel), "Duplicate selector (%s,%s,%s) is not allowed."%sel

    def childName(self, iSlice) : return "%s_%d"%(self.name, iSlice)
    def slice(self, iSlice, nSlices) :
        out = copy.deepcopy(self)
        out.inputFiles = out.inputFiles[iSlice::nSlices]
        out.name = self.childName(iSlice)
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
        self.moveFiles()
        if not self.quietMode : print utils.hyphens

    def loop(self) :
        if self.nEventsMax!=0 :
            chainWrapper = wrappedChain.wrappedChain( self.chains[self.mainTree],
                                                      calculables = self.calculables,
                                                      useSetBranchAddress = not any([step.requiresNoSetBranchAddress() for step in self.steps]),
                                                      leavesToBlackList = self.leavesToBlackList,
                                                      maxArrayLength = configuration.maxArrayLength(),
                                                      trace = configuration.trace(),
                                                      )
            [ all(step(eventVars) for step in self.steps) for eventVars in chainWrapper.entries(self.nEventsMax) ]
            self.recordLeavesAndCalcsUsed( chainWrapper.activeKeys(), chainWrapper.calcDependencies() )
        else : self.recordLeavesAndCalcsUsed([], {})

    def recordLeavesAndCalcsUsed(self, activeKeys, calculableDependencies) :
        calcs = dict([(calc.name,calc) for calc in self.calculables])
        def calcTitle(key) : return "%s%s%s"%(calcs[key].moreName, calcs[key].moreName2, configuration.fakeString() if calcs[key].isFake() else "")
        self.calculablesUsed = set([ (key,calcTitle(key)) for key,isLeaf,keyType in filter(lambda k:not k[1], activeKeys)])
        self.leavesUsed      = set([ (key,       keyType) for key,isLeaf,keyType in filter(lambda k:k[1], activeKeys)])
        self.calculableDependencies = {}
        for key,val in calculableDependencies.iteritems() :
            self.calculableDependencies[key] = set(map(lambda c: c if type(c)==tuple else (c,c),val))
        
    def prepareOutputDirectory(self) :
        utils.mkdir(self.localStem)
        self.tmpDir = tempfile.mkdtemp(dir = self.localStem)
        self.outputDir = self.outputDir.replace(self.globalStem, self.tmpDir)
        utils.mkdir(self.outputDir)
        
    def moveFiles(self) :
        utils.mkdir(self.globalDir)
        os.system("rsync -a %s/ %s/"%(self.outputDir, self.globalDir))
        os.system("rm -r %s"%self.tmpDir)
        
    def setupChains(self) :
        self.chains = dict( [(item,r.TChain("chain%d"%iItem)) for iItem,item in enumerate([self.mainTree]+self.otherTreesToKeepWhenSkimming)])
        for (dirName,treeName),chain in self.chains.iteritems() :
            for infile in self.inputFiles : chain.Add("%s/%s/%s"%(infile, dirName, treeName))
            r.SetOwnership(chain, False)

        if not self.quietMode :
            nFiles = len(self.inputFiles)
            nEventsString = str(self.chains[self.mainTree].GetEntries()) if configuration.computeEntriesForReport() else "(number not computed)"
            print utils.hyphens
            print "The %d \"%s\" input file%s:"%(nFiles, self.name, "s" if nFiles>1 else '')
            print '\n'.join(self.inputFiles[:2]+["..."][:len(self.inputFiles)-1]+self.inputFiles[2:][-2:])
            print "contain%s %s events."%(("s" if nFiles==1 else ""), nEventsString)
            print utils.hyphens

    def deleteChains(self) : #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
        for chain in self.chains.values() : chain.IsA().Destructor( chain )        


    def setupSteps(self, minimal = False) :
        r.gROOT.cd()
        current = r.gDirectory
        priorFilters = []
        self.steps[0].books = []

        for step in self.steps :
            step.setOutputFileStem(self.outputFileStem)
            current = current.mkdir(step.name)
            step.book = autoBook(current)
            step.tracer = wrappedChain.keyTracer(None) if configuration.trace() else None
            step.priorFilters = set(priorFilters)

            self.steps[0].books.append(step.book)
            if step.isSelector : priorFilters.append((step.name,step.moreName+step.moreName2))

            if minimal : continue
            if self.quietMode : step.makeQuiet()
            assert step.isSelector ^ hasattr(step,"uponAcceptance"), "Step %s must implement 1 and only 1 of {select,uponAcceptance}"%step.name
            step.setup(self.chains[self.mainTree], self.mainTree[0])

    def endSteps(self) : [ step.endFunc(self.chains) for step in self.steps ]
        
    def writeRoot(self) :
        def writeFromSteps() :
            while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
            for step in self.steps :
                r.gDirectory.mkdir(step.book.title, step.moreName+step.moreName2).cd()
                for hist in [step.book[name] for name in step.book.fillOrder] : hist.Write()
                if configuration.trace() and step.isSelector :
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
                for dep in self.calculableDependencies[calc[0]] : r.gDirectory.mkdir(*dep)
                r.gDirectory.GetMother().cd()
            r.gDirectory.GetMother().cd()

        outputFile = r.TFile(self.steps[0].outputFileName, "RECREATE")
        writeNodesUsed()
        writeFromSteps()
        outputFile.Close()

    def writePickle(self) :
        def pickleJar(step) :
            inter = set(step.varsToPickle()).intersection(set(['nPass','nFail','outputFileName']))
            assert not inter, "%s is trying to pickle %s, which %s reserved for use by analysisStep."%(step.name, str(inter), "is" if len(inter)==1 else "are")
            return dict([ (item, getattr(step,item)) for item in step.varsToPickle()+['nPass','nFail']] +
                        [('outputFileName', getattr(step,'outputFileName').replace(self.outputDir, self.globalDir))])

        utils.writePickle( self.pickleFileName,
                           [ [pickleJar(step) for step in self.steps], self.calculablesUsed, self.leavesUsed] )

    def readyMerge(self, listOfSlices) :
        foundAll = True
        for pickleFileName in [ self.pickleFileName.replace(self.name, self.childName(iSlice)) for iSlice in listOfSlices ] :
            if not os.path.exists(pickleFileName) :
                print "Can't find file : %s"%pickleFileName
                foundAll = False
        return foundAll

    def mergeFunc(self, listOfSlices) :
        cleanUpList = []
        self.setupSteps(minimal = True)
        self.calculablesUsed = set()
        self.leavesUsed = set()
        products = [collections.defaultdict(list) for step in self.steps]
        
        for iSlice in listOfSlices :
            cleanUpList.append( self.pickleFileName.replace(self.name, self.childName(iSlice)) )
            dataByStep,calcsUsed,leavesUsed = utils.readPickle( cleanUpList[-1] )
            self.calculablesUsed |= calcsUsed
            self.leavesUsed |= leavesUsed
            for stepDict,data in zip(products, dataByStep) :
                for key,val in data.iteritems() : stepDict[key].append(val)
    
        for step,stepDict in filter(lambda s: s[0].isSelector, zip(self.steps, products)) :
            step.increment(True, sum(stepDict["nPass"]))
            step.increment(False,sum(stepDict["nFail"]))
                
        self.printStats()
        print utils.hyphens
        for step,stepDict in zip(self.steps, products) : step.mergeFunc(stepDict)
        for fileName in cleanUpList : os.remove(fileName)

    def printStats(self) :
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
        for calc in filter( lambda x: x[1]!="", self.calculablesUsed) :
            print "%s\t\t%s"%calc
                
        #print step statistics
        if not len(self.steps) : return
        print utils.hyphens
        width = self.steps[0].integerWidth
        print "Steps:%s" % ("nPass ".rjust(width) + "(nFail)".rjust(width+2)).rjust(len(utils.hyphens)-len("Steps:"))
        for step in self.steps :
            step.printStatistics()
        print utils.hyphens

#####################################
