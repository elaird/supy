from wrappedChain import *
from inspect import isclass,ismodule,getargspec

##############################
class indicesOther(wrappedChain.calculable) :
    def name(self) : return self.indicesOther
    
    def __init__(self, collection = None) :
        self.indices      = "%sIndices%s"%collection
        self.indicesOther = "%sIndicesOther%s"%collection

    def update(self,ignored) :
        self.value = []
        if not dict.__getitem__(self.source,self.indices).updated :
            self.source[self.indices]
##############################

def zeroArgs() :
    """Returns a list of instances of all zero argument calculables."""

    zeroArg = []
    for name,calc in globals().iteritems() :
        if not isclass(calc) : continue
        if not issubclass(calc, wrappedChain.calculable) : continue
        try:
            args = len(getargspec(eval("%s.__init__.im_func"%str(name)))[0])
            if args < 2 :
                zeroArg.append(calc())
        except: zeroArg.append(calc())
    return zeroArg

def fromCollections(moduleName,collections) :
    """Returns a list of instances of all calculables in moduleName taking only the collection as arg."""

    calcs = []
    for name,calc in globals().iteritems() :
        if not isclass(calc) : continue
        if not issubclass(calc, wrappedChain.calculable) : continue
        if not moduleName+"." in str(calc) : continue
        args = getargspec(eval("%s.__init__.im_func"%name))[0]
        if "collection" in args and len(args) is 2:
            for col in collections : calcs.append(calc(col))
    return calcs

from calculablesGen import *
from calculablesJet import *
from calculablesMuon import *
from calculablesElectron import *
from calculablesPhoton import *
from calculablesOther import *
from calculablesXClean import *
