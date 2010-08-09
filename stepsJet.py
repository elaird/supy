import ROOT as r
from analysisStep import analysisStep
#####################################
class jetPtSelector(analysisStep) :
    """jetPtSelector"""

    def __init__(self,cs,jetPtThreshold,jetIndex):
        self.jetIndex = jetIndex
        self.jetPtThreshold = jetPtThreshold
        self.cs = cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.moreName = "(%s %s; pT[%d]>=%.1f GeV)" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.p4sName]
        if p4s.size() <= self.jetIndex : return False
        return self.jetPtThreshold <= p4s.at(self.jetIndex).pt()
#####################################
class jetPtVetoer(analysisStep) :
    """jetPtVetoer"""

    def __init__(self,cs,jetPtThreshold,jetIndex):
        self.jetPtThreshold = jetPtThreshold
        self.jetIndex = jetIndex
        self.cs = cs
        self.jetP4s = "%sCorrectedP4%s" % self.cs
        self.moreName = "(%s %s; pT[%d]<%.1f GeV)" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

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
        self.moreName2 = "corr pT[leading uncorr jet]>=%.1f GeV" % self.jetPtThreshold 
        self.moreName2+=")"

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
        
        self.moreName = "(%s %s" % (collection,suffix)
        self.moreName2 = " pT>=%.1f GeV; EMF<=%.1f)" % (ptMin,emfMax)

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

    def __init__(self,cs,minNCleanJets):
        self.minNCleanJets = minNCleanJets
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.moreName = "(%s %s>=%d)" % (self.cs[0], self.cs[1], minNCleanJets)
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["clean"]) >= self.minNCleanJets
######################################
class maxNOtherJetEventFilter(analysisStep) :
    """maxNOtherJetEventFilter"""

    def __init__(self,cs,maxNOtherJets):
        self.maxNOtherJets = maxNOtherJets
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.moreName = "(%s %s<=%d)" % (self.cs[0], self.cs[1], maxNOtherJets)
        
    def select (self,eventVars) :
        return len(eventVars[self.indicesName]["other"]) <= self.maxNOtherJets
#####################################
class cleanJetHtMhtHistogrammer(analysisStep) :
    """cleanJetHtMhtHistogrammer"""

    def __init__(self,cs):
        self.cs = cs
        self.histoMax = 1.0e3
        self.moreName="(%s %s)" % self.cs

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

    def __init__(self,cs) :
        self.cs = cs
        self.moreName="(%s %s)" % self.cs
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
class alphaHistogrammer(analysisStep) :
    """alphaHistogrammer"""

    def __init__(self,cs) :
        self.cs = cs
        self.moreName = "(%s %s)"%self.cs
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        bins,min,max = (80,0.0,2.0)

        mht = eventVars["%sSumP4%s"%self.cs].pt() 
        ht = eventVars["%sSumPt%s"%self.cs]
        deltaHt = eventVars["%sDeltaPseudoJet%s"%self.cs]
        alphaT = eventVars["%sAlphaT%s"%self.cs]
        diJetAlpha = eventVars["%sDiJetAlpha%s"%self.cs]
        indices = eventVars["%sIndices%s"%self.cs]

        if diJetAlpha :
            book.fill( diJetAlpha, "%sdijet_alpha%s"%self.cs, bins,min,max,
                       title = ";di-jet #alpha (using p_{T});events / bin")

        book.fill( alphaT, "%snjet_alphaT%s"%self.cs, bins,min,max,
                   title = ";N-jet #alpha_{T} (using p_{T});events / bin")

        book.fill( deltaHt, "%snjet_deltaHt%s"%self.cs, 50,0.0,500,
                   title = ";N-jet #Delta H_{T} (GeV);events / bin")

        book.fill( (mht/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_mHtOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                   title = ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

        for njets in ["ge2jets","2jets" if len(indices) == 2 else "ge3jets"] :
            book.fill( (alphaT,ht), "%s%s_alphaT_vs_Ht_%s"%(self.cs[0],self.cs[1],njets), (300,200), (0.0,0.0), (3.0,1000),
                       title = "%s;#alpha_{T};H_{T};events / bin"%njets)

#####################################
class metHistogrammer(analysisStep) :
    """metHistogrammer"""

    def __init__(self,collection,tag) :
        self.ct = (collection,tag)
                
    def uponAcceptance (self,eventVars) :
        self.book(eventVars).fill( eventVars[self.metCollection].pt(), "%s_%s" % self.ct, 80, 0.0, 80.0, title = "; p_{T} (GeV);events / bin")
#####################################
class deltaPhiSelector(analysisStep) :
    """deltaPhiSelector"""

    def __init__(self,cs,minAbs,maxAbs) :
        self.cs = cs
        self.minAbs = minAbs
        self.maxAbs = maxAbs
        self.moreName = "(%s; %s; minAbs=%.1f; maxAbs=%.1f)" % (self.cs[0],self.cs[1],minAbs,maxAbs)
    
    def select(self,eventVars) :
        value = abs( eventVars["%sDeltaX01%s"%self.cs]["phi"] )
        if value<self.minAbs or value>self.maxAbs : return False
        return True
#####################################
class mHtOverHtSelector(analysisStep) :
    """mHtOverHtSelector"""

    def __init__(self,cs,min,max) :
        self.cs = cs
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
#####################################
class deltaPhiHistogrammer(analysisStep) :
    """deltaPhiHistogrammer"""

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
        self.var = "%sDeltaX01%s"%self.cs

    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        book.fill( eventVars[self.var]["phi"], self.var, 50, -4.0, 4.0, title = ";"+self.var+";events / bin")
        book.fill( eventVars[self.var]["R"]  , self.var, 20, 0.0, 10.0, title = ";"+self.var+";events / bin")
        book.fill( eventVars[self.var]["eta"], self.var, 50, -10, 10.0, title = ";"+self.var+";events / bin")
#####################################
class deltaPhiStarHistogrammer(analysisStep) :
    """deltaPhiStarHistogrammer"""

    def __init__(self,cs) :
        self.cs = cs
        self.var = "%sDeltaPhiStar%s"%self.cs
        self.moreName = "(%s %s)"%self.cs
        self.title=";%s#Delta#phi^{*}%s;events / bin"%self.cs
        
    def uponAcceptance (self,eventVars) :
        self.book(eventVars).fill( eventVars[self.var], self.var, 50, 0.0, r.TMath.Pi(), title = self.title)
#####################################
