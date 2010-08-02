import ROOT as r
from analysisStep import analysisStep
#####################################
class jetPtSelector(analysisStep) :
    """jetPtSelector"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetIndex):
        self.jetPtThreshold = jetPtThreshold
        self.jetIndex = jetIndex
        self.jetP4s = jetCollection+"CorrectedP4"+jetSuffix
        
        self.moreName = "(%s; %s; corr. pT[%d]>=%.1f GeV)" % (jetCollection, jetSuffix, jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.jetP4s]
        if p4s.size() <= self.jetIndex : return False
        return self.jetPtThreshold <= p4s.at(self.jetIndex).pt()
#####################################
class jetPtVetoer(analysisStep) :
    """jetPtVetoer"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetIndex):
        self.jetPtThreshold = jetPtThreshold
        self.jetIndex = jetIndex
        self.jetP4s = jetCollection+"CorrectedP4"+jetSuffix
        
        self.moreName = "(%s; %s; corr. pT[%d]<%.1f GeV)" % (jetCollection, jetSuffix, jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.jetP4s]
        if p4s.size() <= self.jetIndex : return True
        return p4s.at(self.jetIndex).pt() < self.jetPtThreshold
#####################################
class leadingUnCorrJetPtSelector(analysisStep) :
    """leadingUnCorrJetPtSelector"""

    def __init__(self,jetCollectionsAndSuffixes,jetPtThreshold):
        self.jetCollectionsAndSuffixes = jetCollectionsAndSuffixes
        self.jetPtThreshold = jetPtThreshold

        self.moreName = "("+''.join(["%s%s;" % cS for cS in self.jetCollectionsAndSuffixes])
        self.moreName2 = "corr. pT[leading uncorr. jet]>=%.1f GeV" % self.jetPtThreshold 

    def select (self,eventVars) :
        # Corrected pt of leading jet (by uncorrected pt) >= threshold
        for cS in self.jetCollectionsAndSuffixes :
            p4s = eventVars["%sCorrectedP4%s" % cS]
            corr = eventVars["%sCorrFactor%s" % cS]
            size = p4s.size()
            if not size : continue
            maxUncorrPt,index = max( [ (p4s.at(i).pt()/corr.at(i),i) for i in range(size) ] )
            if self.jetPtThreshold <= p4s.at(index).pt() :
                return True
        return False
#####################################
class cleanJetEmfFilter(analysisStep) :
    """cleanJetEmfFilter"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetEmfMax):
        self.indicesName = "%sIndices%s" % jetCollection,jetSuffix
        self.p4sName = "%sCorrectedP4%s"         % jetCollection,jetSuffix
        self.emfName = "%sEmEnergyFraction%s"    % jetCollection,jetSuffix

        self.jetPtThreshold = jetPtThreshold
        self.jetEmfMax = jetEmfMax
        
        self.moreName = "(%s; %s" % self.jetCollection, self.jetSuffix
        self.moreName2 = " corr. pT>=%.1f GeV; EMF<=%.1f)" % jetPtThreshold,self.jetEmfMax

    def select (self,eventVars) :
        p4s = eventVars[self.p4sName]
        emf = eventVars[self.emfName]

        for index in eventVars[self.indicesName]["clean"] :
            if p4s.at(index).pt() <= self.jetPtThreshold : #assumes sorted
                return True
            if emf.at(index) > self.jetEmfMax :
                return False
        return True
######################################
class nCleanJetHistogrammer(analysisStep) :
    """nCleanJetHistogrammer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.indicesName = "%sIndices%s" % jetCollection,jetSuffix
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+")"
        
    def uponAcceptance (self,eventVars) :
        self.book(eventVars).fill(len(eventVars[self.indicesName]["clean"]),
                                  self.indicesName+"clean", 15,-0.5,14.5,
                                  title=";number of jets passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin")
