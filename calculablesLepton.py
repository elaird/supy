from wrappedChain import *
##############################
class muonNumberStationsWithMatchingChamberPat(wrappedChain.calculable) :
    def __init__(self) :
        self.moreName = "WARNING: dummy value always = 2"
    def update(self,ignored) :
        self.value = [2] * self.source["muonIsTrackerMuonPat"].size()
##############################
class muonPixelNumberOfValidHitsPat(wrappedChain.calculable) :
    def __init__(self) :
        self.moreName = "WARNING: dummy value always = 1"
    def update(self,ignored) :
        self.value = [1]*self.source["muonIsTrackerMuonPat"].size()
##############################
class muonIDtightPat(wrappedChain.calculable) :
    def __init__(self) :
        self.moreName = "(implemented by hand, CMS AN-2010/211)"

    def tight(self,isTrk, idGlbTight, nStationsMatch, nTrkPxHits, nPxHits, dxy) :
        return isTrk               and \
               idGlbTight          and \
               nStationsMatch >  1 and \
               nTrkPxHits     > 10 and \
               nPxHits        >  0 and \
               abs(dxy)       <  0.2#cm

    def update(self,ignored) :
        self.value = map(self.tight,
                         self.source["muonIsTrackerMuonPat"],
                         self.source["muonIDGlobalMuonPromptTightPat"],
                         self.source["muonNumberStationsWithMatchingChamberPat"],
                         self.source["muonInnerTrackNumberOfValidHitsPat"],
                         self.source["muonPixelNumberOfValidHitsPat"],
                         self.source["muonGlobalTrackDxyPat"])    
##############################
class muonCombinedRelativeIsoPat(wrappedChain.calculable) :
    def __init__(self) :
        self.moreName = "(trackIso + ecalIso + hcalIso) / pt_mu"

    def combinedRelativeIso(self,isoTrk,isoEcal,isoHcal,p4) :
        return (isoTrk+isoEcal+isoHcal)/p4.pt()

    def update(self,ignored) :
        self.value = map(self.combinedRelativeIso,
                         self.source["muonTrackIsoPat"],
                         self.source["muonEcalIsoPat"],
                         self.source["muonHcalIsoPat"],
                         self.source["muonP4Pat"])
##############################
class muonIndicesPat(wrappedChain.calculable) :
    
    def __init__(self, ptMin = None, combinedRelIsoMax = None ) :
        self.ptMin = ptMin
        self.relIsoMax = combinedRelIsoMax
        self.moreName = "(tight; pt>%.1f; cmbRelIso<%.2f)"%( ptMin, combinedRelIsoMax )

    def update(self,ignored) :
        self.value = []
        p4s = self.source["muonP4Pat"]
        tight = self.source["muonIDtightPat"]
        relIso = self.source["muonCombinedRelativeIsoPat"]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break
            if tight[i] and relIso[i] < self.relIsoMax : self.value.append(i)
##############################
