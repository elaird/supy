from wrappedChain import *
from inspect import isclass,ismodule,getargspec

from calculablesJet import *
from calculablesGen import *
from calculablesPhoton import *
from calculablesOther import *

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