######################################
class nCleanJetEventFilter(analysisStep) :
    """nCleanJetEventFilter"""

    def __init__(self,jetCollection,jetSuffix,nCleanJets):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.nCleanJets=nCleanJets
        self.indicesName = "%sIndices%s" % (jetCollection,jetSuffix)
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+">="+str(self.nCleanJets)+")"
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["clean"]) >= self.nCleanJets
######################################
class nOtherJetEventFilter(analysisStep) :
    """nOtherJetEventFilter"""

    def __init__(self,jetCollection,jetSuffix,nOtherJets):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.nOtherJets=nOtherJets
        self.indicesName = "%sIndices%s" % (jetCollection,jetSuffix)
        self.moreName="("+self.jetCollection+" "+self.jetSuffix+"<"+str(self.nOtherJets)+")"
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["other"]) < self.nOtherJets
#####################################
class cleanJetHtMhtProducer(analysisStep) :
    """cleanJetHtMhtProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.cs = (jetCollection,jetSuffix)
        self.indicesName = "%sIndices%s" % self.cs

        self.moreName="(%s; %s)"% self.cs
        self.helper=r.htMhtHelper()
        self.cleanJetIndices=r.std.vector('int')()
        self.cleanJetIndices.reserve(256)
        
    def select (self,eventVars) :
        p4Vector=eventVars["%sCorrectedP4%s"%self.cs]
        cleanJetIndices = eventVars[self.indicesName]["clean"]

        self.cleanJetIndices.clear()
        for index in cleanJetIndices :
            self.cleanJetIndices.push_back(index)

        self.helper.Loop(p4Vector,self.cleanJetIndices)
        eventVars["crock"]["%sMht%s" %self.cs]=self.helper.GetMht()
        eventVars["crock"]["%sHtEt%s"%self.cs]=self.helper.GetHtEt()
        return True
#####################################
class cleanJetHtMhtHistogrammer(analysisStep) :
    """cleanJetHtMhtHistogrammer"""

    def __init__(self,jetCollection,jetSuffix,corrRatherThanUnCorr=True):
        self.histoMax=1.0e3
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.corrRatherThanUnCorr=corrRatherThanUnCorr
        self.corrString = "" if corrRatherThanUnCorr else " uncorrected"
        self.htVar = "%sSumPt%s%s"%(self.jetCollection,"" if corrRatherThanUnCorr else "UnCorr", self.jetSuffix)

        self.moreName="(%s; %s%s)" % (jetCollection,jetSuffix,self.corrString)

    def bookHistos(self):
        self.ht_Histo          =r.TH1D(self.jetCollection+"ht"   +self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,self.histoMax)
        self.ht_et_Histo       =r.TH1D(self.jetCollection+"ht_et"+self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" H_{T} (GeV) from clean jet E_{T}'s;events / bin" ,50,0.0,self.histoMax)
        self.mht_Histo         =r.TH1D(self.jetCollection+"mht"  +self.jetSuffix+" "+self.corrString
                                       ,";"+self.corrString+" #slash{H}_{T} (GeV) from clean jets;events / bin",50,0.0,self.histoMax)
        self.m_Histo           =r.TH1D(self.jetCollection+"m"    +self.jetSuffix+" "+self.corrString
                                 ,";"+self.corrString+" mass (GeV) of system of clean jets;events / bin" ,50,0.0,self.histoMax)
        self.mHtOverHt_Histo   =r.TH1D(self.jetCollection+"mHtOverHt"   +self.jetSuffix+" "+self.corrString
                                 ,";"+self.corrString+" MHT / H_{T} (GeV) from clean jet p_{T}'s;events / bin" ,50,0.0,1.1)

        title=";"+self.corrString+" H_{T} (GeV) from clean jets;"+self.corrString+" #slash{H}_{T} (GeV) from clean jet p_{T}'s;events / bin"
        self.mhtHt_Histo=r.TH2D(self.jetCollection+"mht_vs_ht"+self.jetSuffix+" "+self.corrString
                                ,title,50,0.0,self.histoMax,50,0.0,self.histoMax)
        
    def uponAcceptance (self,eventVars) :
        mhtVar="Mht"
        htEtVar="HtEt"
        
        if (not self.corrRatherThanUnCorr) :
            mhtVar+="UnCorr"
            htEtVar+="UnCorr"
            
        mht =eventVars["crock"][self.jetCollection+mhtVar +self.jetSuffix]
        ht = eventVars[self.htVar]
        htet=eventVars["crock"][self.jetCollection+htEtVar+self.jetSuffix]

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
        self.histoMax=500.0
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="(%s; %s)" % (jetCollection,jetSuffix)
        self.indicesName = "%sIndices%s" % (jetCollection,jetSuffix)
        self.p4sName = "%sCorrectedP4%s" % (jetCollection,jetSuffix)
        self.cFactorName = "%sCorrFactor%s" % (jetCollection,jetSuffix)

    def uponAcceptance (self,eventVars) :
        ptleading=0.0
        p4Vector=eventVars[self.p4sName]
        cleanJetIndices = eventVars[self.indicesName]["clean"]

        for iJet in cleanJetIndices :
            p4=p4Vector.at(iJet)
            pt=p4.pt()
            self.book(eventVars).fill(pt, self.jetCollection+" ptAll "+self.jetSuffix, 50,0.0,self.histoMax, title=";p_{T} (GeV) of clean jets;events / bin")

            if iJet==0 :#assumes sorted
                self.book(eventVars).fill(ptleading, self.jetCollection+" ptLeading "+self.jetSuffix, 50,0.0,self.histoMax, title=";p_{T} (GeV) of leading clean jet;events / bin")
#####################################
class cleanNJetAlphaProducer(analysisStep) :
    """cleanNJetAlphaProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix
        self.indicesName = "%sIndices%s" % (jetCollection,jetSuffix)
        self.moreName = "(%s; %s)" % (jetCollection,jetSuffix)

        self.helper=r.alphaHelper()
        self.cleanJetIndices = r.std.vector('int')()
        self.cleanJetIndices.reserve(256)

    def select (self,eventVars) :
        nJetDeltaHt=0.0
        nJetAlphaT=0.0

        #return if fewer than two clean jets
        cleanJetIndices = eventVars[self.indicesName]["clean"]
        if (len(cleanJetIndices)<2) :
            self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
            return True

        #return if HT is tiny
        ht = eventVars[ self.jetCollection+"SumPt"+self.jetSuffix ]
        if (ht<=1.0e-2) :
            self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
            return True

        p4Vector = eventVars[self.jetCollection+"CorrectedP4"+self.jetSuffix]

        self.cleanJetIndices.clear()
        for index in cleanJetIndices :
            self.cleanJetIndices.push_back(index)

        self.helper.go(p4Vector,self.cleanJetIndices)
        nJetDeltaHt=self.helper.GetMinDiff()
        mht=eventVars["crock"][self.jetCollection+"Mht"+self.jetSuffix]
        nJetAlphaT=0.5*(1.0-nJetDeltaHt/ht)/r.TMath.sqrt(1.0-(mht.pt()/ht)**2)

        self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
        return True

    def setExtraVars(self,eventVars,nJetDeltaHt,nJetAlphaT) :
        eventVars["crock"][self.jetCollection+"nJetDeltaHt"+self.jetSuffix]=nJetDeltaHt
        eventVars["crock"][self.jetCollection+"nJetAlphaT" +self.jetSuffix]=nJetAlphaT
        print "hi"
