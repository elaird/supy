from wrappedChain import *
import copy
import ROOT as r

##############################
class xcJet(wrappedChain.calculable) :
    def name(self) : return "%sCorrectedP4%s"%self.xcjets

    def __init__(self,xcjets = None,
                 gamma    = None, gammaDR    = 0,
                 electron = None, electronDR = 0,
                 muon     = None, muonDR     = 0,
                 jesAbs = 1,
                 jesRel = 0 ) :
        self.value = r.std.vector('LorentzV')()
        self.jetP4Source = ("%sCorrectedP4%s"%xcjets)[2:]
        self.xcjets = xcjets
        self.other = dict( [ (i,(eval(i),eval(i+"DR"))) for i in ["gamma","electron","muon"]] )
        self.jesAbs = jesAbs
        self.jesRel = jesRel
        
        self.moreName = "; ".join(["%s%sDR<%.2f"%(v[0]+(v[1],)) for v in filter(lambda v: v[0], self.other.values())])
        if jesAbs!=1.0 or jesRel!=0.0:
            self.moreName2 += "jes corr: %.2f*(1+%.2f|eta|)"%(jesAbs,jesRel)
    
    def jes(self,p4) : return p4 * (self.jesAbs*(1+self.jesRel*abs(p4.eta())))

    def update(self,ignored) :
        jetP4s = self.source[self.jetP4Source]
        killed = self.source["%sIndicesKilled%s"%self.xcjets]
        matchedMuons = []

        self.value.clear()
        for iJet,jet in enumerate(jetP4s) :
            xcJet = self.jes(jet)
            self.value.push_back(xcJet)

            if self.matchesIn("gamma",xcJet) \
            or self.matchesIn("electron",xcJet) :
                killed.add(iJet)
                continue

            for p4 in self.matchesIn("muon",xcJet, exitEarly=False, indicesStr="%sIndicesNonIso%s") :
                matchedMuons.append(p4)
                xcJet += p4

        if self.other["muon"][0] :
            muset = set(matchedMuons)
            nonisomu = self.source["%sIndicesNonIso%s"%self.other["muon"][0]]

            self.source["crock"]["%s%sNonIsoMuonsUnmatched"%self.xcjets] = len(muset) == len(nonisomu)
            self.source["crock"]["%s%sNonUniqueMuonMatch"%self.xcjets] = len(matchedMuons) == len(muset)

    def matchesIn(self,label,p4, exitEarly = True, indicesStr = "%sIndices%s") :
        collection,dR = self.other[label]
        if not collection : return False
        indices = self.source[indicesStr % collection]
        objects = self.source["%sP4%s"%collection]
        matches = []
        for i in indices :
            objP4 = objects.at(i)
            if dR > r.Math.VectorUtil.DeltaR(objP4,p4) :
                if exitEarly: return True
                else: matches.append(objP4)
        return matches
