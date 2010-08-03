from wrappedChain import *
import math

class indices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s"% self.cs
    
    def __init__(self, collection = None, suffix = None, ptMin = None, etaMax = None, flagName = None ):
        self.cs = (collection,suffix)
        self.ptThreshold = ptMin
        self.etaMax = etaMax
        self.flagName = None if not flagName else \
                        "%s"+flagName+"%s" if collection[-2:] != "PF" else \
                        "%sPF"+flagName+"%s"
        self.flagName = self.flagName % self.cs if self.flagName else None
        self.p4sName = '%sCorrectedP4%s'%self.cs

        self.moreName = "(%s; %s; %s; "% (self.cs[0], self.cs[1],flagName if flagName else "")
        self.moreName2 = " corr. pT>=%.1f GeV; |eta|<=%.1f)"% (ptMin , etaMax)
        
        self.value = {}

    def update(self,ignored) :
        p4s    = self.source[self.p4sName]
        jetIds = self.source[self.flagName] if self.flagName else p4s.size()*[1]

        self.value["clean"] = []
        self.value["other"] = []

        for iJet in range(p4s.size()) :
            if p4s.at(iJet).pt() < self.ptThreshold : #pt cut, assumes sorted
                break 
            elif jetIds[iJet] and abs(p4s.at(iJet).eta()) < self.etaMax :
                self.value["clean"].append(iJet)
            else: self.value["other"].append(iJet)

##############################
class leadingPt(wrappedChain.calculable) :
    def name(self) : return "%sLeadingPt%s"% self.cs

    def __init__(self, collection = None, suffix = None) :
        self.cs = collection, suffix
        self.p4sName = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4sName]
        indices = self.source[self.indicesName]["clean"]
        self.value = p4s.at(indices[0]).pt() if len(indices) else None

##############################
class sumPt(wrappedChain.calculable) :
    def name(self) : return "%sSumPt%s"% self.cs

    def __init__(self, collection = None, suffix = None) :
        self.cs = collection, suffix
        self.p4sName = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4sName]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i).pt(), indices , 0)

##############################
class sumP4(wrappedChain.calculable) :
    def name(self) : return "%sSumP4%s" % self.cs

    def __init__(self, collection = None, suffix = None) :
        self.cs = (collection, suffix)
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4sName]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices[1:], p4s.at(indices[0]) ) if len(indices) else None


class deltaPseudoJet(wrappedChain.calculable) :
    def name(self) : return "%sDeltaPseudoJet%s" % self.cs

    def __init__(self, collection = None, suffix = None) :
        self.cs = (collection, suffix)
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        indices = self.source[self.indicesName]["clean"]
        p4s = self.source[self.p4sName]
        
        size = len(indices)
        diff = [0.] * (1<<size)
        for j in range( size ) :
            pt = p4s.at(j).pt()
            for i in range( len(diff) ) :
                diff[i] += pt * (1|-(1&(i>>j)))
        
        self.value = min([abs(d) for d in diff])

class alphaT(wrappedChain.calculable) :
    def name(self) : return "%sAlphaT%s" % self.cs

    def __init__(self, collection = None, suffix = None ) :
        self.cs = (collection, suffix)
        self.sumP4Name = "%sSumP4%s" % self.cs
        self.sumPtName = "%sSumPt%s" % self.cs
        self.deltaPseudoName = "%sDeltaPseudoJet%s" % self.cs

    def update(self,ignored) :
        sumP4 = self.source[self.sumP4Name]
        sumPt = self.source[self.sumPtName]
        dPseudo = self.source[self.deltaPseudoName]
        self.value = 0.5 * ( sumPt - dPseudo ) / math.sqrt( sumPt*sumPt - sumP4.Perp2() ) 
