#import copy
import math
import ROOT as r
from base import analysisStep
#####################################
beamSpotX=0.0
beamSpotY=0.0322
#####################################
def correctBeamSpot(d0LeptonTrack,beamSpotX,beamSpotY,leptonPhi) :
    return d0LeptonTrack - beamSpotX*math.sin(leptonPhi) + beamSpotY*math.cos(leptonPhi)
#####################################
def relIso(ecalIso,hcalIso,trkIso,pT) :
    return (ecalIso+hcalIso+trkIso)/pT
#####################################
class icfJetPtSorter(analysisStep) :
    """icfJetPtSorter"""

    def __init__(self):
        self.neededBranches=["Njets","Jetpt"]

    def uponAcceptance(self,chain,chainVars,extraVars) :
        jetPtsAndIndices=[]
        for iJet in  range(chainVars.Njets) :
            jetPtsAndIndices.append( (chainVars.Jetpt[iJet],iJet) )
        jetPtsAndIndices.sort()
        jetPtsAndIndices.reverse()

        extraVars.jetPtsSortedByPt=[]
        extraVars.jetIndicesSortedByPt=[]
        for i in range(len(jetPtsAndIndices)) :
            extraVars.jetPtsSortedByPt.append(jetPtsAndIndices[i][0])
            extraVars.jetIndicesSortedByPt.append(jetPtsAndIndices[i][1])
