import copy,array
import ROOT as r
from collections import defaultdict

class keyTracer(object) :
    def __init__(self,someDict) :
        self.someDict = someDict
        self.tracedKeys = set()
    def node(self,key) : return self.someDict.node(key)
    def __getitem__(self,key) :
        if key not in self.tracedKeys : self.tracedKeys.add(key)
        return self.someDict[key]
    def __call__(self,someDict) :
        self.someDict = someDict
        return self

class wrappedChain(dict) : 

    def __init__(self, chain, calculables = [], useSetBranchAddress = True, leavesToBlackList = [], preferredCalcs = [], maxArrayLength = 256, trace = False, cacheSizeMB = 0) :
        """Set up the nodes"""
        self.__activeNodes = defaultdict(int)
        self.__activeNodeList = []
        self.__chain = chain

        if (not chain) or chain.GetEntry(0)==0 : return
        chain.SetCacheSize( cacheSizeMB * 1024**2 )

        for branch in chain.GetListOfBranches() :
            nameB = branch.GetName()
            nameL = (lambda nL: nameB if (nL=="_" or nL==nameB+"_") else nL )(branch.GetListOfLeaves().At(0).GetName())
            if nameL in leavesToBlackList : continue
            dict.__setitem__(self, nameL, self.__branchNode( nameL, nameB, chain, useSetBranchAddress, maxArrayLength) )

        names = [c.name for c in calculables]
        if len(names)!=len(set(names)) :
            for name in names :
                assert names.count(name)==1,"Duplicate calculable name: %s"%name

        for calc in calculables :
            name = calc.name
            if name in self and name not in preferredCalcs : continue
            dict.__setitem__(self, name, calc )
            dict.__getitem__(self, name).source = keyTracer(self) if trace else self
            dict.__getitem__(self, name).updated = False

    def activeKeys(self) : return [( key, node.isLeaf(), str(type(node.value)).split("'")[1].replace("wrappedChain.","") ) for key,node in self.__activeNodes.iteritems()]
    def calcDependencies(self) : return defaultdict(set,[(node.name,node.source.tracedKeys) for node in self.__activeNodes.values() if hasattr(node,"source") and hasattr(node.source,"tracedKeys")])

    def entries(self, nEntries = None, skip = 0 ) :
        """Generate the access dictionary (self) for each entry in TTree."""
        if not self.__chain: return
        chain = self.__chain
        nEntries = (lambda x,y : min(x,y) if x>=0 else y)( nEntries, chain.GetEntries() )
        iTreeFirstEntry = 0
        
        for nTree in range(chain.GetNtrees()) :
            chain.LoadTree(iTreeFirstEntry)
            for node in self.__activeNodeList : node.setAddress() 
            tree = chain.GetTree()
            if not tree : continue
            nTreeEntries = tree.GetEntries()
            if iTreeFirstEntry + nTreeEntries < skip :
                iTreeFirstEntry += nTreeEntries
                continue

            for iTreeEntry in range( nTreeEntries )  :
                if (not nTree) and iTreeEntry==100 : tree.StopCacheLearningPhase()
                self.entry = iTreeFirstEntry + iTreeEntry
                if nEntries <= self.entry : self.entry-=1; return
                #if nEntries!=None and nEntries <= self.entry : self.entry-=1; return
                self.__localEntry = iTreeEntry
                for node in self.__activeNodeList : node.updated = False
                if skip<=self.entry : yield self
            #tree.PrintCacheStats()
            iTreeFirstEntry += nTreeEntries
            
    def node(self,key) : return dict.__getitem__(self,key)
    def __getitem__(self,key) :
        """Access the value of the branch or calculable specified by 'key' for the current entry"""
        node = self.__activeNodes[key]
        if not node :
            node = dict.__getitem__(self,key)
            self.__activeNodes[key] = node
            self.__activeNodeList.append(node)
            node.setAddress()
            node.updated = True
            node.update(self.__localEntry)
        elif not node.updated :
            node.updated = True
            node.update(self.__localEntry)
        return node.value

    def __setitem__(self,key,value) :
        raise Exception("wrappedChain entries are read-only.")


    class __branchNode(object) :
        """Internal wrapper for branch nodes."""
        def __init__(self, nameL, nameB, chain, useSetBranchAddress, maxArrayLength) :
            def address(nameL, nameB, chain, useSetBranchAddress, maxArrayLength) :
                if not useSetBranchAddress : return None
                leaf = getattr(chain, nameL)

                if type(leaf) in [int,float,long,str] :
                    typenames = {'Bool_t'  :'B',
                                 'Char_t'  :'b', 'UChar_t'  :'B',
                                 'Short_t' :'h', 'UShort_t' :'H',
                                 'Int_t'   :'i', 'UInt_t'   :'I',
                                 'Long64_t':'l', 'ULong64_t':'L',
                                 'Float_t' :'f', 'Double_t' :'d'
                                 }
                    typename = chain.GetBranch(nameB).GetLeaf(nameL).GetTypeName()
                    if typename not in typenames :
                        assert False,"leaf %s %s %s %s is not supported"%(nameB, nameL, str(type(leaf)), typename)
                    return array.array(typenames[typename],[0])

                elif str(type(leaf))=="<type 'ROOT.PyIntBuffer'>"    : return array.array('i',[0]*maxArrayLength)
                elif str(type(leaf))=="<type 'ROOT.PyShortBuffer'>"  : return array.array('h',[0]*maxArrayLength)
                elif str(type(leaf))=="<type 'ROOT.PyUIntBuffer'>"   : return array.array('I',[0]*maxArrayLength)
                elif str(type(leaf))=="<type 'ROOT.PyDoubleBuffer'>" : return array.array('d',[0]*maxArrayLength)
                elif str(type(leaf))=="<type 'ROOT.PyFloatBuffer'>"  : return array.array('f',[0]*maxArrayLength)
                else :
                    self.value = copy.deepcopy(leaf)
                    return r.AddressOf(self.value)

            self.value = None
            self.updated = False
            self.nameL = nameL
            self.nameB = nameB
            self.chain = chain
            self.branch = None
            self.address = address(nameL, nameB, chain, useSetBranchAddress, maxArrayLength)
            self.valIsArrayZero = type(self.address) == array.array and len(self.address) == 1
            if type(self.address) == array.array and len(self.address)>1 :
                self.value = self.address

        def setAddress(self) :
            self.branch = self.chain.GetBranch(self.nameB)
            if self.address : self.branch.SetAddress( self.address )
            
        def update(self,localEntry) :
            self.branch.GetEntry(localEntry)
            if      not self.address : self.value = getattr(self.chain, self.nameL)
            elif self.valIsArrayZero : self.value = self.address[0]

        def isLeaf(self) :
            return True

    class calculable(object) :
        """Inherit wrappedChain.calculable and define update(self,localEntry) for a calculable node"""
        moreName = ""
        moreName2 = ""
        def isLeaf(self) : return False
        def isFake(self) : return False
        def setAddress(self) : pass
        
        def update(self,localEntry) :
            """Set self.value according to dictionary self.source.

            You can safely ignore localEntry.
            You can override the name function.
            """
            raise Exception("Not Implemented!")

        @property
        def name(self) :
            if not hasattr(self,"fixes") : self.fixes = ("","")
            return self.fixes[0] + self.__class__.__name__ + self.fixes[1]

        def stash(self, leafNames = [], fixes = None) :
            Name = self.name
            for leaf in leafNames:
                assert not hasattr(self,leaf), "%s already has attribute %s"%(Name,leaf)
                setattr(self,leaf,("%s"+leaf+"%s")%(fixes if fixes else self.fixes))

        def __str__(self) : return "%s\t%s"%(self.name[:39].ljust(40),self.moreName)
