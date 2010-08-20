from wrappedChain import *
import math

def jesStrip(collection) :
    return tuple([i.strip("jes_") for i in collection])
##############################
class jetIndices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s"% self.cs
    
    def __init__(self, collection = None, ptMin = None, etaMax = None, flagName = None):
        self.cs = collection
        self.ptMin = ptMin
        self.etaMax = etaMax
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.flagName = None if not flagName else \
                        ( "%s"+flagName+"%s" if jesStrip(self.cs)[0][-2:] != "PF" else \
                          "%sPF"+flagName+"%s" ) % jesStrip(self.cs)
        self.moreName = "pT>=%.1f GeV; |eta|<%.1f; %s"% (ptMin, etaMax, flagName if flagName else "")

    def update(self,ignored) :
        p4s    = self.source[self.p4Name]
        jetIds = self.source[self.flagName] if self.flagName else p4s.size()*[1]
        self.value = []

        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break #pt cut, assumes sorted
            elif jetIds[i] and abs(p4s.at(i).eta()) < self.etaMax :
                self.value.append(i)

##############################
class jetIndicesOther(wrappedChain.calculable) :
    def name(self) : return "%sIndicesOther%s"% self.cs
    
    def __init__(self, collection = None, ptMin = None) :
        self.cs = collection
        self.ptMin = ptMin
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = '%sIndices%s' % self.cs
        self.moreName = "unaccepted; pT>=%.1f GeV"% ptMin

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        self.value = filter( lambda i: p4s.at(i).pt() > self.ptMin,
                             list(set(range(p4s.size()))-set(self.source[self.indicesName]) ) ) 
        
####################################
class PFJetIDloose(wrappedChain.calculable) :
    def name(self) : return "%sPFJetIDloose%s"%self.cs

    def __init__(self, collection = None, fNeutralEmMax = None, fChargedEmMax = None, fNeutralHadMax = None, fChargedHadMin = None, nChargedMin = None ) :
        self.cs = collection
        self.p4Name = "%sCorrectedP4%s"%self.cs
        self.fNeutralEmMax  = fNeutralEmMax   ;  self.fNeutralEmName  = "%sFneutralEm%s" % jesStrip(self.cs)
        self.fChargedEmMax  = fChargedEmMax   ;  self.fChargedEmName  = "%sFchargedEm%s" % jesStrip(self.cs)
        self.fNeutralHadMax = fNeutralHadMax  ;  self.fNeutralHadName = "%sFneutralHad%s" % jesStrip(self.cs)
        self.fChargedHadMin = fChargedHadMin  ;  self.fChargedHadName = "%sFchargedHad%s" % jesStrip(self.cs)
        self.nChargedMin    = nChargedMin     ;  self.nChargedName    = "%sNcharged%s" % jesStrip(self.cs)

        self.moreName = "fN_em<%.1f; fC_em<%.1f; fN_had<%.1f; |eta|>2.4 or {fC_had>%.1f; nC>%d}" % \
                        ( fNeutralEmMax,fChargedEmMax,fNeutralHadMax, fChargedHadMin, nChargedMin)
            
    def update(self,ignored) :
        self.value = map(self.passId, 
                         self.source[self.p4Name],
                         self.source[self.fNeutralEmName ],
                         self.source[self.fChargedEmName ],
                         self.source[self.fNeutralHadName],
                         self.source[self.fChargedHadName],
                         self.source[self.nChargedName   ] )

    def passId(self, p4, fNem, fCem, fNhad, fChad, nC ) :
        return fNem < self.fNeutralEmMax and \
               fCem < self.fChargedEmMax and \
               fNhad < self.fNeutralHadMax and \
               ( abs(p4.eta()) > 2.4 or \
                 fChad > self.fChargedHadMin and \
                 nC > self.nChargedMin )

#############################
class leadingJetPt(wrappedChain.calculable) :
    def name(self) : return "%sLeadingPt%s"% self.cs

    def __init__(self, collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]
        self.value = p4s.at(indices[0]).pt() if len(indices) else None
##############################
class jetSumPt(wrappedChain.calculable) :
    def name(self) : return "%sSumPt%s"% self.cs

    def __init__(self, collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]
        self.value = reduce( lambda x,i: x+p4s.at(i).pt(), indices , 0)
##############################
class jetSumP4(wrappedChain.calculable) :
    def name(self) : return "%sSumP4%s" % self.cs

    def __init__(self, collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices[1:], p4s.at(indices[0]) ) if len(indices) else None
