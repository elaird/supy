from wrappedChain import *
import calculables
##############################
class photonIndicesOtherPat(calculables.indicesOther) :
    def __init__(self,collection = ("photon","Pat")) :
        super(photonIndicesOtherPat, self).__init__(collection)
        self.moreName = "pass ptMin; fail id/iso"
##############################
class photonIndicesPat(wrappedChain.calculable) :

    def __init__(self, ptMin = None, flagName = None ):
        self.ptMin = ptMin
        self.flagName = flagName
        self.moreName = "pT>=%.1f GeV; %s"% (ptMin, flagName if flagName else "")

    def update(self,ignored) :
        p4s = self.source["photonP4Pat"]
        ids = self.source[self.flagName] if self.flagName else p4s.size()*[1]
        self.value = []
        other = self.source["photonIndicesOtherPat"]
        
        for i in range(p4s.size()):
            if p4s.at(i).pt() < self.ptMin: continue
            elif ids[i] : self.value.append(i)
            else: other.append(i)
##############################
class leadingPt(wrappedChain.calculable) :
    def name(self) : return "%sLeadingPt%s"%self.photons

    def __init__(self, collection = ("photon","Pat")) :
        self.photons = collection
        
    def update(self,ignored) :
        indices = self.source["%sIndices%s"%self.photons]
        self.value = self.source["%sP4%s"%self.photons].at(indices[0]).pt() if len(indices) else None
