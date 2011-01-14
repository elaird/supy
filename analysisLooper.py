import copy,array,os,cPickle
import wrappedChain,utils,steps,configuration
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self, fileDirectory, treeName, otherTreesToKeepWhenSkimming, leavesToBlackList,
                 outputDir, outputPlotFileName, steps, calculables, fileListCommand,
                 computeEntriesForReport, printNodesUsed, sampleName, nEventsMax, color, markerStyle) :

        self.name = sampleName

        for arg in ["fileDirectory", "treeName", "otherTreesToKeepWhenSkimming", "leavesToBlackList",
                    "outputDir", "outputPlotFileName", "fileListCommand", "nEventsMax", "color", "markerStyle",
                    "computeEntriesForReport","printNodesUsed"] :
            setattr(self,arg,eval(arg))

        self.inputFiles = None
        self.steps = copy.deepcopy(steps)
        self.calculables = copy.deepcopy(calculables)

        self.parentName = self.name
        self.quietMode = False
        self.setOutputFileNames()

    def setOutputFileNames(self) :
        self.outputStepAndCalculableDataFileName = self.outputPlotFileName.replace(".root",".pickledData")
        self.inputFileListFileName               = self.outputPlotFileName.replace(".root",".inputFileList")

    def go(self) :
        self.setupChains(self.inputFiles)
        useSetBranchAddress = self.setupSteps()

        #check for problems with the master
        for iStep,step in enumerate(self.steps) :
            if step.name()=="master" :
                assert not iStep,"The master step must occur first."
                assert hasattr(step,"select"), "The master step must be a selector."

        #loop through entries
        chainWrapper = wrappedChain.wrappedChain(self.inputChain,
                                                 calculables = self.calculables,
                                                 useSetBranchAddress = useSetBranchAddress,
                                                 leavesToBlackList = self.leavesToBlackList,
                                                 maxArrayLength = configuration.maxArrayLength(),
                                                 )
        map( self.processEvent, chainWrapper.entries(self.nEventsMax) )

        self.makeListsOfLeavesAndCalcsUsed( chainWrapper.activeKeys() )

        self.endSteps()
        self.pickleStepAndCalculableData()
        self.writeHistos()
        if not self.quietMode : print utils.hyphens
        
        #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
        self.inputChain.IsA().Destructor( self.inputChain )
        for chain in self.otherChainDict.values() :
            chain.IsA().Destructor( chain )

    def processEvent(self,eventVars) :
        for step in self.steps :
            if not step.go(eventVars) : break

    def setupChains(self,inputFiles) :
        nFiles=len(inputFiles)
        alreadyPrintedEllipsis=False

        if not self.quietMode : print utils.hyphens
        outString="The "+str(nFiles)+" \""+self.name+"\" input file"
        if (nFiles>1) : outString+="s"
        if not self.quietMode : print outString+":"

        self.inputChain=r.TChain("chain")
        r.SetOwnership(self.inputChain,False)
        
        self.otherChainDict={}
        otherChainCount=0
        for item in self.otherTreesToKeepWhenSkimming :
            self.otherChainDict[item]=r.TChain("chain%d"%otherChainCount)
            r.SetOwnership(self.otherChainDict[item],False)
        
        for infile in inputFiles :
            #add main tree to main chain
            self.inputChain.Add(infile+"/"+self.fileDirectory+"/"+self.treeName)
            
            #add other trees to other chains
            for (dirName,treeName),chain in self.otherChainDict.iteritems() :
                chain.Add(infile+"/"+dirName+"/"+treeName)

            if (inputFiles.index(infile)<2 or inputFiles.index(infile)>(nFiles-3) ) :
                if not self.quietMode : print infile
            elif (not alreadyPrintedEllipsis) :
                if not self.quietMode : print "..."
                alreadyPrintedEllipsis=True

        outString="contain"
        if (nFiles==1) : outString+="s"

        if self.computeEntriesForReport : outString+=" "+str(self.inputChain.GetEntries())
        else :                            outString+=" (number not computed)"

        outString+=" events."
            
        if not self.quietMode : print outString
        if not self.quietMode : print utils.hyphens
        r.gROOT.cd()

    def setupSteps(self, booksOnly = False) :
        returnValue = True
        r.gROOT.cd()
        current = r.gDirectory
        book = autoBook(current)

        for step in self.steps :
            if hasattr(step,"select") :
                current = current.mkdir(step.name())
                book = autoBook(current)
            step.book = book
            if booksOnly : continue
            if self.quietMode : step.makeQuiet()
            step.isSelector = hasattr(step,"select")            
            assert step.isSelector ^ hasattr(step,"uponAcceptance"), "Step %s must implement 1 and only 1 of {select,uponAcceptance}"%step.name()
            if step.requiresNoSetBranchAddress() : returnValue = False
            step.setup(self.inputChain, self.fileDirectory, self.name, self.outputDir)

        r.gROOT.cd()
        self.steps[0].notify(self.outputPlotFileName)#inform the master of the name of this job's output file
        return returnValue

    def setQuietMode(self, nWorkers) :
        if nWorkers!=None and nWorkers>1 :
            self.quietMode = True

    def makeListsOfLeavesAndCalcsUsed(self, activeKeys) :
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
        
        if self.printNodesUsed :
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
            else: r.gDirectory.mkdir(name,step.moreName+step.moreName2).cd()
            
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
        for calc in self.listOfCalculablesUsed : r.gDirectory.mkdir(*calc)
        r.gDirectory.GetMother().cd()

    def writeHistos(self) :
        outputFile = r.TFile(self.outputPlotFileName,"RECREATE")
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
                items = ["nPass","nFail"]
                assert not vars.intersection(set(items)), "Variables to be pickled cannot be called anything in %s."%str(items)
                for item in vars :
                    d[item] = getattr(step, item)
                for item in items :
                    d[item] = getattr(step, item)()
                out.append(d)
            return out
            
        outFileName = os.path.expanduser(self.outputStepAndCalculableDataFileName)
        outFile = open(outFileName,"w")
        cPickle.dump([listToDump(), self.listOfCalculablesUsed, self.listOfLeavesUsed], outFile)
        outFile.close()
#####################################
