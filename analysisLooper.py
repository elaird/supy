import copy,array,os
import wrappedChain
from autoBook import autoBook
import ROOT as r
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,outputDir,inputFiles,name,nEvents,outputPrefix,steps,xs,lumi,isMc):
        self.hyphens="".ljust(95,"-")

        self.name=name
        self.nEvents=nEvents
        self.inputFiles=inputFiles
        self.steps=copy.deepcopy(steps)
        self.xs=xs
        self.lumi=lumi
        self.isMc=isMc

        self.outputDir=outputDir
        self.outputPrefix=outputPrefix

        self.parentName=name
        self.splitMode=False
        self.quietMode=False

        self.fileDirectory="susyTree"
        self.treeName="tree"

        self.outputPlotFileName=self.outputDir+"/"+self.outputPrefix+"_"+self.name+"_plots.root"
        self.outputStepDataFileName=self.outputPlotFileName.replace(".root",".steps")

        self.extraVariableContainer=eventVariableContainer()

    def doSplitMode(self,parentName) :
        self.splitMode=True
        self.quietMode=True
        self.parentName=parentName

    def showBranches(self) :
        for branch in self.inputChain.GetListOfBranches() :
            branchName=branch.GetName()
            branch.GetEntry(1)
            print branchName,type(getattr(self.inputChain,branchName))

    def go(self) :
        self.setupChain(self.inputFiles)
        #self.showBranches()

        self.books = {}
        self.books[None] = autoBook()
        useSetBranchAddress=self.setupSteps()

        #loop through entries
        chainWrapper=wrappedChain.wrappedChain(self.inputChain,useSetBranchAddress=useSetBranchAddress)
        map( self.processEvent, chainWrapper.entries(self.nEvents) )

        #set data member to number actually used
        self.nEvents=0
        if hasattr(chainWrapper,"entry") : self.nEvents=1+chainWrapper.entry

        self.printStats()
        self.endSteps()
        self.writeHistos()
        if self.splitMode : self.pickleStepData()
        if not self.quietMode : print self.hyphens
        
        #free up memory
        del self.inputChain

    def setupChain(self,inputFiles) :
        nFiles=len(inputFiles)
        alreadyPrintedEllipsis=False

        if not self.quietMode : print self.hyphens
        outString="The "+str(nFiles)+" \""+self.name+"\" input file"
        if (nFiles>1) : outString+="s"
        if not self.quietMode : print outString+":"

        self.inputChain=r.TChain("chain")
        for infile in inputFiles :
            self.inputChain.Add(infile+"/"+self.fileDirectory+"/"+self.treeName)

            if (inputFiles.index(infile)<2 or inputFiles.index(infile)>(nFiles-3) ) :
                if not self.quietMode : print infile
            elif (not alreadyPrintedEllipsis) :
                if not self.quietMode : print "..."
                alreadyPrintedEllipsis=True

        outString="contain"
        if (nFiles==1) : outString+="s"

        outString+=" "+str(self.inputChain.GetEntries())
        outString+=" events."
        if self.xs!=None :   outString+=" (xs=%6.4g"%self.xs+" pb)"
        if self.lumi!=None : outString+=" (lumi=%6.4g"%self.lumi+" / pb)"
            
        if not self.quietMode : print outString
        if not self.quietMode : print self.hyphens
        r.gROOT.cd()

    def setupSteps(self) :
        returnValue=True
        for step in self.steps :
            step.bookHistos()
            step.books = self.books
            if self.quietMode : step.makeQuiet()
            if self.splitMode : step.setSplitMode()
            step.selectNotImplemented=not hasattr(step,"select")
            step.uponAcceptanceImplemented=hasattr(step,"uponAcceptance")
            step.uponRejectionImplemented=hasattr(step,"uponRejection")
            if step.__doc__==step.skimmerStepName : returnValue=False
            if hasattr(step,"setup") : step.setup(self.inputChain,self.fileDirectory,self.name)
        return returnValue
    
    def processEvent(self,eventVars) :
        extraVars=self.extraVariableContainer
        extraVars.localEntry=eventVars._wrappedChain__localEntry
        extraVars.entry=eventVars.entry
        
        for step in self.steps :
            if not step.go(eventVars,extraVars) : break
        
    def printStats(self) :
        if not self.quietMode :
            print self.hyphens
            for step in self.steps :
                step.printStatistics()

    def writeHistos(self) :
        if not self.quietMode : print self.hyphens
        #r.gDirectory.ls()
        objectList=r.gDirectory.GetList()
        outputFile=r.TFile(self.outputPlotFileName,"RECREATE")
        zombie=outputFile.IsZombie()

        for object in objectList :
            object.Write()
            object.Delete()

        for book in self.books.values() :
            for object in book.values() :
                object.Write()
                object.Delete()

        #write some "special" histograms
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
        
        outputFile.Close()
        if not zombie :
            if not self.quietMode :            
                print "The output file \""+self.outputPlotFileName+"\" has been written."
            #else :
            #    print self.steps[-1].nPass,"/",self.steps[0].nTotal,"events were selected"

    def endSteps(self) :
        for step in self.steps :
            if hasattr(step,"endFunc") :
                step.endFunc(self.inputChain,self.hyphens,self.nEvents,self.xs)

    def pickleStepData(self) :
        keepList=["nTotal","nPass","nFail","outputFileName"]
        keepList.extend(["__doc__","moreName","moreName2"])#not strictly needed; only for debugging
        outList=[]
        for step in self.steps :
            outList.append( {} )
            for item in keepList :
                if hasattr(step,item): outList[-1][item]=getattr(step,item)

        import os,cPickle
        outFileName=os.path.expanduser(self.outputStepDataFileName)
        outFile=open(outFileName,"w")
        cPickle.dump(outList,outFile)
        outFile.close()
#####################################
class eventVariableContainer :
    """holds the values of variables that are not in the tree"""
#####################################