#####################################
class cleanDiJetAlphaProducer(analysisStep) :
    """cleanDiJetAlphaProducer"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix
        self.indicesName = "%sIndices%s" % (jetCollection,jetSuffix)
        self.moreName = "(%s; %s;)" % (jetCollection,jetSuffix)
        self.lvSum=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def select (self,eventVars) :
        self.lvSum.SetCoordinates(0.0,0.0,0.0,0.0)

        diJetM       =0.0
        diJetMinPt   =1.0e6
        diJetMinEt   =1.0e6
        diJetAlpha   =0.0
        diJetAlpha_Et=0.0

        cleanJetIndices = eventVars[self.indicesName]["clean"]
        #return if not dijet
        if (len(cleanJetIndices)!=2) :
            self.setExtraVars(eventVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
            return True
            
        p4Vector=eventVars[self.jetCollection+"CorrectedP4"+self.jetSuffix]
        for iJet in cleanJetIndices :
            jet=p4Vector.at(iJet)
            pt=jet.pt()
            Et=jet.Et()

            if (pt<diJetMinPt) : diJetMinPt=pt
            if (Et<diJetMinEt) : diJetMinEt=Et

            self.lvSum+=jet

        diJetM=self.lvSum.M()
        
        if (diJetM>0.0) :
            diJetAlpha   =diJetMinPt/diJetM
            diJetAlpha_Et=diJetMinEt/diJetM

        self.setExtraVars(eventVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
        return True

    def setExtraVars(self,eventVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et) :
            eventVars["crock"][self.jetCollection+"diJetM"       +self.jetSuffix]=diJetM
            eventVars["crock"][self.jetCollection+"diJetMinPt"   +self.jetSuffix]=diJetMinPt
            eventVars["crock"][self.jetCollection+"diJetMinEt"   +self.jetSuffix]=diJetMinEt
            eventVars["crock"][self.jetCollection+"diJetAlpha"   +self.jetSuffix]=diJetAlpha
            eventVars["crock"][self.jetCollection+"diJetAlpha_Et"+self.jetSuffix]=diJetAlpha_Et
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
        #self.diJetAlpha_ET_Histo=r.TH1D(self.jetCollection+"dijet alpha_ET"+self.jetSuffix,";di-jet #alpha (using E_{T});events / bin"   ,bins,min,max)
        self.nJetAlphaT_Histo   =r.TH1D(self.jetCollection+"njet alphaT"   +self.jetSuffix,";N-jet #alpha_{T} (using p_{T});events / bin",bins,min,max)
        self.nJetDeltaHt_Histo  =r.TH1D(self.jetCollection+"njet deltaHt"  +self.jetSuffix,";N-jet #Delta H_{T} (GeV);events / bin",50,0.0,500.0)
        self.alpha2D_c_Histo=r.TH2D("deltaHtOverHt vs mHtOverHt",
                                    ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin",
                                    30,0.0,1.0,
                                    30,0.0,0.7)
        
    def uponAcceptance (self,eventVars) :
        self.diJetAlpha_Histo.Fill(   eventVars["crock"][self.jetCollection+"diJetAlpha"+self.jetSuffix])
        #self.diJetAlpha_ET_Histo.Fill(eventVars["crock"][self.jetCollection+"diJetAlpha_Et"+self.jetSuffix])
        self.nJetAlphaT_Histo.Fill(   eventVars["crock"][self.jetCollection+"nJetAlphaT"   +self.jetSuffix])

        mht=eventVars["crock"][self.jetCollection+"Mht"+self.jetSuffix].pt()
        ht = eventVars[self.jetCollection+"SumPt"+self.jetSuffix]
        deltaHt=eventVars["crock"][self.jetCollection+"nJetDeltaHt"+self.jetSuffix]
        self.nJetDeltaHt_Histo.Fill(deltaHt)
        self.alpha2D_c_Histo.Fill(mht/ht,deltaHt/ht)
#####################################
class metHistogrammer(analysisStep) :
    """metHistogrammer"""

    def __init__(self,metCollection,tag) :
        self.tag=tag
        self.metCollection=metCollection
        
    def bookHistos(self) :
        bins=80
        min=0.0
        max=80.0
        self.caloMetNoHf_Histo=r.TH1D(self.metCollection+" "+self.tag,";"+self.metCollection+" p_{T} (GeV);events / bin",bins,min,max)
        
    def uponAcceptance (self,eventVars) :
        self.caloMetNoHf_Histo.Fill(   eventVars[self.metCollection].pt() )
#####################################
class deltaPhiProducer(analysisStep) :
    """deltaPhiProducer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix
        self.indicesName = "%sIndices%s" %(jetCollection,jetSuffix)
    
    def select(self,eventVars) :

        eventVars["crock"][self.jetCollection+"deltaPhi01"+self.jetSuffix]= -4.0
        eventVars["crock"][self.jetCollection+"deltaR01"  +self.jetSuffix]=-40.0
        eventVars["crock"][self.jetCollection+"deltaEta01"+self.jetSuffix]=-40.0

        p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        cleanJetIndices = eventVars[self.indicesName]["clean"]

        if len(cleanJetIndices)>=2 :
            jet0=p4Vector[cleanJetIndices[0]]
            jet1=p4Vector[cleanJetIndices[1]]
            eventVars["crock"][self.jetCollection+"deltaPhi01"+self.jetSuffix]=r.Math.VectorUtil.DeltaPhi(jet0,jet1)
            eventVars["crock"][self.jetCollection+"deltaR01"  +self.jetSuffix]=r.Math.VectorUtil.DeltaR(jet0,jet1)
            eventVars["crock"][self.jetCollection+"deltaEta01"+self.jetSuffix]=jet0.eta()-jet1.eta()
        return True
