import calculables
from wrappedChain import *
##############################
class electronIndices(wrappedChain.calculable) :
    def name(self) : return self.indices

    def __init__(self, collection = None, ptMin = None, electronIsoID = None, useCombinedIso = True) :
        self.ptMin = ptMin
        self.indices = "%sIndices%s" % collection
        self.p4s = "%sP4%s" % collection
        self.eID = "%sID%s%s" % (collection[0],electronIsoID,collection[1])
        self.eIso = "%sIso%s%s%s" % (collection[0],electronIsoID,"Combined" if useCombinedIso else "Relative", collection[1])
        self.moreName = "%s; pt>%.1f; %s" % (self.eID, ptMin, self.eIso)

    def update(self,ignored) :
        self.value = []
        p4s = self.source[self.p4s]
        eID = self.source[self.eID]
        eIso = self.source[self.eIso]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break
            if eID[i] and eIso[i]:
                self.value.append(i)
##############################
