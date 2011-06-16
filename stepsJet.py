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
class jetSelector(analysisStep) :

    def __init__(self, cs, referenceThresholds, jetIndex) :
        for item in ["jetIndex", "cs"] :
            setattr(self, item, eval(item))

        self.fraction = referenceThresholds["jet%dPt"%(jetIndex+1)]/referenceThresholds["ht"]
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sCorrectedP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%4.3f * HtBin" % (self.cs[0], self.cs[1], jetIndex, self.fraction)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.jetIndex : return False
        value = eventVars[self.p4sName].at(indices[self.jetIndex]).pt()
        return self.fraction*eventVars["%sHtBin%s"%self.cs] <= value
#####################################
class mhtSelector(analysisStep) :
    def __init__(self, cs, referenceThresholds) :
        self.cs = cs
        self.fraction = referenceThresholds["mht"]/referenceThresholds["ht"]
        self.indicesName = "%sIndices%s" % self.cs
        self.mhtName = "%sSumP4%s" % self.cs
        self.moreName = "%s >= %4.3f * HtBin" % (self.mhtName, self.fraction)

    def select (self,eventVars) :
        return self.fraction*eventVars["%sHtBin%s"%self.cs] <= eventVars[self.mhtName].pt()
#####################################
class htBinFilter(analysisStep) :

    def __init__(self, cs, min = None, max = None) :
        for item in ["cs", "min", "max"] :
            setattr(self, item, eval(item))
        self.moreName = "%s%s"%self.cs
        if self.min :
            self.moreName += "; %g <= HtBin"%self.min
            if self.max : self.moreName += " <= %g"%self.max
        elif self.max :
            self.moreName += "; %g <= HtBin"%self.max
        
    def select(self,eventVars) :
        bin = eventVars["%sHtBin%s"%self.cs]
        return ( (self.min==None or self.min<=bin) and (self.max==None or bin<=self.max) )
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
class forwardFailedJetVeto(analysisStep) :
    def __init__(self,cs, ptAbove=None, etaAbove=None) :
        self.cs = cs
        self.pt = ptAbove
        self.eta = etaAbove
        self.indices= "%sIndicesOther%s"%self.cs
        self.jetP4s = "%sCorrectedP4%s"%self.cs
        self.moreName = "%s%s indicesOther with pt>%.1f and |eta|>%.2f"%(cs+(self.pt,self.eta))
    def select(self,eventVars) :
        indices = eventVars[self.indices]
        p4s = eventVars[self.jetP4s]
        for i in indices:
            p4= p4s.at(i)
            if p4.pt() > self.pt and abs(p4.eta()) > self.eta : return False
        return True
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
        mht = sumP4.pt() if sumP4 else 0.0
        m = sumP4.mass() if sumP4 else 0.0
        
        self.book.fill(           ht,"%sHt%s"       %self.cs, 50,275.0, 2775.0, title = ";H_{T} (GeV) from %s%s %s_{T}'s;events / bin"%(self.cs[0],self.cs[1],self.letter))
        self.book.fill(          mht,"%sMht%s"      %self.cs, 50,  0.0, 1000.0, title = ";#slash{H}_{T} (GeV) from %s%s;events / bin"%self.cs)
        self.book.fill(       mht+ht,"%sHtPlusMht%s"%self.cs, 50,  0.0, 2500.0, title = ";H_{T} + #slash{H}_{T} (GeV) from %s%s %s_{T}'s;events / bin"%(self.cs[0],self.cs[1],self.letter))
        self.book.fill(        m,"%sm%s"         %self.cs, 50, 0.0,  7.0e3, title = ";mass (GeV) of system of clean jets;events / bin")
        self.book.fill( (ht,mht), "%smht_vs_ht%s"%self.cs, (50, 50), (0.0, 0.0), (2000.0, 2000.0),
                   title = "; H_{T} (GeV) from clean jets; #slash{H}_{T} (GeV) from clean jet %s_{T}'s;events / bin"%self.letter)

        value = mht / ht  if ht>0.0 else -1.0
        self.book.fill(value, "%smHtOverHt%s"%self.cs, 50, 0.0, 1.1, title = "; MHT / H_{T} (GeV) from clean jet %s_{T}'s;events / bin"%self.letter )
