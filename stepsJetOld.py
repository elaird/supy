import ROOT as r
from analysisStep import analysisStep
#####################################
class cleanJetIndexProducerOld(analysisStep) :
    """cleanJetIndexProducerOld"""

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
        
    def step1 (self,eventVars,extraVars) :
        setattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix,[])
        self.cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        setattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix,[])
        self.otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        self.p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        self.size=self.p4Vector.size()

        if not self.corrRatherThanUnCorr :
            self.corrFactorVector=eventVars[self.jetCollection+'CorrFactor'+self.jetSuffix]
        
        self.emfVector    =eventVars[self.jetCollection+'EmEnergyFraction'+self.jetSuffix]
        self.fHpdVector   =eventVars[self.jetCollection+'JetIDFHPD'+self.jetSuffix       ]
        self.n90HitsVector=eventVars[self.jetCollection+'JetIDN90Hits'+self.jetSuffix    ]
        
    def jetLoop (self,eventVars) :
        for iJet in range(self.size) :
            #pt cut
            if (self.corrRatherThanUnCorr) :
                if (self.p4Vector.at(iJet).pt()<self.jetPtThreshold) : break #assumes sorted
            else :
                corrFactor=self.corrFactorVector.at(iJet)
                if (corrFactor<self.corrFactorThreshold) : continue
                if (self.p4Vector.at(iJet).pt()/corrFactor<self.jetPtThreshold) : continue
            
            #if pass pt cut, add to "other" category
            self.otherJetIndices.append(iJet)
            
            #eta cut
            absEta=r.TMath.Abs(self.p4Vector.at(iJet).eta())
            if (absEta>self.jetEtaMax) : continue
            
            #jet ID loose cut
            #jetIDLooseVector=eventVars[self.jetCollection+'JetIDloose'+self.jetSuffix]
            #if (not jetIDLooseVector[iJet]) : continue
            
            if (absEta<=2.6) :
                if (self.emfVector.at(iJet)<=0.01) : continue
            if (self.fHpdVector.at(iJet)>=0.98) : continue
            if (self.n90HitsVector.at(iJet)<2) : continue
            #if (eventVars[self.jetCollection+'JetIDFRBX'+self.jetSuffix][iJet]>=0.98) : continue
            #if (eventVars[self.jetCollection+'Eta2Moment'+self.jetSuffix][iJet]<0.0) : continue
            #if (eventVars[self.jetCollection+'Phi2Moment'+self.jetSuffix][iJet]<0.0) : continue

            self.cleanJetIndices.append(iJet)
            self.otherJetIndices.remove(iJet)

    def select (self,eventVars,extraVars) :
        self.step1(eventVars,extraVars)
        self.jetLoop(eventVars)
        return True
#####################################
class cleanJetHtMhtProducerOld(analysisStep) :
    """cleanJetHtMhtProducerOld"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"

        self.mht=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def select (self,eventVars,extraVars) :
        self.mht.SetCoordinates(0.0,0.0,0.0,0.0)
        
        setattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix,self.mht)

        Ht=0.0
        HtEt=0.0

        p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        
        for iJet in cleanJetIndices :
            jet=p4Vector.at(iJet)
            self.mht-=jet
            Ht+=jet.pt()
            HtEt+=jet.Et()


        setattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix,Ht)
        setattr(extraVars,self.jetCollection+"HtEt"+self.jetSuffix,HtEt)

        return True
#####################################
class cleanNJetAlphaProducerOld(analysisStep) :
    """cleanNJetAlphaProducerOld"""

    def __init__(self,jetCollection,jetSuffix):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"

    def select (self,eventVars,extraVars) :
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
        p4Vector=eventVars[self.jetCollection+"CorrectedP4"+self.jetSuffix]

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
