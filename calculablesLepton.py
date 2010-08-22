import calculables
from wrappedChain import *
##############################
class numberStationsWithMatchingChamber(wrappedChain.calculable) :
    def name(self) : return "%sNumberStationsWithMatchingChamber%s"%self.muons
    
    def __init__(self, collection = None) :
        self.moreName = "WARNING: dummy value always = 2"
        self.muons = collection
        
    def update(self,ignored) :
        self.value = [2] * self.source["%sIsTrackerMuon%s"%self.muons].size()
##############################
class pixelNumberOfValidHits(wrappedChain.calculable) :
    def name(self) : return "%sPixelNumberOfValidHits%s"%self.muons
    
    def __init__(self, collection = None) :
        self.moreName = "WARNING: dummy value always = 1"
        self.muons = collection
        
    def update(self,ignored) :
        self.value = [1]*self.source["%sIsTrackerMuon%s"%self.muons].size()
##############################
class IDtight(wrappedChain.calculable) :
    def name(self): return "%sIDtight%s"%self.muons
    
    def __init__(self, collection = None) :
        self.moreName = "implemented by hand, CMS AN-2010/211"
        self.muons = collection

    def tight(self,isTrk, idGlbTight, nStationsMatch, nTrkPxHits, nPxHits, dxy) :
        return isTrk               and \
               idGlbTight          and \
               nStationsMatch >  1 and \
               nTrkPxHits     > 10 and \
               nPxHits        >  0 and \
               abs(dxy)       <  0.2#cm

    def update(self,ignored) :
        self.value = map(self.tight,
                         self.source["%sIsTrackerMuon%s"%self.muons],
                         self.source["%sIDGlobalMuonPromptTight%s"%self.muons],
                         self.source["%sNumberStationsWithMatchingChamber%s"%self.muons],
                         self.source["%sInnerTrackNumberOfValidHits%s"%self.muons],
                         self.source["%sPixelNumberOfValidHits%s"%self.muons],
                         self.source["%sGlobalTrackDxy%s"%self.muons])    
##############################
class combinedRelativeIso(wrappedChain.calculable) :
    def name(self): return "%sCombinedRelativeIso%s"%self.muons
    def __init__(self, collection = None) :
        self.muons = collection
        self.moreName = "(trackIso + ecalIso + hcalIso) / pt_mu"

    def combinedRelativeIso(self,isoTrk,isoEcal,isoHcal,p4) :
        return (isoTrk+isoEcal+isoHcal)/p4.pt()

    def update(self,ignored) :
        self.value = map(self.combinedRelativeIso,
                         self.source["%sTrackIso%s"%self.muons],
                         self.source["%sEcalIso%s"%self.muons],
                         self.source["%sHcalIso%s"%self.muons],
                         self.source["%sP4%s"%self.muons])
##############################
class muonIndicesOther(calculables.indicesOther) :
    def __init__(self, collection = None) :
        super(muonIndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail id"
##############################
class muonIndicesNonIso(calculables.indicesOther) :
    def __init__(self, collection = None) :
        super(muonIndicesNonIso, self).__init__(collection)
        self.indicesOther = "%sIndicesNonIso%s"%collection
        self.moreName = "pass ptMin & id; fail iso;"
##############################
class muonIndices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s"%self.muons
    
    def __init__(self, collection = None, ptMin = None, combinedRelIsoMax = None ) :
        self.ptMin = ptMin
        self.relIsoMax = combinedRelIsoMax
        self.muons = collection
        self.moreName = "tight; pt>%.1f; cmbRelIso<%.2f"%( ptMin, combinedRelIsoMax )

    def update(self,ignored) :
        self.value = []
        nonIso = self.source["%sIndicesNonIso%s"%self.muons]
        other = self.source["%sIndicesOther%s"%self.muons]
        p4s = self.source["%sP4%s"%self.muons]
        tight = self.source["%sIDtight%s"%self.muons]
        relIso = self.source["%sCombinedRelativeIso%s"%self.muons]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break
            if tight[i] :
                if relIso[i] < self.relIsoMax :
                    self.value.append(i)
                else: nonIso.append(i)
            else: other.append(i)
##############################
