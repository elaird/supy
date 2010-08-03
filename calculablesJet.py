from wrappedChain import *

class indices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s"% self.cs
    
    def __init__(self, collection = None, suffix = None, ptMin = None, etaMax = None, flagName = None ):
        self.cs = (collection,suffix)
        self.ptThreshold = ptMin
        self.etaMax = etaMax
        self.flagName = None if not flagName else \
                        "%s"+flagName+"%s" if collection[-2:] != "PF" else \
                        "%sPF"+flagName+"%s"

        self.moreName = "(%s; %s; %s; "% (self.cs[0], self.cs[1],flagName)
        self.moreName2 = " corr. pT>=%.1f GeV; |eta|<=%.1f)"% (ptMin , etaMax)
        
        self.value = {}

    def update(self,ignored) :
        p4s    = self.source['%sCorrectedP4%s'%self.cs]
        jetIds = self.source[self.flagName % self.cs] if self.flagName else p4s.size()*[1]

        self.value["clean"] = []
        self.value["other"] = []

        for iJet in range(p4s.size()) :
            if p4s.at(iJet).pt() < self.ptThreshold : #pt cut, assumes sorted
                break 
            elif jetIds.at(iJet) and abs(p4s.at(iJet).eta()) < self.etaMax :
                self.value["clean"].append(iJet)
            else: self.value["other"].append(iJet)

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
        self.cs = collection, suffix
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4sName]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices[1:], p4s.at(indices[0]) ) if len(indices) else None

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
        self.value = p4s.at(indices[0]) if len(indices) else None

