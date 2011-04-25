from wrappedChain import *
from inspect import isclass,ismodule,getargspec
import configuration
##############################
class weight(wrappedChain.calculable) :
    value = 1
    def __init__(self, calcName) : self.calcName = calcName
    def update(self, ignored) :
        if self.calcName : self.value = self.source[self.calcName]
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
    for mod in globals().values() :
        if not ismodule(mod) : continue
        for name,calc in mod.__dict__.iteritems() :
            if not isclass(calc) : continue
            if not issubclass(calc, wrappedChain.calculable) : continue
            try:
                args = len(getargspec(calc.__init__.im_func)[0])
                if args < 2 :
                    zeroArg.append(calc())
            except: zeroArg.append(calc())
    return zeroArg
##############################
def fromCollections(module,collections) :
    """Returns a list of instances of all calculables in module taking only the collection as arg."""

    calcs = []
    for name,calc in module.__dict__.iteritems() :
        if not isclass(calc) : continue
        if not issubclass(calc, wrappedChain.calculable) : continue
        args = getargspec(calc.__init__.im_func)[0]
        if "collection" in args and len(args) is 2:
            for col in collections : calcs.append(calc(col))
    return calcs
##############################
for module in configuration.calculablesFiles() :
    exec("import calculables%s as %s"%(module, module))
##############################
