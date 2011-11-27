import operator
from inspect import isclass,ismodule,getargspec
from supy import wrappedChain
#more modules are imported at the end of this file
##############################
class weight(wrappedChain.calculable) :
    def __init__(self, weights) :
        self.calcNames = [w.name for w in weights]
        self.moreName = ".".join(["1"]+sorted(self.calcNames))
    def update(self,_) :
        weights = [self.source[n] for n in self.calcNames]
        self.value = reduce(operator.mul, weights, 1) if None not in weights else None
##############################
class IndicesOther(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Indices'])
    def update(self,_) :
        self.value = []
        if not self.source.node(self.Indices).updated :
            self.source[self.indices]
##############################
class size(wrappedChain.calculable) :
    @property
    def name(self) : return "%s.size"%self.calc
    def __init__(self, calc) : self.calc = calc
    def update(self,_) : self.value = len(self.source[self.calc])
##############################
def zeroArgs(module) :
    """Returns a list of instances of all zero argument calculables."""

    zeroArg = []
    for modName in dir(module) :
        mod = getattr(module,modName)
        if not ismodule(mod) : continue
        for name,calc in mod.__dict__.iteritems() :
            if not isclass(calc) : continue
            if not issubclass(calc, wrappedChain.calculable) : continue
            if name=='secondary': continue
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
        if not hasattr(calc.__init__,"im_func") : continue
        args = getargspec(calc.__init__.im_func)[0]
        if "collection" in args and len(args) is 2:
            for col in collections : calcs.append(calc(col))
    return calcs
##############################

from __secondary__ import secondary
for module in ['other'] : exec("import %s"%module)
