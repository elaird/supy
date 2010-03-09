import ROOT as r
from base import analysisStep
#####################################
class jetPtSelector(analysisStep) :
    """jetPtSelector"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetIndex):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        
        self.moreName ="("+self.jetCollection+"; "+self.jetSuffix+"; "
        self.moreName+="corr. pT["+str(self.jetIndex)+"]>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=[self.jetCollection+"CorrectedP4"+self.jetSuffix]

    def select (self,chain,chainVars,extraVars) :
        p4Vector=getattr(chainVars,self.jetCollection+"CorrectedP4"+self.jetSuffix)
        size=p4Vector.size()
        if (size<=self.jetIndex) : return False
        return (p4Vector[self.jetIndex].pt()>=self.jetPtThreshold)
#####################################
class jetPtVetoer(analysisStep) :
    """jetPtVetoer"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetIndex):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.jetPtThreshold=jetPtThreshold
        self.jetIndex=jetIndex
        
        self.moreName ="("+self.jetCollection+"; "+self.jetSuffix+"; "
        self.moreName+="corr. pT["+str(self.jetIndex)+"]< "+str(self.jetPtThreshold)+" GeV"
        self.moreName+=")"

        self.neededBranches=[self.jetCollection+"CorrectedP4"+self.jetSuffix]

    def select (self,chain,chainVars,extraVars) :
        p4Vector=getattr(chainVars,self.jetCollection+"CorrectedP4"+self.jetSuffix)
        size=p4Vector.size()
        if (size<=self.jetIndex) : return True
        return (p4Vector[self.jetIndex].pt()<self.jetPtThreshold)
#####################################
class cleanJetIndexProducer(analysisStep) :
    """cleanJetIndexProducer"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax):
        self.corrFactorThreshold=1.0e-2
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.jetPtThreshold=jetPtThreshold
        self.corrRatherThanUnCorr=corrRatherThanUnCorr
        self.jetEtaMax=jetEtaMax
        
        self.moreName="("+self.jetCollection+"; "+self.jetSuffix
        self.moreName+="; jetID; "

        self.moreName2=" "
        if (self.corrRatherThanUnCorr) :
            self.moreName2+="corr. "
        else :
            self.moreName2+="u.c. "            

        self.moreName2+="pT>="+str(self.jetPtThreshold)+" GeV"
        self.moreName2+="; |eta|<="+str(self.jetEtaMax)
        self.moreName2+=")"
        
        self.neededBranches=["CorrectedP4"]
        if (not self.corrRatherThanUnCorr) :
            self.neededBranches.append("CorrFactor")

        #self.neededBranches.append("JetIDloose")
        self.neededBranches.append("EmEnergyFraction")
        self.neededBranches.append("JetIDN90Hits")
        self.neededBranches.append("JetIDFHPD")
        #self.neededBranches.append("JetIDFRBX")
        #self.neededBranches.append("Eta2Moment")
        #self.neededBranches.append("Phi2Moment")
        for i in range(len(self.neededBranches)) :
            self.neededBranches[i]=self.jetCollection+self.neededBranches[i]+self.jetSuffix

    def step1 (self,chain,chainVars,extraVars) :
        setattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix,[])
        self.cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        setattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix,[])
        self.otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        self.p4Vector=getattr(chainVars,self.jetCollection+'CorrectedP4'+self.jetSuffix)
        self.size=self.p4Vector.size()

        if (not self.corrRatherThanUnCorr) :
            self.corrFactorVector=getattr(chainVars,self.jetCollection+'CorrFactor'+self.jetSuffix)
        
        self.emfVector=getattr(chainVars,self.jetCollection+'EmEnergyFraction'+self.jetSuffix)
        self.fHpdVector=getattr(chainVars,self.jetCollection+'JetIDFHPD'+self.jetSuffix)
        self.n90HitsVector=getattr(chainVars,self.jetCollection+'JetIDN90Hits'+self.jetSuffix)
        
    def jetLoop (self,chainVars) :
        for iJet in range(self.size) :
            #pt cut
            if (self.corrRatherThanUnCorr) :
                if (self.p4Vector[iJet].pt()<self.jetPtThreshold) : break #assumes sorted
            else :
                corrFactor=self.corrFactorVector[iJet]
                if (corrFactor<self.corrFactorThreshold) : continue
                if (self.p4Vector[iJet].pt()/corrFactor<self.jetPtThreshold) : continue
            
            #if pass pt cut, add to "other" category
            self.otherJetIndices.append(iJet)
            
            #eta cut
            absEta=r.TMath.Abs(self.p4Vector[iJet].eta())
            if (absEta>self.jetEtaMax) : continue
            
            #jet ID loose cut
            #jetIDLooseVector=getattr(chain,self.jetCollection+'JetIDloose'+self.jetSuffix)
            #if (not jetIDLooseVector[iJet]) : continue
            
            if (absEta<=2.6) :
                if (self.emfVector[iJet]<=0.01) : continue
            if (self.fHpdVector[iJet]>=0.98) : continue
            if (self.n90HitsVector[iJet]<2) : continue
            #if (getattr(chainVars,self.jetCollection+'JetIDFRBX'+self.jetSuffix)[iJet]>=0.98) : continue
            #if (getattr(chainVars,self.jetCollection+'Eta2Moment'+self.jetSuffix)[iJet]<0.0) : continue
            #if (getattr(chainVars,self.jetCollection+'Phi2Moment'+self.jetSuffix)[iJet]<0.0) : continue
            
            self.cleanJetIndices.append(iJet)
            self.otherJetIndices.remove(iJet)

    def select (self,chain,chainVars,extraVars) :
        self.step1(chain,chainVars,extraVars)
        self.jetLoop(chainVars)
        return True
######################################
class nCleanJetHistogrammer(analysisStep) :
    """nCleanJetHistogrammer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+")"

    def bookHistos(self) :
        nBins=15
        title=";number of jets passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"
        self.nCleanJetsHisto=r.TH1D(self.jetCollection+"nCleanJets"+self.jetSuffix,title,nBins,-0.5,nBins-0.5)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.nCleanJetsHisto.Fill( len(getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)) )
