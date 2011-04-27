from wrappedChain import *
import calculables,utils
##############################
class IndicesOther(calculables.indicesOther) :
    def __init__(self,collection = None) :
        super(IndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail id/iso"
##############################
class Indices(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, flagName = None):
        self.fixes = collection
        self.stash(["IndicesOther", "P4"])
        self.ptMin = ptMin
        self.flagName = flagName
        self.moreName = "pT>=%.1f GeV; %s"% (ptMin, flagName if flagName else "")
    def update(self,ignored) :
        p4s = self.source[self.P4]
        ids = self.source[self.flagName] if self.flagName else p4s.size()*[1]
        self.value = []
        other = self.source[self.IndicesOther]
        for i in range(p4s.size()):
            if p4s.at(i).pt() < self.ptMin: continue
            elif ids[i] : self.value.append(i)
            else: other.append(i)
##############################
class SumP4(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","P4"])
    def update(self, ignored) :
        p4s = self.source[self.P4]
        indices = self.source[self.Indices]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices, utils.LorentzV()) if len(indices) else None
##############################
class SumEt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","P4"])
    def update(self, ignored) :
        p4s = self.source[self.P4]
        indices = self.source[self.Indices]
        self.value = reduce( lambda x,i: x+p4s.at(i).Et(), indices , 0)
##############################
class metPlusPhotons(wrappedChain.calculable) :
    def name(self) :
        return "%sPlus%s%s"%(self.met, self.photons[0], self.photons[1])
    def __init__(self, met, photons) :
        self.met = met
        self.photons = photons
        self.moreName = "%s + %s%s"%(self.met, self.photons[0], self.photons[1])
    def update(self, ignored) :
        self.value = self.source[self.met] + self.source["%sSumP4%s"%self.photons]
##############################
class minDeltaRToJet(wrappedChain.calculable) :
    def name(self) : return "%s%sMinDeltaRToJet%s%s"% (self.photons[0], self.photons[1], self.jets[0], self.jets[1])

    def __init__(self, photons, jets) :
        for item in ["photons","jets"] :
            setattr(self,item,eval(item))
        self.photonIndices = "%sIndices%s"%self.photons
        self.photonP4s     = "%sP4%s"     %self.photons

        self.jetIndices = "%sIndices%s"    %self.jets
        self.jetP4s     = "%sCorrectedP4%s"%self.jets

    def update(self, ignored) :
        self.value = {}
        photonIndices = self.source[self.photonIndices]
        photons       = self.source[self.photonP4s]

        jetIndices    = self.source[self.jetIndices]
        jets          = self.source[self.jetP4s]
        for iPhoton in photonIndices :
            self.value[iPhoton] = min([r.Math.VectorUtil.DeltaR( photons.at(iPhoton), jets.at(iJet) ) for iJet in jetIndices]) if len(jetIndices) else None
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

        for var in ["EcalRecHitEtConeDR04", "HcalTowSumEtConeDR04",
                    "HadronicOverEm", "TrkSumPtHollowConeDR04", "SigmaIetaIeta","HasPixelSeed"] :
            setattr(self,var, ("%s"+var+"%s")%self.cs)

        jei = {}; jeiLower = {}; tbhi = {}; tbhiLower = {}; hcti = {}; hctiLower = {};
        hoe = {}; shhBarrel = {}; shhEndcap = {}; ptVar = {}; etaBE = {}; moreName = {}
        for l in ["EmFromTwiki","LooseFromTwiki","TightFromTwiki",
                  "AnalysisNote_10_268","EGM_10_006_Loose","EGM_10_006_Tight","TrkIsoSideBand","TrkIsoRelaxed","IsoSideBand","IsoRelaxed","NoIsoReq"] :
            jei [l]      = (4.2,  0.0060); jeiLower[l]  = None
            tbhi[l]      = (2.2,  0.0025); tbhiLower[l] = None
            hcti[l]      = None          ; hctiLower[l] = None
            hoe [l]      = (0.05, 0.0000)
            shhBarrel[l] = None
            shhEndcap[l] = None
            ptVar[l]     = "pt"
            etaBE[l]     = 1.479 #from CMS PAS EGM-10-005
            moreName[l]  = "PhotonID twiki, 2010-10-14, %s"%("is"+l.replace("FromTwiki",""))

        hcti     ["LooseFromTwiki"] = (3.5, 0.001)

        hcti     ["TightFromTwiki"] = (2.0, 0.001)
        shhBarrel["TightFromTwiki"] = (0.013, 0.0)
        shhEndcap["TightFromTwiki"] = (0.030, 0.0)

        jei      ["AnalysisNote_10_268"] = (4.2, 0.003)
        tbhi     ["AnalysisNote_10_268"] = (2.2, 0.001)
        hcti     ["AnalysisNote_10_268"] = (2.0, 0.001)
        ptVar    ["AnalysisNote_10_268"] = "Et"
        moreName ["AnalysisNote_10_268"] = "from CMS AN 10-268"

        jei      ["EGM_10_006_Tight"] = (2.4,  0.0)
        tbhi     ["EGM_10_006_Tight"] = (1.0,  0.0)
        hcti     ["EGM_10_006_Tight"] = (0.9,  0.0)
        hoe      ["EGM_10_006_Tight"] = (0.03, 0.0)
        shhBarrel["EGM_10_006_Tight"] = (0.01, 0.0)
        shhEndcap["EGM_10_006_Tight"] = (0.028,0.0)
        moreName ["EGM_10_006_Tight"] = "EGM 10-006 tight"

        jei      ["EGM_10_006_Loose"] = (4.2,  0.0)
        tbhi     ["EGM_10_006_Loose"] = (2.2,  0.0)
        hcti     ["EGM_10_006_Loose"] = (2.0,  0.0)
        hoe      ["EGM_10_006_Loose"] = (0.05, 0.0)
        shhBarrel["EGM_10_006_Loose"] = (0.01, 0.0)
        shhEndcap["EGM_10_006_Loose"] = (0.03, 0.0)
        moreName ["EGM_10_006_Loose"] = "EGM 10-006 loose"

        hcti     ["TrkIsoRelaxed"] = (10.0, 0.001)
        moreName ["TrkIsoRelaxed"] = "relaxed trkIso"

        hcti     ["TrkIsoSideBand"] = (10.0, 0.001)
        hctiLower["TrkIsoSideBand"] = ( 2.0, 0.001)
        moreName ["TrkIsoSideBand"] = "side-band of trkIso"

        jei      ["NoIsoReq"] = (100.0, 0.0)
        tbhi     ["NoIsoReq"] = (100.0, 0.0)
        hcti     ["NoIsoReq"] = (100.0, 0.0)
        moreName ["NoIsoReq"] = "relaxed trkIso [ ,100]; hcalIso[ ,100]; ecalIso[ ,100]"

        jei      ["IsoRelaxed"] = (8.2,  0.0060)
        tbhi     ["IsoRelaxed"] = (6.2,  0.0025)
        hcti     ["IsoRelaxed"] = (10.0, 0.001)
        moreName ["IsoRelaxed"] = "relaxed trkIso [ ,10]; hcalIso[ ,6]; ecalIso[ ,8]"

        jei      ["IsoSideBand"] = (8.2,  0.0060)
        jeiLower ["IsoSideBand"] = jei ["TightFromTwiki"]
        tbhi     ["IsoSideBand"] = (6.2,  0.0025)
        tbhiLower["IsoSideBand"] = tbhi["TightFromTwiki"]
        hcti     ["IsoSideBand"] = (10.0, 0.001)
        hctiLower["IsoSideBand"] = hcti["TightFromTwiki"]
        moreName ["IsoSideBand"] = "side-band of trkIso [2,10]; hcalIso[2,6]; ecalIso[4,8]"

        for item in ["jei","jeiLower",
                     "tbhi","tbhiLower",
                     "hcti","hctiLower",
                     "hoe","shhBarrel","shhEndcap","ptVar","etaBE","moreName"] :
            setattr(self,item,eval(item)[level])

    def update(self,ignored) :
        self.value = utils.hackMap(self.passId, 
                         self.source[self.p4Name],
                         self.source[self.EcalRecHitEtConeDR04],
                         self.source[self.HcalTowSumEtConeDR04],
                         self.source[self.HadronicOverEm],
                         self.source[self.TrkSumPtHollowConeDR04],
                         self.source[self.SigmaIetaIeta],
                         self.source[self.HasPixelSeed],
                         )

    def passId(self, p4, jei, tbhi, hoe, hcti, shh, hasPixelSeed) :
        def pass1(item, value, alsoLower = False) :
            member = getattr(self,item)
            if member!=None and value > (member[0] + pt*member[1]) :
                return False
            if alsoLower :
                memberLower = getattr(self,item+"Lower")
                if memberLower!=None and value < (memberLower[0] + pt*memberLower[1]) : return False
            return True
        
        pt = getattr(p4,self.ptVar)()

        if not pass1("jei",  eval("jei"),  alsoLower = True)  : return False
        if not pass1("tbhi", eval("tbhi"), alsoLower = True)  : return False
        if not pass1("hcti", eval("hcti"), alsoLower = True)  : return False
        if not pass1("hoe",  eval("hoe"),  alsoLower = False) : return False

        shhVar = self.shhBarrel if abs(p4.eta())<self.etaBE else self.shhEndcap
        if shhVar!=None and shh  > (shhVar[0] + pt*shhVar[1]) : return False
        
        if hasPixelSeed : return False
        return True
####################################    
class HcalTowSumEtConeDR04(wrappedChain.calculable) :
    def name(self) : return "%sHcalTowSumEtConeDR04%s"%self.collection
    def __init__(self, collection = None) :
        self.collection = collection
        self.var1 = "%sHcalDepth1TowSumEtConeDR04%s"%collection
        self.var2 = "%sHcalDepth2TowSumEtConeDR04%s"%collection
        self.moreName = "depth 1 + depth 2"
    def update(self, ignored) :
        size = len(self.source[self.var1])
        self.value = [self.source[self.var1].at(i)+self.source[self.var2].at(i) for i in range(size)]
####################################    
class SeedTime(wrappedChain.calculable) :
    def name(self) : return "%sSeedTime%s"%self.collection
    def __init__(self, collection = None) :
        self.collection = collection
        self.p4s = "%sP4%s"%self.collection
    def isFake(self) : return True
    def update(self, ignored) :
        self.value = [-100.0]*len(self.source[self.p4s])
####################################
class photonIDEmFromTwiki(photonID) :
    def __init__(self, collection = None) :
        super(photonIDEmFromTwiki,self).__init__(collection,"EmFromTwiki")
####################################
class photonIDLooseFromTwiki(photonID) :
    def __init__(self, collection = None) :
        super(photonIDLooseFromTwiki,self).__init__(collection,"LooseFromTwiki")
####################################
class photonIDTightFromTwiki(photonID) :
    def __init__(self, collection = None) :
        super(photonIDTightFromTwiki,self).__init__(collection,"TightFromTwiki")
####################################
class photonIDTrkIsoSideBand(photonID) :
    def __init__(self, collection = None) :
        super(photonIDTrkIsoSideBand,self).__init__(collection,"TrkIsoSideBand")
####################################
class photonIDNoIsoReq(photonID) :
    def __init__(self, collection = None) :
        super(photonIDNoIsoReq,self).__init__(collection,"NoIsoReq")
####################################
class photonIDIsoRelaxed(photonID) :
    def __init__(self, collection = None) :
        super(photonIDIsoRelaxed,self).__init__(collection,"IsoRelaxed")
####################################
class photonIDIsoSideBand(photonID) :
    def __init__(self, collection = None) :
        super(photonIDIsoSideBand,self).__init__(collection,"IsoSideBand")
####################################
class photonIDTrkIsoRelaxed(photonID) :
    def __init__(self, collection = None) :
        super(photonIDTrkIsoRelaxed,self).__init__(collection,"TrkIsoRelaxed")
####################################
class photonIDAnalysisNote_10_268(photonID) :
    def __init__(self, collection = None) :
        super(photonIDAnalysisNote_10_268,self).__init__(collection,"AnalysisNote_10_268")
####################################
class photonIDEGM_10_006_Tight(photonID) :
    def __init__(self, collection = None) :
        super(photonIDEGM_10_006_Tight,self).__init__(collection,"EGM_10_006_Tight")
####################################
class photonIDEGM_10_006_Loose(photonID) :
    def __init__(self, collection = None) :
        super(photonIDEGM_10_006_Loose,self).__init__(collection,"EGM_10_006_Loose")
####################################
class photonWeight(wrappedChain.calculable) :
    def __init__(self, var = None) :
        #self.weight = {0:1.0001, 1:0.296134, 2:0.934791, 3:1.61404, 4:1.72028, 5:1.48318, 6:0.967893, 7:0.598355, 8:0.399606, 9:0.232468, 10:0.144349, 11:0.117307, 12:0.0486522, 13:0.230382, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0} #determined on 2011-04-23 requiring a photon and leading jets
        self.weight = {0:1.00047, 1:0.302948, 2:1.00326, 3:1.64012, 4:1.72804, 5:1.37661, 6:0.921953, 7:0.612364, 8:0.341528, 9:0.237224, 10:0.180099, 11:0.0957888, 12:0.0385848, 13:0.0785021, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0}#determined on 2011-04-26 requiring a photon
        self.var = var
    def update(self, ignored) :
        self.value = self.weight[len(self.source[self.var])]
####################################
