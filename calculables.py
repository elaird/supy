from wrappedChain import *
from inspect import isclass,ismodule,getargspec
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
            try:
                args = len(getargspec(eval("%s.%s.__init__.im_func"%(moduleName,className)))[0])
                if args < 2 :
                    zeroArg.append(calc())
            except: zeroArg.append(calc())
    return zeroArg