######################################
class nCleanJetEventFilter(analysisStep) :
    """nCleanJetEventFilter"""

    def __init__(self,jetCollection,jetSuffix,nCleanJets):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.nCleanJets=nCleanJets
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+">="+str(self.nCleanJets)+")"
        self.neededBranches=[]
        
    def select (self,chain,chainVars,extraVars) :
        return len(getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix))>=self.nCleanJets
######################################
class nOtherJetEventFilter(analysisStep) :
    """nOtherJetEventFilter"""

    def __init__(self,jetCollection,jetSuffix,nOtherJets):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.nOtherJets=nOtherJets
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+"<"+str(self.nOtherJets)+")"
        self.neededBranches=[]
        
    def select (self,chain,chainVars,extraVars) :
        return len(getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix))<self.nOtherJets
#####################################
class cleanJetHtMhtProducer(analysisStep) :
    """cleanJetHtMhtProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"
        self.neededBranches=[
            self.jetCollection+'CorrectedP4'+self.jetSuffix,
            self.jetCollection+'CorrFactor'+self.jetSuffix
            ]
        self.mht=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.mhtUnCorr=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def select (self,chain,chainVars,extraVars) :
        self.mht.SetCoordinates(0.0,0.0,0.0,0.0)
        self.mhtUnCorr.SetCoordinates(0.0,0.0,0.0,0.0)
        
        setattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix,self.mht)
        setattr(extraVars,self.jetCollection+"MhtUnCorr"+self.jetSuffix,self.mhtUnCorr)

        Ht=0.0
        HtUnCorr=0.0
        HtEt=0.0
        HtEtUnCorr=0.0

        p4Vector=getattr(chainVars,self.jetCollection+'CorrectedP4'+self.jetSuffix)
        corrFactorVector=getattr(chainVars,self.jetCollection+'CorrFactor'+self.jetSuffix)
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        
        for iJet in cleanJetIndices :
            jet=p4Vector[iJet]
            self.mht-=jet
            Ht+=jet.pt()
            HtEt+=jet.Et()

            #print "--"
            #print jet.pt()
            ujet=jet/corrFactorVector[iJet]
            #print jet.pt()
            self.mhtUnCorr-=ujet
            HtUnCorr+=ujet.pt()
            HtEtUnCorr+=ujet.Et()

        setattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix,Ht)
        setattr(extraVars,self.jetCollection+"HtUnCorr"+self.jetSuffix,HtUnCorr)
        setattr(extraVars,self.jetCollection+"HtEt"+self.jetSuffix,HtEt)
        setattr(extraVars,self.jetCollection+"HtEtUnCorr"+self.jetSuffix,HtEtUnCorr)

        return True
#####################################
class cleanJetHtMhtHistogrammer(analysisStep) :
    """cleanJetHtMhtHistogrammer"""

    def __init__(self,jetCollection,jetSuffix,corrRatherThanUnCorr):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.corrRatherThanUnCorr=corrRatherThanUnCorr
        self.corrString=""
        if (not self.corrRatherThanUnCorr) : self.corrString=" uncorrected"
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=self.corrString
        self.moreName+=")"

    def bookHistos(self):
        self.ht_Histo          =r.TH1D(self.jetCollection+"ht"   +self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,100.0)
        self.ht_et_Histo       =r.TH1D(self.jetCollection+"ht_et"+self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" H_{T} (GeV) from clean jet E_{T}'s;events / bin" ,50,0.0,100.0)
        self.mht_Histo         =r.TH1D(self.jetCollection+"mht"  +self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" #slash{H}_{T} (GeV) from clean jets;events / bin",50,0.0, 50.0)
        self.m_Histo           =r.TH1D(self.jetCollection+"m"    +self.jetSuffix+" "+self.corrString
                                 ,";"+self.corrString+" mass (GeV) of system of clean jets;events / bin" ,50,0.0,400.0)
        self.mHtOverHt_Histo   =r.TH1D(self.jetCollection+"mHtOverHt"   +self.jetSuffix+" "+self.corrString
                                 ,";"+self.corrString+" MHT / H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,1.1)

        title=";"+self.corrString+" H_{T} (GeV) from clean jets;"+self.corrString+" #slash{H}_{T} (GeV) from clean jet p_{T}'s;events / bin"
        self.mhtHt_Histo=r.TH2D(self.jetCollection+"mht_vs_ht"+self.jetSuffix+" "+self.corrString
                                ,title,50,0.0,100.0,50,0.0,100.0)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        mhtVar="Mht"
        htVar="Ht"
        htEtVar="HtEt"
        
        if (not self.corrRatherThanUnCorr) :
            mhtVar+="UnCorr"
            htVar+="UnCorr"
            htEtVar+="UnCorr"
            
        mht =getattr(extraVars,self.jetCollection+mhtVar +self.jetSuffix)
        ht  =getattr(extraVars,self.jetCollection+htVar  +self.jetSuffix)
        htet=getattr(extraVars,self.jetCollection+htEtVar+self.jetSuffix)

        self.mht_Histo.Fill(mht.pt())
        self.ht_Histo.Fill(ht)
        self.ht_et_Histo.Fill(htet)
        self.m_Histo.Fill(mht.mass())
        self.mhtHt_Histo.Fill(ht,mht.pt())

        value=-1.0
        if (ht>0.0) : value=mht.pt()/ht
        self.mHtOverHt_Histo.Fill(value)
#####################################
class cleanJetPtHistogrammer(analysisStep) :
    """cleanJetPtHistogrammer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"
        self.neededBranches=[
            self.jetCollection+'CorrectedP4'+self.jetSuffix,
            self.jetCollection+'CorrFactor'+self.jetSuffix
            ]

    def bookHistos(self) :
        self.ptAllHisto=          r.TH1D(self.jetCollection+" ptAll "          +self.jetSuffix
                                         ,";p_{T} (GeV) of clean jets;events / bin"                   ,50,0.0,50.0)
        self.ptUnCorrAllHisto=    r.TH1D(self.jetCollection+" ptUnCorrAll "    +self.jetSuffix
                                         ,";uncorrected p_{T} (GeV) of clean jets;events / bin"       ,50,0.0,50.0)
        self.ptLeadingHisto=      r.TH1D(self.jetCollection+" ptLeading "      +self.jetSuffix
                                         ,";p_{T} (GeV) of leading clean jet;events / bin"            ,50,0.0,50.0)
        self.ptUnCorrLeadingHisto=r.TH1D(self.jetCollection+" ptUnCorrLeading "+self.jetSuffix
                                         ,";uncorrected p_{T} (GeV) of leading clean jet;events / bin",50,0.0,50.0)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        ptleading=0.0
        ptuncorrleading=0.0
        p4Vector=getattr(chainVars,self.jetCollection+'CorrectedP4'+self.jetSuffix)
        corrFactorVector=getattr(chainVars,self.jetCollection+'CorrFactor'+self.jetSuffix)
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        for iJet in cleanJetIndices :
            p4=p4Vector[iJet]
            pt=p4.pt()
            pt_uc=pt/corrFactorVector[iJet]

            self.ptAllHisto.Fill(pt)
            self.ptUnCorrAllHisto.Fill(pt_uc)

            if (pt>ptleading) :
                ptleading=pt
            if (pt_uc>ptuncorrleading) :
                ptuncorrleading=pt_uc

        self.ptLeadingHisto.Fill(ptleading)
        self.ptUnCorrLeadingHisto.Fill(ptuncorrleading)
