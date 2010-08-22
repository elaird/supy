from wrappedChain import *

class photonIndicesPat(wrappedChain.calculable) :

    def __init__(self, ptMin = None, flagName = None ):
        self.ptMin = ptMin
        self.flagName = flagName
        self.moreName = "pT>=%.1f GeV; %s"% (ptMin, flagName if flagName else "")

    def update(self,ignored) :
        p4s = self.source["photonP4Pat"]
        ids = self.source[self.flagName] if self.flagName else p4s.size()*[1]
        
        self.value = filter(lambda i: ids[i] and p4s.at(i).pt() > self.ptMin, range(p4s.size()))
