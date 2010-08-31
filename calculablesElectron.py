import calculables
from wrappedChain import *
##############################
barrelEtaMax = 1.4442
endcapEtaMin = 1.560
##############################
class electronIndicesOther(calculables.indicesOther) :
    def __init__(self,collection = None) :
        super(electronIndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail id/iso"
##############################
class electronIndices(wrappedChain.calculable) :
    def name(self) : return "%sIndices%s" % self.ele

    def __init__(self, collection = None, ptMin = None, simpleEleID = None, useCombinedIso = True) :
        isotype = "c" if useCombinedIso else "rel"
        self.ele = collection
        self.ptMin = ptMin
        self.eID = self.ele[0] + "ID%s"%simpleEleID + self.ele[1]
        self.eIso = self.ele[0] + "%sIso%s"%(isotype,simpleEleID) + self.ele[1]
        self.moreName = "pt>%.1f; simple%s; %sIso; no conversion cut" % (ptMin, simpleEleID, isotype)

    def update(self,ignored) :
        self.value = []
        other = self.source["%sIndicesOther%s"%self.ele]
        p4s = self.source["%sP4%s"%self.ele]
        eID = self.source[self.eID]
        eIso = self.source[self.eIso]
        for i in range(p4s.size()) :
            if p4s.at(i).pt() < self.ptMin : break
            elif eID[i] and eIso[i]:
                self.value.append(i)
            else: other.append(i)
##############################
class eleID(wrappedChain.calculable) :
    def name(self) : return self.idName

    def id(self, hoe, dphi, deta, sieie, p4) :
        absEta = abs(p4.eta())
        return hoe < self.Bhoe and dphi < self.Bdphi and deta < self.Bdeta and sieie < self.Bsieie if absEta < barrelEtaMax else \
               hoe < self.Ehoe and dphi < self.Edphi and deta < self.Edeta and sieie < self.Esieie if absEta > endcapEtaMin else \
               None

    def update(self,ignored) :
        self.value = map(self.id, 
                         self.source["%sHcalOverEcal%s"%self.ele],
                         self.source["%sDeltaPhiSuperClusterTrackAtVtx%s"%self.ele],
                         self.source["%sDeltaEtaSuperClusterTrackAtVtx%s"%self.ele],
                         self.source["%sSigmaIetaIeta%s"%self.ele],
                         self.source["%sP4%s"%self.ele])

    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SimpleCutBasedEleID
    def __init__(self,collection, eff) :
        self.idName = collection[0]+"ID"+eff+collection[1]
        self.ele = collection
        i = ["95","90","85","80","70","60"].index(eff)
        self.Bsieie = [0.01,    0.01,    0.01,    0.01,    0.01,    0.01  ][i]
        self.Bdphi  = [0.80,    0.80,    0.06,    0.06,    0.03,    0.025 ][i]
        self.Bdeta  = [0.007,   0.007,   0.006,   0.004,   0.004,   0.004 ][i]
        self.Bhoe   = [0.15,    0.12,    0.04,    0.04,    0.025,   0.025 ][i]
        self.Esieie = [0.03,   0.03,   0.03,   0.03,   0.03,   0.03  ][i]
        self.Edphi  = [0.7,    0.7,    0.04,   0.03,   0.02,   0.02  ][i]
        self.Edeta = 10.0 #[0.01,   0.009,  0.007,  0.007,  0.005,  0.005 ][i] # note on twiki not to apply these
        self.Ehoe   = [0.07,   0.05,   0.025,  0.025,  0.025,  0.025 ][i]
class eleID95(eleID) :
    def __init__(self,collection) : super(eleID95,self).__init__(collection,"95")
class eleID90(eleID) :
    def __init__(self,collection) : super(eleID90,self).__init__(collection,"90")
class eleID85(eleID) :
    def __init__(self,collection) : super(eleID85,self).__init__(collection,"85")
class eleID80(eleID) :
    def __init__(self,collection) : super(eleID80,self).__init__(collection,"80")
class eleID70(eleID) :
    def __init__(self,collection) : super(eleID70,self).__init__(collection,"70")
class eleID60(eleID) :
    def __init__(self,collection) : super(eleID60,self).__init__(collection,"60")
##############################
class eleIso(wrappedChain.calculable) :
    def name(self) : return self.isoName
    
    def __init__(self, collection, eff, combined) :
        self.combined = combined
        self.isoName = collection[0]+("c" if combined else "rel")+"Iso"+eff+collection[1]
        self.ele = collection
        i = ["95","90","85","80","70","60"].index(eff)
        self.Bc    = [0.15,   0.10,   0.09,   0.07,   0.04,   0.03 ][i]
        self.Btrk  = [0.15,   0.12,   0.09,   0.09,   0.05,   0.04 ][i]
        self.Becal = [2.00,   0.09,   0.08,   0.07,   0.06,   0.04 ][i]
        self.Bhcal = [0.12,   0.10,   0.10,   0.10,   0.03,   0.03 ][i]
        self.Ec    = [0.1,    0.07,   0.06,    0.06,    0.03,    0.02  ][i]
        self.Etrk  = [0.08,   0.05,   0.05,    0.04,    0.025,   0.025 ][i]
        self.Eecal = [0.06,   0.06,   0.05,    0.05,    0.025,   0.02  ][i]
        self.Ehcal = [0.05,   0.03,   0.025,   0.025,   0.02,    0.02  ][i]
        
    def cIso(self, iso, p4) :
        absEta = abs(p4.eta())
        if absEta < barrelEtaMax: return iso < self.Bc
        if absEta > endcapEtaMin: return iso < self.Ec
        return None

    def relIso(self, trk, ecal, hcal, p4) :
        absEta = abs(p4.eta())
        if absEta < barrelEtaMax : return trk < self.Btrk and ecal < self.Becal and hcal < self.Bhcal
        if absEta > endcapEtaMin : return trk < self.Etrk and ecal < self.Eecal and hcal < self.Ehcal
        return None

    def update(self,ignored) :
        self.value = map(self.cIso,
                         self.source["%sIsoCombined%s"%self.ele],
                         self.source["%sP4%s"%self.ele]) if self.combined else \
                     map(self.relIso,
                         self.source["%sTrackIsoRel%s"%self.ele],
                         self.source["%sEcalIsoRel%s"%self.ele],
                         self.source["%sHcalIsoRel%s"%self.ele])
class elecIso95(eleIso) :
    def __init__(self,collection) : super(elecIso95,self).__init__(collection,"95", True)
class elecIso90(eleIso) :
    def __init__(self,collection) : super(elecIso90,self).__init__(collection,"90", True)
class elecIso85(eleIso) :
    def __init__(self,collection) : super(elecIso85,self).__init__(collection,"85", True)
class elecIso80(eleIso) :
    def __init__(self,collection) : super(elecIso80,self).__init__(collection,"80", True)
class elecIso70(eleIso) :
    def __init__(self,collection) : super(elecIso70,self).__init__(collection,"70", True)
class elecIso60(eleIso) :
    def __init__(self,collection) : super(elecIso60,self).__init__(collection,"60", True)
class elerelIso95(eleIso) :
    def __init__(self,collection) : super(elerelIso95,self).__init__(collection,"95", False)
class elerelIso90(eleIso) :
    def __init__(self,collection) : super(elerelIso90,self).__init__(collection,"90", False)
class elerelIso85(eleIso) :
    def __init__(self,collection) : super(elerelIso85,self).__init__(collection,"85", False)
class elerelIso80(eleIso) :
    def __init__(self,collection) : super(elerelIso80,self).__init__(collection,"80", False)
class elerelIso70(eleIso) :
    def __init__(self,collection) : super(elerelIso70,self).__init__(collection,"70", False)
class elerelIso60(eleIso) :
    def __init__(self,collection) : super(elerelIso60,self).__init__(collection,"60", False)
##############################
class eleIsoCombined(wrappedChain.calculable) :
    def name(self) : return "%sIsoCombined%s"%self.ele

    def __init__(self,collection = None) : self.ele = collection

    def update(self,ignored) :
        self.value = map(self.combinedIso,
                         self.source["%sDr03TkSumPt%s"%self.ele],
                         self.source["%sDr03EcalRecHitSumEt%s"%self.ele],
                         self.source["%sDr03HcalTowerSumEt%s"%self.ele],
                         self.source["%sP4%s"%self.ele])

    def combinedIso(self,trk,ecal,hcal,p4) :
        absEta = abs(p4.eta())
        return (trk + max(0.,ecal-1) + hcal) / p4.pt() if absEta < barrelEtaMax else \
               (trk + ecal + hcal) / p4.pt() if absEta > endcapEtaMin else \
               None
##############################
class eleIsoRel(wrappedChain.calculable) :
    def name(self) : return self.isoName
    def __init__(self, collection, isoName, isoSource) :
        self.isoSource = collection[0]+isoSource+collection[1]
        self.isoName = collection[0]+isoName+collection[1]
        self.p4 = "%sP4%s"%collection
    def relIso(self, iso, p4) : return iso/p4.pt()
    def update(self,ignored) : self.value = map(self.relIso, self.isoSource, self.p4)
    
class eleTrackIsoRel(eleIsoRel) :
    def __init__(self, collection = None) : super(eleTrackIsoRel,self).__init__(collection, "TrackIsoRel", "Dr03TkSumPt")
class eleEcalIsoRel(eleIsoRel) :
    def __init__(self, collection = None) : super(eleEcalIsoRel,self).__init__(collection, "EcalIsoRel", "Dr03EcalRecHitSumEt")
class eleHcalIsoRel(eleIsoRel) :
    def __init__(self, collection = None) : super(eleHcalIsoRel,self).__init__(collection, "HcalIsoRel", "Dr03HcalTowerSumEt")
##############################
