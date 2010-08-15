import copy,array,os
import wrappedChain,utils
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,fileDirectory,treeName,otherTreesToKeepWhenSkimming,
                 outputDir,outputPlotFileName,steps,calculables,
                 sampleSpec,fileListCommand,xs,lumi,lumiWarn,
                 computeEntriesForReport,printNodesUsed,inputFiles = None):

        for arg in ["name","nEventsMax","color","markerStyle"] :
            setattr(self,arg,getattr(sampleSpec,arg))

        for arg in ["fileDirectory","treeName","otherTreesToKeepWhenSkimming",
                    "inputFiles","outputDir","fileListCommand","xs","lumi","lumiWarn",
                    "computeEntriesForReport","printNodesUsed","outputPlotFileName"] :
            setattr(self,arg,eval(arg))

        self.steps = copy.deepcopy(steps)
        self.calculables = copy.deepcopy(calculables)

        #these are needed to fill histograms properly in the case of overlapping MC ptHat samples
        self.needToConsiderPtHatThresholds = False
        self.ptHatThresholds=[]
        
        self.parentName = self.name
        self.splitMode = False
        self.quietMode = False
        self.setOutputFileNames()

    def setOutputFileNames(self) :
        self.outputStepAndCalculableDataFileName = self.outputPlotFileName.replace(".root",".pickledData")
        self.inputFileListFileName               = self.outputPlotFileName.replace(".root",".inputFileList")

    def go(self) :
        self.setupChains(self.inputFiles)
        useSetBranchAddress = self.setupSteps()

        #loop through entries
        chainWrapper = wrappedChain.wrappedChain(self.inputChain, calculables = self.calculables, useSetBranchAddress = useSetBranchAddress)
        map( self.processEvent, chainWrapper.entries(self.nEventsMax) )
        for step in self.steps :
            step.nPass = 0
            step.nFail = 0
            step.nTotal = 0
            for book in step.books.values() :
                if "counts" not in book : continue
                counts = book["counts"]
                step.nPass += int(counts.GetBinContent(2))
                step.nFail += int(counts.GetBinContent(1))
                step.nTotal += int(counts.Integral())

        #set data member to number actually used
        self.nEvents = 0
        if hasattr(chainWrapper,"entry") : self.nEvents = chainWrapper.entry
        for step in self.steps :
            if step.ignoreInAccounting or not step.isSelector : continue
            self.nEvents = step.nTotal
            break

        activeKeys = chainWrapper.activeKeys()
        self.makeDictOfCalculableConfigs(activeKeys)
        self.makeListOfLeavesUsed(activeKeys)
        self.printStats()
        self.endSteps()
        self.writeHistos()
        if self.splitMode : self.pickleStepAndCalculableData()
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
        if self.xs!=None :   outString+=" (xs input =%6.4g"%self.xs+" pb)"
        if self.lumi!=None : outString+=" (lumi input =%6.4g"%self.lumi+" / pb)"
            
        if not self.quietMode : print outString
        if not self.quietMode : print utils.hyphens
        r.gROOT.cd()

    def setupBooks(self,directory) :
        #set up books
        books = {}
        books[None] = autoBook(directory)
        #make books for ptHat bins (keyed by lower threshold)
        for iThreshold in range(len(self.ptHatThresholds)) :
            books[iThreshold+1] = autoBook(directory)
        return books

    def setupSteps(self) :
        returnValue=True
        r.gROOT.cd()
        current = r.gDirectory
        books = self.setupBooks(current)
        for step in self.steps :
            if hasattr(step,"select") and not step.ignoreInAccounting :
                current = current.mkdir(step.__doc__)
                books = self.setupBooks(current)
            step.books = books
            if self.quietMode : step.makeQuiet()
            if self.splitMode : step.setSplitMode()
            step.isSelector = hasattr(step,"select")            
            assert step.isSelector ^ hasattr(step,"uponAcceptance"), "Step %s must implement 1 and only 1 of {select,uponAcceptance}"%step.__doc__            
            if step.__doc__==step.skimmerStepName : returnValue=False
            if hasattr(step,"setup") : step.setup(self.inputChain,self.fileDirectory,self.name)

            step.needToConsiderPtHatThresholds = self.needToConsiderPtHatThresholds
            step.ptHatThresholds = self.ptHatThresholds
        r.gROOT.cd()
        return returnValue

    def doSplitMode(self,parentName) :
        self.splitMode=True
        self.quietMode=True
        self.parentName=parentName

    def makeDictOfCalculableConfigs(self,activeKeys) :
        self.calculableConfigDict={}
        for calc in self.calculables :
            if calc.name() not in activeKeys : continue
            self.calculableConfigDict[calc.name()]=""
            if hasattr(calc,"moreName")  : self.calculableConfigDict[calc.name()]+=" "+str(calc.moreName)
            if hasattr(calc,"moreName2") : self.calculableConfigDict[calc.name()]+="\n"+str(calc.moreName2)

    def makeListOfLeavesUsed(self,activeKeys) :
        self.listOfLeavesUsed=[]
        listOfCalcNames=[calc.name() for calc in self.calculables]
        for key in activeKeys :
            if key in listOfCalcNames : continue
            self.listOfLeavesUsed.append(key)
                                   
    def printStats(self) :
        if not self.quietMode :
            calcs = self.calculableConfigDict.keys()
            calcs.sort()
            self.listOfLeavesUsed.sort()
            if self.printNodesUsed :
            	print utils.hyphens
            	print "Leaves accessed:"
            	print str(self.listOfLeavesUsed).replace("'","")
            	print utils.hyphens
                print "Calculables accessed:"
                print str(calcs).replace("'","")

            print utils.hyphens
            print "Calculables' configuration:"
            for calc in calcs :
                if self.calculableConfigDict[calc]!="" :
                    print calc,self.calculableConfigDict[calc]
                
            #print step statistics
            if not len(self.steps) : return
            print utils.hyphens
            width = self.steps[0].integerWidth
            print "Steps:%s" % ("nPass ".rjust(width) + "(nFail)".rjust(width+2)).rjust(len(utils.hyphens)-len("Steps:"))
            for step in self.steps :
                step.printStatistics()

    def writeAllObjects(self) :
        for object in objectList :
            object.Write()
            object.Delete()

    def writeHistosFromBooks(self) :
        filedir = r.gDirectory.GetName()
        for iStep,step in enumerate(self.steps) :
            if (iStep and not step.isSelector) or step.ignoreInAccounting: continue
            name = step.books[None]._autoBook__directory.GetName()
            if '/' in name :
                r.TNamed("moreName",self.name).Write()
            else: r.gDirectory.mkdir(name).cd()
                
            for book in step.books.values() :
                for item in book.fillOrder :
                    object = book[item]
                    object.Write()
                    object.Delete()
        while "/" not in r.gDirectory.GetName() :
            r.gDirectory.GetMotherDir().cd()
                    
    def writeSpecialHistos(self) :
        xsHisto=r.TH1D("xsHisto",";dummy axis;#sigma (pb)",1,-0.5,0.5)
        if self.xs!=None : xsHisto.SetBinContent(1,self.xs)
        xsHisto.Write()
        
        lumiHisto=r.TH1D("lumiHisto",";dummy axis;integrated luminosity (pb^{-1})",1,-0.5,0.5)
        if self.lumi!=None : lumiHisto.SetBinContent(1,self.lumi)
        lumiHisto.Write()
        
        nEventsHisto=r.TH1D("nEventsHisto",";dummy axis;N_{events} read in",1,-0.5,0.5)
        nEventsHisto.SetBinContent(1,self.nEvents)
        nEventsHisto.Write()
        
        nJobsHisto=r.TH1D("nJobsHisto",";dummy axis;N_{jobs}",1,-0.5,0.5)
        nJobsHisto.SetBinContent(1,1)
        nJobsHisto.Write()

        if self.lumiWarn :
            lumiWarn=r.TNamed("lumiWarn","")
            lumiWarn.Write()

    def writeHistos(self) :
        if not self.quietMode : print utils.hyphens
        #r.gDirectory.ls()
        objectList = r.gDirectory.GetList()
        outputFile = r.TFile(self.outputPlotFileName,"RECREATE")
        zombie = outputFile.IsZombie()

        #self.writeAllObjects()
        self.writeHistosFromBooks()
        self.writeSpecialHistos()
        
        outputFile.Close()
        if not zombie :
            if not self.quietMode :            
                print "The output file \""+self.outputPlotFileName+"\" has been written."
            #else :
            #    print self.steps[-1].nPass,"/",self.steps[0].nTotal,"events were selected"

    def endSteps(self) :
        for step in self.steps :
            if hasattr(step,"endFunc") :
                step.endFunc(self.inputChain,self.otherChainDict,self.nEvents,self.xs)

    def pickleStepAndCalculableData(self) :
        keepList=["nTotal","nPass","nFail"]                 #used by all steps
        keepList.extend(["outputFileName","runLsDict"])     #for displayer,skimmer,jsonMaker
        keepList.extend(["__doc__","moreName","moreName2"]) #not strictly needed; only for debugging
        outListSteps=[]
        for step in self.steps :
            outListSteps.append( {} )
            for item in keepList :
                if hasattr(step,item): outListSteps[-1][item]=getattr(step,item)

        import os,cPickle
        outFileName=os.path.expanduser(self.outputStepAndCalculableDataFileName)
        outFile=open(outFileName,"w")
        cPickle.dump([outListSteps,self.calculableConfigDict,self.listOfLeavesUsed],outFile)
        outFile.close()
#####################################
