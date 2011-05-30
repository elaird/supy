import copy,array,os,cPickle,tempfile,sys
import wrappedChain,utils,steps,configuration
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self, fileDirectory = None, treeName = None, otherTreesToKeepWhenSkimming = None, leavesToBlackList = None,
                 localStem = None, globalStem = None, subDir = None, steps = None, calculables = None, inputFiles = None, name = None,
                 nEventsMax = None, quietMode = None, color = None, markerStyle = None) :

        for arg in ["fileDirectory", "treeName", "otherTreesToKeepWhenSkimming", "leavesToBlackList",
                    "localStem", "globalStem", "subDir", "inputFiles", "name", "nEventsMax", "quietMode", "color", "markerStyle"] :
            setattr(self, arg, eval(arg))

        for arg in ["steps", "calculables"] :
            setattr(self, arg, eval("copy.deepcopy(%s)"%arg))

        self.globalDir = "%s/%s/"%(self.globalStem, self.subDir)
        self.outputDir = self.globalDir #the value will be modified in self.prepareOutputDirectory()
        self.checkSteps()

    def childName(self, iSlice) :
        return "%s_%d"%(self.name, iSlice)

    def slice(self, iSlice, nSlices) :
        out = copy.deepcopy(self)
        out.inputFiles = out.inputFiles[iSlice::nSlices]
        out.name = self.childName(iSlice)
        return out

    def outputFileStem(self) :
        return "%s/%s"%(self.outputDir, self.name)

    def outputStepAndCalculableDataFileName(self) :
        return "%s%s"%(self.outputFileStem(), ".pickledData")

    def checkSteps(self) :
        for iStep,step in enumerate(self.steps) :
            if step.name()=="Master" :
                assert not iStep,"The master step must occur first."
                assert hasattr(step,"select"), "The master step must be a selector."
            else :
                assert iStep,"The master step must occur first."
        
    def go(self) :
        self.prepareOutputDirectory()
        
        self.setupChains(self.inputFiles)
        useSetBranchAddress = self.setupSteps()

        #loop through entries
        if self.nEventsMax!=0 :
            chainWrapper = wrappedChain.wrappedChain(self.inputChain,
                                                     calculables = self.calculables,
                                                     useSetBranchAddress = useSetBranchAddress,
                                                     leavesToBlackList = self.leavesToBlackList,
                                                     maxArrayLength = configuration.maxArrayLength(),
                                                     trace = configuration.trace(),
                                                     )
            map( self.processEvent, chainWrapper.entries(self.nEventsMax) )
            self.makeListsOfLeavesAndCalcsUsed( chainWrapper.activeKeys(), chainWrapper.calcDependencies() )
        else : self.makeListsOfLeavesAndCalcsUsed([], {})

        self.endSteps()
        self.pickleStepAndCalculableData()
        self.writeHistos()
        if not self.quietMode : print utils.hyphens
        
        #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
        self.inputChain.IsA().Destructor( self.inputChain )
        for chain in self.otherChainDict.values() :
            chain.IsA().Destructor( chain )

        self.moveFiles()

    def prepareOutputDirectory(self) :
        utils.mkdir(self.localStem)
        self.tmpDir = tempfile.mkdtemp(dir = self.localStem)
        self.outputDir = self.outputDir.replace(self.globalStem, self.tmpDir)
        utils.mkdir(self.outputDir)
        
    def moveFiles(self) :
        utils.mkdir(self.globalDir)
        os.system("rsync -a %s/ %s/"%(self.outputDir, self.globalDir))
        os.system("rm -r %s"%self.tmpDir)
        
    def processEvent(self,eventVars) :
        for step in self.steps :
            try:
                if not step.go(eventVars) : break
            except Exception as e:
                print
                print "Problem with %s"%type(step)
                print step.moreName
                print
                import traceback
                tb = sys.exc_info()[2]
                traceback.print_tb(tb, limit=10, file=sys.stdout)
                print e.__class__.__name__,":", e
                sys.exit(0)
        
    def setupChains(self,inputFiles) :
        nFiles = len(inputFiles)
        alreadyPrintedEllipsis = False

        if not self.quietMode :
            print utils.hyphens
            print "The %d \"%s\" input file%s:"%(nFiles, self.name, "s" if nFiles>1 else "")

        self.inputChain = r.TChain("chain")
        r.SetOwnership(self.inputChain, False)
        
        self.otherChainDict = {}
        otherChainCount = 0
        for item in self.otherTreesToKeepWhenSkimming :
            self.otherChainDict[item] = r.TChain("chain%d"%otherChainCount)
            r.SetOwnership(self.otherChainDict[item], False)
        
        for infile in inputFiles :
            #add main tree to main chain
            self.inputChain.Add("%s/%s/%s"%(infile, self.fileDirectory, self.treeName))
            
            #add other trees to other chains
            for (dirName,treeName),chain in self.otherChainDict.iteritems() :
                chain.Add("%s/%s/%s"%(infile, dirName, treeName))
            if (inputFiles.index(infile)<2 or inputFiles.index(infile)>(nFiles-3) ) :
                if not self.quietMode : print infile
            elif (not alreadyPrintedEllipsis) :
                if not self.quietMode : print "..."
                alreadyPrintedEllipsis = True

        outString = "contain%s %s events."%(("s" if nFiles==1 else ""),
                                            str(self.inputChain.GetEntries()) if configuration.computeEntriesForReport() else "(number not computed)",
                                            )
        if not self.quietMode :
            print outString
            print utils.hyphens
        r.gROOT.cd()

    def setupSteps(self, minimal = False) :
        returnValue = True
        r.gROOT.cd()
        current = r.gDirectory
        book = autoBook(current)

        for step in self.steps :
            step.setOutputFileStem(self.outputFileStem())            
            if hasattr(step,"select") :
                current = current.mkdir(step.name())
                book = autoBook(current)
            step.book = book
            step.tracer = wrappedChain.keyTracer(None) if configuration.trace() else None
            if minimal : continue
            if self.quietMode : step.makeQuiet()
            step.isSelector = hasattr(step,"select")            
            assert step.isSelector ^ hasattr(step,"uponAcceptance"), "Step %s must implement 1 and only 1 of {select,uponAcceptance}"%step.name()
            if step.requiresNoSetBranchAddress() : returnValue = False
            step.setup(self.inputChain, self.fileDirectory)

        #make Master aware of all steps' books
        self.steps[0].books = [step.book for step in self.steps]

        r.gROOT.cd()
        return returnValue

    def makeListsOfLeavesAndCalcsUsed(self, activeKeys, calculableDependencies) :
        self.calculableDependencies = calculableDependencies
        self.listOfLeavesUsed = []
        self.listOfCalculablesUsed = []
        for key,isLeaf,keyType in activeKeys :
            if isLeaf :
                self.listOfLeavesUsed.append((key, keyType))
            else :
                for calc in self.calculables :
                    if calc.name()!=key : continue
                    self.listOfCalculablesUsed.append( (calc.name(), "%s%s%s" % \
                                                        (calc.moreName if hasattr(calc,"moreName") else "",\
                                                         calc.moreName2 if hasattr(calc,"moreName2") else "",\
                                                         configuration.fakeString() if calc.isFake() else "") ) )
        
        self.listOfLeavesUsed.sort()
        self.listOfCalculablesUsed.sort()
        
    def printStats(self) :
        print utils.hyphens
        print self.name
        
        if configuration.printNodesUsed() :
            print utils.hyphens
            print "Leaves accessed:"
            print str([x[0] for x in self.listOfLeavesUsed]).replace("'","")
            print utils.hyphens
            print "Calculables accessed:"
            print str([x[0] for x in self.listOfCalculablesUsed]).replace("'","")

        print utils.hyphens
        print "Calculables' configuration:"
        for calc in filter( lambda x: x[1]!="", self.listOfCalculablesUsed) :
            print "%s\t\t%s"%calc
                
        #print step statistics
        if not len(self.steps) : return
        print utils.hyphens
        width = self.steps[0].integerWidth
        print "Steps:%s" % ("nPass ".rjust(width) + "(nFail)".rjust(width+2)).rjust(len(utils.hyphens)-len("Steps:"))
        for step in self.steps :
            step.printStatistics()
        print utils.hyphens
        
    def writeHistosFromBooks(self) :
        while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
        wroteSlash = False
        for step in self.steps :
            name = step.book._autoBook__directory.GetName()
            if '/' in name :
                if wroteSlash: continue
                wroteSlash = True
            elif not step.isSelector: continue
            else:
                r.gDirectory.mkdir(name,step.moreName+step.moreName2).cd()
                if configuration.trace() :
                    r.gDirectory.mkdir("Calculables").cd()
                    for key in step.tracer.tracedKeys : r.gDirectory.mkdir(key)
                    r.gDirectory.GetMother().cd()
            
            for item in step.book.fillOrder :
                object = step.book[item]
                object.Write()
                object.Delete()
        while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
                    
    def writeNodesUsed(self) :
        while "/" not in r.gDirectory.GetName() : r.gDirectory.GetMotherDir().cd()
        r.gDirectory.mkdir("Leaves",".").cd()
        for leaf in self.listOfLeavesUsed: r.gDirectory.mkdir(*leaf)
        r.gDirectory.GetMother().cd()
        r.gDirectory.mkdir("Calculables",".").cd()
        for calc in self.listOfCalculablesUsed :
            r.gDirectory.mkdir(*calc).cd()
            for dep in self.calculableDependencies[calc[0]] : r.gDirectory.mkdir(dep)
            r.gDirectory.GetMother().cd()
        r.gDirectory.GetMother().cd()

    def writeHistos(self) :
        outputFile = r.TFile(self.steps[0].outputFileName(), "RECREATE")
        self.writeNodesUsed()
        self.writeHistosFromBooks()
        outputFile.Close()

    def endSteps(self) :
        for step in self.steps :
            step.endFunc(self.otherChainDict)

    def pickleStepAndCalculableData(self) :
        def listToDump() :
            out = []
            for step in self.steps :
                d = {}
                vars = set(step.varsToPickle())
                items = ["nPass", "nFail", "outputFileName"]
                inter = vars.intersection(set(items))
                assert not inter, "Variables to be pickled cannot be called anything in %s; %s is trying to pickle %s."%(str(items), step.name(), str(inter))
                for item in vars :
                    d[item] = getattr(step, item)
                for item in items :
                    if item=="outputFileName" :
                        d[item] = getattr(step, item)().replace(self.outputDir, self.globalDir)
                    else :
                        d[item] = getattr(step, item)()
                out.append(d)
            return out
            
        outFile = open(self.outputStepAndCalculableDataFileName(), "w")
        cPickle.dump([listToDump(), self.listOfCalculablesUsed, self.listOfLeavesUsed], outFile)
        outFile.close()
#####################################
