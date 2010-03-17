import copy,array
import ROOT as r

#####################################
def globalSetup() :
    r.gROOT.ProcessLine(".L SusyCAFpragmas.h+")
    r.TH1.SetDefaultSumw2(True)
#####################################
class sampleSpecification :
    """name, data sample, cuts"""

    def __init__(self,dict,name,nEvents,outputPrefix,steps,xs=1.0):
        self.name=name
        self.nEvents=nEvents
        self.inputFiles=dict[name]
        self.outputPlotFileName=outputPrefix+"_"+self.name+"_plots.root"
        self.steps=copy.deepcopy(steps)
        self.xs=xs

        self.fileDirectory="susyTree"
        self.treeName="tree"
        self.useSetBranchAddress=True
        self.leafNamePrefixes=[]
        self.leafNameSuffixes=[]
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,sample,outDir):
        self.hyphens="".ljust(95,"-")

        #copy some stuff
        stuffToCopy=["nEvents","name","steps","inputFiles","xs","fileDirectory","treeName","useSetBranchAddress","leafNamePrefixes","leafNameSuffixes"]
        for item in stuffToCopy :
            setattr(self,item,getattr(sample,item))
            
        self.outputPlotFileName=outDir+"/"+sample.outputPlotFileName
        self.inputChain=r.TChain("chain")
        self.currentTreeNumber=-1

        self.chainVariableContainer=eventVariableContainer()
        self.extraVariableContainer=eventVariableContainer()

    def makeFinalBranchNameLists(self) :
        showDebug=False
        self.allReadBranchNames=[]
        self.allBoundBranchNames=[]
        for step in self.steps :
            if (showDebug) :
                print "-------------------------"
                step.printStatistics()
                print "needed: ",step.neededBranches

            #branches to read
            step.finalBranchNameList=[]
            for branchName in step.neededBranches :
                if (not branchName in self.allReadBranchNames) :
                    step.finalBranchNameList.append(branchName)
                    self.allReadBranchNames.append(branchName)

            #branches to bind (binding done only when self.shallWeBindVars=True)
            step.finalBindList=[]
            if (not hasattr(step,"branchesToBind")) :
                step.branchesToBind=step.neededBranches
            for branchName in step.branchesToBind :
                if (not branchName in self.allBoundBranchNames) :
                    step.finalBindList.append(branchName)
                    self.allBoundBranchNames.append(branchName)

            if (showDebug) :
                print "final:  ",step.finalBranchNameList
                print "all:    ",self.allReadBranchNames

    def setBranchAddresses(self) :
        showDebug=False
        builtInExamples=[   0,  0L, 0.0, False,""]
        #arrayStrings   =[ "i", "l", "d"]
        builtInTypes   =[]
        for example in builtInExamples :
            builtInTypes.append(type(example))

        self.inputChain.GetEntry(self.extraVariableContainer.entry)

        for branchName in self.allReadBranchNames :
            leafNameOptions=[branchName]
            for prefix in self.leafNamePrefixes : leafNameOptions.append(prefix+branchName)
            for suffix in self.leafNameSuffixes : leafNameOptions.append(branchName+suffix)
                
            branchType=None
            leafName=""
            for leafNameOption in leafNameOptions :
                if hasattr(self.inputChain,leafNameOption) :
                    branchType=type(getattr(self.inputChain,leafNameOption))
                    leafName=leafNameOption
                    break
                    
            if (showDebug) :
                print branchName,getattr(self.inputChain,leafName),branchType
            if (branchType in builtInTypes) :
                index=0
                #index=builtInTypes.index(branchType)

                #not yet perfect
                #setattr(self.chainVariableContainer,branchName,array.array(arrayStrings[index],[builtInExamples[index]]))
                #self.inputChain.SetBranchAddress(branchName,getattr(self.chainVariableContainer,branchName))
            elif (str(branchType)=="<type 'ROOT.PyDoubleBuffer'>") :
                setattr(self.chainVariableContainer,branchName,array.array('d',[0.0]*256)) #hard-coded max of 256
                self.inputChain.SetBranchAddress(branchName,getattr(self.chainVariableContainer,branchName))
            elif (str(branchType)=="<type 'ROOT.PyFloatBuffer'>") :
                setattr(self.chainVariableContainer,branchName,array.array('f',[0.0]*256)) #hard-coded max of 256
                self.inputChain.SetBranchAddress(branchName,getattr(self.chainVariableContainer,branchName))
            else :
                #method 1
                #setattr(self.chainVariableContainer,branchName,getattr(self.inputChain,branchName))

                #method 2
                setattr(self.chainVariableContainer,branchName,copy.deepcopy(getattr(self.inputChain,branchName)))
                self.inputChain.SetBranchAddress(branchName,r.AddressOf(getattr(self.chainVariableContainer,branchName)))

        if (showDebug) :
            for item in dir(self.chainVariableContainer) :
                thing=getattr(self.chainVariableContainer,item)
                print item,thing,type(thing)

    def showBranches(self) :
        for branch in self.inputChain.GetListOfBranches() :
            branchName=branch.GetName()
            branch.GetEntry(1)
            print branchName,type(getattr(self.inputChain,branchName))
            
    def go(self) :
        self.setupChain(self.inputFiles)
        self.makeFinalBranchNameLists()
        self.setupSteps()
        #self.showBranches()

        self.loop()
        self.printStats()
        self.writeHistos()
        self.writeSkimTree()
        print self.hyphens

    def setupChain(self,inputFiles) :
        nFiles=len(inputFiles)
        alreadyPrintedEllipsis=False

        print self.hyphens
        outString="The "+str(nFiles)+" \""+self.name+"\" input file"
        if (nFiles>1) : outString+="s"
        print outString+":"

        for infile in inputFiles :
            self.inputChain.Add(infile+"/"+self.fileDirectory+"/"+self.treeName)

            if (inputFiles.index(infile)<2 or inputFiles.index(infile)>(nFiles-3) ) :
                print infile
            elif (not alreadyPrintedEllipsis) :
                print "..."
                alreadyPrintedEllipsis=True

        outString="contain"
        if (nFiles==1) : outString+="s"

        outString+=" "+str(self.inputChain.GetEntries())
        outString+=" events."
        outString+=" (xs=%6.4g"%self.xs+" pb)"
        print outString
        print self.hyphens
        r.gROOT.cd()

    def chain(self) :
        return self.inputChain

    def setupSteps(self) :
        for step in self.steps :
            step.bookHistos()
            step.needToReadData=False
            step.selectNotImplemented=not hasattr(step,"select")
            step.uponAcceptanceImplemented=hasattr(step,"uponAcceptance")
            step.uponRejectionImplemented=hasattr(step,"uponRejection")
            step.shallWeBindVars=not self.useSetBranchAddress
            step.needToReadData=(len(step.finalBranchNameList)>0)
            if (step.__doc__==step.skimmerStepName) :
                step.setup(self.inputChain,self.fileDirectory,self.name)

    def setupBranchLists(self) :
        for step in self.steps :
            step.makeBranchList(self.inputChain)
            
    def lookForChangeOfTree(self,chain) :
        someTreeNumber=chain.GetTreeNumber()
        if (someTreeNumber!=self.currentTreeNumber) :
            if (self.useSetBranchAddress) :
                self.setBranchAddresses()
            self.setupBranchLists()
            self.currentTreeNumber=someTreeNumber
                                                                                        
    def loop(self) :
        chain=self.inputChain
        chainVars=self.chainVariableContainer
        extraVars=self.extraVariableContainer

        nEntries=chain.GetEntries()
        if (self.nEvents<0 or self.nEvents>nEntries) :
            self.nEvents=nEntries

        for entry in range(self.nEvents) :
            localEntry=chain.LoadTree(entry)
            if (localEntry<0) : break
            extraVars.localEntry=localEntry
            extraVars.entry=entry
            self.lookForChangeOfTree(chain)
                
            for step in self.steps :
                if (not step.go(chain,chainVars,extraVars)) : break
                
    def printStats(self) :
        print self.hyphens
        for step in self.steps :
            step.printStatistics()

    def writeHistos(self) :
        print self.hyphens
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
        nEventsHisto.SetBinContent(1,self.nEvents)
        nEventsHisto.Write()
        
        outputFile.Close()
        if (not zombie) :  print "The output file \""+self.outputPlotFileName+"\" has been written."

    def writeSkimTree(self) :
        skimmerStepName=analysisStep().skimmerStepName
        for step in self.steps :
            if (step.__doc__==skimmerStepName) :
                print self.hyphens
                step.writeTree()
                print "The skim file \""+step.outputFileName+"\" has been written."
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

    def go(self,chain,chainVars,extraVars) :
        self.nTotal+=1
        if (self.needToReadData) :
            self.readData(chain,extraVars.localEntry)
            if (self.shallWeBindVars) :
                self.bindVars(chain,chainVars)

        if (self.selectNotImplemented) :
            self.nPass+=1
            if (self.uponAcceptanceImplemented) :
                self.uponAcceptance(chain,chainVars,extraVars)
            return True

        if (self.select(chain,chainVars,extraVars)) :
            self.nPass+=1
            if (self.uponAcceptanceImplemented) :
                self.uponAcceptance(chain,chainVars,extraVars)
            return True
        else :
            self.nFail+=1
            if (self.uponRejectionImplemented) :
                self.uponRejection(chain,chainVars,extraVars)
            return False

    def name(self) :
        return self.__doc__.ljust(self.docWidth)+self.moreName.ljust(self.moreWidth)

    def name2(self) :
        return "".ljust(self.docWidth)+self.moreName2.ljust(self.moreWidth)

    def printStatistics(self) :
        outString=self.name()
        outString2=self.name2()
        statString =   " nPass ="+str(self.nPass) .rjust(self.integerWidth)+";"
        statString+= "   nFail ="+str(self.nFail) .rjust(self.integerWidth)+";"
        statString+="   nTotal ="+str(self.nTotal).rjust(self.integerWidth)+";"
        if (self.moreName2=="") :
            print outString+statString
        else :
            print outString
            print outString2+statString

    def bindVars(self,chain,chainVars) :
        for branchName in self.finalBindList :
            setattr(chainVars,branchName,getattr(chain,branchName))

    def readData(self,chain,localEntry) :
        for branch in self.finalBranches :
            branch.GetEntry(localEntry)

    def makeBranchList(self,chain) :
        self.finalBranches=[]
        for branchName in self.finalBranchNameList :
            self.finalBranches.append(chain.GetBranch(branchName))
            
    def bookHistos(self) : return
#####################################
class eventVariableContainer :
    """holds the values of variables that are not in the tree"""
#####################################