#####################################
class htMultiHistogrammer(analysisStep) :
    def __init__(self, cs, bins):
        self.cs = cs
        self.bins = bins
        self.htName = "%sSumEt%s"%self.cs
        self.moreName="%s%s"%self.cs
        self.binZip = zip(self.bins, self.bins[1:]+[""])
    def uponAcceptance (self,eventVars) :
        ht =  eventVars[self.htName]
        nJets = len(eventVars["%sIndices%s"%self.cs])
        for bin,next in self.binZip :
            if ht<bin : continue
            if next!=None and next<ht : continue
            self.book.fill(nJets, "%sNjets%s_%s_%s"%(self.cs[0], self.cs[1], str(bin), str(next)), 20, -0.5, 19.5,
                           title=";number of %s%s jets; %s<HT<%s;events / bin"%(self.cs[0], self.cs[1], str(bin), str(next)))
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
        p4s = eventVars[self.p4sName]
        cleanJetIndices = eventVars[self.indicesName]
        phi2mom = eventVars["%sPhi2Moment%s"%self.csbase]
        eta2mom = eventVars["%sEta2Moment%s"%self.csbase]

        self.book.fill( len(cleanJetIndices), "jetMultiplicity", 10, -0.5, 9.5,
                        title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%self.cs)
        
        for i,iJet in enumerate(cleanJetIndices) :
            jet = p4s.at(iJet)
            pt = jet.pt()
            eta = jet.eta()
            phi2 = phi2mom.at(iJet)
            eta2 = eta2mom.at(iJet)
            mom2Max = 0.1
            jetLabel = str(i+1) if i <= self.maxIndex else "_ge%d"%(self.maxIndex+2)

            self.book.fill(eta2,  "%s%s%sEta2mom" %(self.cs+(jetLabel,)), 50,  0.0, mom2Max, title=";jet%s #sigma_{#eta}^{2};events / bin"%jetLabel)
            self.book.fill(phi2,  "%s%s%sPhi2mom" %(self.cs+(jetLabel,)), 50,  0.0, mom2Max, title=";jet%s #sigma_{#phi}^{2};events / bin"%jetLabel)
            self.book.fill(pt,  "%s%s%sPt" %(self.cs+(jetLabel,)), 50,  0.0, 500.0, title=";jet%s p_{T} (GeV);events / bin"%jetLabel)
            self.book.fill(eta, "%s%s%seta"%(self.cs+(jetLabel,)), 50, -5.0,   5.0, title=";jet%s #eta;events / bin"%jetLabel)
            if i>self.maxIndex: continue
            for j,jJet in list(enumerate(cleanJetIndices))[i+1:self.maxIndex+1] :
                self.book.fill(abs(r.Math.VectorUtil.DeltaPhi(jet,p4s.at(jJet))), "%s%sdphi%d%d"%(self.cs+(i+1,j+1)), 50,0, r.TMath.Pi(),
                               title = ";#Delta#phi_{jet%d,jet%d};events / bin"%(i+1,j+1))
