from core import utils
from core.wrappedChain import *
import calculables
##############################
class NumberOfMatches(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IsTrackerMuon"])
        self.moreName = "hard-coded to 2"
    def isFake(self) :
        return True
    def update(self,ignored) :
        self.value = [2] * self.source[self.IsTrackerMuon].size()
##############################
class NumberOfValidPixelHits(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IsTrackerMuon"])
        self.moreName = "hard-coded to 1"
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
        self.value = utils.hackMap(self.tight,
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
        return (isoTrk+isoEcal+isoHcal)/p4.pt() if p4.pt() > 0.1 else 1e10

    def update(self,ignored) :
        self.value = utils.hackMap(self.combinedRelativeIso,
                         self.source[self.TrackIso],
                         self.source[self.EcalIso],
                         self.source[self.HcalIso],
                         self.source[self.P4])
##############################
class TrackRelIso(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["TrackIso","P4"])
    def trackreliso(self,iso,p4) : return iso/(iso+p4.pt()) if iso or p4.pt() else 1
    def update(self,ignored) :
        self.value = utils.hackMap(self.trackreliso, self.source[self.TrackIso],self.source[self.P4] )
##############################
class HcalRelIso(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["HcalIso","P4"])
    def hcalreliso(self,iso,p4) : return iso/(iso+p4.pt()) if iso or p4.pt() else 1
    def update(self,ignored) :
        self.value = utils.hackMap(self.hcalreliso, self.source[self.HcalIso],self.source[self.P4] )
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
    def __init__(self, collection = None, ptMin = None, combinedRelIsoMax = None, requireIsGlobal = True ) :
        self.fixes = collection
        self.requireIsGlobal = requireIsGlobal
        self.stash(["IndicesNonIso","IndicesOther","P4","IDtight","CombinedRelativeIso","IsGlobalMuon"])
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
        isGlobal = self.source[self.IsGlobalMuon]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : continue
            if self.requireIsGlobal and not isGlobal.at(i) : continue
            if tight[i] :
                if relIso[i] < self.relIsoMax :
                    self.value.append(i)
                else: nonIso.append(i)
            else: other.append(i)
##############################
class IndicesAnyIso(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","IndicesNonIso"])
        self.moreName = "sorted(Indices+IndicesNonIso)"

    def update(self, ignored) :
        self.value = sorted(self.source[self.Indices]+self.source[self.IndicesNonIso])
##############################
class IndicesAnyIsoIsoOrder(wrappedChain.calculable) :
    def __init__(self, collection = None, key = None) :
        self.fixes = collection
        self.stash(["IndicesAnyIso"])
        self.key = ("%s"+key+"%s")%collection
        self.moreName = "sorted(IndicesAnyIso,key=%s)"%key

    def update(self, ignored) :
        self.value = sorted(self.source[self.IndicesAnyIso],key = self.source[self.key].__getitem__)
##############################
class LeadingPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","P4"])

    def update(self,ignored) :
        indices = self.source[self.Indices]
        self.value = 0 if not indices else self.source[self.P4][indices[0]].pt()
class LeadingPtAny(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IndicesAnyIso","P4"])

    def update(self,ignored) :
        indices = self.source[self.IndicesAnyIso]
        self.value = 0 if not indices else self.source[self.P4][indices[0]].pt()
class LeadingIsoAny(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, iso = None) :
        self.fixes = collection
        self.stash(["IndicesAnyIsoIsoOrder","P4"])
        self.iso = ("%s"+iso+"%s")%self.fixes
        self.ptMin = ptMin
        self.moreName = "%s of most isolated w/ pt>%.1f"%(iso,ptMin)

    def update(self,ignored) :
        p4 = self.source[self.P4]
        indices = filter(lambda i: p4[i].pt()>self.ptMin, self.source[self.IndicesAnyIsoIsoOrder])
        self.value = 10e10 if not indices else self.source[self.iso][indices[0]]
##############################
class DiMuon(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","P4"])
    def update(self,ignored) :
        indices = self.source[self.Indices]
        if len(indices)!= 2 :
            self.value = None
        else :
            p4s = self.source[self.P4]
            self.value = p4s.at(indices[0])+p4s.at(indices[1])
##############################
class DiMuonMass(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["DiMuon"])
    def update(self,ignored) :
        Z = self.source[self.DiMuon]
        self.value = 0 if not Z else Z.mass()
##############################
class DiMuonPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["DiMuon"])
    def update(self,ignored) :
        Z = self.source[self.DiMuon]
        self.value = 0 if not Z else Z.pt()
##############################
class TriggeringIndex(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['IndicesTriggering'])
    def update(self,_) : self.value = next(iter(self.source[self.IndicesTriggering]), None)
##############################
class IndicesTriggering(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, absEtaMax = 2.1) :
        self.fixes = collection
        self.stash(["P4","IndicesAnyIso"])
        self.absEtaMax = absEtaMax
        self.ptMin = ptMin
        self.moreName = "%s in |eta|<%.1f; max pt>%.1f"%(self.IndicesAnyIso,self.absEtaMax,self.ptMin if self.ptMin else 0.)

    def update(self,ignored) :
        self.value = []
        p4 = self.source[self.P4]
        for i in self.source[self.IndicesAnyIso] :
            if p4[i].pt() < self.ptMin : break
            if abs(p4[i].eta()) < self.absEtaMax : self.value.append( i )
#####################################
class TriggeringPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["P4","TriggeringIndex"])

    def update(self,ignored) :
        index = self.source[self.TriggeringIndex]
        self.value = 0 if index==None else self.source[self.P4][index].pt()
#####################################
class Pt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["P4"])
    def update(self,_) :
        p4 = self.source[self.P4]
        self.value = [p4[i].pt() for i in range(len(p4))]