#####################################
class deltaPhiSelector(analysisStep) :
    """deltaPhiSelector"""

    def __init__(self,jetCollection,jetSuffix,minAbs,maxAbs) :
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix
        self.minAbs = minAbs
        self.maxAbs = maxAbs
    
    def select(self,eventVars) :
        value = abs( eventVars["crock"][self.jetCollection+"deltaPhi01"+self.jetSuffix] )
        if (value<self.minAbs or value>self.maxAbs) : return False
        return True
#####################################
class mHtOverHtSelector(analysisStep) :
    """mHtOverHtSelector"""

    def __init__(self,jetCollection,jetSuffix,min,max) :
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix
        self.min = min
        self.max = max
    
    def select(self,eventVars) :
        mht = eventVars["crock"][self.jetCollection+"Mht"+self.jetSuffix].pt()
        ht = eventVars[self.jetCollection+"SumPt"+self.jetSuffix]
        if (ht<1.0e-2) : return False
        value = mht/ht
        if (value<self.min or value>self.max) : return False
        return True
#####################################
class deltaPhiHistogrammer(analysisStep) :
    """deltaPhiHistogrammer"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection = jetCollection
        self.jetSuffix = jetSuffix

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
        
    def uponAcceptance (self,eventVars) :
        self.deltaPhi01_Histo.Fill(eventVars["crock"][self.jetCollection+"deltaPhi01"+self.jetSuffix])
        self.deltaR01_Histo.Fill(  eventVars["crock"][self.jetCollection+"deltaR01"+self.jetSuffix])
        self.deltaEta01_Histo.Fill(eventVars["crock"][self.jetCollection+"deltaEta01"+self.jetSuffix])
#####################################
