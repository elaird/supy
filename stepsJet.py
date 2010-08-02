import ROOT as r
from analysisStep import analysisStep
#####################################
class jetPtSelector(analysisStep) :
    """jetPtSelector"""

    def __init__(self,collection,suffix,jetPtThreshold,jetIndex):
        self.jetIndex = jetIndex
        self.jetPtThreshold = jetPtThreshold
        self.p4sName = "%sCorrectedP4%s" % (collection,suffix)
        
        self.moreName = "(%s; %s; corr. pT[%d]>=%.1f GeV)" % (collection, suffix, jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.p4sName]
        if p4s.size() <= self.jetIndex : return False
        return self.jetPtThreshold <= p4s.at(self.jetIndex).pt()
#####################################
class jetPtVetoer(analysisStep) :
    """jetPtVetoer"""

    def __init__(self,collection,suffix,jetPtThreshold,jetIndex):
        self.jetPtThreshold = jetPtThreshold
        self.jetIndex = jetIndex
        self.jetP4s = "%sCorrectedP4%s" % (collection,suffix)
        
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
        for cs in self.jetCollectionsAndSuffixes :
            p4s = eventVars["%sCorrectedP4%s" % cs]
            corr = eventVars["%sCorrFactor%s" % cs]
            size = p4s.size()
            if not size : continue
            maxUncorrPt,index = max( [ (p4s.at(i).pt()/corr.at(i),i) for i in range(size) ] )
            if self.jetPtThreshold <= p4s.at(index).pt() :
                return True
        return False
#####################################
class cleanJetEmfFilter(analysisStep) :
    """cleanJetEmfFilter"""

    def __init__(self,collection,suffix,ptMin,emfMax):
        self.indicesName = "%sIndices%s" % (collection,suffix)
        self.p4sName = "%sCorrectedP4%s" % (collection,suffix)
        self.emfName = "%sEmEnergyFraction%s" % (collection,suffix)

        self.ptMin = ptMin
        self.emfMax = emfMax
        
        self.moreName = "(%s; %s" % (collection,suffix)
        self.moreName2 = " corr. pT>=%.1f GeV; EMF<=%.1f)" % (ptMin,emfMax)

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

    def __init__(self,collection,suffix):
        self.indicesName = "%sIndices%s" % (collection,suffix)
        self.moreName = "(%s %s)" % (collection,suffix)
        
    def uponAcceptance (self,eventVars) :
        self.book(eventVars).fill(len(eventVars[self.indicesName]["clean"]),
                                  self.indicesName+"clean", 15,-0.5,14.5,
                                  title=";number of jets passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin")
######################################
class minNCleanJetEventFilter(analysisStep) :
    """minNCleanJetEventFilter"""

    def __init__(self,collection,suffix,minNCleanJets):
        self.minNCleanJets = minNCleanJets
        self.indicesName = "%sIndices%s" % (collection,suffix)
        self.moreName = "(%s %s>=%d)" % (collection,suffix,minNCleanJets)
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["clean"]) >= self.minNCleanJets
######################################
class maxNOtherJetEventFilter(analysisStep) :
    """maxNOtherJetEventFilter"""

    def __init__(self,collection,suffix,maxNOtherJets):
        self.maxNOtherJets = maxNOtherJets
        self.indicesName = "%sIndices%s" % (collection,suffix)
        self.moreName = "(%s %s<=%d)" % (collection,suffix,maxNOtherJets)
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["other"]) <= self.maxNOtherJets
#####################################
class cleanJetHtMhtHistogrammer(analysisStep) :
    """cleanJetHtMhtHistogrammer"""

    def __init__(self,collection,suffix):
        self.cs = (collection,suffix)
        self.histoMax = 1.0e3

        self.moreName="(%s; %s)" % self.cs

    def uponAcceptance (self,eventVars) :
        sumP4 = eventVars["%sSumP4%s"%self.cs]
        ht = eventVars["%sSumPt%s"%self.cs]
        
        book = self.book(eventVars)
        book.fill(   sumP4.pt(), "%smht%s"%self.cs, 50, 0.0, self.histoMax, title = "; #slash{H}_{T} (GeV) from clean jets;events / bin")
        book.fill(           ht,  "%sht%s"%self.cs, 50, 0.0, self.histoMax, title = "; H_{T} (GeV) from clean jet p_{T}'s;events / bin")
        book.fill( sumP4.mass(),   "%sm%s"%self.cs, 50, 0.0, self.histoMax, title = "; mass (GeV) of system of clean jets;events / bin")
        book.fill( (ht,sumP4.pt()), "%smht_vs_ht%s"%self.cs, (50,50), (0.0,0.0), (self.histoMax,self.histoMax),
                   title = "; H_{T} (GeV) from clean jets; #slash{H}_{T} (GeV) from clean jet p_{T}'s;events / bin")

        value = sumP4.pt() / ht  if ht>0.0 else -1.0
        book.fill(value, "%smHtOverHt%s"%self.cs, 50, 0.0, 1.1, title = "; MHT / H_{T} (GeV) from clean jet p_{T}'s;events / bin" )
