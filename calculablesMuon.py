import calculables
from wrappedChain import *
##############################
class NumberOfMatches(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IsTrackerMuon"])
        self.moreName = "WARNING: dummy value always = 2"
    def isFake(self) :
        return True
    def update(self,ignored) :
        self.value = [2] * self.source[self.IsTrackerMuon].size()
##############################
class NumberOfValidPixelHits(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IsTrackerMuon"])
        self.moreName = "WARNING: dummy value always = 1"
    def isFake(self) :
        return True
    def update(self,ignored) :
        self.value = [1]*self.source[self.IsTrackerMuon].size()
##############################
class IDtight(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IsTrackerMuon","IDGlobalMuonPromptTight","NumberOfMatches",
                    "InnerTrackNumberOfValidHits","NumberOfValidPixelHits","GlobalTrackDxy"])
        self.moreName = "implemented by hand, CMS AN-2010/211"

    def tight(self,isTrk, idGlbTight, nStationsMatch, nTrkPxHits, nPxHits, dxy) :
        return isTrk               and \
               idGlbTight          and \
               nStationsMatch >  1 and \
               nTrkPxHits     > 10 and \
               nPxHits        >  0 and \
               abs(dxy)       <  0.2#cm

    def update(self,ignored) :
        self.value = map(self.tight,
                         self.source[self.IsTrackerMuon],
                         self.source[self.IDGlobalMuonPromptTight],
                         self.source[self.NumberOfMatches],
                         self.source[self.InnerTrackNumberOfValidHits],
                         self.source[self.NumberOfValidPixelHits],
                         self.source[self.GlobalTrackDxy])    
##############################
class CombinedRelativeIso(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["TrackIso","EcalIso","HcalIso","P4"])
        self.moreName = "(trackIso + ecalIso + hcalIso) / pt_mu"

    def combinedRelativeIso(self,isoTrk,isoEcal,isoHcal,p4) :
        return (isoTrk+isoEcal+isoHcal)/p4.pt()

    def update(self,ignored) :
        self.value = map(self.combinedRelativeIso,
                         self.source[self.TrackIso],
                         self.source[self.EcalIso],
                         self.source[self.HcalIso],
                         self.source[self.P4])
##############################
class IndicesOther(calculables.indicesOther) :
    def __init__(self, collection = None) :
        super(IndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail id"
##############################
class IndicesNonIso(calculables.indicesOther) :
    def __init__(self, collection = None) :
        super(IndicesNonIso, self).__init__(collection)
        self.indicesOther = "%sIndicesNonIso%s"%collection
        self.moreName = "pass ptMin & id; fail iso"
##############################
class Indices(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, combinedRelIsoMax = None ) :
        self.fixes = collection
        self.stash(["IndicesNonIso","IndicesOther","P4","IDtight","CombinedRelativeIso"])
        self.ptMin = ptMin
        self.relIsoMax = combinedRelIsoMax
        self.moreName = "tight; pt>%.1f GeV; cmbRelIso<%.2f"%( ptMin, combinedRelIsoMax )

    def update(self,ignored) :
        self.value = []
        nonIso = self.source[self.IndicesNonIso]
        other  = self.source[self.IndicesOther]
        p4s    = self.source[self.P4]
        tight  = self.source[self.IDtight]
        relIso = self.source[self.CombinedRelativeIso]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break
            if tight[i] :
                if relIso[i] < self.relIsoMax :
                    self.value.append(i)
                else: nonIso.append(i)
            else: other.append(i)
##############################
