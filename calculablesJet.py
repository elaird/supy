from wrappedChain import *

class jetIndicesFromFlag(wrappedChain.calculable) :
    """JetIndices producer"""
    
    def __init__(self,jetCollection,jetSuffix,jetPtThreshold=20.0,jetEtaMax=3.0,flagName = "JetIDloose" ):
        self.collection = jetCollection
        self.suffix = jetSuffix
        self.ptThreshold = jetPtThreshold
        self.etaMax = jetEtaMax
        self.flagName = None if not flagName else \
                        flagName if jetCollection[-2:] != "PF" else \
                        "PF"+flagName

        self.moreName = "(%s; %s; %s; ", (jetCollection,jetSuffix,flagName)
        self.moreName2 = " corr. pT>=%.1f GeV; |eta|<=%.1f)" , (jetPtThreshold , jetEtaMax)
        
        self.value = {}

    def name(self) : return "%sIndices%s"% (self.collection,self.suffix)

    def update(self,ignored) :
        p4s    = self.source['%sCorrectedP4%s'% (self.collection,self.suffix)]
        jetIds = self.source[self.collection + self.flagName + self.suffix] if self.flagName else p4s.size()*[1]

        self.value["clean"] = []
        self.value["other"] = []

        for iJet in range(p4s.size()) :
            if p4s.at(iJet).pt() < self.ptThreshold : #pt cut, assumes sorted
                break 
            elif jetIds.at(iJet) and abs(p4s.at(iJet).eta()) < self.etaMax :
                self.value["clean"].append(iJet)
            else: self.value["other"].append(iJet)
    

class jetSumPt(wrappedChain.calculable) :
    def __init__(self,jetCollection,jetSuffix) :
        self.cs = jetCollection,jetSuffix
        self.p4sName = '%sCorrectedP4%s' % self.cs
        self.indicesName = "%sIndices%s" % self.cs

    def name(self) : return "%sSumPt%s"% self.cs

    def update(self,ignored) :
        p4s = self.source[self.p4sName]
        indices = self.source[self.indicesName]["clean"]
        self.value = reduce( lambda x,i: x+p4s.at(i).pt(), indices , 0)


