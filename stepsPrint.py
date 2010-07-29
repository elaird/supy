import time
import ROOT as r
from analysisStep import analysisStep
#####################################
class progressPrinter(analysisStep) :
    """progressPrinter"""

    def __init__(self,factor,cut):
        self.num=1
        self.factor=factor
        self.cut=cut
        self.moreName="("
        self.moreName+=str(self.factor)+","
        self.moreName+=str(self.cut)+")"
        self.neededBranches=[]

    def uponAcceptance (self,eventVars,extraVars) :
        if (self.nTotal==self.num) :
            self.num=self.factor*self.num
            toPrint="event "+str(self.nTotal).rjust(self.integerWidth," ")
            toPrint=toPrint.ljust(self.docWidth+self.moreWidth+1)+time.ctime()
            if (self.num==self.factor or self.num>self.cut) and not self.quietMode :
                print toPrint
#####################################
class eventPrinter(analysisStep) :
    """eventPrinter"""

    def __init__(self) :
        self.nHyphens=56

    def uponAcceptance(self,eventVars,extraVars) :
        print
        print "".ljust(self.nHyphens,"-")
        outString ="run %7d"%eventVars["run"]
        outString+="  event %10d"%eventVars["event"]
        outString+="  ls %#5d"%eventVars["lumiSection"]
        outString+="  bx %4d"%eventVars["bunch"]
        print outString
#####################################
class jetPrinter(analysisStep) :
    """jetPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"

    def uponAcceptance (self,eventVars,extraVars) :
        p4Vector        =eventVars[self.jetCollection+'CorrectedP4'     +self.jetSuffix]
        corrFactorVector=eventVars[self.jetCollection+'CorrFactor'      +self.jetSuffix]
        jetEmfVector    =eventVars[self.jetCollection+'EmEnergyFraction'+self.jetSuffix]
        jetFHpdVector   =eventVars[self.jetCollection+'JetIDFHPD'       +self.jetSuffix]
        jetN90Vector    =eventVars[self.jetCollection+'JetIDN90Hits'    +self.jetSuffix]

        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        print " jet   u. pT (GeV)   c. pT (GeV)    eta   phi"
        print "---------------------------------------------"
        for iJet in range(len(p4Vector)) :
            jet=p4Vector[iJet]

            outString=" "
            if (iJet in otherJetIndices) : outString="-"
            if (iJet in cleanJetIndices) : outString="*"
            
            outString+=" %2d"   %iJet
            outString+="        %#6.1f"%(jet.pt()/corrFactorVector[iJet])
            outString+="        %#6.1f"%jet.pt()
            outString+="   %#4.1f"%jet.eta()
            outString+="  %#4.1f"%jet.phi()
            outString+="; corr factor %#5.1f" %corrFactorVector[iJet]
            outString+="; EMF %#6.3f"         %jetEmfVector[iJet]
            outString+="; fHPD %#6.3f"        %jetFHpdVector[iJet]
            outString+="; N90 %#2d"           %jetN90Vector[iJet]
            print outString
        print
#####################################
class htMhtPrinter(analysisStep) :
    """htMhtPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        
    def uponAcceptance(self,eventVars,extraVars) :
        outString ="HT %#6.1f GeV"   %getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        outString+="; MHT %#6.1f GeV"%getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix).pt()
        print outString
#####################################
class diJetAlphaPrinter(analysisStep) :
    """diJetAlphaPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        
    def uponAcceptance(self,eventVars,extraVars) :
        outString ="di-jet minPt %#6.1f GeV" %getattr(extraVars,self.jetCollection+"diJetMinPt"+self.jetSuffix)
        outString+="; di-jet m %#6.1f GeV"   %getattr(extraVars,self.jetCollection+"diJetM"    +self.jetSuffix)
        outString+="; di-jet alpha  %#6.3f"  %getattr(extraVars,self.jetCollection+"diJetAlpha"+self.jetSuffix)
        print outString
#####################################
class nJetAlphaTPrinter(analysisStep) :
    """nJetAlphaTPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        
    def uponAcceptance(self,eventVars,extraVars) :
        outString ="n-jet deltaHT %#6.3f"  %getattr(extraVars,self.jetCollection+"nJetDeltaHt"+self.jetSuffix)
        outString+=";  n-jet alphaT %#6.3f"%getattr(extraVars,self.jetCollection+"nJetAlphaT"+self.jetSuffix)
        print outString