##############################
class deltaPseudoJet(wrappedChain.calculable) :
    def name(self) : return "%sDeltaPseudoJet%s" % self.cs

    def __init__(self, collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        indices = self.source[self.indicesName]
        p4s = self.source[self.p4Name]
        
        size = len(indices)
        diff = [0.] * (1<<size)
        for j in range( size ) :
            pt = p4s.at(j).pt()
            for i in range( len(diff) ) :
                diff[i] += pt * (1|-(1&(i>>j)))
        
        self.value = min([abs(d) for d in diff])
##############################
class alphaT(wrappedChain.calculable) :
    def name(self) : return "%sAlphaT%s" % self.cs

    def __init__(self, collection = None) :
        self.cs = collection
        self.sumP4Name = "%sSumP4%s" % self.cs
        self.sumPtName = "%sSumPt%s" % self.cs
        self.deltaPseudoName = "%sDeltaPseudoJet%s" % self.cs

    def update(self,ignored) :
        sumP4 = self.source[self.sumP4Name]
        sumPt = self.source[self.sumPtName]
        dPseudo = self.source[self.deltaPseudoName]
        self.value = 0.5 * ( sumPt - dPseudo ) / math.sqrt( sumPt*sumPt - sumP4.Perp2() ) 
##############################
class diJetAlpha(wrappedChain.calculable) :
    def name(self) : return "%sDiJetAlpha%s" % self.cs
    
    def __init__(self,collection = None) :
        self.cs = collection
        self.indicesName = "%sIndices%s" % self.cs
        self.p4Name = '%sCorrectedP4%s' % self.cs
        
    def update(self,ignored) :
        cleanJetIndices = self.source[self.indicesName]
        #return if not dijet
        if len(cleanJetIndices)!=2 :
            self.value=None
            return
        p4s=self.source[self.p4Name]
        mass=(p4s.at(cleanJetIndices[0])+p4s.at(cleanJetIndices[1])).M()
        if mass<=0.0 :
            self.value=None
        else :
            self.value=p4s.at(cleanJetIndices[1]).pt()/mass
##############################
class jetDeltaX01(wrappedChain.calculable) :
    def name(self) : return "%sDeltaX01%s" % self.cs

    def __init__(self,collection = None) :
        self.cs = collection
        self.indicesName = "%sIndices%s" % self.cs
        self.p4Name = '%sCorrectedP4%s' % self.cs
        
    def update(self,ignored) :
        self.value={}
        
        indices = self.source[self.indicesName]
        if len(indices)<2 :
            self.value["phi"]=None
            self.value["eta"]=None
            self.value["R"]=None
            return
        p4s=self.source[self.p4Name]
        jet0=p4s.at(indices[0])
        jet1=p4s.at(indices[1])
        self.value["phi"] = r.Math.VectorUtil.DeltaPhi(jet0,jet1)
        self.value["R"  ] = r.Math.VectorUtil.DeltaR(jet0,jet1)
        self.value["eta"] = jet0.eta()-jet1.eta()
##############################
class deltaPhiStar(wrappedChain.calculable) :
    def name(self) : return "%sDeltaPhiStar%s" % self.cs

    def __init__(self,collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = '%sIndices%s' % self.cs
        self.sumP4Name = "%sSumP4%s" % self.cs
        
    def update(self,ignored) :
        self.value=None

        indices = self.source[self.indicesName]
        if not len(indices) : return
        jets = self.source[self.p4Name]
        sumP4 = self.source[self.sumP4Name]

        self.value = min([abs(r.Math.VectorUtil.DeltaPhi(jets.at(i),jets.at(i)-sumP4)) for i in indices])
##############################
class maxProjMHT(wrappedChain.calculable) :
    def name(self) : return "%sMaxProjMHT%s"%self.cs

    def __init__(self,collection = None) :
        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.indicesName = '%sIndices%s' % self.cs
        self.sumP4Name = "%sSumP4%s" % self.cs

    def update(self,ignored) :
        self.value = None

        indices = self.source[self.indicesName]
        if not len(indices) : return
        jets = self.source[self.p4Name]
        sumP4 = self.source[self.sumP4Name]

        self.value = -min( [ sumP4.pt() / math.sqrt(jets.at(i).pt()) * \
                             math.cos(r.Math.VectorUtil.DeltaPhi(jets.at(i),sumP4)) for i in indices])
##############################
class jesAdjustedP4s(wrappedChain.calculable) :
    def name(self) : return "jes_%sCorrectedP4%s"%self.cs

    def __init__(self,collection = None, jesAbs = 1.0, jesRel = 0.0 ) :
        self.cs = jesStrip(collection)
        self.moreName = "%.3f * (1 + %.3f*|eta|) * p4;  %s%s" % ((jesAbs,jesRel)+self.cs)
        self.jesAbs = jesAbs
        self.jesRel = jesRel
        self.p4name = "%sCorrectedP4%s"%self.cs
        self.value = r.vector(r.Math.LorentzVector(r.Math.PxPyPzE4D('double')))()

    def jes(self,p4) : self.value.push_back( p4 * (self.jesAbs*(1+self.jesRel*abs(p4.eta()))))
        
    def update(self,ignored) :
        self.value.clear()
        map(self.jes, self.source[self.p4name])
