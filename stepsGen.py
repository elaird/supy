import ROOT as r
from analysisStep import analysisStep
#####################################
pdgLookupExists=False
try:
    import pdgLookup
    pdgLookupExists=True
except ImportError:
    pass
#####################################
def makeCodes(iTry,nOps,nItems) :
    codes=[0]*nItems
    for iItem in range(nItems) :
        code=iTry-iTry%(nOps**iItem)
        code/=(nOps**iItem)
        code=code%nOps
        codes[iItem]=code
    return codes
#####################################
def makeCodeString(iTry,nOps,nItems) :
    codeList=makeCodes(iTry,nOps,nItems)
    outString=""
    for code in codeList : outString+=str(code)
    return outString
#####################################
class susyScanPointPrinter(analysisStep) :
    """susyScanPointPrinter"""

    def __init__(self) :
        self.leavesToPrint=["susyScanA0",
                            "susyScanCrossSection",
                            "susyScanM0",
                            "susyScanM12",
                            "susyScanMu",
                            "susyScanRun",
                            "susyScanTanBeta"
                            ]
        
    def uponAcceptance (self,eventVars,extraVars) :
        outString=""
        for leafName in self.leavesToPrint :
            outString+=leafName.replace("susyScan","")+" = "+str(eventVars[leafName])+"\t"
        print outString