#####################################
class alphaHistogrammer(analysisStep) :

    def __init__(self, cs = None, deltaPhiStarExtraName = "", etRatherThanPt = None) :
        self.cs = cs
        self.letter = "E" if etRatherThanPt else "P"
        self.fixes = (cs[0], self.letter+"t"+cs[1])
        for var in ["Sum","DeltaPseudoJet","AlphaT"] : setattr(self,var,("%s"+var+"%s")%self.fixes)
        self.DeltaPhiStar = "%sDeltaPhiStar%s%s"% (self.cs[0], cs[1], deltaPhiStarExtraName)
        self.SumP4 = "%sSumP4%s" % cs
        self.moreName = "%s%s" % cs
        
    def uponAcceptance (self,eventVars) :
        if not eventVars[self.SumP4] : return
        mht = eventVars[self.SumP4].pt()
        ht  = eventVars[self.Sum]
        deltaHt = eventVars[self.DeltaPseudoJet]
        alphaT = eventVars[self.AlphaT]
        deltaPhiStar = eventVars[self.DeltaPhiStar]["DeltaPhiStar"]

        #if diJetAlpha :
        #    self.book.fill( eventVars["%sDiJetAlpha%s"%self.cs], "%sdijet_alpha%s"%self.cs, 80,0.0,2.0,
        #               title = ";di-jet #alpha (using p_{T});events / bin")

        if not alphaT :
            return

        self.book.fill( alphaT, "%sAlphaT%s"%self.cs, 80,0.0,2.0,
                        title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        self.book.fill( alphaT, "%sAlphaTRough%s"%self.cs, 40,0.0,2.0,
                        title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        self.book.fill( alphaT, "%sAlphaTZoom%s"%self.cs, 120, 0.48, 0.60,
                        title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        self.book.fill( alphaT, "%sAlphaTFewBins%s"%self.cs, 4, 0.0, 0.55*4,
                        title = ";#alpha_{T} (using %s_{T});events / bin"%self.letter)

        self.book.fill( deltaHt, "%sDeltaHt%s"%self.cs, 50,0.0,500,
                        title = ";#Delta H_{T} (GeV);events / bin")

        self.book.fill( deltaHt/ht, "%sDeltaHtOverHt%s"%self.cs, 50, 0.0, 1.1,
                        title = ";#Delta H_{T}/H_{T};events / bin")

        self.book.fill( (mht/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_mHtOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                        title = ";#slash(H_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

        self.book.fill( (alphaT,ht), "%s_Ht_vs_alphaT_%s"%self.cs, (300,200), (0.0,0.0), (3.0,1000),
                        title = ";#alpha_{T} (using %s_{T});H_{T};events / bin"%self.letter)
        
        self.book.fill( (alphaT,deltaPhiStar),"%s_deltaPhiStar_vs_alphaT_%s"%self.cs,
                        (500,50), (0.0,0.0),(1.0,r.TMath.Pi()),
                        title=";#alpha_{T} (using %s_{T});#Delta#phi*;events / bin"%self.letter)
#####################################
class alphaMetHistogrammer(analysisStep) :

    def __init__(self, cs = None, deltaPhiStarExtraName = "", etRatherThanPt = None, metName = None) :
        self.cs = cs
        self.letter = "E" if etRatherThanPt else "p"
        fixes = (cs[0], self.letter+"t"+cs[1])
        for var in ["Sum","AlphaT","AlphaTMet","DeltaPseudoJet"] : setattr(self,var,("%s" + var + "%s")%fixes)
        self.deltaPhiStar = "%sDeltaPhiStar%s%s"%(self.cs[0], self.cs[1], deltaPhiStarExtraName)
        self.etRatherThanPt = etRatherThanPt
        self.metName = metName
        self.moreName = "%s%s"%self.cs
        
    def uponAcceptance (self,eventVars) :
        if self.metName!=None :
            met = eventVars[self.metName].pt()
        ht  = eventVars[self.Sum]
        deltaHt = eventVars[self.DeltaPseudoJet]
        alphaT = eventVars[self.AlphaT]
        alphaTMet = eventVars[self.AlphaTMet]
        deltaPhiStar = eventVars[self.deltaPhiStar]["DeltaPhiStar"]
        
        if not alphaT : return

        self.book.fill( alphaTMet, "%sAlphaTMet%s"%self.cs, 80,0.0,2.0,
                        title = ";#alpha_{T} (using jet %s_{T}#semicolon %s);events / bin"%(self.letter,self.metName))
        
        self.book.fill( alphaTMet, "%sAlphaTMetZooom%s"%self.cs, 120, 0.48, 0.60,
                        title = ";#alpha_{T} (using jet %s_{T}#semicolon %s);events / bin"%(self.letter,self.metName))

        self.book.fill( (met/ht,deltaHt/ht), "%s_deltaHtOverHt_vs_metOverHt_%s"%self.cs, (30,30), (0.0,0.0), (1.0,0.7),
                        title = ";#slash(E_{T}) / H_{T};#Delta H_{T} of two pseudo-jets / H_{T};events / bin")

        self.book.fill( (alphaTMet,ht), "%s_Ht_vs_alphaTMet_%s"%self.cs, (300,200), (0.0,0.0), (3.0,1000),
                        title = ";#alpha_{T} (using %s_{T}#semicolon %s);H_{T};events / bin"%(self.letter,self.metName))
        
        self.book.fill( (alphaTMet,deltaPhiStar),"%s_deltaPhiStar_vs_alphaTMet_%s"%self.cs,
                        (500,50), (0.0,0.0),(1.0,r.TMath.Pi()),
                        title=";#alpha_{T} (using %s_{T}#semicolon %s);#Delta#phi*;events / bin"%(self.letter,self.metName))

        self.book.fill( (alphaT,alphaTMet), "%s_alphaTMet_vs_alphaT_%s"%self.cs, (80,80), (0.0,0.0), (2.0,2.0),
                        title = ";#alpha_{T};#alpha_{T} (from MET);events / bin")
        
        self.book.fill( (alphaT,alphaTMet), "%s_alphaTMet_zoomvs_alphaT_%s"%self.cs, (60,60), (0.48,0.48), (0.60,0.60),
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

        self.book.fill(maxCorrPt,"%sMaxCorrJetPt%s"%self.cs, 50, 0.0,350.0, title = ";leading c. %s%s's c. p_{T} (GeV);events / bin"%self.cs)
        self.book.fill(eta      ,"%sMaxCorrJetEta%s"%self.cs, 50, -5.0, 5.0, title = ";leading c. %s%s's #eta;events / bin"%self.cs)
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
            self.book.fill(maxUnCorrPt,"%sMaxUnCorrJetPt%s"%self.cs, 50, 0.0,250.0, title = ";leading u.c. %s%s's u.c. p_{T} (GeV);events / bin"%self.cs)
            bigTuple = (self.cs[0],self.cs[1],self.cs[0],self.cs[1])
            self.book.fill( (eta,maxUnCorrPt), "%sMaxUnCorrJetPtVsEta%s"%self.cs, (50, 50), (-5.0, 0.0), (5.0,250.0),
                                       title = ";leading u.c. %s%s's #eta;leading u.c. %s%s's u.c. p_{T} (GeV);events / bin"%bigTuple)

        self.book.fill(eta        ,"%sMaxUnCorrJetEta%s"%self.cs, 50, -5.0, 5.0, title = ";leading u.c. %s%s's #eta;events / bin"%self.cs)
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
        self.book.fill( eventVars[self.var]["phi"], self.var, 50, -4.0, 4.0, title = ";"+self.var+";events / bin")
        self.book.fill( eventVars[self.var]["R"]  , self.var, 20, 0.0, 10.0, title = ";"+self.var+";events / bin")
        self.book.fill( eventVars[self.var]["eta"], self.var, 50, -10, 10.0, title = ";"+self.var+";events / bin")
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
        self.book.fill(mht, "mht%s"%level, 200, 0, 500 , title = "%s;MHT (GeV);events / bin"%level)
        
        for i in range(nBad.size()) :
            sub = "barrel" if isBarrel[i] else "endcap"
            p4 = tpP4.at(i)
            self.book.fill( (p4.eta(),p4.phi()), "tpEtaPhi%d%s"%(maxStatus[i],sub), (100,100),(-4,-4),(4,4), title = "TP status%d, %s;#eta;#phi;events / bin"%(maxStatus[i],sub))
            self.book.fill( (maxStatus[i],nBad[i]), "tpStatusNbad%s"%sub, (16, 30), (-0.5,-0.5), (15.5,29.5), title="%s;TP maxStatus;TP number bad xtals;TP / bin"%sub)

            if recoverable[i] :
                self.book.fill( tpEt[i], "tpEt%d%sMatched%d"%(nBad[i],sub,matched[i]) , 256, 0, 128, title = "%d bad,%s,matched%d;tp.Et;TPs / bin"%(nBad[i],sub,matched[i]))

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


#####################################
class metVsMhtHistogrammer(analysisStep) :
    def __init__(self, mht = None, met = None) :
        self.mht = mht
        self.met = met
    
    def uponAcceptance(self,eventVars) :
        self.book.fill( (eventVars[self.mht].pt(), eventVars[self.met].pt()), "%sVs%s"%(self.mht,self.met),
                        (25, 25), (0.0, 0.0), (100.0, 100.0), title = ";MHT [%s] (GeV);MET [%s] (GeV);events / bin"%(self.mht,self.met))
#####################################
class cutBitHistogrammer(analysisStep) :
    def __init__(self, jets = None, met = None) :
        self.key = "cutBitHistogram"

        self.jets = jets
        self.met = met
        self.ht         = "%sSumEt%s"%self.jets
        self.alphaT     = "%sAlphaTEt%s"%self.jets
        self.mhtOverMet = "%sMht%s_Over_%s"%(self.jets[0], self.jets[1], self.met)
        self.binLabels = [self.binString(i) for i in range(8)]
        
    def uponAcceptance(self, eventVars) :
        passHt         = eventVars[self.ht]!=None         and eventVars[self.ht]>350.0
        passAlphaT     = eventVars[self.alphaT]!=None     and eventVars[self.alphaT]>0.55
        passMhtOverMet = eventVars[self.mhtOverMet]!=None and eventVars[self.mhtOverMet]<1.25

        value = (passHt<<0) | (passAlphaT<<1) | (passMhtOverMet<<2)
        self.book.fill(value, self.key, 8, -0.5, 7.5,
                                  title = ";HT-alphaT-MHT/MET[%s%s#semicolon %s];events/bin"%(self.jets[0], self.jets[1], self.met), xAxisLabels = self.binLabels)

    def binString(self, i) :
        out  = ""
        out += "h" if i&(1<<0) else "#slash{h}"
        out += "a" if i&(1<<1) else "#slash{a}"
        out += "m" if i&(1<<2) else "#slash{m}"
        return out
#####################################
class photon1PtOverHtHistogrammer(analysisStep) :
    def __init__(self, jets = None, photons = None, etRatherThanPt = None) :
        self.jets = jets
        self.ht = "%sSum%s%s"%(jets[0],"Et" if etRatherThanPt else "pT",jets[1])
        self.photonIndices = "%sIndices%s"%photons
        self.photonP4 = "%sP4%s"%photons
    
    def uponAcceptance(self,eventVars) :
        if not len(eventVars[self.photonIndices]) : return
        index = eventVars[self.photonIndices][0]
        self.book.fill( eventVars[self.photonP4][index].pt()/eventVars[self.ht], "photon1PtOverHt",
                        15, 0.0, 1.5, title = ";photon1 pT / HT [%s%s];events / bin"%self.jets)
#####################################
class sensitivityHistogrammer(analysisStep) :
    def __init__(self, jets = None) :
        self.jets = jets
    def uponAcceptance(self,ev) :
        indices = ev["%sIndices%s"%self.jets]
        if not indices : return

        maxAbsS = ev["%sMaxAbsMhtSensitivity%s"%self.jets]
        maxS = ev["%sMaxMhtSensitivity%s"%self.jets]
        combS = ev["%sMhtCombinedSensitivity%s"%self.jets]
        sump4 = ev["%sSumP4%s"%self.jets]
        mht = sump4.pt()
        
        self.book.fill(combS, "combinedMhtSensitivity", 100, 0, 5, title=";combined MHT Sensitivity;events / bin")
        self.book.fill((mht,combS), "combinedMhtSensitivityVMhT", (100,100), (0,0), (500,5), title=";MHT;combined MHT Sensitivity;events / bin")
        self.book.fill(maxS, "maxMhtSensitivity", 100, -2,2, title=";max MHT Sensitivity;events / bin")
        self.book.fill((mht,maxS), "maxMhtSensitivityVMHT", (100,100), (0,-2),(500,2), title=";MhT;max MHT Sensitivity;events / bin")
        self.book.fill(maxAbsS, "maxAbsSensitivity", 100, -2,2, title = ";maxAbsSensitivity;events / bin")
        self.book.fill((mht,maxAbsS), "maxAbsSensitivityVMHT", (100,100), (0,-2),(500,2), title = ";MHT;maxAbsSensitivity;events / bin")
#####################################
class longHistogrammer(analysisStep) :
    def __init__(self, jets = None) :
        self.jets = jets
    def uponAcceptance(self,ev) :
        stretch = ev["%sStretch%s"%self.jets]
        ht = ev["%sSumPt%s"%self.jets]
        zspread = ev['%sSumPz%s'%self.jets]/ht
        coslongmht = ev["%sCosLongMHT%s"%self.jets]
        mht = ev["%sSumP4%s"%self.jets].pt()
        alphaT = ev["%sAlphaTEt%s"%self.jets] # hack: hardcoded Et
        area =  ev["%sPartialSumP4Area%s"%self.jets]
        
        self.book.fill( coslongmht, "coslongmht", 100,0,1, title=";coslongmht;event / bin")
        self.book.fill( stretch, "Stretch", 100,0,1, title=";stretch;events / bin")
        self.book.fill( zspread, "Zspread", 100,0,3, title=";zspread;events / bin")
        self.book.fill( (stretch,ht), "Stretch_v_ht", (100,150), (0,0), (1,1500), title=";stretch;HT;event / bin")
        self.book.fill( (stretch,mht/ht), "Stretch_v_mhtht", (100,100), (0,0), (1,1), title=";stretch;MHT/HT;event / bin")
        self.book.fill( (stretch,zspread), "Stretch_v_zspread", (100,100), (0,0), (1,3), title=";stretch;zspread;event / bin")
        self.book.fill( (stretch,mht), "Stretch_v_mht", (100,100), (0,0), (1,800), title=";stretch;MHT;event / bin")
        self.book.fill( (stretch,coslongmht), "Stretch_v_coslongmht", (100,100),(0,0),(1,1), title=";stretch;coslongmht;event / bin")
        self.book.fill( mht, "mht", 100,0,800, title=";mht;event / bin")
        self.book.fill( (coslongmht,mht/ht), "mhtht_v_coslongmht", (100,100), (0,0), (1,1), title = ";coslongmht;mht/ht;events / bin")
        self.book.fill( (coslongmht,mht), "mht_v_coslongmht", (100,100), (0,0), (1,800), title = ";coslongmht;mht;events / bin")
        self.book.fill( (coslongmht,alphaT), "alphaT_v_coslongmht", (100,100), (0,0), (1,3), title = ";coslongmht;alphaT;events / bin")
        self.book.fill( (stretch,alphaT), "alphaT_v_stretch", (100,100), (0,0), (1,3), title = ";stretch;alphaT;events / bin")
        self.book.fill( area, "polygon_area", 100,0,100000, title=";jet Polygon Area (GeV^{2}); events / bin")
        self.book.fill( (stretch,area), "stretch_v_polygon_area",(100,100),(0,0),(1,100000),title=";stretch;jet Polygon Area (GeV^{2}); events / bin")

        
        ("CosLongMHT" ,100,0,1)
        ("Stretch"    ,100,0,1)
        ("SumPzOverHt",100,0,5)
        ("PartialSumP4AreaOverHt2",100,0,1)
        ("MHT",100,0,800)
        ("DeltaPseudoJetPt")