#####################################
class cleanJetPtHistogrammer(analysisStep) :
    """cleanJetPtHistogrammer"""

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
        self.moreName="(%s; %s)" % self.cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.cFactorName = "%sCorrFactor%s" % self.cs

    def uponAcceptance (self,eventVars) :
        ptleading = 0.0
        p4s = eventVars[self.p4sName]
        cleanJetIndices = eventVars[self.indicesName]["clean"]

        for iJet in cleanJetIndices :
            pt = p4s.at(iJet).pt()
            self.book(eventVars).fill(pt, "%sptAll%s"%self.cs, 50, 0.0, 500.0, title=";p_{T} (GeV) of clean jets;events / bin")

            if iJet==0 :#assumes sorted
                self.book(eventVars).fill(pt, "%sptLeading%s"%self.cs, 50, 0.0, 500.0, title=";p_{T} (GeV) of leading clean jet;events / bin")
#####################################
class cleanNJetAlphaProducer(analysisStep) :
    """cleanNJetAlphaProducer"""

    def __init__(self,collection,suffix):
        self.cs = (collection,suffix)
        self.moreName = "(%s; %s)" % self.cs

        self.helper = r.alphaHelper()
        self.cleanJetIndices = r.std.vector('int')()
        self.cleanJetIndices.reserve(256)

    def select (self,eventVars) :
        nJetDeltaHt=0.0
        nJetAlphaT=0.0

        #return if fewer than two clean jets
        cleanJetIndices = eventVars["%sIndices%s"%self.cs]["clean"]
        if (len(cleanJetIndices)<2) :
            self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
            return True

        #return if HT is tiny
        ht = eventVars["%sSumPt%s"%self.cs]
        if (ht<=1.0e-2) :
            self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
            return True

        p4s = eventVars["%sCorrectedP4%s"%self.cs]

        self.cleanJetIndices.clear()
        for index in cleanJetIndices :
            self.cleanJetIndices.push_back(index)

        self.helper.go(p4s,self.cleanJetIndices)
        nJetDeltaHt = self.helper.GetMinDiff()
        mht = eventVars["%sSumP4%s"%self.cs].pt()
        nJetAlphaT = 0.5*(1.0-nJetDeltaHt/ht)/r.TMath.sqrt(1.0-(mht/ht)**2)

        self.setExtraVars(eventVars,nJetDeltaHt,nJetAlphaT)
        return True

    def setExtraVars(self,eventVars,nJetDeltaHt,nJetAlphaT) :
        eventVars["crock"]["%snJetDeltaHt%s"%self.cs] = nJetDeltaHt
        eventVars["crock"]["%snJetAlphaT%s"%self.cs] = nJetAlphaT
#####################################
class cleanDiJetAlphaProducer(analysisStep) :
    """cleanDiJetAlphaProducer"""

    def __init__(self,collection,suffix):
        self.cs = (collection,suffix)
        self.indicesName = "%sIndices%s" % self.cs
        self.moreName = "(%s; %s;)" % self.cs
        self.lvSum = r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
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
            
        p4s = eventVars["%sCorrectedP4%s" % self.cs]
        for iJet in cleanJetIndices :
            jet = p4s.at(iJet)
            pt = jet.pt()
            Et = jet.Et()

            if (pt<diJetMinPt) : diJetMinPt=pt
            if (Et<diJetMinEt) : diJetMinEt=Et

            self.lvSum += jet

        diJetM = self.lvSum.M()
        
        if (diJetM>0.0) :
            diJetAlpha   =diJetMinPt/diJetM
            diJetAlpha_Et=diJetMinEt/diJetM

        self.setExtraVars(eventVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et)
        return True

    def setExtraVars(self,eventVars,diJetM,diJetMinPt,diJetMinEt,diJetAlpha,diJetAlpha_Et) :
            eventVars["crock"]["%sdiJetM%s"       %self.cs]=diJetM
            eventVars["crock"]["%sdiJetMinPt%s"   %self.cs]=diJetMinPt
            eventVars["crock"]["%sdiJetMinEt%s"   %self.cs]=diJetMinEt
            eventVars["crock"]["%sdiJetAlpha%s"   %self.cs]=diJetAlpha
            eventVars["crock"]["%sdiJetAlpha_Et%s"%self.cs]=diJetAlpha_Et