#####################################
class genJetPrinter(analysisStep) :
    """genJetPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"

    def uponAcceptance (self,eventVars,extraVars) :
        p4Vector        =eventVars[self.jetCollection+'GenJetP4'     +self.jetSuffix]
        #emEnergy        =eventVars[self.jetCollection+'EmEnergy'        +self.jetSuffix]
        #hadEnergy       =eventVars[self.jetCollection+'HadEnergy'       +self.jetSuffix]
        #invisibleEnergy =eventVars[self.jetCollection+'InvisibleEnergy' +self.jetSuffix]
        #auxiliaryEnergy =eventVars[self.jetCollection+'AuxiliaryEnergy' +self.jetSuffix]

        #cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        #otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        print " jet   pT (GeV)    eta    phi    emF   hadF   invF   auxF"
        print "---------------------------------------------------------"
        for iJet in range(len(p4Vector)) :
            jet=p4Vector[iJet]
            totalEnergy=jet.energy()
            
            outString=" "
            #if (iJet in otherJetIndices) : outString="-"
            #if (iJet in cleanJetIndices) : outString="*"
            
            outString+=" %2d"   %iJet
            outString+="     %#6.1f"%jet.pt()
            outString+="   %#4.1f"%jet.eta()
            outString+="   %#4.1f"%jet.phi()
            #outString+="   %#4.2f"%(       emEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(      hadEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(invisibleEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(auxiliaryEnergy[iJet]/totalEnergy)
            ##outString+="  %#4.2f"%( (emEnergy[iJet]+hadEnergy[iJet]+invisibleEnergy[iJet]+auxiliaryEnergy[iJet]) / totalEnergy )
            print outString
        print
#####################################
class genParticleCounter(analysisStep) :
    """genParticleCounter"""

        self.tanBetaThreshold=0.1
        self.tanBeta=tanBeta
        self.pdgToCategory={}
        #copied from PDG
        self.initPdgToCategory(1000001,1000004,"squarkL")#left-handed
        self.initPdgToCategory(1000005,1000006,"squarkA")#ambiguous
        self.initPdgToCategory(1000011,1000016,"slepton")
        self.initPdgToCategory(2000001,2000004,"squarkR")#right-handed
        self.initPdgToCategory(2000005,2000006,"squarkA")#ambiguous
        self.initPdgToCategory(2000011,2000011,"slepton")
        self.initPdgToCategory(2000013,2000013,"slepton")
        self.initPdgToCategory(2000015,2000015,"slepton")
        self.initPdgToCategory(1000021,1000021,"gluino")
        self.initPdgToCategory(1000022,1000023,"chi0")
        self.initPdgToCategory(1000024,1000024,"chi+")
        self.initPdgToCategory(1000025,1000025,"chi0")
        self.initPdgToCategory(1000035,1000035,"chi0")
        self.initPdgToCategory(1000037,1000037,"chi+")
        self.initPdgToCategory(1000039,1000039,"gravitino")

        self.combineCategories(["squarkL","squarkR","squarkA"],"squark")
        self.combineCategories(["slepton","chi0","chi+","gravitino"],"other name")

        self.badCategoryName="no name"
        self.categories=list(set(self.pdgToCategory.values()))
        self.categories.append(self.badCategoryName)
        self.categories.sort()
        #self.printDict(self.pdgToCategory)
        self.maxCountsPerCategory=2 #0 ... this number counted explicitly; otherwise overflows

    def bookHistos(self) :
        histoBaseName="genParticleCounter"

        nCategories=len(self.categories)
        self.labelHisto=r.TH1D(histoBaseName+"CategoryLabels",";categories",nCategories,-0.5,nCategories-0.5)
        for iCategory in range(nCategories) :
            self.labelHisto.GetXaxis().SetBinLabel(iCategory+1,self.categories[iCategory])
            self.labelHisto.SetBinContent(iCategory+1,self.maxCountsPerCategory)


        #Lo and Hi are both sampled in scan
        m0Lo=0.0
        m0Hi=4000.0
        m0StepSize=50.0
        nBinsM0=int(1+(m0Hi-m0Lo)/m0StepSize)

        m12Lo=100.0
        m12Hi=600.0
        m12StepSize=20.0
        nBinsM12=int(1+(m12Hi-m12Lo)/m12StepSize)

        self.nEventsHisto=r.TH2D(histoBaseName+"nEvents",histoBaseName+"nEvents;m_{0} (GeV);m_{1/2} (GeV)",
                                 nBinsM0,m0Lo-m0StepSize/2.0,m0Hi+m0StepSize/2.0,
                                 nBinsM12,m12Lo-m12StepSize/2.0,m12Hi+m12StepSize/2.0)

        self.xsHisto=self.nEventsHisto.Clone(histoBaseName+"XS")
        self.xsHisto.SetTitle(histoBaseName+"XS")

        self.histoDictionary={}
        maxHistos=(self.maxCountsPerCategory+2)**nCategories
        for iHisto in range(maxHistos) :
            codeString=makeCodeString(iHisto,self.maxCountsPerCategory+2,nCategories)
            self.histoDictionary[codeString]=self.xsHisto.Clone(histoBaseName+codeString)
            self.histoDictionary[codeString].SetTitle(histoBaseName+codeString)

    def combineCategories(self,someList,someLabel) :
        for key in self.pdgToCategory :
            if self.pdgToCategory[key] in someList :
                self.pdgToCategory[key]=someLabel
        
    def printDict(self,someDict) :
        for key in someDict :
            print key,someDict[key]

    def initPdgToCategory(self,lower,upper,label) :
        for i in range(lower,upper+1) :
            self.pdgToCategory[i]=label
        for i in range(-upper,-lower+1) :
            self.pdgToCategory[i]=label

    def zeroCategoryCounts(self,extraVars) :
        extraVars.categoryCounts={}
        for key in self.categories :
            extraVars.categoryCounts[key]=0

    def isSusy(self,pdgId) :
        reducedPdgId=abs(pdgId)/1000000
        #if (reducedPdgId==2) : print "isSusy(",pdgId,"):",reducedPdgId,reducedPdgId==1 or reducedPdgId==2
        return reducedPdgId==1 or reducedPdgId==2

    def incrementCategory(self,pdgId,extraVars) :
        if pdgId in self.pdgToCategory:
            category=self.pdgToCategory[pdgId]
        else :
            category=self.badCategoryName
        extraVars.categoryCounts[category]+=1
        #print "found one:",iParticle,pdgId

    def doCounting (self,eventVars,extraVars) :
        self.zeroCategoryCounts(extraVars)

        if not eventVars["genHandleValid"] : return
        #print dir(eventVars)
        nParticles=len(eventVars["genPdgId"])
        for iParticle in range(nParticles) :
            #consider only status 3 particles
            if eventVars["genStatus"].at(iParticle)!=3 : continue
            #which are SUSY particles
            if not self.isSusy(eventVars["genPdgId"].at(iParticle)) : continue
            #which have mothers
            if not eventVars["genHasMother"].at(iParticle) : continue
            #which are stored
            if not eventVars["genMotherStored"].at(iParticle) : continue
            motherIndex=eventVars["genMother"].at(iParticle)
            if (motherIndex<0) : continue
            #and are not SUSY particles
            if self.isSusy(eventVars["genPdgId"].at(motherIndex)) : continue
        
            pdgId=eventVars["genPdgId"].at(iParticle)
            self.incrementCategory(pdgId,extraVars)
        #self.printDict(extraVars.categoryCounts)
        
    def fillHistograms (self,eventVars,extraVars) :
        if abs(eventVars["susyScanTanBeta"]-self.tanBeta)>self.tanBetaThreshold : return

        #make code string
        codeString=""
        for category in self.categories :
            count=extraVars.categoryCounts[category]
            if count>self.maxCountsPerCategory :
                count=self.maxCountsPerCategory+1
            codeString+=str(count)

        #get scan point info
        xs=eventVars["susyScanCrossSection"]
        m0=eventVars["susyScanM0"]
        m12=eventVars["susyScanM12"]

        #fill histos
        self.histoDictionary[codeString].Fill(m0,m12)
        self.nEventsHisto.Fill(m0,m12)
        self.xsHisto.Fill(m0,m12,xs)
        
    def uponAcceptance (self,eventVars,extraVars) :
        self.doCounting(eventVars,extraVars)
        self.fillHistograms(eventVars,extraVars)
#####################################
class genParticleCounterOld(analysisStep) :
    """genParticleCounterOld"""

    def __init__(self):
        self.d={}

        for i in range(1000001,1000005) : self.d[i]="q~_L"
        for i in range(1000005,1000007) : self.d[i]="q~_A"
        for i in range(2000001,2000005) : self.d[i]="q~_R"
        for i in range(2000005,2000007) : self.d[i]="q~_A"
        self.d[1000021]="g~"
        
    def uponAcceptance (self,eventVars,extraVars) :
        extraVars.particleCounts={}
        extraVars.particleCounts["q~_L"]=0
        extraVars.particleCounts["q~_R"]=0
        extraVars.particleCounts["q~_A"]=0
        extraVars.particleCounts["g~"  ]=0

        for pdgId in eventVars["genPdgId"] :
            if pdgId in self.d :
                category=self.d[pdgId]
                if (not category in extraVars.particleCounts) :
                    extraVars.particleCounts[category]=1
                else :
                    extraVars.particleCounts[category]+=1                

        for key in extraVars.particleCounts :
            counts=extraVars.particleCounts[key]
            if (counts>0) : print key,counts
#####################################
class genParticlePrinter(analysisStep) :
    """genParticlePrinter"""

    def __init__(self):
        self.oneP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.sumP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        
    def uponAcceptance (self,eventVars,extraVars) :

        self.sumP4.SetCoordinates(0.0,0.0,0.0,0.0)

        mothers=set(eventVars["genMother"])
        print "mothers: ",mothers
        print "---------------------------------------------------------------------------"
        print " i  st    mo         id            name        E        pt       eta    phi"
        print "---------------------------------------------------------------------------"

        size=len(eventVars["genP4"])
        for iGen in range(size) :
            p4=eventVars["genP4"][iGen]
            pdgId=eventVars["genPdgId"][iGen]
            outString=""
            outString+="%#2d"%iGen
            outString+=" %#3d"%eventVars["genStatus"][iGen]
            outString+="  %#4d"%eventVars["genMother"][iGen]
            outString+=" %#10d"%pdgId
            if (pdgLookupExists) : outString+=" "+pdgLookup.pdgid_to_name(pdgId).rjust(15)
            else :                 outString+="".rjust(16)
            outString+="  %#7.1f"%p4.E()
            outString+="  %#8.1f"%p4.pt()
            outString+="  %#8.1f"%p4.eta()
            outString+="  %#5.1f"%p4.phi()
        
            if (not (iGen in mothers)) :
                outString+="   non-mo"
        #        self.sumP4+=self.oneP4
        #        #outString2="non-mo P4 sum".ljust(37)
        #        #outString2+="  %#7.1f"%self.sumP4.E()
        #        #outString2+="  %#8.1f"%self.sumP4.eta()
        #        #outString2+="  %#8.1f"%self.sumP4.pt()
        #        #outString2+="  %#5.1f"%self.sumP4.phi()
        #        #print outString2
        #
            print outString
        #
        #outString="non-mo P4 sum".ljust(37)
        #outString+="  %#7.1f"%self.sumP4.E()
        #outString+="  %#8.1f"%self.sumP4.eta()
        #outString+="  %#8.1f"%self.sumP4.pt()
        #outString+="  %#5.1f"%self.sumP4.phi()
        #print outString
        print
#####################################
class cleanGenJetIndexProducer(analysisStep) :
    """cleanGenJetIndexProducer"""

    def __init__(self,jetCollection,jetSuffix,jetPtThreshold,jetEtaMax):
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.jetPtThreshold=jetPtThreshold
        self.jetEtaMax=jetEtaMax
        
        self.moreName="("+self.jetCollection+"; "+self.jetSuffix
        self.moreName+="; pT>="+str(self.jetPtThreshold)+" GeV"
        self.moreName+="; |eta|<="+str(self.jetEtaMax)
        self.moreName+=")"
        
    def step1 (self,eventVars,extraVars) :
        setattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix,[])
        self.cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        setattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix,[])
        self.otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        self.p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        self.size=self.p4Vector.size()

    def jetLoop (self,eventVars) :
        for iJet in range(self.size) :
            #pt cut
            if (self.p4Vector[iJet].pt()<self.jetPtThreshold) : break #assumes sorted
            
            #if pass pt cut, add to "other" category
            self.otherJetIndices.append(iJet)
            
            #eta cut
            absEta=r.TMath.Abs(self.p4Vector[iJet].eta())
            if (absEta>self.jetEtaMax) : continue
            
            self.cleanJetIndices.append(iJet)
            self.otherJetIndices.remove(iJet)

    def select (self,eventVars,extraVars) :
        self.step1(eventVars,extraVars)
        self.jetLoop(eventVars)
        return True
#####################################
