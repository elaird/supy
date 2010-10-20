import ROOT as r
import math
from analysisStep import analysisStep
#####################################
class preIdJetPtSelector(analysisStep) :

    def __init__(self,cs,jetPtThreshold,jetIndex):
        self.jetIndex = jetIndex
        self.jetPtThreshold = jetPtThreshold
        self.cs = cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        if self.p4sName[:2] == "xc" : self.p4sName = self.p4sName[2:]
        self.moreName = "%s%s; pT[%d]>=%.1f GeV" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.p4sName]
        if p4s.size() <= self.jetIndex : return False
        return self.jetPtThreshold <= p4s.at(self.jetIndex).pt()
#####################################
class jetPtSelector(analysisStep) :

    def __init__(self,cs,jetPtThreshold,jetIndex):
        self.jetIndex = jetIndex
        self.jetPtThreshold = jetPtThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%.1f GeV" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.jetIndex : return False
        p4s = eventVars[self.p4sName]
        return self.jetPtThreshold <= p4s.at(indices[self.jetIndex]).pt()
#####################################
class jetEtaSelector(analysisStep) :

    def __init__(self,cs,jetEtaThreshold,jetIndex):
        self.jetIndex = jetIndex
        self.jetEtaThreshold = jetEtaThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.moreName = "%s%s; |eta[index[%d]]|<=%.1f" % (self.cs[0], self.cs[1], jetIndex, jetEtaThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.jetIndex : return False
        p4s = eventVars[self.p4sName]
        return self.jetEtaThreshold > abs(p4s.at(indices[self.jetIndex]).eta())
#####################################
class jetPtVetoer(analysisStep) :

    def __init__(self,cs,jetPtThreshold,jetIndex):
        self.jetPtThreshold = jetPtThreshold
        self.jetIndex = jetIndex
        self.cs = cs
        self.jetP4s = "%sCorrectedP4%s" % self.cs
        self.moreName = "%s%s; pT[%d]<%.1f GeV" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        p4s = eventVars[self.jetP4s]
        if p4s.size() <= self.jetIndex : return True
        return p4s.at(self.jetIndex).pt() < self.jetPtThreshold
#####################################
class leadingUnCorrJetPtSelector(analysisStep) :

    def __init__(self,jetCollectionsAndSuffixes,jetPtThreshold):
        self.jetCollectionsAndSuffixes = jetCollectionsAndSuffixes
        self.jetPtThreshold = jetPtThreshold
        self.moreName = ''.join(["%s%s;" % cS for cS in self.jetCollectionsAndSuffixes])
        self.moreName2 = " corr pT[leading uncorr jet]>=%.1f GeV" % self.jetPtThreshold 

    def select (self,eventVars) :
        # Corrected pt of leading jet (by uncorrected pt) >= threshold
        for cs in self.jetCollectionsAndSuffixes :
            p4s = eventVars["%sCorrectedP4%s" % cs]
            corr = eventVars["%sCorrFactor%s" % (cs[0].lstrip("xc"),cs[1])]
            size = p4s.size()
            if not size : continue
            maxUncorrPt,index = max( [ (p4s.at(i).pt()/corr.at(i),i) for i in range(size) ] )
            if self.jetPtThreshold <= p4s.at(index).pt() :
                return True
        return False
#####################################
class leadingUnCorrJetEtaSelector(analysisStep) :

    def __init__(self,cs,jetEtaThreshold):
        self.cs = cs
        self.jetEtaThreshold = jetEtaThreshold
        self.moreName = "%s%s;" % cs
        self.moreName2 = " |corr eta[leading uncorr jet]|<%.1f" % self.jetEtaThreshold 

    def select (self,eventVars) :
        # |Corrected eta of leading jet (by uncorrected pt)| < threshold 
        p4s = eventVars["%sCorrectedP4%s" % self.cs]
        corr = eventVars["%sCorrFactor%s" % (self.cs[0].lstrip("xc"),self.cs[1])]
        size = p4s.size()
        if not size : return False
        maxUncorrPt,index = max( [ (p4s.at(i).pt()/corr.at(i),i) for i in range(size) ] )
        return self.jetEtaThreshold > abs (p4s.at(index).eta())
#####################################
class cleanJetEmfFilter(analysisStep) :

    def __init__(self,collection,suffix,ptMin,emfMax):
        self.indicesName = "%sIndices%s" % (collection,suffix)
        self.p4sName = "%sCorrectedP4%s" % (collection,suffix)
        self.emfName = "%sEmEnergyFraction%s" % (collection,suffix)

        self.ptMin = ptMin
        self.emfMax = emfMax
        
        self.moreName = "%s%s" % (collection,suffix)
        self.moreName += "; pT>=%.1f GeV; EMF<=%.1f" % (ptMin,emfMax)

    def select (self,eventVars) :
        p4s = eventVars[self.p4sName]
        emf = eventVars[self.emfName]

        for index in eventVars[self.indicesName] :
            if p4s.at(index).pt() <= self.jetPtThreshold : #assumes sorted
                return True
            if emf.at(index) > self.jetEmfMax :
                return False
        return True
#####################################
class htSelector(analysisStep) :

    def __init__(self,jetCollectionsAndSuffixes,htThreshold):
        self.jetCollectionsAndSuffixes = jetCollectionsAndSuffixes
        self.htThreshold = htThreshold
        self.moreName = ''.join(["%s%s;" % cS for cS in self.jetCollectionsAndSuffixes])
        self.moreName2 = " HT>=%.1f GeV" % self.htThreshold

    def select (self,eventVars) :
        for cs in self.jetCollectionsAndSuffixes :
            if eventVars["%sSumEt%s"%cs]>self.htThreshold : return True
        return False
######################################
class cleanJetHtMhtHistogrammer(analysisStep) :

    def __init__(self,cs,etRatherThanPt):
        self.cs = cs
        self.etRatherThanPt = etRatherThanPt
        self.letter = "P" if not self.etRatherThanPt else "E"
        self.htName = "%sSum%st%s"%(self.cs[0],self.letter,self.cs[1])
        self.moreName="%s%s" % self.cs

    def uponAcceptance (self,eventVars) :
        sumP4 = eventVars["%sSumP4%s"%self.cs]
        ht =  eventVars[self.htName]
        mht = sumP4.pt()
        
        book = self.book(eventVars)
        book.fill(           ht,"%sHt%s"       %self.cs, 50, 0.0, 1500.0, title = ";H_{T} (GeV) from %s%s %s_{T}'s;events / bin"%(self.cs[0],self.cs[1],self.letter))
        book.fill(          mht,"%sMht%s"      %self.cs, 50, 0.0,  700.0, title = ";#slash{H}_{T} (GeV) from %s%s;events / bin"%self.cs)
        book.fill(       mht+ht,"%sHtPlusMht%s"%self.cs, 50, 0.0, 1500.0, title = ";H_{T} + #slash{H}_{T} (GeV) from %s%s %s_{T}'s;events / bin"%(self.cs[0],self.cs[1],self.letter))
        book.fill( sumP4.mass(),"%sm%s"        %self.cs, 50, 0.0,  7.0e3, title = ";mass (GeV) of system of clean jets;events / bin")
        book.fill( (ht,mht), "%smht_vs_ht%s"%self.cs, (50,50), (0.0,0.0), (1500.0,1500.0),
                   title = "; H_{T} (GeV) from clean jets; #slash{H}_{T} (GeV) from clean jet %s_{T}'s;events / bin"%self.letter)

        value = mht / ht  if ht>0.0 else -1.0
        book.fill(value, "%smHtOverHt%s"%self.cs, 50, 0.0, 1.1, title = "; MHT / H_{T} (GeV) from clean jet %s_{T}'s;events / bin"%self.letter )
#####################################
class singleJetHistogrammer(analysisStep) :

    def __init__(self,cs, maxIndex = 2) :
        self.cs = cs
        self.csbase = (cs[0].replace("xc",""),cs[1])
        self.maxIndex = maxIndex
        self.moreName="%s%s through index %d" % (self.cs+(maxIndex,))
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sCorrectedP4%s" % self.cs

    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        p4s = eventVars[self.p4sName]
        cleanJetIndices = eventVars[self.indicesName]
        phi2mom = eventVars["%sPhi2Moment%s"%self.csbase]
        eta2mom = eventVars["%sEta2Moment%s"%self.csbase]

        book.fill( len(cleanJetIndices), "jetMultiplicity", 10, -0.5, 9.5,
                   title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%self.cs)
        
        for i,iJet in enumerate(cleanJetIndices) :
            jet = p4s.at(iJet)
            pt = jet.pt()
            eta = jet.eta()
            phi2 = phi2mom.at(iJet)
            eta2 = eta2mom.at(iJet)
            mom2Max = 0.1
            jetLabel = str(i+1) if i <= self.maxIndex else "_ge%d"%(self.maxIndex+2)

            book.fill(eta2,  "%s%s%sEta2mom" %(self.cs+(jetLabel,)), 50,  0.0, mom2Max, title=";jet%s #sigma_{#eta}^{2};events / bin"%jetLabel)
            book.fill(phi2,  "%s%s%sPhi2mom" %(self.cs+(jetLabel,)), 50,  0.0, mom2Max, title=";jet%s #sigma_{#phi}^{2};events / bin"%jetLabel)
            book.fill(pt,  "%s%s%sPt" %(self.cs+(jetLabel,)), 50,  0.0, 500.0, title=";jet%s p_{T} (GeV);events / bin"%jetLabel)
            book.fill(eta, "%s%s%seta"%(self.cs+(jetLabel,)), 50, -5.0,   5.0, title=";jet%s #eta;events / bin"%jetLabel)
            if i>self.maxIndex: continue
            for j,jJet in list(enumerate(cleanJetIndices))[i+1:self.maxIndex+1] :
                book.fill(abs(r.Math.VectorUtil.DeltaPhi(jet,p4s.at(jJet))), "%s%sdphi%d%d"%(self.cs+(i+1,j+1)), 50,0, r.TMath.Pi(),
                          title = ";#Delta#phi_{jet%d,jet%d};events / bin"%(i+1,j+1))
#####################################
class alphaHistogrammer(analysisStep) :

    def __init__(self, cs = None, deltaPhiStarExtraName = "", etRatherThanPt = None) :
        self.cs = cs
        self.deltaPhiStar = "%sDeltaPhiStar%s%s"%(self.cs[0], self.cs[1], deltaPhiStarExtraName)
        self.letter = "E" if etRatherThanPt else "p"
        self.deltaPseudoName = "%sDeltaPseudoJet%st%s" % (self.cs[0], self.letter, self.cs[1])
        self.htName = "%sSum%st%s" % (self.cs[0], self.letter, self.cs[1])
        self.moreName = "%s%s"%self.cs
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)

        mht = eventVars["%sSumP4%s"%self.cs].pt()
        ht  = eventVars[self.htName]
        deltaHt = eventVars[self.deltaPseudoName]
        alphaT = eventVars["%sAlphaT%s"%self.cs]
        deltaPhiStar = eventVars[self.deltaPhiStar]["DeltaPhiStar"]

        #if diJetAlpha :
        #    book.fill( eventVars["%sDiJetAlpha%s"%self.cs], "%sdijet_alpha%s"%self.cs, 80,0.0,2.0,
        #               title = ";di-jet #alpha (using p_{T});events / bin")

        if not alphaT :
            return

        book.fill( alphaT, "%sAlphaT%s"%self.cs, 80,0.0,2.0,
                   title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        book.fill( alphaT, "%sAlphaTRough%s"%self.cs, 40,0.0,2.0,
                   title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        book.fill( alphaT, "%sAlphaTZoom%s"%self.cs, 120, 0.48, 0.60,
                   title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        book.fill( alphaT, "%sAlphaTFewBins%s"%self.cs, 4, 0.0, 0.55*4,
                   title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        book.fill( deltaHt, "%sDeltaHt%s"%self.cs, 50,0.0,500,
                   title = ";#Delta H_{T} (GeV);events / bin")

        book.fill( deltaHt/ht, "%sDeltaHtOverHt%s"%self.cs, 50, 0.0, 1.1,
                   title = ";#Delta H_{T}/H_{T};events / bin")

        book.fill( (mht/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_mHtOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                   title = ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

        book.fill( (alphaT,ht), "%s_Ht_vs_alphaT_%s"%self.cs, (300,200), (0.0,0.0), (3.0,1000),
                   title = ";#alpha_{T} (using %s_{T});H_{T};events / bin"%self.letter)
        
        book.fill( (alphaT,deltaPhiStar),"%s_deltaPhiStar_vs_alphaT_%s"%self.cs,
                   (500,50), (0.0,0.0),(1.0,r.TMath.Pi()),
                   title=";#alpha_{T} (using %s_{T});#Delta#phi*;events / bin"%self.letter)
#####################################
class alphaMetHistogrammer(analysisStep) :

    def __init__(self, cs = None, deltaPhiStarExtraName = "", etRatherThanPt = None, metName = None) :
        self.cs = cs

        self.deltaPhiStar = "%sDeltaPhiStar%s%s"%(self.cs[0], self.cs[1], deltaPhiStarExtraName)
        self.etRatherThanPt = etRatherThanPt
        self.letter = "E" if self.etRatherThanPt else "p"
        self.deltaPseudoName = "%sDeltaPseudoJetPt%s" % self.cs if not self.etRatherThanPt else "%sDeltaPseudoJetEt%s" % self.cs
        self.htName = "%sSumPt%s" % self.cs if not self.etRatherThanPt else "%sSumEt%s" % self.cs
        self.metName = metName
        self.moreName = "%s%s"%self.cs
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)

        if self.metName!=None :
            met = eventVars[self.metName].pt()
        ht  = eventVars[self.htName]
        deltaHt = eventVars[self.deltaPseudoName]
        alphaT = eventVars["%sAlphaT%s"%self.cs]
        alphaTMet = eventVars["%sAlphaTMet%s"%self.cs]
        deltaPhiStar = eventVars[self.deltaPhiStar]["DeltaPhiStar"]
        
        if not alphaT : return

        book.fill( alphaTMet, "%sAlphaTMet%s"%self.cs, 80,0.0,2.0,
                   title = ";#alpha_{T} (using jet %s_{T}#semicolon %s);events / bin"%(self.letter,self.metName))
        
        book.fill( alphaTMet, "%sAlphaTMetZooom%s"%self.cs, 120, 0.48, 0.60,
                   title = ";#alpha_{T} (using jet %s_{T}#semicolon %s);events / bin"%(self.letter,self.metName))

        book.fill( (met/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_metOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                   title = ";#slash(E_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

        book.fill( (alphaTMet,ht), "%s_Ht_vs_alphaTMet_%s"%self.cs, (300,200), (0.0,0.0), (3.0,1000),
                   title = ";#alpha_{T} (using %s_{T}#semicolon %s);H_{T};events / bin"%(self.letter,self.metName))
        
        book.fill( (alphaTMet,deltaPhiStar),"%s_deltaPhiStar_vs_alphaTMet_%s"%self.cs,
                   (500,50), (0.0,0.0),(1.0,r.TMath.Pi()),
                   title=";#alpha_{T} (using %s_{T}#semicolon %s);#Delta#phi*;events / bin"%(self.letter,self.metName))

        book.fill( (alphaT,alphaTMet), "%s_alphaTMet_vs_alphaT_%s"%self.cs, (80,80), (0.0,0.0), (2.0,2.0),
                   title = ";#alpha_{T};#alpha_{T} (from MET);events / bin")
        
        book.fill( (alphaT,alphaTMet), "%s_alphaTMet_zoomvs_alphaT_%s"%self.cs, (60,60), (0.48,0.48), (0.60,0.60),
                   title = ";#alpha_{T};#alpha_{T} (from MET);events / bin")
######################################
class leadingCorrJetFilter(analysisStep) :

    def __init__(self, cs, ptMin, etaMax):
        self.cs = cs
        self.ptMin = ptMin
        self.etaMax = etaMax
        self.moreName="%s%s; c. pT>%.1f GeV and |eta|<%.1f"%(self.cs[0],self.cs[1],self.ptMin,self.etaMax)

    def select (self,eventVars) :
        p4s = eventVars["%sCorrectedP4%s" % self.cs]
        size = p4s.size()
        if not size :
            return False
        maxCorrPt,index = max( [ (p4s.at(i).pt(),i) for i in range(size) ] )
        if index!=0 : print "zomg index =",index
        eta = p4s.at(index).eta()

        if maxCorrPt<self.ptMin or abs(eta)>self.etaMax :
            return False

        self.book(eventVars).fill(maxCorrPt,"%sMaxCorrJetPt%s"%self.cs, 50, 0.0,350.0, title = ";leading c. %s%s's c. p_{T} (GeV);events / bin"%self.cs)
        self.book(eventVars).fill(eta      ,"%sMaxCorrJetEta%s"%self.cs, 50, -5.0, 5.0, title = ";leading c. %s%s's #eta;events / bin"%self.cs)
        return True
######################################
class leadingUnCorrJetFilter(analysisStep) :

    def __init__(self, cs, ptMin, etaMax, extraHistos = False):
        for item in ["cs","ptMin","etaMax","extraHistos"] :
            setattr(self,item,eval(item))
        self.moreName="%s%s; u.c. pT>%.1f GeV and |eta|<%.1f"%(self.cs[0],self.cs[1],self.ptMin,self.etaMax)

    def select (self,eventVars) :
        p4s = eventVars["%sCorrectedP4%s" % self.cs]
        corr = eventVars["%sCorrFactor%s" % (self.cs[0].lstrip("xc"),self.cs[1])]
        size = p4s.size()
        if not size :
            return False
        maxUnCorrPt,index = max( [ (p4s.at(i).pt()/corr.at(i),i) for i in range(size) ] )
        eta = p4s.at(index).eta()

        if maxUnCorrPt<self.ptMin or abs(eta)>self.etaMax :
            return False

        if self.extraHistos :
            self.book(eventVars).fill(maxUnCorrPt,"%sMaxUnCorrJetPt%s"%self.cs, 50, 0.0,250.0, title = ";leading u.c. %s%s's u.c. p_{T} (GeV);events / bin"%self.cs)
            bigTuple = (self.cs[0],self.cs[1],self.cs[0],self.cs[1])
            self.book(eventVars).fill( (eta,maxUnCorrPt), "%sMaxUnCorrJetPtVsEta%s"%self.cs, (50, 50), (-5.0, 0.0), (5.0,250.0),
                                       title = ";leading u.c. %s%s's #eta;leading u.c. %s%s's u.c. p_{T} (GeV);events / bin"%bigTuple)

        self.book(eventVars).fill(eta        ,"%sMaxUnCorrJetEta%s"%self.cs, 50, -5.0, 5.0, title = ";leading u.c. %s%s's #eta;events / bin"%self.cs)
        return True
#####################################
class deltaPhiSelector(analysisStep) :

    def __init__(self,cs,minAbs,maxAbs) :
        self.cs = cs
        self.minAbs = minAbs
        self.maxAbs = maxAbs
        self.moreName = "%s; %s; minAbs=%.1f; maxAbs=%.1f" % self.cs+(minAbs,maxAbs)
    
    def select(self,eventVars) :
        value = abs( eventVars["%sDeltaX01%s"%self.cs]["phi"] )
        if value<self.minAbs or value>self.maxAbs : return False
        return True
#####################################
class mHtOverHtSelector(analysisStep) :

    def __init__(self,cs,min,max) :
        self.cs = cs
        self.min = min
        self.max = max
        self.moreName = "%s%s; min=%.1f; max=%.1f" % self.cs+(min,max)
    
    def select(self,eventVars) :
        mht = eventVars["%sSumP4%s"%self.cs].pt()
        ht = eventVars["%sSumPt%s"%self.cs]
        if (ht<1.0e-2) : return False
        value = mht/ht
        if (value<self.min or value>self.max) : return False
        return True
#####################################
class deltaPhiHistogrammer(analysisStep) :

    def __init__(self,collection,suffix) :
        self.cs = (collection,suffix)
        self.var = "%sDeltaX01%s"%self.cs

    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        book.fill( eventVars[self.var]["phi"], self.var, 50, -4.0, 4.0, title = ";"+self.var+";events / bin")
        book.fill( eventVars[self.var]["R"]  , self.var, 20, 0.0, 10.0, title = ";"+self.var+";events / bin")
        book.fill( eventVars[self.var]["eta"], self.var, 50, -10, 10.0, title = ";"+self.var+";events / bin")
#####################################
class alphatEtaDependence(analysisStep) :

    def __init__(self,collection) :
        self.cs = collection
        self.alphaT = "%sAlphaT%s"%self.cs
        self.ptBin = 20
        self.iMax = 10

    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        nJet= len(eventVars["%sIndices%s"%self.cs])
        nJet = "2jet" if nJet==2 else "ge3jet"
        alphaT = eventVars[self.alphaT]

        iGamma = eventVars["photonIndicesPat"]
        iZ = eventVars["genIndicesZ"]

        p4 = None
        if len(iZ) :
            p4 = eventVars["genP4"].at(iZ[0])
            label = "Z"
        elif len(iGamma) == 1 :
            p4 = eventVars["photonP4Pat"].at(iGamma[0])
            label = "gamma"

        if p4 :
            absEta = abs(p4.eta())
            iPt = math.floor(p4.pt()/self.ptBin)
            book.fill( (alphaT,absEta), "%sAlphaT_%s_pt%02d"%(label,nJet,min(iPt,self.iMax)), (100,10), (0,0), (2,5),
                       title = "%s %s;%s #alpha_{T};|#eta|;events / bin"%(label,self.ptLabel(iPt),nJet))

    def ptLabel(self,ipt) :
        return "pt %d-%d"%(self.ptBin*ipt,self.ptBin*(ipt+1)) if ipt<self.iMax else "pt>%d"%(self.iMax*self.ptBin)
#####################################
class uniquelyMatchedNonisoMuons(analysisStep) :

    def __init__(self,collection) :
        self.cs = collection
        self.moreName = "%s%s"%self.cs
    def select(self,eventVars) :
        return eventVars["crock"]["%s%sNonIsoMuonsUniquelyMatched"%self.cs]
#####################################
class ecalDeadTowerHistogrammer(analysisStep) :

    def __init__(self,collection,thresholds = [0]) :
        self.cs = collection
        self.moreName = "%s%s"%self.cs
        self.thresholds = sorted(thresholds)
    
    def uponAcceptance(self,eventVars) :
        book = self.book(eventVars)

        tpP4 = eventVars["ecalDeadTowerTrigPrimP4"]
        nBad = eventVars["ecalDeadTowerNBadXtals"]
        maxStatus = eventVars["ecalDeadTowerMaxStatus"]
        isBarrel = eventVars["ecalDeadTowerIsBarrel"]
        tpJetIndices = eventVars["ecalDeadTowerMatched%sIndices%s"%self.cs]

        tpEt = [p4.Et() for p4 in tpP4]
        tpEtlost = [et*n/25.0 for et,n in zip(tpEt,nBad)]
        recoverable = [stat<14 and (n!=15 or not barrel) for stat,n,barrel in zip(maxStatus,nBad,isBarrel)]
        matched = [i>=0 for i in tpJetIndices]
        jetP4s = eventVars["%sCorrectedP4%s"%self.cs]
        mht = eventVars["%sSumP4%s"%self.cs].pt()

        matchedUnrecoverable = any(map(lambda m,r: m and not r, matched,recoverable))
        overThresh = sum(tpEtlost) > 10
        level = "Danger" if overThresh or matchedUnrecoverable else "Clean"
        book.fill(mht, "mht%s"%level, 200, 0, 500 , title = "%s;MHT (GeV);events / bin"%level)
        
        for i in range(nBad.size()) :
            sub = "barrel" if isBarrel[i] else "endcap"
            p4 = tpP4.at(i)
            book.fill( (p4.eta(),p4.phi()), "tpEtaPhi%d%s"%(maxStatus[i],sub), (100,100),(-4,-4),(4,4), title = "TP status%d, %s;#eta;#phi;events / bin"%(maxStatus[i],sub))
            book.fill( (maxStatus[i],nBad[i]), "tpStatusNbad%s"%sub, (16, 30), (-0.5,-0.5), (15.5,29.5), title="%s;TP maxStatus;TP number bad xtals;TP / bin"%sub)

            if recoverable[i] :
                book.fill( tpEt[i], "tpEt%d%sMatched%d"%(nBad[i],sub,matched[i]) , 256, 0, 128, title = "%d bad,%s,matched%d;tp.Et;TPs / bin"%(nBad[i],sub,matched[i]))

        #maxTpEt = max(tpEt)
        #maxTpEtlost = max(tpEtlost)
        #book.fill((maxTpEt,mht),"tpEtMaxMHTcorr",(256,200),(0,0),(128,500), title=";max tp.Et;MHT;events / bin")
        #book.fill((maxTpEtlost,mht),"tpEtlostMaxMHTcorr",(256,200),(0,0),(128,500), title=";max tp.Et*badFraction;MHT;events / bin")
        #for thresh in self.thresholds :
        #    if maxTpEt > thresh : book.fill( mht, "mhtwMaxTpEtOver%02d"%thresh, 200,0,500, title = ";MHT, tp.Et_{max}>%02d;events / bin"%thresh)
        #    if maxTpEtlost > thresh : book.fill( mht, "mhtwMaxTpEtlostOver%02d"%thresh, 200,0,500, title = ";MHT, (tp.Et*badFraction)_{max}>%02d;events / bin"%thresh)
        #
        #indicesOverThresh = filter(lambda i: tpEt[i] > 0, range(len(tpEt)))
        #if not len(indicesOverThresh) : book.fill( mht, "mhtClean", 200,0,500, title="No TP et from dead ecal;MHT;events / bin")
        #for thresh in self.thresholds :
        #    indicesOverThresh = filter(lambda i: tpEt[i]>thresh, indicesOverThresh)
        #    overThreshTpJetIndices = [tpJetIndices[i] for i in indicesOverThresh]
        #    
        #    book.fill( map(lambda x: x<0, overThreshTpJetIndices).count(False), "tpsMatchedAbove%02d"%thresh, 10,-0.5,9.5,
        #               title=";Number of in-jet ecal dead regions with tp.Et>%02d GeV;events / bin"%thresh)
        #    book.fill( overThreshTpJetIndices.count(-2), "tpsUnmatchedAbove%02d"%thresh, 10,-0.5,9.5,
        #               title=";Number of isolated ecal dead regions with tp.Et>%02d GeV;events / bin"%thresh)