#####################################
class alphaHistogrammer(analysisStep) :
    """alphaHistogrammer"""

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
        self.moreName = "(%s; %s)"%self.cs
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        bins,min,max = (80,0.0,2.0)

        mht = eventVars["%sSumP4%s"%self.cs].pt() 
        ht = eventVars["%sSumPt%s"%self.cs]
        deltaHt = eventVars["crock"]["%snJetDeltaHt%s"%self.cs]

        book.fill( eventVars["crock"]["%sdiJetAlpha%s"%self.cs], "%sdijet_alpha%s"%self.cs, bins,min,max,
                   title = ";di-jet #alpha (using p_{T});events / bin")

        # book.fill( eventVars["crock"]["%sdiJetAlpha_Et%s"%self.cs], "%sdijet_alpha_ET%s"%self.cs, bins,min,max,
        #            title = ";di-jet #alpha (using E_{T});events / bin")

        book.fill( eventVars["crock"]["%snJetAlphaT%s"%self.cs], "%snjet_alphaT%s", bins,min,max,
                   title = ";N-jet #alpha_{T} (using p_{T});events / bin")

        book.fill( deltaHt, "%snjet_deltaHt%s"%self.cs, 50,0.0,500,
                   title = ";N-jet #Delta H_{T} (GeV);events / bin")

        book.fill( (mht/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_mHtOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                   title = ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

#####################################
class metHistogrammer(analysisStep) :
    """metHistogrammer"""

    def __init__(self,collection,tag) :
        self.ct = (collection,tag)
                
    def uponAcceptance (self,eventVars) :
        self.book(eventVars).fill( eventVars[self.metCollection].pt(), "%s_%s" % self.ct, 80, 0.0, 80.0, title = "; p_{T} (GeV);events / bin")
#####################################
class deltaPhiProducer(analysisStep) :
    """deltaPhiProducer"""

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
    
    def select(self,eventVars) :

        eventVars["crock"]["%sdeltaPhi01%s"%self.cs] =  -4.0
        eventVars["crock"]["%sdeltaR01%s"  %self.cs] = -40.0
        eventVars["crock"]["%sdeltaEta01%s"%self.cs] = -40.0

        p4s = eventVars['%sCorrectedP4%s'%self.cs]
        index = eventVars["%sIndices%s"%self.cs]["clean"]

        if len(index)>=2 :
            jet0 = p4s[index[0]]
            jet1 = p4s[index[1]]
            eventVars["crock"]["%sdeltaPhi01%s"%self.cs] = r.Math.VectorUtil.DeltaPhi(jet0,jet1)
            eventVars["crock"]["%sdeltaR01%s"  %self.cs] = r.Math.VectorUtil.DeltaR(jet0,jet1)
            eventVars["crock"]["%sdeltaEta01%s"%self.cs] = jet0.eta()-jet1.eta()
        return True
#####################################
class deltaPhiSelector(analysisStep) :
    """deltaPhiSelector"""

    def __init__(self,collection,suffix,minAbs,maxAbs) :
        self.cs = (collection,suffix)
        self.minAbs = minAbs
        self.maxAbs = maxAbs
        self.moreName = "(%s; %s; minAbs=%.1f; maxAbs=%.1f)" % (self.cs[0],self.cs[1],minAbs,maxAbs)
    
    def select(self,eventVars) :
        value = abs( eventVars["crock"]["%sdeltaPhi01%s"%self.cs] )
        if (value<self.minAbs or value>self.maxAbs) : return False
        return True
#####################################
class mHtOverHtSelector(analysisStep) :
    """mHtOverHtSelector"""

    def __init__(self,collection,suffix,min,max) :
        self.cs = (collection,suffix)
        self.min = min
        self.max = max
        self.moreName = "(%s; %s; min=%.1f; max=%.1f)" % (self.cs[0],self.cs[1],min,max)
    
    def select(self,eventVars) :
        mht = eventVars["%sSumP4%s"%self.cs].pt()
        ht = eventVars["%sSumPt%s"%self.cs]
        if (ht<1.0e-2) : return False
        value = mht/ht
        if (value<self.min or value>self.max) : return False
        return True
class deltaPhiHistogrammer(analysisStep) :
    """deltaPhiHistogrammer"""

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)

        var = "%sdeltaPhi01%s"%self.cs
        book.fill( eventVars["crock"][var], var, 50, -4.0, 4.0, title = var+";events / bin")

        var = "%sdeltaR01%s"%self.cs
        book.fill( eventVars["crock"][var], var, 20, 0.0, 10.0, title = var+";events / bin")

        var = "%sdeltaEta01%s"%self.cs
        book.fill( eventVars["crock"][var], var, 50, -10, 10.0, title = var+";events / bin")

#####################################
