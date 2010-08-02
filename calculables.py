from wrappedChain import *
from inspect import isclass,ismodule
import calculablesJet
import calculablesOther


def zeroArgs() :
    """Returns a list of instances of all zero argument calculables."""

    zeroArg = []
    for moduleName in globals() :
        if not ismodule(eval(moduleName)) : continue
        for className in dir(eval(moduleName)) :
            calc = eval("%s.%s"%(moduleName,className))
            if not isclass(calc) : continue
            if not issubclass(calc, wrappedChain.calculable) : continue
            try: eval('%s.%s.__init__.im_func'%(moduleName,className))
            except: zeroArg.append(calc())
    return zeroArg

