import copy,array,os,collections
import ROOT as r
from supy import analysisStep,utils,autoBook
#####################################
class touchstuff(analysisStep) :
    def __init__(self,stuff) :
        self.stuff = stuff
        self.moreName = "touch all in %s" % str(stuff)
    def uponAcceptance(self,eventVars) :
        for s in self.stuff : eventVars[s]
#####################################
class collector(analysisStep) :
    def __init__(self, vars) :
        self.vars = vars
        self.collection = set([])
    def uponAcceptance(self, eventVars) :
        self.collection.add(tuple([eventVars[var] for var in self.vars]))
    def varsToPickle(self) :
        return ["collection"]
    def mergeFunc(self, products) :
        print "These points %s have been found:"%str(self.vars)
        s = set([]).union(*products["collection"])
        print sorted(list(s))
#####################################
class noSetBranchAddress(analysisStep) :
    def requiresNoSetBranchAddress(self) :
        return True
    def uponAcceptance(self, _) :
        pass
#####################################
class skimmer(analysisStep) :
    
    def __init__(self) :
        self.outputTree=0
        self.moreName="(see below)"
        self.alsoWriteExtraTree=False #hard-code until this functionality is fixed
        self.outputTreeExtraIsSetup=False

    def requiresNoSetBranchAddress(self) :
        return True

    def requiresNoTrace(self) :
        return True

    def setup(self, chain, fileDir) :
        self.fileDir = fileDir
        self.outputFile = r.TFile(self.outputFileName, "RECREATE")
        self.setupMainChain(chain)
        self.initExtraTree()

    def setupMainChain(self, chain) :
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        if chain and chain.GetEntry(0)>0 :
            self.outputTree = chain.CloneTree(0)  #clone structure of tree (but no entries)
        if not self.outputTree :                  #in case the chain has 0 entries
            r.gROOT.cd()
            return

        self.outputTree.SetDirectory(utils.root.gDirectory())#put output tree in correct place
        chain.CopyAddresses(self.outputTree)      #associate branch addresses

    def writeOtherChains(self, chains) :
        for (dirName,treeName),chain in chains.iteritems() :
            if dirName==self.fileDir and self.outputTree and treeName==self.outputTree.GetName() : continue
            self.outputFile.mkdir(dirName)
            self.outputFile.cd(dirName)
            if chain and chain.GetEntry(0)>0 :
                outChain = chain.CloneTree()
                if outChain :
                    outChain.SetName(treeName)
                    outChain.SetDirectory(utils.root.gDirectory())
                    outChain.Write()

    def initExtraTree(self) :
        if self.alsoWriteExtraTree :
            raise Exception("at the moment, adding the extra tree with the skimmer is broken")
            self.arrayDictionary={}
            self.supportedBuiltInTypes=[type(True),type(0),type(0L),type(0.0)]
            self.supportedOtherTypes=[type(utils.LorentzV())]
            
            extraName=self.outputTree.GetName()+"Extra"
            self.outputTreeExtra=r.TTree(extraName,extraName)
            self.outputTreeExtra.SetDirectory(utils.root.gDirectory())
        r.gROOT.cd()


    def select(self,eventVars) :
        #read all the data for this event
        if eventVars["chain"].GetEntry(eventVars["entry"],1)<=0 :
            assert False, "skimmer failed to write TChain entry "+str(eventVars["entry"])
        #fill the skim tree
        self.outputTree.Fill()

        #optionally fill an extra tree
        if self.alsoWriteExtraTree :
            if not self.outputTreeExtraIsSetup : self.setupExtraTree(eventVars)
            self.fillExtraVariables(eventVars)
            self.outputTreeExtra.Fill()

        # use of weight/self.increment follows supy.steps.master
        self.increment(False, 1.0 - eventVars["weight"])
        return True

    def setupExtraTree(self,eventVars) :
        crockCopy=copy.deepcopy(eventVars["crock"])
        branchNameList=dir(crockCopy)
        skipList=['__doc__','__init__','__module__']

        #set up remaining suitable branches as doubles
        for branchName in branchNameList :
            if (branchName in skipList) : continue

            thisType=type(eventVars["crock"][branchName])
            if (thisType in self.supportedBuiltInTypes) :
                self.arrayDictionary[branchName]=array.array('d',[0.0])
                self.outputTreeExtra.Branch(branchName,self.arrayDictionary[branchName],branchName+"/D")
            elif (thisType in self.supportedOtherTypes) :
                self.outputTreeExtra.Branch(branchName,eventVars["crock"][branchName])
            else :
                #print "The variable \""+branchName+"\" has been rejected from the extra tree."
                continue
            
        self.outputTreeExtraIsSetup=True

    def fillExtraVariables(self,eventVars) :
        for key in self.arrayDictionary :
            self.arrayDictionary[key][0]=eventVars["crock"][key]
        
    def endFunc(self, chains) :
        self.outputFile.cd(self.fileDir)                          #cd to file
        if self.outputTree :         self.outputTree.Write()      #write main tree
        if self.alsoWriteExtraTree : self.outputTreeExtra.Write() #write a tree with "extra" variables
        self.writeOtherChains(chains)
        self.outputFile.Close()

    def outputSuffix(self) :
        return "_skim.root"
    
    def modifiedFileName(self, s) :
        l = s.split("/")
        return "/".join(l[:-2]+l[-1:])

    def mergeFunc(self, products) :
        print "The %d skim files have been written."%len(products["outputFileName"])
        for fileName in products["outputFileName"] :
            os.system("mv %s %s"%(fileName, self.modifiedFileName(fileName)))
        print "( e.g. %s )"%self.modifiedFileName(products["outputFileName"][0])
        print utils.hyphens
#####################################
class reweights(analysisStep) :
    '''Repeat arbitrary analysisStep with different global weights.

    Note that only uponAcceptance() in self.step is supported;
    setup,endFunc,mergeFunc are not, but perhaps it could be
    extended.'''

    def __init__(self,step,reweights,N, doAll=True, predicate = None) :
        self.moreName="%s(%d); %s;%s"%(reweights,N,step.name,step.moreName)
        if predicate : self.moreName += "; %s;%s"%(predicate.name,predicate.moreName)
        for item in ['step','N','reweights','doAll','predicate'] : setattr(self,item,eval(item))
        assert not step.isSelector
        assert not predicate or predicate.isSelector
        self.books = []

    def uponAcceptance(self,ev) :
        '''Perform the analysisStep for the default weight, and for each reweight.'''

        if self.predicate and not self.predicate.select(ev) : return

        self.step.book = self.book
        self.step.uponAcceptance(ev)
        if not self.doAll : return

        weights = ev[self.reweights]
        assert len(weights)==self.N
        for weight,book in zip(weights,self.books) :
            self.step.book = book
            self.step.book.weight = weight * self.book.weight
            dict.__getitem__(ev, 'weight').value = weight * self.book.weight
            self.step.uponAcceptance(ev)
        dict.__getitem__(ev, 'weight').value = self.book.weight

    def setup(self,*_) :
        '''Make a new book for each weight'''
        dir = r.gDirectory.GetDirectory("")
        self.book._autoBook__directory.cd()
        for i in range(self.N): self.books.append(autoBook("w%d"%i))
        dir.cd()

    def endFunc(self,*_) :
        '''Rename and move the histograms into the main book.'''
        dir = self.book._autoBook__directory
        for i,book in enumerate(self.books) :
            for name,val in book.items() :
                newname = "%03d_%s"%(i,name)
                val.SetName(newname)
                val.SetDirectory(dir)
                self.book[newname] = val
                self.book.fillOrder.append(newname)
#####################################
