from wrappedChain import *
import math
##############################
class indices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s"% self.cs
    
    def __init__(self, collection = None, ptMin = None, etaMax = None, flagName = None , p4Name = "CorrectedP4"):
        self.cs = collection
        self.ptMin = ptMin
        self.etaMax = etaMax
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.flagName = None if not flagName else \
                        ( "%s"+flagName+"%s" if collection[-2:] != "PF" else \
                          "%sPF"+flagName+"%s" ) % self.cs
        self.moreName = "(pT>=%.1f GeV; |eta|<%.1f; %s)"% (ptMin, etaMax, flagName if flagName else "")
        self.value = {}

    def update(self,ignored) :
        p4s    = self.source[self.p4Name]
        jetIds = self.source[self.flagName] if self.flagName else p4s.size()*[1]

        clean = self.value["clean"] = []
        other = self.value["other"] = []

        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break #pt cut, assumes sorted
            elif jetIds[i] and abs(p4s.at(i).eta()) < self.etaMax :
                clean.append(i)
            else: other.append(i)

############################
class pfIndicesByHand(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s" % self.cs

    def __init__(self, collection = None, ptMin = None, etaMax = None,
                 fNeutralEmMax = None, fChargedEmMax = None, fNeutralHadMax = None, fChargedHadMin = None, nChargedMin = None) :

        self.cs = collection
        self.p4Name = '%sCorrectedP4%s' % self.cs
        self.ptMin = ptMin
        self.etaMax = etaMax

        self.moreName = "(pT>=%.1f; |eta|<%.1f; pfN_em<%.1f; fC_em<%.1f; fN_had<%.1f; and" % \
                        ( ptMin, etaMax, fNeutralEmMax,fChargedEmMax,fNeutralHadMax)
        self.moreName2 = " |eta|>2.4 or {fC_had>%.1f; nC>%d})" % (fChargedHadMin, nChargedMin)
        
        self.fNeutralEmMax  = fNeutralEmMax   ;  self.fNeutralEmName  = "%sFneutralEm%s" % self.cs   
        self.fChargedEmMax  = fChargedEmMax   ;  self.fChargedEmName  = "%sFchargedEm%s" % self.cs   
        self.fNeutralHadMax = fNeutralHadMax  ;  self.fNeutralHadName = "%sFneutralHad%s" % self.cs  
        self.fChargedHadMin = fChargedHadMin  ;  self.fChargedHadName = "%sFchargedHad%s" % self.cs  
        self.nChargedMin    = nChargedMin     ;  self.nChargedName    = "%sNcharged%s" % self.cs     

        self.value = {}

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        fNeutralEm  = self.source[self.fNeutralEmName ]
        fChargedEm  = self.source[self.fChargedEmName ]
        fNeutralHad = self.source[self.fNeutralHadName]
        fChargedHad = self.source[self.fChargedHadName]
        nCharged    = self.source[self.nChargedName   ]

        clean = self.value["clean"] = []
        other = self.value["other"] = []

        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break #pt cut, assumes sorted
            absEta = p4s.at(i).eta()
            if absEta < self.etaMax and \
                   fNeutralEm.at(i) < self.fNeutralEmMax and \
                   fChargedEm.at(i) < self.fChargedEmMax and \
                   fNeutralHad.at(i) < self.fNeutralHadMax and \
                   ( absEta > 2.4 or \
                     fChargedHad.at(i) > self.fChargedHadMin and \
                     nCharged.at(i) > self.nChargedMin ) :
                clean.append(i)
            else: other.append(i)

#############################
class leadingPt(wrappedChain.calculable) :
    def name(self) : return "%sLeadingPt%s"% self.cs

    def __init__(self, collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]["clean"]
        self.value = p4s.at(indices[0]).pt() if len(indices) else None
##############################
class sumPt(wrappedChain.calculable) :
    def name(self) : return "%sSumPt%s"% self.cs

    def __init__(self, collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i).pt(), indices , 0)
##############################
class sumP4(wrappedChain.calculable) :
    def name(self) : return "%sSumP4%s" % self.cs

    def __init__(self, collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4Name]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices[1:], p4s.at(indices[0]) ) if len(indices) else None
##############################
class deltaPseudoJet(wrappedChain.calculable) :
    def name(self) : return "%sDeltaPseudoJet%s" % self.cs

    def __init__(self, collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        indices = self.source[self.indicesName]["clean"]
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
    
    def __init__(self,collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.indicesName = "%sIndices%s" % self.cs
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        
    def update(self,ignored) :
        cleanJetIndices = self.source[self.indicesName]["clean"]
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
class deltaX01(wrappedChain.calculable) :
    def name(self) : return "%sDeltaX01%s" % self.cs

    def __init__(self,collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.indicesName = "%sIndices%s" % self.cs
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        
    def update(self,ignored) :
        self.value={}
        
        cleanJetIndices = self.source[self.indicesName]["clean"]
        if len(cleanJetIndices)<2 :
            self.value["phi"]=None
            self.value["eta"]=None
            self.value["R"]=None
            return
        p4s=self.source[self.p4Name]
        jet0=p4s.at(cleanJetIndices[0])
        jet1=p4s.at(cleanJetIndices[1])
        self.value["phi"] = r.Math.VectorUtil.DeltaPhi(jet0,jet1)
        self.value["R"  ] = r.Math.VectorUtil.DeltaR(jet0,jet1)
        self.value["eta"] = jet0.eta()-jet1.eta()
##############################
class deltaPhiStar(wrappedChain.calculable) :
    def name(self) : return "%sDeltaPhiStar%s" % self.cs

    def __init__(self,collection = None, p4Name = "CorrectedP4") :
        self.cs = collection
        self.indicesName = "%sIndices%s" % self.cs
        self.p4Name = '%s%s%s' % (self.cs[0],p4Name,self.cs[1])
        self.sumP4Name = "%sSumP4%s" % self.cs
        
    def update(self,ignored) :
        self.value=None

        jets=self.source[self.p4Name]
        nJets=jets.size()
        if nJets==0 :
            return

        sumP4=self.source[self.sumP4Name]
        self.value=min([abs(r.Math.VectorUtil.DeltaPhi(jets.at(i),jets.at(i)-sumP4)) for i in range(nJets)])
##############################
