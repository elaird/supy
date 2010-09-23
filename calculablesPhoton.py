from wrappedChain import *
import calculables
##############################
class photonIndicesOtherPat(calculables.indicesOther) :
    def __init__(self,collection = ("photon","Pat")) :
        super(photonIndicesOtherPat, self).__init__(collection)
        self.moreName = "pass ptMin; fail id/iso"
##############################
class photonIndicesPat(wrappedChain.calculable) :

    def __init__(self, ptMin = None, flagName = None ):
        self.ptMin = ptMin
        self.flagName = flagName
        self.moreName = "pT>=%.1f GeV; %s"% (ptMin, flagName if flagName else "")

    def update(self,ignored) :
        p4s = self.source["photonP4Pat"]
        ids = self.source[self.flagName] if self.flagName else p4s.size()*[1]
        self.value = []
        other = self.source["photonIndicesOtherPat"]
        
        for i in range(p4s.size()):
            if p4s.at(i).pt() < self.ptMin: continue
            elif ids[i] : self.value.append(i)
            else: other.append(i)
##############################
class leadingPt(wrappedChain.calculable) :
    def name(self) : return "%sLeadingPt%s"%self.photons

    def __init__(self, collection = ("photon","Pat")) :
        self.photons = collection
        
    def update(self,ignored) :
        indices = self.source["%sIndices%s"%self.photons]
        self.value = self.source["%sP4%s"%self.photons].at(indices[0]).pt() if len(indices) else None
####################################
class photonID(wrappedChain.calculable) :
    def name(self) : return self.idName
    
    # following https://twiki.cern.ch/twiki/bin/viewauth/CMS/PhotonID
    def __init__(self, collection = None, level = None) :
        self.cs = collection
        self.idName = "%sID%s%s" % (self.cs[0],level,self.cs[1])
        self.p4Name = "%sP4%s" % self.cs

        for var in ["EcalRecHitEtConeDR04", "HcalDepth1TowSumEtConeDR04", "HcalDepth2TowSumEtConeDR04",
                    "HadronicOverEm", "TrkSumPtHollowConeDR04", "SigmaIetaIeta","HasPixelSeed"] :
            setattr(self,var, ("%s"+var+"%s")%self.cs)

        levels = ["em","loose","tight"]
        jei  = [ (4.2,  0.006 ) for l in levels ]
        tbhi = [ (2.2,  0.0025) for l in levels ]
        hoe  = [ (0.05, 0.000 ) for l in levels ]
        hcti = [ None           for l in levels ]; hcti[1] = (3.5, 0.001); hcti[2] = (2.0, 0.001)
        shhBarrel = [ None      for l in levels ]; shhBarrel[2] = (0.013, 0.0)
        shhEndcap = [ None      for l in levels ]; shhEndcap[2] = (0.030, 0.0)

        self.etaBE = 1.479 #from CMS PAS EGM-10-005
        for item in ["jei","tbhi","hoe","hcti","shhBarrel","shhEndcap"] :
            setattr(self,item,eval(item)[levels.index(level)])
        self.moreName = "twiki.cern.ch/twiki/bin/viewauth/CMS/PhotonID, 2010-09-19"
        
    def update(self,ignored) :
        self.value = map(self.passId, 
                         self.source[self.p4Name],
                         self.source[self.EcalRecHitEtConeDR04],
                         self.source[self.HcalDepth1TowSumEtConeDR04],
                         self.source[self.HcalDepth2TowSumEtConeDR04],
                         self.source[self.HadronicOverEm],
                         self.source[self.TrkSumPtHollowConeDR04],
                         self.source[self.SigmaIetaIeta],
                         self.source[self.HasPixelSeed],
                         )

    def passId(self, p4, jei, hi1, hi2, hoe, hcti, shh, hasPixelSeed) :
        pt = p4.pt()
        if jei       > (self.jei [0] + pt*self.jei [1]) : return False
        if (hi1+hi2) > (self.tbhi[0] + pt*self.tbhi[1]) : return False
        if hoe       > (self.hoe [0] + pt*self.hoe [1]) : return False
        if self.hcti!=None and hcti > (self.hcti[0] + pt*self.hcti[1]) : return False

        shhVar = self.shhBarrel if abs(p4.eta())<self.etaBE else self.shhEndcap
        if shhVar!=None and shh  > (shhVar[0] + pt*shhVar[1]) : return False

        if hasPixelSeed : return False
        return True
class photonIDem(photonID) :
    def __init__(self, collection = None) :
        super(photonIDem,self).__init__(collection,"em")
class photonIDloose(photonID) :
    def __init__(self, collection = None) :
        super(photonIDloose,self).__init__(collection,"loose")
class photonIDtight(photonID) :
    def __init__(self, collection = None) :
        super(photonIDtight,self).__init__(collection,"tight")
####################################
