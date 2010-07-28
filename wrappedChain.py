import copy,array
import ROOT as r
from collections import defaultdict

class wrappedChain(dict) : 

    def __init__(self, chain, calculables = [] ) :
        """Set up the nodes"""
        self.__activeNodes = defaultdict(int)
        self.__activeNodeList = []
        self.__chain = chain
        
        chain.GetEntry(0)
        for branch in chain.GetListOfBranches() :
            nameB = branch.GetName()
            nameL = (lambda nL: nameB if nL=="_" else nL )(branch.GetListOfLeaves().At(0).GetName())
            dict.__setitem__(self, nameL, self.__branchNode( nameB, chain ) )

        for calc in calculables :
            name = calc.name()
            if name in self :
                raise Exception("Duplicate name",name)
            dict.__setitem__(self, name, calc )
            calc.source = self
            calc.updated = False

    def entries(self, nEntries = -1 ) :
        """Generate the access dictionary (self) for each entry in TTree."""
        chain = self.__chain
        nEntries = (lambda x,y : min(x,y) if x>=0 else y)( nEntries, chain.GetEntries() )
        iTreeFirstEntry = 0
        
        for nTree in range(chain.GetNtrees()) :
            chain.LoadTree(iTreeFirstEntry)
            for node in self.__activeNodeList : node.setAddress() 
            nTreeEntries = chain.GetTree().GetEntries()

            for iTreeEntry in range( nTreeEntries )  :
                self.entry = iTreeFirstEntry + iTreeEntry
                if nEntries <= self.entry : return
                self.__localEntry = iTreeEntry
                for node in self.__activeNodeList : node.updated = False
                yield self
            iTreeFirstEntry += nTreeEntries

    def __getitem__(self,key) :
        """Access the value of the branch or calculable specified by 'key' for the current entry"""
        node = self.__activeNodes[key]
        if not node :
            node = dict.__getitem__(self,key)
            self.__activeNodes[key] = node
            self.__activeNodeList.append(node)
            node.setAddress()
            node.update(self.__localEntry)
            node.updated = True
        else :
            if not node.updated :
                node.update(self.__localEntry)
                node.updated = True
        return node.value

    def __setitem__(self,key,value) :
        raise Exception("wrappedChain entries are read-only.")


    class __branchNode(object) :
        """Internal wrapper for branch nodes."""
        def __init__(self, name, chain) :
            self.name = name
            self.chain = chain
            self.branch = 0
            self.updated = False
            self.value = copy.deepcopy(getattr(chain,name))
            self.address = array.array('l',[0]) if type(self.value) == int else \
                           array.array('l',[0]) if type(self.value) == long else \
                           array.array('d',[0.0]) if type(self.value) == float else \
                           array.array('i',[0]*256) if str(type(self.value)) == "<type 'ROOT.PyUIntBuffer'>" else \
                           array.array('d',[0]*256) if str(type(self.value)) == "<type 'ROOT.PyDoubleBuffer'>" else \
                           array.array('f',[0]*256) if str(type(self.value)) == "<type 'ROOT.PyFloatBuffer'>" else \
                           r.AddressOf( self.value ) 

        def setAddress(self) :
            self.branch = self.chain.GetBranch(self.name)
            self.branch.SetAddress( self.address )
            
        def update(self,localEntry) :
            self.branch.GetEntry(localEntry)
            if type(self.address) == array.array and \
               len(self.address) == 1 :
                self.value = self.address[0]


    class calculable(object) :
        """Inherit wrappedChain.calculable and define update(self,localEntry) for a calculable node"""

        def update(self,localEntry) :
            """Set self.value according to dictionary self.source.

            You can safely ignore localEntry.
            You can override the name function.
            """
            raise Exception("Not Implemented!")

        def name(self) :
            return self.__class__.__name__

        def setAddress(self) :
            pass
