import copy,array,os,collections
import ROOT as r
from supy import analysisStep,utils,autoBook
import configuration
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


class skimmer(analysisStep):
    """
    This step writes all events to a TFile.  The options:

    mainChain controls whether the chain being looper over (defined in
    configuration.py) is stored.

    otherChains controls whether 'spectator' chains (also defined in
    configuration.py) are stored.

    extraVars is a list of calculable names to add as branches to the
    mainChain.  See self.setupExtraVars() for supported types.  If the
    mainChain has zero events, then the extra branches will not be
    created.
    """

    def __init__(self, mainChain=True, otherChains=True, extraVars=[], haddOutput=False, suffix="skim"):
        assert mainChain or extraVars
        self.outputTree = None
        self.moreName = "(see below)"
        for var in ["mainChain", "otherChains", "extraVars"]:
            setattr(self, var, eval(var))
        self.addresses = None
        self.haddOutput = haddOutput
        self.suffix = suffix

    def requiresNoSetBranchAddress(self):
        return True  # check

    def requiresNoTrace(self):
        return True  # check

    def setup(self, chain, fileDir):
        self.outputFile = r.TFile(self.outputFileName, "RECREATE")
        self.fileDir = fileDir
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)

        if self.mainChain:
            if chain and chain.GetEntry(0) > 0:
                # clone structure of tree (but no entries)
                self.outputTree = chain.CloneTree(0)
            if self.outputTree:
                self.outputTree.SetDirectory(utils.root.gDirectory())
                chain.CopyAddresses(self.outputTree)
        elif self.extraVars:
            if chain:
                dirAndName = chain.GetName()
                name = dirAndName.split("/")[-1]
                self.outputTree = r.TTree(name, chain.GetTitle())
        else:
            assert False, "mainChain or extraVars"

        r.gROOT.cd()

    def writeOtherChains(self, chains):
        for (dirName, treeName), chain in chains.iteritems():
            if dirName == self.fileDir:
                if self.outputTree and treeName == self.outputTree.GetName():
                    continue
            else:
                self.outputFile.mkdir(dirName)

            self.outputFile.cd(dirName)
            if chain and chain.GetEntry(0) > 0:
                outChain = chain.CloneTree()
                if outChain:
                    outChain.SetName(treeName)
                    outChain.SetDirectory(utils.root.gDirectory())
                    outChain.Write()

    def select(self, eventVars):
        # read all the data for this event
        if eventVars["chain"].GetEntry(eventVars["entry"], 1) <= 0:
            msg = "skimmer failed to read TChain entry %s" % eventVars["entry"]
            assert False, msg

        if self.extraVars:
            if self.addresses is None:
                self.setupExtraVars(eventVars)
            # assign values at relevant addresses
            for key in self.addresses:
                self.addresses[key][0] = eventVars[key]

        self.outputTree.Fill()

        # use of weight/self.increment follows supy.steps.master
        self.increment(False, 1.0 - eventVars["weight"])
        return True

    def setupExtraVars(self, eventVars):
        self.addresses = {}
        for var in self.extraVars:
            t = type(eventVars[var])
            if t in [bool, int, long, float]:
                self.addresses[var] = array.array('d', [0.0])
                self.outputTree.Branch(var, self.addresses[var], var+"/D")
            elif t is type(utils.lvClass):
                self.outputTree.Branch(var, eventVars[var])
            else:
                msg = "Variable '%s' has type '%s'" % (var, str(t))
                assert False, "%s and cannot be stored." % msg

    def endFunc(self, chains):
        self.outputFile.cd(self.fileDir)
        if self.outputTree:
            self.outputTree.Write()
        if self.otherChains:
            self.writeOtherChains(chains)
        self.outputFile.Close()

    def outputSuffix(self):
        return "_%s.root" % self.suffix

    def modifiedFileName(self, s):
        l = s.split("/")
        return "/".join(l[:-2]+l[-1:])

    def mergeFunc(self, products):
        if self.haddOutput:
            self.mergeFuncHadd(products)
        else:
            self.mergeFuncMv(products)

    # copied from supy.steps.master
    def mergeFuncHadd(self, products):
        def printComment(lines) :
            if self.quietMode : return
            skip = ['Source file','Target path','Found subdirectory']
            line = next(L for L in lines.split('\n') if not any(item in L for item in skip))
            print line.replace("Target","The output") + " has been written."

        def cleanUp(stderr, files) :
            okList = configuration.haddErrorsToIgnore()
            assert (stderr in okList), "hadd had this stderr: '%s'"%stderr
            if stderr : print stderr
            for fileName in files : os.remove(fileName)

        hAdd = utils.getCommandOutput("%s -f %s %s"%(configuration.hadd(),self.outputFileName, " ".join(products["outputFileName"])))
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], products["outputFileName"])

    def mergeFuncMv(self, products):
        for fileName in products["outputFileName"]:
            os.system("mv %s %s" % (fileName, self.modifiedFileName(fileName)))
        if not self.quietMode:
            print "The %d skim files have been written." % len(products["outputFileName"])
            print "( e.g. %s )" % self.modifiedFileName(products["outputFileName"][0])
            print utils.hyphens


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
