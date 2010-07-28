import copy,array,os
import wrappedChain
import ROOT as r
#####################################
class sampleSpecification :
    """name, data sample, cuts"""

    def __init__(self,inputFiles,name,nEvents,outputPrefix,steps,xs):
        self.name=name
        self.nEvents=nEvents
        self.inputFiles=inputFiles
        self.outputPrefix=outputPrefix
        self.outputPlotFileName=outputPrefix+"_"+self.name+"_plots.root"
        self.steps=copy.deepcopy(steps)
        self.xs=xs

        self.parentName=name
        self.splitMode=False

        self.fileDirectory="susyTree"
        self.treeName="tree"

    def doSplitMode(self,parentName) :
        self.splitMode=True
        self.parentName=parentName
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,sample,outDir):
        self.hyphens="".ljust(95,"-")

        #copy some stuff
        stuffToCopy=["nEvents","name","steps","inputFiles","xs","parentName","splitMode","fileDirectory","treeName"]
        for item in stuffToCopy :
            setattr(self,item,getattr(sample,item))

        #run in quiet mode iff the sample has been split
        self.quietMode=sample.splitMode

        self.outputPlotFileName=outDir+"/"+sample.outputPlotFileName
        self.outputStepDataFileName=self.outputPlotFileName.replace(".root",".steps")
        self.inputChain=r.TChain("chain")
        self.currentTreeNumber=-1

        self.chainVariableContainer=eventVariableContainer()
        self.extraVariableContainer=eventVariableContainer()

    def showBranches(self) :
        for branch in self.inputChain.GetListOfBranches() :
            branchName=branch.GetName()
            branch.GetEntry(1)
            print branchName,type(getattr(self.inputChain,branchName))
            
    def go(self) :
        self.setupChain(self.inputFiles)
        self.chainWrapper=wrappedChain.wrappedChain(self.inputChain)
        
        self.setupSteps()
        #self.showBranches()

        #loop through entries
        map( self.processEvent, self.chainWrapper.entries(self.nEvents) )

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
        outString+=" (xs=%6.4g"%self.xs+" pb)"
        if not self.quietMode : print outString
        if not self.quietMode : print self.hyphens
        r.gROOT.cd()

    def setupSteps(self) :
        for step in self.steps :
            step.bookHistos()
            if self.quietMode : step.makeQuiet()
            if self.splitMode : step.setSplitMode()
            step.selectNotImplemented=not hasattr(step,"select")
            step.uponAcceptanceImplemented=hasattr(step,"uponAcceptance")
            step.uponRejectionImplemented=hasattr(step,"uponRejection")
            if (hasattr(step,"setup")) : step.setup(self.inputChain,self.fileDirectory,self.name)

    def processEvent(self,eventVars) :
        chainVars=self.chainVariableContainer
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

        #write two "special" histograms
        xsHisto=r.TH1D("xsHisto",";dummy axis;#sigma (pb)",1,-0.5,0.5)
        xsHisto.SetBinContent(1,self.xs)
        xsHisto.Write()
            
        nEventsHisto=r.TH1D("nEventsHisto",";dummy axis;N_{events} read in",1,-0.5,0.5)
        nEventsHisto.SetBinContent(1,self.chainWrapper.entry)
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
class analysisStep :
    """generic analysis step"""

    nPass=0
    nFail=0
    nTotal=0
    integerWidth=10
    docWidth=30
    moreWidth=40
    moreName=""
    moreName2=""
    skimmerStepName="skimmer"
    displayerStepName="displayer"
    quietMode=False
    splitMode=False
    
    def go(self,eventVars,extraVars) :
        self.nTotal+=1

        if self.selectNotImplemented :
            self.nPass+=1
            if (self.uponAcceptanceImplemented) :
                self.uponAcceptance(eventVars,extraVars)
            return True

        if self.select(eventVars,extraVars) :
            self.nPass+=1
            if (self.uponAcceptanceImplemented) :
                self.uponAcceptance(eventVars,extraVars)
            return True
        else :
            self.nFail+=1
            if (self.uponRejectionImplemented) :
                self.uponRejection(eventVars,extraVars)
            return False

    def name(self) :
        return self.__doc__.ljust(self.docWidth)+self.moreName.ljust(self.moreWidth)

    def name2(self) :
        return "".ljust(self.docWidth)+self.moreName2.ljust(self.moreWidth)

    def makeQuiet(self) :
        self.quietMode=True
        
    def setSplitMode(self) :
        self.splitMode=True
        
    def printStatistics(self) :
        outString=self.name()
        outString2=self.name2()
        statString =   " nPass ="+str(self.nPass) .rjust(self.integerWidth)+";"
        statString+= "   nFail ="+str(self.nFail) .rjust(self.integerWidth)+";"
        #statString+="   nTotal ="+str(self.nTotal).rjust(self.integerWidth)+";"
        if (self.moreName2=="") :
            print outString+statString
        else :
            print outString
            print outString2+statString

    def bookHistos(self) : return
#####################################
class eventVariableContainer :
    """holds the values of variables that are not in the tree"""

    def __init__(self) :
        self.icfCleanJets=r.std.vector(r.Math.LorentzVector(r.Math.PxPyPzE4D('double')))()
        self.icfCleanJets.reserve(256)
#####################################
