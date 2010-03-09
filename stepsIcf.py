import copy
import ROOT as r
from base import analysisStep
#####################################
class icfJetPtSelector(analysisStep) :
    """icfJetPtSelector"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        
        self.moreName ="(pT["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=["Njets","Jetpt"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Njets<=self.jetIndex) : return False
        return (chain.Jetpt[self.jetIndex]>=self.jetPtThreshold)
#####################################
class icfJetPtVetoer(analysisStep) :
    """icfJetPtVetoer"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        
        self.moreName ="(pT["+str(self.jetIndex)+"]<"+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=["Njets","Jetpt"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Njets<=self.jetIndex) : return True
        return (chain.Jetpt[self.jetIndex]<self.jetPtThreshold)
#####################################
class icfJetEtaSelector(analysisStep) :
    """icfJetEtaSelector"""

    def __init__(self,jetEtaThreshold,jetIndex):
        self.jetEtaThreshold=jetEtaThreshold
        self.jetIndex=jetIndex
        
        self.moreName ="(eta["+str(self.jetIndex)+"]<"+str(self.jetEtaThreshold)+")"
        self.neededBranches=["Njets","Jeteta"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Njets<=self.jetIndex) : return False
        return (chain.Jeteta[self.jetIndex]<self.jetEtaThreshold)
#####################################
class icfMuonPtVetoer(analysisStep) :
    """icfMuonPtVetoer"""

    def __init__(self,muonPtThreshold,muonIndex):
        self.muonPtThreshold=muonPtThreshold
        self.muonIndex=muonIndex
        
        self.moreName ="(pT["+str(self.muonIndex)+"]<"+str(self.muonPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=["Nmuon","Muonpt"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Nmuon<=self.muonIndex) : return True
        return (chain.Muonpt[self.muonIndex]<self.muonPtThreshold)
#####################################
class icfElecPtVetoer(analysisStep) :
    """icfElecPtVetoer"""

    def __init__(self,elecPtThreshold,elecIndex):
        self.elecPtThreshold=elecPtThreshold
        self.elecIndex=elecIndex
        
        self.moreName ="(pT["+str(self.elecIndex)+"]<"+str(self.elecPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=["Nelec","Elecpt"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Nelec<=self.elecIndex) : return True
        return (chain.Elecpt[self.elecIndex]<self.elecPtThreshold)
#####################################
class icfPhotPtVetoer(analysisStep) :
    """icfPhotPtVetoer"""

    def __init__(self,photPtThreshold,photIndex):
        self.photPtThreshold=photPtThreshold
        self.photIndex=photIndex
        
        self.moreName ="(pT["+str(self.photIndex)+"]<"+str(self.photPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=["Nphot","Photpt"]

    def select (self,chain,chainVars,extraVars) :
        if (chain.Nphot<=self.photIndex) : return True
        return (chain.Photpt[self.photIndex]<self.photPtThreshold)
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

        Jetpx =chain.Jetpx
        Jetpy =chain.Jetpy
        Jetpz =chain.Jetpz
        JetE  =chain.JetE
        Jetpt =chain.Jetpt
        Jeteta=chain.Jeteta
        JetFem=chain.JetFem

        nJets=chain.Njets
        for iJet in range(nJets) :
            #pt cut
            if (Jetpt[iJet]<self.jetPtThreshold) : continue
        
            #if pass pt cut, add to "other" category
            extraVars.otherJetIndices.append(iJet)
        
            #eta cut
            absEta=r.TMath.Abs(Jeteta[iJet])
            if (absEta>self.jetEtaMax) : continue

            #emf cut
            if (JetFem[iJet]>=0.9) : continue

            self.dummyP4.SetCoordinates(Jetpx[iJet],
                                        Jetpy[iJet],
                                        Jetpz[iJet],
                                        JetE[iJet])
            
            #extraVars.cleanJets.append(copy.deepcopy(self.dummyP4))
            extraVars.cleanJets.append(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.cleanJetIndices.append(iJet)
            extraVars.otherJetIndices.remove(iJet)
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
        Jetpx =chain.Jetpx
        Jetpy =chain.Jetpy
        Jetpz =chain.Jetpz
        JetE  =chain.JetE
        Jetpt =chain.Jetpt

        nJets=chain.Njets
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
class icfCleanJetPtHistogrammer(analysisStep) :
    """icfCleanJetPtHistogrammer"""

    def __init__(self) :
        self.neededBranches=[]

    def bookHistos(self) :
        self.ptAllHisto=    r.TH1D("ptAll",";p_{T} (GeV) of clean jets;events / bin",50,0.0,800.0)
        self.ptLeadingHisto=r.TH1D("ptLeading",";p_{T} (GeV) of leading clean jet;events / bin",50,0.0,800.0)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        ptleading=0.0
        for iJet in extraVars.cleanJetIndices :
            pt=chain.Jetpt[iJet]
            self.ptAllHisto.Fill(pt)
            if (pt>ptleading) :
                ptleading=pt
        self.ptLeadingHisto.Fill(ptleading)
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
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.diJetAlpha_Histo.Fill(   extraVars.diJetAlpha   )
        #self.diJetAlpha_ET_Histo.Fill(extraVars.diJetAlpha_Et)
        self.nJetAlphaT_Histo.Fill(   extraVars.nJetAlphaT   )
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
