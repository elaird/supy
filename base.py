import copy,array
import ROOT as r

#####################################
def globalSetup() :
    r.gROOT.ProcessLine(".L SusyCAFpragmas.h+")
    r.TH1.SetDefaultSumw2(True)
#####################################
fileDirectory="susyTree"
treeName="tree"
#####################################
class sampleSpecification :
    """name, data sample, cuts"""

    def __init__(self,dict,name,nEvents,outputPrefix,steps):
        self.name=name
        self.nEvents=nEvents
        self.inputFiles=dict[name]
        self.outputPlotFileName=outputPrefix+"_"+self.name+"_plots.root"
        self.steps=copy.deepcopy(steps)
#####################################
class analysisLooper :
    """class to set up and loop over events"""

    def __init__(self,sample,outDir):
        self.hyphens="".ljust(95,"-")

        self.nEvents=sample.nEvents
        self.name=sample.name

        self.outputPlotFileName=outDir+"/"+sample.outputPlotFileName
        self.steps=sample.steps

        self.inputChainEntries=0
        self.inputChain=r.TChain("chain")
        self.setupChain(sample.inputFiles)

        self.currentTreeNumber=-1

        self.chainVariableContainer=eventVariableContainer()
        self.extraVariableContainer=eventVariableContainer()

    def makeFinalBranchNameLists (self) :
        showDebug=False
        self.allReadBranchNames=[]
        for step in self.steps :
            if (showDebug) :
                print "-------------------------"
                step.printStatistics()
                print "needed: ",step.neededBranches
                
            step.finalBranchNameList=[]
            for branchName in step.neededBranches :
                if (self.allReadBranchNames.count(branchName)==0) :
                    step.finalBranchNameList.append(branchName)
                    self.allReadBranchNames.append(branchName)

            if (showDebug) :
                print "final:  ",step.finalBranchNameList
                print "all:    ",self.allReadBranchNames

    def setBranchAddresses(self) :
        showDebug=False
        builtInExamples=[   0,  0L, 0.0]
        arrayStrings   =[ "i", "l", "d"]
        builtInTypes   =[]
        for example in builtInExamples :
            builtInTypes.append(type(example))

        self.inputChain.GetEntry(self.extraVariableContainer.entry)

        for branchName in self.allReadBranchNames :
            branchType=type(getattr(self.inputChain,branchName))
            if (showDebug) :
                print branchName,getattr(self.inputChain,branchName),branchType
            if (builtInTypes.count(branchType)>0) :
                index=builtInTypes.index(branchType)

                #not yet perfect
                #setattr(self.chainVariableContainer,branchName,array.array(arrayStrings[index],[builtInExamples[index]]))
                #self.inputChain.SetBranchAddress(branchName,getattr(self.chainVariableContainer,branchName))
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
            
    def go (self) :
        self.makeFinalBranchNameLists()
        self.setupSteps()
        #self.showBranches()

        self.loop()
        self.printStats()
        self.writeHistos()
        self.writeSkimTree()
        print self.hyphens

    def setupChain (self,inputFiles) :
        nFiles=len(inputFiles)
        alreadyPrintedEllipsis=False

        print self.hyphens
        outString="The "+str(nFiles)+" \""+self.name+"\" input file"
        if (nFiles>1) : outString+="s"
        print outString+":"

        for infile in inputFiles :
            self.inputChain.Add(infile+"/"+fileDirectory+"/"+treeName)

            if (inputFiles.index(infile)<2 or inputFiles.index(infile)>(nFiles-3) ) :
                print infile
            elif (not alreadyPrintedEllipsis) :
                print "..."
                alreadyPrintedEllipsis=True

        self.inputChainEntries=self.inputChain.GetEntries()
        outString="contain"
        if (nFiles==1) : outString+="s"

        print outString,self.inputChainEntries,"events."
        print self.hyphens
        r.gROOT.cd()

    def chain (self) :
        return self.inputChain

    def setupSteps(self) :
        for step in self.steps :
            step.bookHistos()
            step.needToReadData=False
            if (len(step.finalBranchNameList)>0) :
                step.needToReadData=True
            if (step.__doc__==step.skimmerStepName) :
                step.setup(self.inputChain,fileDirectory,self.name)

    def setupBranchLists(self) :
        for step in self.steps :
            step.makeBranchList(self.inputChain)
            
    def lookForChangeOfTree(self,chain) :
        someTreeNumber=chain.GetTreeNumber()
        if (someTreeNumber!=self.currentTreeNumber) :
            self.setBranchAddresses()
            self.setupBranchLists()
            self.currentTreeNumber=someTreeNumber
                                                                                        
    def loop (self) :
        chain=self.inputChain
        chainVars=self.chainVariableContainer
        extraVars=self.extraVariableContainer

        nEntries=chain.GetEntries()
        if (self.nEvents>=0 and self.nEvents<nEntries) : nEntries=self.nEvents

        for entry in range(nEntries) :
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
    neededBranches=[]
    skimmerStepName="skimmer"

    def go (self,chain,chainVars,extraVars) :
        self.nTotal+=1
        if (self.needToReadData) :
            self.readData(chain,extraVars.localEntry)
        if (self.select(chain,chainVars,extraVars)) :
            self.uponAcceptance(chain,chainVars,extraVars)
            self.nPass+=1
            return True
        else :
            self.uponRejection(chain,chainVars,extraVars)
            self.nFail+=1
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

    def readData(self,chain,localEntry) :
        for branch in self.finalBranches :
            branch.GetEntry(localEntry)

    def makeBranchList(self,chain) :
        self.finalBranches=[]
        for branchName in self.finalBranchNameList :
            self.finalBranches.append(chain.GetBranch(branchName))
            
    def bookHistos(self) : return
    def select(self,chain,chainVars,extraVars) : return True
    def uponAcceptance(self,chain,chainVars,extraVars) : return
    def uponRejection(self,chain,chainVars,extraVars) : return
#####################################
class eventVariableContainer :
    """holds the values of variables that are not in the tree"""
#####################################
