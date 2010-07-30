#import copy
import math
import ROOT as r
from analysisStep import analysisStep
#import pdgLookup
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

    def uponAcceptance(self,eventVars,extraVars) :
        jetPtsAndIndices=[]
        nJets=eventVars["Njets"]
        for iJet in  range(nJets) :
            jetPtsAndIndices.append( (eventVars["Jetpt"][iJet],iJet) )
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

    def select (self,eventVars,extraVars) :
        extraVars.cleanJetIndices=[]
        extraVars.otherJetIndices=[]
        extraVars.icfCleanJets.clear()

        Jetpx =eventVars["Jetpx"]
        Jetpy =eventVars["Jetpy"]
        Jetpz =eventVars["Jetpz"]
        JetE  =eventVars["JetE"]
        Jetpt =eventVars["Jetpt"]
        Jeteta=eventVars["Jeteta"]
        JetFem=eventVars["JetFem"]
        
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
            #extraVars.cleanJets.append(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.icfCleanJets.push_back(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.cleanJetIndices.append(jetIndex)
            extraVars.otherJetIndices.remove(jetIndex)

        return True
#####################################
class icfJetFaker(analysisStep) :
    """icfJetFaker"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="( "+self.jetCollection+" "+self.jetSuffix+" )"

        self.dummyStdVector=r.vector(r.Math.LorentzVector(r.Math.PxPyPzE4D('double')))
        
        self.dummyP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)

    def uponAcceptance (self,eventVars,extraVars) :
        Jetpx =eventVars["Jetpx"]
        Jetpy =eventVars["Jetpy"]
        Jetpz =eventVars["Jetpz"]
        JetE  =eventVars["JetE"]

        eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]=self.dummyStdVector
        setattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix,[])
        
        p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

#        nJets=eventVars["Njets"]
#        for iJet in range(nJets) :
#            p4Vector.push_back*

#        for jetIndex in extraVars.jetIndicesSortedByPt :
#            #pt cut
#            if (Jetpt[jetIndex]<self.jetPtThreshold) : continue
#
#            #if pass pt cut, add to "other" category
#            extraVars.otherJetIndices.append(jetIndex)
#        
#            #eta cut
#            absEta=r.TMath.Abs(Jeteta[jetIndex])
#            if (absEta>self.jetEtaMax) : continue
#
#            #emf cut
#            if (JetFem[jetIndex]>=0.9) : continue
#
#            self.dummyP4.SetCoordinates(Jetpx[jetIndex],
#                                        Jetpy[jetIndex],
#                                        Jetpz[jetIndex],
#                                        JetE[jetIndex])
#            
#            #extraVars.cleanJets.append(copy.deepcopy(self.dummyP4))
#            #extraVars.cleanJets.append(self.dummyP4+self.zeroP4) #faster than copying
#            extraVars.icfCleanJets.push_back(self.dummyP4+self.zeroP4) #faster than copying
#            extraVars.cleanJetIndices.append(jetIndex)
#            extraVars.otherJetIndices.remove(jetIndex)

        return True
######################################
class icfNCleanJetHistogrammer(analysisStep) :
    """icfNCleanJetHistogrammer"""

    def bookHistos(self) :
        nBins=15
        title=";number of jets passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"
        self.nCleanJetsHisto=r.TH1D("nCleanJets",title,nBins,-0.5,nBins-0.5)
        
    def uponAcceptance (self,eventVars,extraVars) :
        self.nCleanJetsHisto.Fill( len(extraVars.cleanJetIndices) )
######################################
class icfNCleanJetEventFilter(analysisStep) :
    """icfNCleanJetEventFilter"""

    def __init__(self,nCleanJets):
        self.nCleanJets=nCleanJets
        self.moreName="(>="+str(self.nCleanJets)+")"
        
    def select (self,eventVars,extraVars) :
        return len(extraVars.cleanJetIndices)>=self.nCleanJets
######################################
class icfNOtherJetEventFilter(analysisStep) :
    """icfNOtherJetEventFilter"""

    def __init__(self,nOtherJets):
        self.nOtherJets=nOtherJets
        self.moreName="(<"+str(self.nOtherJets)+")"
        
    def select (self,eventVars,extraVars) :
        return len(extraVars.otherJetIndices)<self.nOtherJets
######################################
class icfOtherJetHistogrammer(analysisStep) :
    """icfOtherJetHistogrammer"""

    def __init__(self,singleJetPtThreshold):
        self.singleJetPtThreshold=singleJetPtThreshold

    def bookHistos(self) :
        nBins=15
        title=";n \"other\" jets with p_{T}>"+str(self.singleJetPtThreshold)+" GeV;events / bin"
        self.nOtherJetsHisto=r.TH1D("nOtherJetHt",title,nBins,-0.5,nBins-0.5)

        self.ptAllHistoOther=    r.TH1D("ptAllOther",";p_{T} (GeV) of \"other\" jets;events / bin",50,0.0,200.0)
        self.ptLeadingHistoOther=r.TH1D("ptLeadingOther",";p_{T} (GeV) of leading \"other\" jet;events / bin",50,0.0,200.0)

        #self.etaAllHisto=    r.TH1D("etaAllOther",";#eta of clean jets;events / bin",50,-5.0,5.0)
        #self.etaLeadingHisto=r.TH1D("etaLeadingOther",";#eta of leading clean jet;events / bin",50,-5.0,5.0)

        title=";H_{T} computed from \"other\" jets with p_{T}>"+str(self.singleJetPtThreshold)+" GeV;events / bin"
        self.otherJetHtHisto=r.TH1D("otherJetHt",title,50,0.0,200.0)

    def uponAcceptance (self,eventVars,extraVars) :
        extraVars.otherHt=0.0
        extraVars.nOtherJets=0

        Jetpt=eventVars["Jetpt"]
        leadingFilled=False
        for jetIndex in  extraVars.jetIndicesSortedByPt :
            if (jetIndex in extraVars.cleanJetIndices) : continue
            pt=Jetpt[jetIndex]
            if (pt<self.singleJetPtThreshold) : continue
            extraVars.otherHt+=pt
            extraVars.nOtherJets+=1

            self.ptAllHistoOther.Fill(pt)

            #eta=eventVars["Jeteta"][iJet]
            #self.etaAllHistoOther.Fill(eta)

            if (not leadingFilled) :
                self.ptLeadingHistoOther.Fill(pt)
                #self.etaLeadingHistoOther.Fill(eta)
                leadingFilled=True

        self.otherJetHtHisto.Fill(extraVars.otherHt)
        self.nOtherJetsHisto.Fill(extraVars.nOtherJets)
#####################################
class icfCleanJetPtSelector(analysisStep) :
    """icfCleanJetPtSelector"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.moreName ="(pt["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV)"

    def select (self,eventVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return False
        return (eventVars["Jetpt"][extraVars.cleanJetIndices[self.jetIndex]]>=self.jetPtThreshold)
#####################################
class icfCleanJetPtVetoer(analysisStep) :
    """icfCleanJetPtVetoer"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.moreName ="(pt["+str(self.jetIndex)+"]<"+str(self.jetPtThreshold)+" GeV)"

    def select (self,eventVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return True
        return (eventVars["Jetpt"][extraVars.cleanJetIndices[self.jetIndex]]<self.jetPtThreshold)
#####################################
class icfCleanJetEtaSelector(analysisStep) :
    """icfCleanJetEtaSelector"""

    def __init__(self,jetEtaThreshold,jetIndex):
        self.jetEtaThreshold=jetEtaThreshold
        self.jetIndex=jetIndex
        self.moreName ="(|eta["+str(self.jetIndex)+"]|<"+str(self.jetEtaThreshold)+")"

    def select (self,eventVars,extraVars) :
        if (len(extraVars.cleanJetIndices)<=self.jetIndex) : return False
        return (r.TMath.Abs(eventVars["Jeteta"][extraVars.cleanJetIndices[self.jetIndex]])<self.jetEtaThreshold)
#####################################
class icfCleanJetHtMhtProducer(analysisStep) :
    """icfCleanJetHtMhtProducer"""

    def __init__(self):
        self.mht=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def select (self,eventVars,extraVars) :
        self.mht.SetCoordinates(0.0,0.0,0.0,0.0)

        extraVars.Ht=0.0
        extraVars.HtEt=0.0

        for jet in extraVars.icfCleanJets :
            self.mht-=jet
            extraVars.Ht+=jet.pt()
            extraVars.HtEt+=jet.Et()

        setattr(extraVars,"Mht",self.mht)
        return True
#####################################
class icfMhtAllProducer(analysisStep) :
    """icfMhtAllProducer"""

    def __init__(self,jetPtThreshold):
        self.jetPtThreshold=jetPtThreshold
        
        self.moreName="(pt>="+str(self.jetPtThreshold)+" GeV"+")"

        self.mhtAll=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.dummyP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)

    def uponAcceptance (self,eventVars,extraVars) :
        Jetpx =eventVars["Jetpx"]
        Jetpy =eventVars["Jetpy"]
        Jetpz =eventVars["Jetpz"]
        JetE  =eventVars["JetE"]
        Jetpt =eventVars["Jetpt"]

        nJets=eventVars["Njets"]
        for iJet in range(nJets) :
            if (Jetpt[iJet]<self.jetPtThreshold) : continue

            self.dummyP4.SetCoordinates(Jetpx[iJet],
                                        Jetpy[iJet],
                                        Jetpz[iJet],
                                        JetE[iJet])
            self.mhtAll-=self.dummyP4
        
        setattr(extraVars,"MhtAll",self.mhtAll)
#####################################
class icfMhtRatioSelector(analysisStep) :
    """icfMhtRatioSelector"""

    def __init__(self,threshold):
        self.threshold=threshold
        
    def select (self,eventVars,extraVars) :
        return ( (extraVars.Mht.pt()/extraVars.MhtAll.pt())<self.threshold )
#####################################
class icfCleanJetHtMhtHistogrammer(analysisStep) :
    """icfCleanJetHtMhtHistogrammer"""

    def bookHistos(self):
        self.ht_Histo          =r.TH1D("ht"       ,";H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,1000.0)
        #self.ht_et_Histo       =r.TH1D("ht_et"    ,";H_{T} (GeV) from clean jet E_{T}'s;events / bin" ,50,0.0,1000.0)
        self.mht_Histo         =r.TH1D("mht"      ,";#slash{H}_{T} (GeV) from clean jets;events / bin",50,0.0, 500.0)
        self.m_Histo           =r.TH1D("m"        ,";mass (GeV) of system of clean jets;events / bin" ,50,0.0,1000.0)
        self.mHtOverHt_Histo   =r.TH1D("mHtOverHt",";MHT / H_{T} from clean jet p_{T}'s;events / bin" ,50,0.0,1.1)

        title=";H_{T} (GeV) from clean jets;#slash{H}_{T} (GeV) from clean jet p_{T}'s;events / bin"
        self.mhtHt_Histo=r.TH2D("mht_vs_ht",title,50,0.0,1000.0,50,0.0,1000.0)
        
    def uponAcceptance (self,eventVars,extraVars) :
        mht=extraVars.Mht.pt()
        self.mht_Histo.Fill(mht)
        self.ht_Histo.Fill(extraVars.Ht)
        #self.ht_et_Histo.Fill(extraVars.HtEt)
        self.m_Histo.Fill(extraVars.Mht.mass())
        self.mhtHt_Histo.Fill(extraVars.Ht,mht)

        value=-1.0
        if (extraVars.Ht>0.0) : value=mht/extraVars.Ht
        self.mHtOverHt_Histo.Fill(value)
#####################################
class icfCleanJetPtEtaHistogrammer(analysisStep) :
    """icfCleanJetPtEtaHistogrammer"""

    def bookHistos(self) :
        self.ptAllHisto=    r.TH1D("ptAll",";p_{T} (GeV) of clean jets;events / bin",50,0.0,800.0)
        self.ptLeadingHisto=r.TH1D("ptLeading",";p_{T} (GeV) of leading clean jet;events / bin",50,0.0,800.0)

        self.etaAllHisto=    r.TH1D("etaAll",";#eta of clean jets;events / bin",50,-5.0,5.0)
        self.etaLeadingHisto=r.TH1D("etaLeading",";#eta of leading clean jet;events / bin",50,-5.0,5.0)

    def uponAcceptance (self,eventVars,extraVars) :
        leadingFilled=False
        for iJet in extraVars.cleanJetIndices :
            pt=eventVars["Jetpt"][iJet]
            self.ptAllHisto.Fill(pt)

            eta=eventVars["Jeteta"][iJet]
            self.etaAllHisto.Fill(eta)
            if (not leadingFilled) :
                self.ptLeadingHisto.Fill(pt)
                self.etaLeadingHisto.Fill(eta)
                leadingFilled=True
#####################################
class icfCleanNJetAlphaProducer(analysisStep) :
    """icfCleanNJetAlphaProducer"""

    def uponAcceptance (self,eventVars,extraVars) :
        nJetDeltaHt=0.0
        nJetAlphaT=0.0

        #return if fewer than two clean jets
        if (len(extraVars.cleanJetIndices)<2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return

        #return if HT is tiny
        if (extraVars.Ht<=1.0e-2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return

        #compute deltaHT
        pTs=[]
        totalPt=0.0
        for jet in extraVars.icfCleanJets :
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
        mht=extraVars.Mht.pt()
        ht=extraVars.Ht
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
        
    def select (self,eventVars,extraVars) :
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
            
        for jet in extraVars.icfCleanJets :
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

    def bookHistos(self) :
        bins=100
        min=0.0
        max=2.0
        self.diJetAlpha_Histo   =r.TH1D("dijet alpha"   ,";di-jet #alpha (using p_{T});events / bin"   ,bins,min,max)
        #self.diJetAlpha_ET_Histo=r.TH1D("dijet alpha_ET",";di-jet #alpha (using E_{T});events / bin"   ,bins,min,max)
        self.nJetAlphaT_Histo   =r.TH1D("njet alphaT"   ,";N-jet #alpha_{T} (using p_{T});events / bin",bins,min,max)
        self.nJetDeltaHt_Histo  =r.TH1D("njet deltaHt"  ,";N-jet #Delta H_{T} (GeV);events / bin",50,0.0,500.0)
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

    def uponAcceptance (self,eventVars,extraVars) :
        self.diJetAlpha_Histo.Fill(   extraVars.diJetAlpha   )
        #self.diJetAlpha_ET_Histo.Fill(extraVars.diJetAlpha_Et)
        self.nJetAlphaT_Histo.Fill(   extraVars.nJetAlphaT   )
        #self.alpha2D_a_Histo.Fill(math.sqrt(extraVars.Ht**2 - extraVars.Mht.pt()**2),extraVars.Ht - extraVars.nJetDeltaHt)
        #self.alpha2D_b_Histo.Fill(extraVars.Ht - extraVars.Mht.pt(),extraVars.Ht - extraVars.nJetDeltaHt)
        self.nJetDeltaHt_Histo.Fill(extraVars.nJetDeltaHt)
        self.alpha2D_c_Histo.Fill(extraVars.Mht.pt()/extraVars.Ht,extraVars.nJetDeltaHt/extraVars.Ht)
#####################################
class icfDeltaPhiProducer(analysisStep) :
    """icfDeltaPhiProducer"""

    def select(self,eventVars,extraVars) :

        extraVars.deltaPhi01= -4.0
        extraVars.deltaR01  =-40.0
        extraVars.deltaEta01=-40.0
        extraVars.deltaPhiMhtJet=[]

        if (len(extraVars.cleanJetIndices)>=2) :
            jet0=extraVars.icfCleanJets[0]
            jet1=extraVars.icfCleanJets[1]
            extraVars.deltaPhi01=r.Math.VectorUtil.DeltaPhi(jet0,jet1)
            extraVars.deltaR01  =r.Math.VectorUtil.DeltaR(jet0,jet1)
            extraVars.deltaEta01=jet0.eta()-jet1.eta()

        for iJet in range(len(extraVars.icfCleanJets)) :
            deltaPhi=r.Math.VectorUtil.DeltaPhi(extraVars.Mht,extraVars.icfCleanJets[iJet])
            extraVars.deltaPhiMhtJet.append(deltaPhi)
                
        return True
#####################################
class icfDeltaPhiSelector(analysisStep) :
    """icfDeltaPhiSelector"""

    def __init__(self,minAbs,maxAbs) :
        self.minAbs=minAbs
        self.maxAbs=maxAbs
    
    def select(self,eventVars,extraVars) :
        value=r.TMath.Abs(extraVars.deltaPhi01)
        if (value<self.minAbs or value>self.maxAbs) : return False
        return True
#####################################
class icfMhtOverHtSelector(analysisStep) :
    """icfMhtOverHtSelector"""

    def __init__(self,min,max) :
        self.min=min
        self.max=max
    
    def select(self,eventVars,extraVars) :
        if (extraVars.Ht<1.0e-2) : return False
        value=extraVars.Mht.pt()/extraVars.Ht
        if (value<self.min or value>self.max) : return False
        return True
#####################################
class icfDeltaPhiHistogrammer(analysisStep) :
    """icfDeltaPhiHistogrammer"""

    def bookHistos(self) :
        bins=50
        min=0.0
        max=r.TMath.Pi()
        xTitle="#Delta#phi(jet 0 , jet 1)"
        self.deltaPhi01_Histo=r.TH1D("deltaPhi01",";"+xTitle+";events / bin",bins,min,max)
        self.deltaPhiMhtJetHisto=[]
        self.deltaPhiMhtJetMax=3
        for iJet in range(self.deltaPhiMhtJetMax) :
            xTitle="#Delta#phi(#slashH_{T} , jet "+str(iJet)+")"
            self.deltaPhiMhtJetHisto.append(r.TH1D("deltaPhiMhtJet"+str(iJet),";"+xTitle+";events / bin",bins,min,max))

        bins=20
        min= 0.0
        max=10.0
        title="deltaR01"
        #self.deltaR01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)

        bins=50
        min=-10.0
        max= 10.0
        title="deltaEta01"
        #self.deltaEta01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)
        
    def uponAcceptance (self,eventVars,extraVars) :
        self.deltaPhi01_Histo.Fill( math.fabs(extraVars.deltaPhi01) )
        #self.deltaR01_Histo.Fill(             extraVars.deltaR01    )
        #self.deltaEta01_Histo.Fill(           extraVars.deltaEta01  )
        
        for iJet in range(min(self.deltaPhiMhtJetMax,len(extraVars.deltaPhiMhtJet))) :
            self.deltaPhiMhtJetHisto[iJet].Fill(extraVars.deltaPhiMhtJet[iJet])
#####################################
class icfAnyJetPtSelector(analysisStep) :
    """icfAnyJetPtSelector"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.moreName ="(pT["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

    def select (self,eventVars,extraVars) :
        if (len(extraVars.jetPtsSortedByPt)<=self.jetIndex) : return False
        return (extraVars.jetPtsSortedByPt[self.jetIndex]>=self.jetPtThreshold)
#####################################
class icfAnyJetPtVetoer(analysisStep) :
    """icfAnyJetPtVetoer"""

    def __init__(self,jetPtThreshold,jetIndex):
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        self.moreName ="(pT["+str(self.jetIndex)+"]<"+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

    def select (self,eventVars,extraVars) :
        if (len(extraVars.jetPtsSortedByPt)<=self.jetIndex) : return True
        return (extraVars.jetPtsSortedByPt[self.jetIndex]<self.jetPtThreshold)
#####################################
class icfMuonVetoer(analysisStep) :
    """icfMuonVetoer"""

    def __init__(self,muonPtThreshold):
        self.muonPtThreshold=muonPtThreshold
        self.moreName ="(no muon with pT>"+str(self.muonPtThreshold)+" GeV passing ID)"

    def select (self,eventVars,extraVars) :
        anyGoodMuon=False

        nMuons=eventVars["Nmuon"]
        pt=eventVars["Muonpt"]
        eta=eventVars["Muoneta"]
        phi=eventVars["Muonphi"]
        ecalDeposit=eventVars["MuonECalIsoDeposit"]
        hcalDeposit=eventVars["MuonHCalIsoDeposit"]

        hcalIso=eventVars["MuonHCalIso"]
        ecalIso=eventVars["MuonECalIso"]
        trkIso=eventVars["MuonTrkIso"]

        trkHits=eventVars["MuonTrkValidHits"]
        d0=eventVars["MuonTrkD0"]
        chi2=eventVars["MuonCombChi2"]
        nDof=eventVars["MuonCombNdof"]
        
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

    def select (self,eventVars,extraVars) :
        anyGoodElec=False

        nElecs=eventVars["Nelec"]
        pt=eventVars["Elecpt"]
        eta=eventVars["Eleceta"]
        phi=eventVars["Elecphi"]
        d0=eventVars["ElecD0"]
        hcalIso=eventVars["ElecHCalIso"]
        ecalIso=eventVars["ElecECalIso"]
        trkIso=eventVars["ElecTrkIso"]
        tight=eventVars["ElecIdRobTight"]

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

    def select (self,eventVars,extraVars) :
        anyGoodPhot=False

        nPhots=eventVars["Nphot"]
        pt=eventVars["Photpt"]
        eta=eventVars["Photeta"]

        for iPhot in range(nPhots) :
            if (pt[iPhot]<self.photPtThreshold) : continue
            if (math.fabs(eta[iPhot])>5.0) : continue
            isTight=chain.GetLeaf("mTempTreePhotTightPhoton").GetValue(iPhot)
            if (isTight<0.5) : continue
            
            anyGoodPhot=True
            break

        return not anyGoodPhot
#####################################
class icfCleanJetFromGenProducer(analysisStep) :
    """icfCleanJetFromGenProducer"""

    def __init__(self,jetPtThreshold,jetEtaMax):
        self.jetPtThreshold=jetPtThreshold
        self.jetEtaMax=jetEtaMax

        self.moreName+="(pT>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+="; |eta|<="+str(self.jetEtaMax)
        self.moreName+=")"

        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.dummyP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)

    def select (self,eventVars,extraVars) :
        extraVars.cleanJetIndices=[]
        extraVars.otherJetIndices=[]
        extraVars.icfCleanJets.clear()

        GenJetpx =eventVars["GenJetpx"]
        GenJetpy =eventVars["GenJetpy"]
        GenJetpz =eventVars["GenJetpz"]
        GenJetE  =eventVars["GenJetE"]
        GenJetpt =eventVars["GenJetpt"]
        GenJeteta=eventVars["GenJeteta"]
        
        for jetIndex in extraVars.jetIndicesSortedByPt :
            #pt cut
            if (GenJetpt[jetIndex]<self.jetPtThreshold) : continue

            #if pass pt cut, add to "other" category
            extraVars.otherJetIndices.append(jetIndex)
        
            #eta cut
            absEta=r.TMath.Abs(GenJeteta[jetIndex])
            if (absEta>self.jetEtaMax) : continue

            self.dummyP4.SetCoordinates(GenJetpx[jetIndex],
                                        GenJetpy[jetIndex],
                                        GenJetpz[jetIndex],
                                        GenJetE[jetIndex])
            
            #extraVars.cleanJets.append(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.icfCleanJets.push_back(self.dummyP4+self.zeroP4) #faster than copying
            extraVars.cleanJetIndices.append(jetIndex)
            extraVars.otherJetIndices.remove(jetIndex)

        return True
#####################################
class icfGenPrinter(analysisStep) :
    """icfGenPrinter"""

    def __init__(self):
        self.oneP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.sumP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def uponAcceptance (self,eventVars,extraVars) :
        nGen=eventVars["genN"]
        self.sumP4.SetCoordinates(0.0,0.0,0.0,0.0)

        mothers=set(eventVars["genMother"][:nGen])
        #print "mothers: ",mothers
        print "-------------------------------------------------------------------------"
        print "run %#7d"%eventVars["run"],"  event %#10d"%eventVars["event"]," |"
        print "---------------------------------"
        print " i  st  mo         id            name        E       eta        pt    phi"
        print "-------------------------------------------------------------------------"
        for iGen in range(nGen) :
            self.oneP4.SetCoordinates(eventVars["genPx"][iGen],
                                      eventVars["genPy"][iGen],
                                      eventVars["genPz"][iGen],
                                      eventVars["genE"] [iGen])

            outString=""
            outString+="%#2d"%iGen
            outString+=" %#3d"%eventVars["genStatus"][iGen]
            outString+="  %#2d"%eventVars["genMother"][iGen]
            outString+=" %#10d"%eventVars["genid"][iGen]
            outString+="".rjust(16)
            #outString+=" "+pdgLookup.pdgid_to_name(eventVars["genid"][iGen]).rjust(15)
            outString+="  %#7.1f"%eventVars["genE"][iGen]
            outString+="  %#8.1f"%self.oneP4.eta()
            outString+="  %#8.1f"%self.oneP4.pt()
            outString+="  %#5.1f"%self.oneP4.phi()

            if (not (iGen in mothers)) :
                outString+="   non-mo"
                self.sumP4+=self.oneP4
                #outString2="non-mo P4 sum".ljust(37)
                #outString2+="  %#7.1f"%self.sumP4.E()
                #outString2+="  %#8.1f"%self.sumP4.eta()
                #outString2+="  %#8.1f"%self.sumP4.pt()
                #outString2+="  %#5.1f"%self.sumP4.phi()
                #print outString2

            print outString

        outString="non-mo P4 sum".ljust(37)
        outString+="  %#7.1f"%self.sumP4.E()
        outString+="  %#8.1f"%self.sumP4.eta()
        outString+="  %#8.1f"%self.sumP4.pt()
        outString+="  %#5.1f"%self.sumP4.phi()
        print outString
        print
#####################################
class icfGenP4Producer(analysisStep) :
    """icfGenP4Producer"""

    def __init__(self):
        self.oneP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.sumP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def uponAcceptance (self,eventVars,extraVars) :
        nGen=eventVars["genN"]
        self.sumP4.SetCoordinates(0.0,0.0,0.0,0.0)

        mothers=set(eventVars["genMother"][:nGen])

        for iGen in range(nGen) :
            if (not (iGen in mothers)) :
                self.oneP4.SetCoordinates(eventVars["genPx"][iGen],
                                          eventVars["genPy"][iGen],
                                          eventVars["genPz"][iGen],
                                          eventVars["genE"] [iGen])

                self.sumP4+=self.oneP4

        extraVars.genNonMotherP4Sum=(self.sumP4+self.zeroP4)
#####################################
class icfGenP4Histogrammer(analysisStep) :
    """icfGenP4Histogrammer"""

    def bookHistos(self) :
        self.ptHisto=r.TH1D("genNonMotherP4Sum",";genNonMotherP4Sum p_{T} (GeV);events / bin",50,0.0,200.0)

    def uponAcceptance (self,eventVars,extraVars) :
        self.ptHisto.Fill(extraVars.genNonMotherP4Sum.pt())
#####################################