#####################################
class particleP4Printer(analysisStep) :
    """particleP4Printer"""

    def __init__(self,collection,suffix) :
        self.collection=collection
        self.suffix=suffix
        self.moreName="("
        self.moreName+=self.collection
        self.moreName+="; "
        self.moreName+=self.suffix
        self.moreName+=")"
        self.nHyphens=56
        self.neededBranches=[]
        self.neededBranches.append(self.collection+'P4'+self.suffix)

    def select (self,chain,chainVars,extraVars) :
        p4Vector=eventVars[self.collection+'P4'+self.suffix]

        nParticles=len(p4Vector)
        for iParticle in range(nParticles) :
            particle=p4Vector[iParticle]

            outString =self.collection+" %2d" %iParticle
            outString+="; pT %#6.1f GeV"      %particle.pt()
            outString+="; eta %#4.1f"         %particle.eta()
            outString+="; phi %#4.1f"         %particle.phi()
            print outString

        if (nParticles>0) : print
        else :
            print "no "+self.collection+"s"

        return True
#####################################
class metPrinter(analysisStep) :
    """metPrinter"""

    def __init__(self,collections) :
        self.collections=collections
        self.moreName="("
        self.moreName+=str(self.collections)
        self.moreName+=")"
        self.nHyphens=56
        self.neededBranches=self.collections

    def select (self,chain,chainVars,extraVars) :
        print
        for met in self.collections :
            metVector=eventVars[met]
            outString=met.ljust(15)
            outString+=" pT %#6.1f GeV"%metVector.pt()
            outString+="; phi %#4.1f"  %metVector.phi()
            print outString
        print
        return True
#####################################
class nFlaggedRecHitFilter(analysisStep) :
    """nFlaggedRecHitFilter"""

    def __init__(self,algoType,detector,nFlagged) :
        self.algoType=algoType
        self.detector=detector
        self.nFlagged=nFlagged
        self.neededBranches=["rechit"+self.algoType+"P4"+self.detector]

    def select(self,chain,chainVars,extraVars) :
        return len(getattr(chainVars,"rechit"+self.algoType+"P4"+self.detector))>=self.nFlagged

#####################################
class recHitPrinter(analysisStep) :
    """recHitPrinter"""

    def __init__(self,algoType,detector) :
        self.algoType=algoType
        self.detector=detector
        self.neededBranches=["rechit"+self.algoType+"P4"+self.detector]
        if (self.algoType=="Calo") : self.neededBranches.append("rechitCaloFlagWord"+self.detector)

        self.sum=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.bitInfo=[]
        if   detector=="Hbhe" :
            self.bitInfo=[("mult.flag",0),
                          ("ps.flag"  ,1)
                          ]
        elif detector=="Hf" :
            self.bitInfo=[("re.flag",31)]

    def bitSet(self,word,bit) :
        return (word&(1<<bit))>>bit
    
    def makeString(self,i,p4,word) :
        outString=""
        outString+=" %3d     "%i
        outString+="  %#7.1f"%p4.pt()
        outString+="               %#7.2f"%p4.eta()
        outString+=" %#5.2f"%p4.phi()

        for i in range(len(self.bitInfo)) :
            outString+="%14d"%self.bitSet(word,self.bitInfo[i][1])
        return outString
    
    def uponAcceptance(self,chain,chainVars,extraVars) :
        flaggedP4s=getattr(chainVars,"rechit"+self.algoType+"P4"+self.detector)

        print "flagged "+self.detector+" RecHits"
        someString="   i      pT (GeV)                  eta   phi"
        hypens    ="---------------------------------------------"
        for tuple in self.bitInfo :
            someString+=tuple[0].rjust(15)
            hypens+="".rjust(15,"-")
        print someString
        print hypens

        self.sum.SetCoordinates(0.0,0.0,0.0,0.0)
        nFlagged=len(flaggedP4s)
        for i in range(nFlagged) :
            flaggedP4=flaggedP4s[i]
            flagWord=0
            if (self.algoType=="Calo") : flagWord=getattr(chainVars,"rechitCaloFlagWord"+self.detector)[i]
            print self.makeString(i,flaggedP4,flagWord)
            self.sum+=flaggedP4

        if (nFlagged>1) :
            print "(sum)",self.makeString(0,self.sum,0)[6:50]
