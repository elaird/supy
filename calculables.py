from wrappedChain import *
import calculablesJet
import calculablesOther
import inspect

def allDefaultCalculables() :
    return defaultCalculablesOther() + \
           defaultCalculablesJet()

def defaultCalculablesOther() :
    otherCalculables = []
    for memb in [eval("calculablesOther."+i) for i in dir(calculablesOther)] :
        if inspect.isclass(memb) and issubclass(memb,wrappedChain.calculable) :
            otherCalculables.append( memb() )
    return otherCalculables

def defaultCalculablesJet() :
    jetTypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
    jetSuffixes = ["Pat"]
    jetCalculables = []
    for memb in [eval("calculablesJet."+i) for i in dir(calculablesJet)] :
        if inspect.isclass(memb) and issubclass(memb,wrappedChain.calculable) :
            for collection in jetTypes:
                for suffix in jetSuffixes:
                    jetCalculables.append( memb(collection,suffix))
    return jetCalculables



