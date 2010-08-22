from wrappedChain import *
import copy
import ROOT as r

##############################
class xcJet(wrappedChain.calculable) :
    def name(self) : return "%sCorrectedP4%s"%self.xcjets

    def __init__(self,jetSource = None,
                 isoGamma    = None, isoGammaDR    = 0,
                 isoElectron = None, isoElectronDR = 0,
                 nonIsoMuon  = None, nonIsoMuonDR  = 0,
                 jesAbs = 1.0,
                 jesRel = 0.0 ) :
        self.value = r.std.vector('LorentzV')()
        self.jetP4Source = "CorrectedP4"%jetSource
        self.xcjets = ("xc"+jetSource[0],jetSource[1])
        self.other = dict( [ (eval(i),eval(i+"DR")) for i in ["isoGamma","isoElectron","nonIsoMuon"]] )

        self.moreName = ";".join(["%sDR<%.2f"%(v[0]+(v[1],)) for v in filter(lambda v: v[0], self.other.values())])
        if jesAbs!=1.0 or jesRel!=0.0:
            self.moreName2 += "jes corr: %.2f*(1+%.2f|eta|)"%(jesAbs,jesRel)
    
    def jes(self,p4) : return p4 * (self.jesAbs*(1+self.jesRel*abs(p4.eta())))

    def update(self,ignored) :
        jetP4s = self.source[self.jetP4Source]
        killed = self.source["%sIndicesKilled%s"%self.xcjets]
        matchedMuons = []

        self.value.clear()
        for iJet,jet in enumerate(jetP4s) :
            xcJet = jes(jet)
            self.value.push_back(xcJet)

            if self.matchesIn("isoGamma",xcJet) \
            or self.matchesIn("isoElectron",xcJet) :
                killed.add(iJet)
                continue

            for p4 in self.matchesIn("nonIsoMuon",xcJet, exitEarly=False) :
                matchedMuons.add(p4)
                xcJet += p4

        if self.other["nonIsoMuon"][0] :
            muset = set(matchedMuons)
            nonisomu = self.source["%sIndices%s"%self.other["muons"][0]]

            self.source["crock"]["%s%sUnmatchedNonisolatedMuons"%self.xcjets] = len(muset) == len(nonisomu)
            self.source["crock"]["%s%sNonUniqueMuonMatch"%self.xcjets] = len(matchedMuons) == len(muset)

    def matchIn(self,label,p4, exitEarly = True) :
        collection,dR = self.other[label]
        if not collection : return False
        indices = self.source["%sIndices%s"%collection]
        objects = self.source["%sP4%s"%collection]
        matches = []
        for i in indices :
            objP4 = objects.at(i)
            if dR > r.Math.VectorUtil.DeltaR(objP4,p4) :
                if exitEarly: return True
                else: matches.append(objP4)
        return matches