#####################################
class recHitHistogrammer(analysisStep) :
    """recHitHistogrammer"""

    def __init__(self,algoType,detector,jetCollection,jetSuffix) :
        self.algoType=algoType
        self.detector=detector
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.neededBranches=["rechit"+self.algoType+"P4"+self.detector]
        self.neededBranches.append(self.jetCollection+"CorrectedP4"+self.jetSuffix)
        
    def bookHistos(self) :
        self.ptMaxHisto1=r.TH1D("ptMaxHisto1"+self.algoType+self.detector,"ptMaxHisto1"+self.algoType+self.detector,100,0.0,200.0)
        self.ptMaxHisto2=r.TH1D("ptMaxHisto2"+self.algoType+self.detector,"ptMaxHisto2"+self.algoType+self.detector,100,0.0,200.0)
        self.ptSumHisto1=r.TH1D("ptSumHisto1"+self.algoType+self.detector,"ptSumHisto1"+self.algoType+self.detector,100,0.0,200.0)
        self.ptSumHisto2=r.TH1D("ptSumHisto2"+self.algoType+self.detector,"ptSumHisto2"+self.algoType+self.detector,100,0.0,200.0)

        self.sumVsPtHisto=r.TH2D("sumVsPtHisto"+self.algoType+self.detector,
                                 "sumVsPtHisto"+self.algoType+self.detector,
                                 100,0.0,200.0,
                                 100,0.0,200.0)
    
    def select(self,chain,chainVars,extraVars) :
        flaggedP4s=getattr(chainVars,"rechit"+self.algoType+"P4"+self.detector)
        leadingJetPt=getattr(chainVars,self.jetCollection+"CorrectedP4"+self.jetSuffix)[0].pt()
        
        pTs=[]
        nFlagged=len(flaggedP4s)
        for i in range(nFlagged) :
            pTs.append(flaggedP4s[i].pt())

        if len(pTs)==0 : pTs=[0.0]
        maxPt=max(pTs)
        sumPt=sum(pTs)

        self.sumVsPtHisto.Fill(leadingJetPt,sumPt)
        
        if leadingJetPt<30.0 :
            self.ptMaxHisto1.Fill(maxPt)
            self.ptSumHisto1.Fill(sumPt)
        elif leadingJetPt>60.0 :
            self.ptMaxHisto2.Fill(maxPt)
            self.ptSumHisto2.Fill(sumPt)

        #special silliness
        if leadingJetPt<70.0 : return False
        if sumPt<70.0 : return False

        return True
        #for i in range(nFlagged) :
        #    hit=flaggedP4s[i]
        #    print "hit:",i,hit.pt(),hit.eta(),hit.phi()
        #
        #jets=getattr(chainVars,self.jetCollection+"CorrectedP4"+self.jetSuffix)
        #for iJet in range(len(jets)) :
        #    jet=jets[iJet]
        #    print "jet:",iJet,jet.pt(),jet.eta(),jet.phi()

#####################################