#####################################
class icfCleanJetProducer(analysisStep) :
    """icfCleanJetProducer"""

    def __init__(self,jetPtThreshold,jetEtaMax):
        self.jetPtThreshold=jetPtThreshold
        self.jetEtaMax=jetEtaMax
        
        self.moreName="(jetID; "

        self.moreName2+="pT>="+str(self.jetPtThreshold)+" GeV"
        self.moreName2+="; |eta|<="+str(self.jetEtaMax)
        self.moreName2+=")"

        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.dummyP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)

        self.neededBranches=["Njets","Jeteta","Jetpt","JetFem",
                             "Jetpx","Jetpy","Jetpz","JetE"]

    def select (self,chain,chainVars,extraVars) :
        extraVars.cleanJetIndices=[]
        extraVars.otherJetIndices=[]
        extraVars.cleanJets=[]

        Jetpx =chainVars.Jetpx
        Jetpy =chainVars.Jetpy
        Jetpz =chainVars.Jetpz
        JetE  =chainVars.JetE
        Jetpt =chainVars.Jetpt
        Jeteta=chainVars.Jeteta
        JetFem=chainVars.JetFem
        
        for jetIndex in extraVars.jetIndicesSortedByPt :
            #pt cut
            if (Jetpt[jetIndex]<self.jetPtThreshold) : continue

            #if pass pt cut, add to "other" category
            extraVars.otherJetIndices.append(jetIndex)
        
            #eta cut
            absEta=r.TMath.Abs(Jeteta[jetIndex])
            if (absEta>self.jetEtaMax) : continue

            #emf cut
            if (JetFem[jetIndex]>=0.9) : continue

            self.dummyP4.SetCoordinates(Jetpx[jetIndex],
                                        Jetpy[jetIndex],
                                        Jetpz[jetIndex],
                                        JetE[jetIndex])
            
            #extraVars.cleanJets.append(copy.deepcopy(self.dummyP4))
            extraVars.cleanJets.append(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.cleanJetIndices.append(jetIndex)
            extraVars.otherJetIndices.remove(jetIndex)

        return True
######################################
class icfNCleanJetHistogrammer(analysisStep) :
    """icfNCleanJetHistogrammer"""

    def __init__(self):
        self.neededBranches=[]

    def bookHistos(self) :
        nBins=15
        title=";number of jets passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"
        self.nCleanJetsHisto=r.TH1D("nCleanJets",title,nBins,-0.5,nBins-0.5)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.nCleanJetsHisto.Fill( len(extraVars.cleanJetIndices) )
######################################
class icfNCleanJetEventFilter(analysisStep) :
    """icfNCleanJetEventFilter"""

    def __init__(self,nCleanJets):
        self.nCleanJets=nCleanJets
        self.moreName="(>="+str(self.nCleanJets)+")"
        self.neededBranches=[]
        
    def select (self,chain,chainVars,extraVars) :
        return len(extraVars.cleanJetIndices)>=self.nCleanJets
######################################
class icfNOtherJetEventFilter(analysisStep) :
    """icfNOtherJetEventFilter"""

    def __init__(self,nOtherJets):
        self.nOtherJets=nOtherJets
        self.moreName="(<"+str(self.nOtherJets)+")"
        self.neededBranches=[]
        
    def select (self,chain,chainVars,extraVars) :
        return len(extraVars.otherJetIndices)<self.nOtherJets
#####################################
class icfCleanJetPtSelector(analysisStep) :
    """icfCleanJetPtSelector"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.neededBranches=["Njets","Jetpt"]
        self.moreName ="(pt["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV)"

    def select (self,chain,chainVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return False
        return (chainVars.Jetpt[extraVars.cleanJetIndices[self.jetIndex]]>=self.jetPtThreshold)
#####################################
class icfCleanJetPtVetoer(analysisStep) :
    """icfCleanJetPtVetoer"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.neededBranches=["Njets","Jetpt"]
        self.moreName ="(pt["+str(self.jetIndex)+"]<"+str(self.jetPtThreshold)+" GeV)"

    def select (self,chain,chainVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return True
        return (chainVars.Jetpt[extraVars.cleanJetIndices[self.jetIndex]]<self.jetPtThreshold)
#####################################
class icfCleanJetEtaSelector(analysisStep) :
    """icfCleanJetEtaSelector"""

    def __init__(self,jetEtaThreshold,jetIndex):
        self.jetEtaThreshold=jetEtaThreshold
        self.jetIndex=jetIndex
        self.neededBranches=["Njets","Jeteta"]
        self.moreName ="(eta["+str(self.jetIndex)+"]<"+str(self.jetEtaThreshold)+")"

    def select (self,chain,chainVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return False
        return (r.TMath.Abs(chainVars.Jeteta[extraVars.cleanJetIndices[self.jetIndex]])<self.jetEtaThreshold)
#####################################
class icfCleanJetHtMhtProducer(analysisStep) :
    """icfCleanJetHtMhtProducer"""

    def __init__(self):
        self.neededBranches=[]
        self.mht=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def select (self,chain,chainVars,extraVars) :
        self.mht.SetCoordinates(0.0,0.0,0.0,0.0)

        extraVars.ht=0.0
        extraVars.htEt=0.0

        for jet in extraVars.cleanJets :
            self.mht-=jet
            extraVars.ht+=jet.pt()
            extraVars.htEt+=jet.Et()

        setattr(extraVars,"mht",self.mht)
        return True
#####################################
class icfMhtAllProducer(analysisStep) :
    """icfMhtAllProducer"""

    def __init__(self,jetPtThreshold):
        self.jetPtThreshold=jetPtThreshold
        
        self.moreName="(pt>="+str(self.jetPtThreshold)+" GeV"+")"

        self.mhtAll=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.dummyP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)

        self.neededBranches=["Njets","Jetpt",
                             "Jetpx","Jetpy","Jetpz","JetE"]

    def uponAcceptance (self,chain,chainVars,extraVars) :
        Jetpx =chainVars.Jetpx
        Jetpy =chainVars.Jetpy
        Jetpz =chainVars.Jetpz
        JetE  =chainVars.JetE
        Jetpt =chainVars.Jetpt

        nJets=chainVars.Njets
        for iJet in range(nJets) :
            if (Jetpt[iJet]<self.jetPtThreshold) : continue

            self.dummyP4.SetCoordinates(Jetpx[iJet],
                                        Jetpy[iJet],
                                        Jetpz[iJet],
                                        JetE[iJet])
            self.mhtAll-=self.dummyP4
        
        setattr(extraVars,"mhtAll",self.mhtAll)
#####################################
class icfMhtRatioSelector(analysisStep) :
    """icfMhtRatioSelector"""

    def __init__(self,threshold):
        self.neededBranches=[]
        self.threshold=threshold
        
    def select (self,chain,chainVars,extraVars) :
        return ( (extraVars.mht.pt()/extraVars.mhtAll.pt())<self.threshold )
#####################################
class icfCleanJetHtMhtHistogrammer(analysisStep) :
    """icfCleanJetHtMhtHistogrammer"""

    def __init__(self):
        self.neededBranches=[]

    def bookHistos(self):
        self.ht_Histo          =r.TH1D("ht"       ,";H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,1000.0)
        #self.ht_et_Histo       =r.TH1D("ht_et"    ,";H_{T} (GeV) from clean jet E_{T}'s;events / bin" ,50,0.0,1000.0)
        self.mht_Histo         =r.TH1D("mht"      ,";#slash{H}_{T} (GeV) from clean jets;events / bin",50,0.0, 500.0)
        self.m_Histo           =r.TH1D("m"        ,";mass (GeV) of system of clean jets;events / bin" ,50,0.0,1000.0)
        self.mHtOverHt_Histo   =r.TH1D("mHtOverHt",";MHT / H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,1.1)

        title=";H_{T} (GeV) from clean jets;#slash{H}_{T} (GeV) from clean jet p_{T}'s;events / bin"
        self.mhtHt_Histo=r.TH2D("mht_vs_ht",title,50,0.0,1000.0,50,0.0,1000.0)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        mht=extraVars.mht.pt()
        self.mht_Histo.Fill(mht)
        self.ht_Histo.Fill(extraVars.ht)
        #self.ht_et_Histo.Fill(extraVars.htEt)
        self.m_Histo.Fill(extraVars.mht.mass())
        self.mhtHt_Histo.Fill(extraVars.ht,mht)

        value=-1.0
        if (extraVars.ht>0.0) : value=mht/extraVars.ht
        self.mHtOverHt_Histo.Fill(value)
#####################################
class icfCleanJetPtEtaHistogrammer(analysisStep) :
    """icfCleanJetPtEtaHistogrammer"""

    def __init__(self) :
        self.neededBranches=["Njets","Jetpt","Jeteta"]

    def bookHistos(self) :
        self.ptAllHisto=    r.TH1D("ptAll",";p_{T} (GeV) of clean jets;events / bin",50,0.0,800.0)
        self.ptLeadingHisto=r.TH1D("ptLeading",";p_{T} (GeV) of leading clean jet;events / bin",50,0.0,800.0)

        self.etaAllHisto=    r.TH1D("etaAll",";#eta of clean jets;events / bin",50,-5.0,5.0)
        self.etaLeadingHisto=r.TH1D("etaLeading",";#eta of leading clean jet;events / bin",50,-5.0,5.0)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        for iJet in extraVars.cleanJetIndices :
            pt=chainVars.Jetpt[iJet]
            self.ptAllHisto.Fill(pt)

            eta=chainVars.Jeteta[iJet]
            self.etaAllHisto.Fill(eta)
            if (iJet==0) :
                self.ptLeadingHisto.Fill(pt)
                self.etaLeadingHisto.Fill(eta)
#####################################
class icfCleanNJetAlphaProducer(analysisStep) :
    """icfCleanNJetAlphaProducer"""

    def __init__(self):
        self.neededBranches=[]

    def uponAcceptance (self,chain,chainVars,extraVars) :
        nJetDeltaHt=0.0
        nJetAlphaT=0.0

        #return if fewer than two clean jets
        if (len(extraVars.cleanJetIndices)<2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return

        #return if HT is tiny
        if (extraVars.ht<=1.0e-2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return

        #compute deltaHT
        pTs=[]
        totalPt=0.0
        for jet in extraVars.cleanJets :
            pt=jet.pt()
            pTs.append(pt)
            totalPt+=pt

        nJets=len(extraVars.cleanJetIndices)
        nCombinations=2**nJets
        diffs=[]
        for iCombination in range(nCombinations) :
            pseudoJetPt=0.0
            for iJet in range(nJets) :
                if (iCombination&(1<<iJet)) :
                    pseudoJetPt+=pTs[iJet]
            diffs.append(r.TMath.Abs(totalPt-2.0*pseudoJetPt))
        nJetDeltaHt=min(diffs)

        #compute alphaT
        mht=extraVars.mht.pt()
        ht=extraVars.ht
        nJetAlphaT=0.5*(1.0-nJetDeltaHt/ht)/r.TMath.sqrt(1.0-(mht/ht)**2)

        self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)

    def setExtraVars(self,extraVars,nJetDeltaHt,nJetAlphaT) :
        extraVars.nJetDeltaHt=nJetDeltaHt
        extraVars.nJetAlphaT=nJetAlphaT
#####################################
class icfCleanDiJetAlphaProducer(analysisStep) :
    """icfCleanDiJetAlphaProducer"""

    def __init__(self):
        self.lvSum=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.neededBranches=[]
        
    def select (self,chain,chainVars,extraVars) :
        self.lvSum.SetCoordinates(0.0,0.0,0.0,0.0)

        diJetM       =0.0
        diJetMinPt   =1.0e6
        diJetMinEt   =1.0e6
        diJetAlpha   =0.0
        diJetAlpha_Et=0.0

        #return if not dijet
        if (len(extraVars.cleanJetIndices)!=2) :
            self.setExtraVars(extraVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
            return True
            
        for jet in extraVars.cleanJets :
            pt=jet.pt()
            Et=jet.Et()

            if (pt<diJetMinPt) : diJetMinPt=pt
            if (Et<diJetMinEt) : diJetMinEt=Et

            self.lvSum+=jet

        diJetM=self.lvSum.M()
        
        if (diJetM>0.0) :
            diJetAlpha   =diJetMinPt/diJetM
            diJetAlpha_Et=diJetMinEt/diJetM

        self.setExtraVars(extraVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
        return True

    def setExtraVars(self,extraVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et) :
        extraVars.diJetM        =diJetM
        extraVars.diJetMinPt    =diJetMinPt
        extraVars.diJetMinEt    =diJetMinEt
        extraVars.diJetAlpha    =diJetAlpha
        extraVars.diJetAlpha_Et =diJetAlpha_Et
#####################################
class icfAlphaHistogrammer(analysisStep) :
    """icfAlphaHistogrammer"""

    def __init__(self) :
        self.neededBranches=[]
        
    def bookHistos(self) :
        bins=100
        min=0.0
        max=2.0
        self.diJetAlpha_Histo   =r.TH1D("dijet alpha"   ,";di-jet #alpha (using p_{T});events / bin"   ,bins,min,max)
        #self.diJetAlpha_ET_Histo=r.TH1D("dijet alpha_ET",";di-jet #alpha (using E_{T});events / bin"   ,bins,min,max)
        self.nJetAlphaT_Histo   =r.TH1D("njet alphaT"   ,";N-jet #alpha_{T} (using p_{T});events / bin",bins,min,max)

        #self.alpha2D_a_Histo=r.TH2D("Ht-deltaHt vs sqrt(Ht2-mHt2)",
        #                            ";H_{T} - #slash(H_{T}) (GeV);sqrt( H_{T}^{2} - {#Delta H_{T}}^{2} ) of two pseudo-jets (GeV);events / bin",
        #                            20,0.0,1000.0,
        #                            20,0.0,1000.0)        
        #
        #self.alpha2D_b_Histo=r.TH2D("Ht-deltaHt vs Ht-mHt",
        #                            ";H_{T} - #slash(H_{T}) (GeV);H_{T} - #Delta H_{T} of two pseudo-jets (GeV);events / bin",
        #                            20,0.0,1000.0,
        #                            20,0.0,1000.0)        

        self.alpha2D_c_Histo=r.TH2D("deltaHtOverHt vs mHtOverHt",
                                    ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin",
                                    30,0.0,1.0,
                                    30,0.0,0.7)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.diJetAlpha_Histo.Fill(   extraVars.diJetAlpha   )
        #self.diJetAlpha_ET_Histo.Fill(extraVars.diJetAlpha_Et)
        self.nJetAlphaT_Histo.Fill(   extraVars.nJetAlphaT   )
        #self.alpha2D_a_Histo.Fill(math.sqrt(extraVars.ht**2 - extraVars.mht.pt()**2),extraVars.ht - extraVars.nJetDeltaHt)
        #self.alpha2D_b_Histo.Fill(extraVars.ht - extraVars.mht.pt(),extraVars.ht - extraVars.nJetDeltaHt)
        self.alpha2D_c_Histo.Fill(extraVars.mht.pt()/extraVars.ht,extraVars.nJetDeltaHt/extraVars.ht)
#####################################
class icfDeltaPhiProducer(analysisStep) :
    """icfDeltaPhiProducer"""

    def __init__(self) :
        self.neededBranches=[]
    
    def select(self,chain,chainVars,extraVars) :

        extraVars.deltaPhi01= -4.0
        extraVars.deltaR01  =-40.0
        extraVars.deltaEta01=-40.0

        if (len(extraVars.cleanJetIndices)>=2) :
            jet0=extraVars.cleanJets[0]
            jet1=extraVars.cleanJets[1]
            extraVars.deltaPhi01=r.Math.VectorUtil.DeltaPhi(jet0,jet1)
            extraVars.deltaR01  =r.Math.VectorUtil.DeltaR(jet0,jet1)
            extraVars.deltaEta01=jet0.eta()-jet1.eta()
        return True
#####################################
class icfDeltaPhiSelector(analysisStep) :
    """icfDeltaPhiSelector"""

    def __init__(self,minAbs,maxAbs) :
        self.minAbs=minAbs
        self.maxAbs=maxAbs
    
    def select(self,chain,chainVars,extraVars) :
        value=r.TMath.Abs(extraVars.deltaPhi01)
        if (value<self.minAbs or value>self.maxAbs) : return False
        return True
#####################################
class icfMhtOverHtSelector(analysisStep) :
    """icfMhtOverHtSelector"""

    def __init__(self,min,max) :
        self.min=min
        self.max=max
    
    def select(self,chain,chainVars,extraVars) :
        if (extraVars.ht<1.0e-2) : return False
        value=extraVars.mht.pt()/extraVars.ht
        if (value<self.min or value>self.max) : return False
        return True
#####################################
class icfDeltaPhiHistogrammer(analysisStep) :
    """icfDeltaPhiHistogrammer"""

    def __init__(self) :
        self.neededBranches=[]

    def bookHistos(self) :
        bins=50
        min=-4.0
        max= 4.0
        title="deltaPhi01"
        self.deltaPhi01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)

        bins=20
        min= 0.0
        max=10.0
        title="deltaR01"
        self.deltaR01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)

        bins=50
        min=-10.0
        max= 10.0
        title="deltaEta01"
        self.deltaEta01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.deltaPhi01_Histo.Fill(extraVars.deltaPhi01 )
        self.deltaR01_Histo.Fill(  extraVars.deltaR01   )
        self.deltaEta01_Histo.Fill(extraVars.deltaEta01 )
#####################################
class icfAnyJetPtSelector(analysisStep) :
    """icfAnyJetPtSelector"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.neededBranches=[]
        self.moreName ="(pT["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

    def select (self,chain,chainVars,extraVars) :
        if (len(extraVars.jetPtsSortedByPt)<=self.jetIndex) : return False
        return (extraVars.jetPtsSortedByPt[self.jetIndex]>=self.jetPtThreshold)
#####################################
class icfAnyJetPtVetoer(analysisStep) :
    """icfAnyJetPtVetoer"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.neededBranches=[]
        self.moreName ="(pT["+str(self.jetIndex)+"]<"+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

    def select (self,chain,chainVars,extraVars) :
        if (len(extraVars.jetPtsSortedByPt)<=self.jetIndex) : return True
        return (extraVars.jetPtsSortedByPt[self.jetIndex]<self.jetPtThreshold)
#####################################
class icfMuonVetoer(analysisStep) :
    """icfMuonVetoer"""

    def __init__(self,muonPtThreshold):
        self.muonPtThreshold=muonPtThreshold
        self.moreName ="(no muon with pT>"+str(self.muonPtThreshold)+" GeV passing ID)"

        #a bit of a hack here
        self.neededBranches=["Nmuon","MuonIsGlobalTight","MuonTrkValidHits","MuonTrkD0","MuonCombChi2","MuonCombNdof"] #Nmuon must be the first element
        self.branchesToBind=["Nmuon","Muonpt","Muoneta","Muonphi","MuonECalIsoDeposit","MuonHCalIsoDeposit","MuonHCalIso","MuonECalIso","MuonTrkIso"]
        self.neededBranches.extend(self.branchesToBind)

    def select (self,chain,chainVars,extraVars) :
        anyGoodMuon=False

        #leaf name matches branch name
        nMuons=chainVars.Nmuon
        pt=chainVars.Muonpt
        eta=chainVars.Muoneta
        phi=chainVars.Muonphi
        ecalDeposit=chainVars.MuonECalIsoDeposit
        hcalDeposit=chainVars.MuonHCalIsoDeposit

        hcalIso=chainVars.MuonHCalIso
        ecalIso=chainVars.MuonECalIso
        trkIso=chainVars.MuonTrkIso

        #leaf name does not match branch name
        trkHits=chain.mTempTreeMuonTrkValidHits
        d0=chain.mTempTreeMuonTrkD0
        chi2=chain.mTempTreeMuonCombChi2
        nDof=chain.mTempTreeMuonCombNdof
        
        for iMuon in range(nMuons) :
            if (pt[iMuon]<self.muonPtThreshold) : continue
            if (math.fabs(eta[iMuon])>3.0) : continue

            isTightGlobal=chain.GetLeaf("mTempTreeMuonIsGlobalTight").GetValue(iMuon)

            if (isTightGlobal<0.5) : continue
            if (not ecalDeposit[iMuon]<4.0) : continue
            if (not hcalDeposit[iMuon]<6.0) : continue
            if (not trkHits>=11.0) : continue
            if (not correctBeamSpot(d0[iMuon],beamSpotX,beamSpotY,phi[iMuon])<0.2) : continue
            if (not chi2[iMuon]/nDof[iMuon]<10.0) : continue
            if (not relIso(ecalIso[iMuon],hcalIso[iMuon],trkIso[iMuon],pt[iMuon])<0.2) : continue

            anyGoodMuon=True
            break

        return not anyGoodMuon
#####################################
class icfElecVetoer(analysisStep) :
    """icfElecVetoer"""

    def __init__(self,elecPtThreshold):
        self.elecPtThreshold=elecPtThreshold
        self.moreName ="(no elec with pT>"+str(self.elecPtThreshold)+" GeV passing ID)"

        #a bit of a hack here
        self.neededBranches=["Nelec","ElecIdRobTight"] #Nelec must be the first element
        self.branchesToBind=["Nelec","Elecpt","Eleceta","Elecphi","ElecD0","ElecECalIso","ElecHCalIso","ElecTrkIso"]
        self.neededBranches.extend(self.branchesToBind)

    def select (self,chain,chainVars,extraVars) :
        anyGoodElec=False

        #leaf name matches branch name
        nElecs=chainVars.Nelec
        pt=chainVars.Elecpt
        eta=chainVars.Eleceta
        phi=chainVars.Elecphi
        d0=chainVars.ElecD0
        hcalIso=chainVars.ElecHCalIso
        ecalIso=chainVars.ElecECalIso
        trkIso=chainVars.ElecTrkIso

        #leaf name does not match branch name
        tight=getattr(chain,"ElecIdRobTight ")#space!

        for iElec in range(nElecs) :
            if (pt[iElec]<self.elecPtThreshold) : continue
            if (math.fabs(eta[iElec])>3.0) : continue
            if (tight[iElec]!=1) : continue
            if (not correctBeamSpot(d0[iElec],beamSpotX,beamSpotY,phi[iElec])<0.2) : continue
            if (not relIso(ecalIso[iElec],hcalIso[iElec],trkIso[iElec],pt[iElec])<0.2) : continue

            anyGoodElec=True
            break

        return not anyGoodElec
#####################################
class icfPhotVetoer(analysisStep) :
    """icfPhotVetoer"""

    def __init__(self,photPtThreshold):
        self.photPtThreshold=photPtThreshold
        self.moreName ="(no phot with pT>"+str(self.photPtThreshold)+" GeV passing ID)"

        #a bit of a hack here
        self.neededBranches=["Nphot","PhotTightPhoton"] #Nphot must be the first element
        self.branchesToBind=["Nphot","Photpt","Photeta"]
        self.neededBranches.extend(self.branchesToBind)

    def select (self,chain,chainVars,extraVars) :
        anyGoodPhot=False

        #leaf name matches branch name
        nPhots=chainVars.Nphot
        pt=chainVars.Photpt
        eta=chainVars.Photeta

        for iPhot in range(nPhots) :
            if (pt[iPhot]<self.photPtThreshold) : continue
            if (math.fabs(eta[iPhot])>5.0) : continue
            isTight=chain.GetLeaf("mTempTreePhotTightPhoton").GetValue(iPhot)
            if (isTight<0.5) : continue
            
            anyGoodPhot=True
            break

        return not anyGoodPhot
#####################################
