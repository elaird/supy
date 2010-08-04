import copy,array,os
import wrappedChain
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,fileDirectory,treeName,otherTreesToKeepWhenSkimming,
                 hyphens,outputDir,inputFiles,name,nEvents,outputPlotFileName,steps,calculables,xs,lumi,
                 computeEntriesForReport,printNodesUsed):

        self.fileDirectory=fileDirectory
        self.treeName=treeName
        self.otherTreesToKeepWhenSkimming=otherTreesToKeepWhenSkimming
        
        self.hyphens=hyphens
        self.name=name
        self.nEvents=nEvents
        self.inputFiles=inputFiles
        self.steps=copy.deepcopy(steps)
        self.calculables=copy.deepcopy(calculables)
        self.xs=xs
        self.lumi=lumi

        #these are needed to fill histograms properly in the case of overlapping MC ptHat samples
        self.needToConsiderPtHatThresholds=False
        self.ptHatThresholds=[]
        
        self.outputDir=outputDir

        self.parentName=name
        self.splitMode=False
        self.quietMode=False

        self.computeEntriesForReport=computeEntriesForReport
        self.printNodesUsed=printNodesUsed

        self.outputPlotFileName=outputPlotFileName
        self.outputStepAndCalculableDataFileName=self.outputPlotFileName.replace(".root",".pickledData")

    def go(self) :
        self.setupChains(self.inputFiles)
        self.setupBooks()
        useSetBranchAddress=self.setupSteps()

        #loop through entries
        chainWrapper=wrappedChain.wrappedChain(self.inputChain,calculables=self.calculables,useSetBranchAddress=useSetBranchAddress)
        map( self.processEvent, chainWrapper.entries(self.nEvents) )

        #set data member to number actually used
        self.nEvents=0
        if hasattr(chainWrapper,"entry") : self.nEvents=1+chainWrapper.entry

        activeKeys=chainWrapper.activeKeys()
        self.makeDictOfCalculableConfigs(activeKeys)
        self.makeListOfLeavesUsed(activeKeys)
        self.printStats()
        self.endSteps()
        self.writeHistos()
        if self.splitMode : self.pickleStepAndCalculableData()
        if not self.quietMode : print self.hyphens
        
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

        if not self.quietMode : print self.hyphens
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
        if not self.quietMode : print self.hyphens
        r.gROOT.cd()

    def setupBooks(self) :
        #set up books
        self.books = {}
        self.books[None] = autoBook()
        #make books for ptHat bins (keyed by lower threshold)
        for iThreshold in range(len(self.ptHatThresholds)) :
            self.books[iThreshold+1]=autoBook()

    def setupSteps(self) :
        returnValue=True
        for step in self.steps :
            step.books = self.books
            if self.quietMode : step.makeQuiet()
            if self.splitMode : step.setSplitMode()
            step.selectNotImplemented=not hasattr(step,"select")
            step.uponAcceptanceImplemented=hasattr(step,"uponAcceptance")
            step.uponRejectionImplemented=hasattr(step,"uponRejection")
            if step.__doc__==step.skimmerStepName : returnValue=False
            if hasattr(step,"setup") : step.setup(self.inputChain,self.fileDirectory,self.name)

            step.needToConsiderPtHatThresholds=self.needToConsiderPtHatThresholds
            step.ptHatThresholds=self.ptHatThresholds
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
            if hasattr(calc,"moreName2") : self.calculableConfigDict[calc.name()]+=" "+str(calc.moreName2)

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
            	print self.hyphens
            	print "Leaves accessed:"
            	print str(self.listOfLeavesUsed).replace("'","")
            	print self.hyphens
                print "Calculables accessed:"
                print str(calcs).replace("'","")

            print self.hyphens
            print "Calculables' configuration:"
            for calc in calcs :
                if self.calculableConfigDict[calc]!="" :
                    print calc,self.calculableConfigDict[calc]
                
            #print step statistics
            if not len(self.steps) : return
            print self.hyphens
            width = self.steps[0].integerWidth
            print "Steps:%s" % ("nPass ".rjust(width) + "(nFail)".rjust(width+2)).rjust(len(self.hyphens)-len("Steps:"))
            for step in self.steps :
                step.printStatistics()

    def writeAllObjects(self) :
        for object in objectList :
            object.Write()
            object.Delete()

    def writeHistosFromBooks(self) :
        for book in self.books.values() :
            for item in book.fillOrder :
                object=book[item]
                object.Write()
                object.Delete()

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

    def writeHistos(self) :
        if not self.quietMode : print self.hyphens
        #r.gDirectory.ls()
        objectList=r.gDirectory.GetList()
        os.system("mkdir -p "+self.outputDir)
        outputFile=r.TFile(self.outputPlotFileName,"RECREATE")
        zombie=outputFile.IsZombie()

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
                step.endFunc(self.inputChain,self.otherChainDict,self.hyphens,self.nEvents,self.xs)

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