#####################################
class cleanNJetAlphaProducer(analysisStep) :
    """cleanNJetAlphaProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"
        self.neededBranches=[self.jetCollection+"CorrectedP4"+self.jetSuffix]

    def select (self,chain,chainVars,extraVars) :
        nJetDeltaHt=0.0
        nJetAlphaT=0.0

        #return if fewer than two clean jets
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        if (len(cleanJetIndices)<2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return True

        #return if HT is tiny
        ht=getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        if (ht<=1.0e-2) :
            self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
            return True
        
        pTs=[]
        totalPt=0.0
        p4Vector=getattr(chain,self.jetCollection+"CorrectedP4"+self.jetSuffix)

        for iJet in cleanJetIndices :
            jet=p4Vector[iJet]
            pt=jet.pt()
            pTs.append(pt)
            totalPt+=pt

        nJets=len(cleanJetIndices)
        nCombinations=2**nJets
        diffs=[]
        for iCombination in range(nCombinations) :
            pseudoJetPt=0.0
            for iJet in range(nJets) :
                if (iCombination&(1<<iJet)) :
                    pseudoJetPt+=pTs[iJet]
            diffs.append(r.TMath.Abs(totalPt-2.0*pseudoJetPt))

        nJetDeltaHt=min(diffs)
        mht=getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix)        
        nJetAlphaT=0.5*(1.0-nJetDeltaHt/ht)/r.TMath.sqrt(1.0-(mht.pt()/ht)**2)

        self.setExtraVars(extraVars,nJetDeltaHt,nJetAlphaT)
        return True

    def setExtraVars(self,extraVars,nJetDeltaHt,nJetAlphaT) :
        setattr(extraVars,self.jetCollection+"nJetDeltaHt"+self.jetSuffix,nJetDeltaHt)
        setattr(extraVars,self.jetCollection+"nJetAlphaT"+self.jetSuffix,nJetAlphaT)
#####################################
class cleanDiJetAlphaProducer(analysisStep) :
    """cleanDiJetAlphaProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"
        self.lvSum=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.neededBranches=[self.jetCollection+"CorrectedP4"+self.jetSuffix]
        
    def select (self,chain,chainVars,extraVars) :
        self.lvSum.SetCoordinates(0.0,0.0,0.0,0.0)

        diJetM       =0.0
        diJetMinPt   =1.0e6
        diJetMinEt   =1.0e6
        diJetAlpha   =0.0
        diJetAlpha_Et=0.0

        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        #return if not dijet
        if (len(cleanJetIndices)!=2) :
            self.setExtraVars(extraVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
            return True
            
        p4Vector=getattr(chainVars,self.jetCollection+"CorrectedP4"+self.jetSuffix)
        for iJet in cleanJetIndices :
            jet=p4Vector[iJet]
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
            setattr(extraVars,self.jetCollection+"diJetM"       +self.jetSuffix,diJetM)
            setattr(extraVars,self.jetCollection+"diJetMinPt"   +self.jetSuffix,diJetMinPt)
            setattr(extraVars,self.jetCollection+"diJetMinEt"   +self.jetSuffix,diJetMinEt)
            setattr(extraVars,self.jetCollection+"diJetAlpha"   +self.jetSuffix,diJetAlpha)
            setattr(extraVars,self.jetCollection+"diJetAlpha_Et"+self.jetSuffix,diJetAlpha_Et)
#####################################
class alphaHistogrammer(analysisStep) :
    """alphaHistogrammer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"
        
    def bookHistos(self) :
        bins=100
        min=0.0
        max=2.0
        self.diJetAlpha_Histo   =r.TH1D(self.jetCollection+"dijet alpha"   +self.jetSuffix,";di-jet #alpha (using p_{T});events / bin"   ,bins,min,max)
        self.diJetAlpha_ET_Histo=r.TH1D(self.jetCollection+"dijet alpha_ET"+self.jetSuffix,";di-jet #alpha (using E_{T});events / bin"   ,bins,min,max)
        self.nJetAlphaT_Histo   =r.TH1D(self.jetCollection+"njet alphaT"   +self.jetSuffix,";N-jet #alpha_{T} (using p_{T});events / bin",bins,min,max)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.diJetAlpha_Histo.Fill(   getattr(extraVars,self.jetCollection+"diJetAlpha"   +self.jetSuffix))
        self.diJetAlpha_ET_Histo.Fill(getattr(extraVars,self.jetCollection+"diJetAlpha_Et"+self.jetSuffix))
        self.nJetAlphaT_Histo.Fill(   getattr(extraVars,self.jetCollection+"nJetAlphaT"   +self.jetSuffix))
#####################################
class metHistogrammer(analysisStep) :
    """metHistogrammer"""

    def __init__(self,metCollection,tag) :
        self.tag=tag
        self.metCollection=metCollection
        self.neededBranches=[self.metCollection]
        
    def bookHistos(self) :
        bins=40
        min=0.0
        max=20.0
        self.caloMetNoHf_Histo=r.TH1D(self.metCollection+" "+self.tag,";"+self.metCollection+" p_{T} (GeV);events / bin",bins,min,max)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.caloMetNoHf_Histo.Fill(   getattr(chainVars,self.metCollection).pt() )
#####################################
class deltaPhiProducer(analysisStep) :
    """deltaPhiProducer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.neededBranches=[self.jetCollection+'CorrectedP4'+self.jetSuffix]
    
    def select(self,chain,chainVars,extraVars) :

        setattr(extraVars,self.jetCollection+"deltaPhi01"+self.jetSuffix, -4.0)
        setattr(extraVars,self.jetCollection+"deltaR01"  +self.jetSuffix,-40.0)
        setattr(extraVars,self.jetCollection+"deltaEta01"+self.jetSuffix,-40.0)

        p4Vector=getattr(chainVars,self.jetCollection+'CorrectedP4'+self.jetSuffix)
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        if (len(cleanJetIndices)>=2) :
            jet0=p4Vector[cleanJetIndices[0]]
            jet1=p4Vector[cleanJetIndices[1]]
            setattr(extraVars,self.jetCollection+"deltaPhi01"+self.jetSuffix,r.Math.VectorUtil.DeltaPhi(jet0,jet1))
            setattr(extraVars,self.jetCollection+"deltaR01"  +self.jetSuffix,r.Math.VectorUtil.DeltaR(jet0,jet1))
            setattr(extraVars,self.jetCollection+"deltaEta01"+self.jetSuffix,jet0.eta()-jet1.eta())
        return True
#####################################
class deltaPhiSelector(analysisStep) :
    """deltaPhiSelector"""

    def __init__(self,jetCollection,jetSuffix,minAbs,maxAbs) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.minAbs=minAbs
        self.maxAbs=maxAbs
    
    def select(self,chain,chainVars,extraVars) :
        value=getattr(extraVars,self.jetCollection+"deltaPhi01"+self.jetSuffix)
        value=r.TMath.Abs(value)
        if (value<self.minAbs or value>self.maxAbs) : return False
        return True
#####################################
class mHtOverHtSelector(analysisStep) :
    """mHtOverHtSelector"""

    def __init__(self,jetCollection,jetSuffix,min,max) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.min=min
        self.max=max
    
    def select(self,chain,chainVars,extraVars) :
        mht=getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix).pt()
        ht=getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        if (ht<1.0e-2) : return False
        value=mht/ht
        if (value<self.min or value>self.max) : return False
        return True
#####################################
class deltaPhiHistogrammer(analysisStep) :
    """deltaPhiHistogrammer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix

    def bookHistos(self) :
        bins=50
        min=-4.0
        max= 4.0
        title=self.jetCollection+" deltaPhi01 "+self.jetSuffix
        self.deltaPhi01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)

        bins=20
        min= 0.0
        max=10.0
        title=self.jetCollection+" deltaR01 "+self.jetSuffix
        self.deltaR01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)

        bins=50
        min=-10.0
        max= 10.0
        title=self.jetCollection+" deltaEta01 "+self.jetSuffix
        self.deltaEta01_Histo=r.TH1D(title,";"+title+";events / bin",bins,min,max)
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.deltaPhi01_Histo.Fill(getattr(extraVars,self.jetCollection+"deltaPhi01"+self.jetSuffix))
        self.deltaR01_Histo.Fill(getattr(extraVars,self.jetCollection+"deltaR01"+self.jetSuffix))
        self.deltaEta01_Histo.Fill(getattr(extraVars,self.jetCollection+"deltaEta01"+self.jetSuffix))
#####################################
