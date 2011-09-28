import time,utils
import ROOT as r
from core.analysisStep import analysisStep
#####################################
class progressPrinter(analysisStep) :

    def __init__(self,suppressionFactor=2,suppressionOffset=300):
        self.nTotal=0
        self.num=1
        self.suppressionFactor=suppressionFactor
        self.suppressionOffset=suppressionOffset
        self.moreName = "factor=%d, offset=%d"%(self.suppressionFactor,self.suppressionOffset)

    def uponAcceptance (self,eventVars) :
        self.nTotal+=1
        if self.nTotal!=self.num : return
        self.num=self.suppressionFactor*self.num
        toPrint="event "+str(self.nTotal).rjust(self.integerWidth," ")
        toPrint=toPrint.ljust(self.docWidth+self.moreWidth+1)+time.ctime()
        if (self.num==self.suppressionFactor or self.num>self.suppressionOffset) and not self.quietMode :
            print toPrint
#####################################
class printstuff(analysisStep) :

    def __init__(self,stuff) :
        self.stuff = stuff
        self.moreName = "print all in %s" % str(stuff)
        print '\t'.join(stuff)
        
    def uponAcceptance(self,eventVars) :
        print '\t'.join([str(eventVars[s]) for s in self.stuff])
#####################################
class eventPrinter(analysisStep) :

    def __init__(self) :
        self.nHyphens=56

    def uponAcceptance(self,eventVars) :
        print
        print "".ljust(self.nHyphens,"-")
        outString ="run %7d"%eventVars["run"]
        outString+="  event %10d"%eventVars["event"]
        outString+="  ls %#5d"%eventVars["lumiSection"]
        outString+="  bx %4d"%eventVars["bunch"]
        print outString
#####################################
class electronPrinter(analysisStep) :
    def __init__(self,cs, id=None) :
        self.cs = cs
        self.id = id
        self.moreName = "%s%s"%cs
    def uponAcceptance(self,eventVars) :
        p4s = eventVars["%sP4%s"%self.cs]
        indices = eventVars["%sIndices%s"%self.cs]
        indicesOther = eventVars["%sIndicesOther%s"%self.cs]
        id = eventVars["%sID%s%s"%(self.cs[0],self.id,self.cs[1])]
        cIso = eventVars["%sIsoCombined%s"%self.cs]
        hoe = eventVars["%sHcalOverEcal%s"%self.cs]
        dphi=eventVars["%sDeltaPhiSuperClusterTrackAtVtx%s"%self.cs]
        deta=eventVars["%sDeltaEtaSuperClusterTrackAtVtx%s"%self.cs]
        inin = eventVars["%sSigmaIetaIeta%s"%self.cs]
        
        print
        print "(%d, %d, %d) electrons" % (eventVars["run"], eventVars["lumiSection"], eventVars["event"] )
        print '\t'.join([" ","  pT","  eta","  phi","  cIso","  hoe","  deta","  dphi","  inin"])
        print "-------------------------------------------------------------------------"
        for i in range(len(p4s)) :
            p4 = p4s[i]
            symbol = "-" if i in indicesOther else \
                     "*" if i in indices else \
                     " "
            print '\t'.join([symbol,
                             "%.1f"%p4.pt(),
                             "%+.1f"%p4.eta(),
                             "%+.1f"%p4.phi(),
                             str(cIso[i])[:6],
                             "%.5f"%hoe[i],
                             "%+.5f"%deta[i],
                             "%+.5f"%dphi[i],
                             "%.5f"%inin[i]])
#####################################
class jetPrinter(analysisStep) :

    def __init__(self,cs) :
        self.cs = cs
        self.cs2 = (cs[0].replace("xc",""),cs[1])
        self.moreName="%s %s"%cs
        
    def uponAcceptance (self,eventVars) :

        isPf = "PF" in self.cs[0]
        p4Vector        =eventVars['%sCorrectedP4%s'     %self.cs]
        corrFactorVector=eventVars['%sCorrFactor%s'      %self.cs2]

        if not isPf :
            jetEmfVector    =eventVars['%sEmEnergyFraction%s'%self.cs2]
            jetFHpdVector   =eventVars['%sJetIDFHPD%s'       %self.cs2]
            jetN90Vector    =eventVars['%sJetIDN90Hits%s'    %self.cs2]

        jetIndices = eventVars["%sIndices%s"%self.cs]
        jetIndicesOther = eventVars["%sIndicesOther%s"%self.cs]

        print " jet   u. pT (GeV)   c. pT (GeV)    eta   phi"
        print "---------------------------------------------"
        for iJet in range(len(p4Vector)) :
            jet=p4Vector[iJet]

            outString = "-" if iJet in jetIndicesOther else \
                        "*" if iJet in jetIndices else \
                        " "
            outString+=" %2d"   %iJet
            outString+="        %#6.1f"%(jet.pt()/corrFactorVector[iJet])
            outString+="        %#6.1f"%jet.pt()
            outString+="   %#4.1f"%jet.eta()
            outString+="  %#4.1f"%jet.phi()
            outString+="; corr factor %#5.1f" %corrFactorVector[iJet]

            if not isPf :
                outString+="; EMF %#6.3f"         %jetEmfVector[iJet]
                outString+="; fHPD %#6.3f"        %jetFHpdVector[iJet]
                outString+="; N90 %#2d"           %jetN90Vector[iJet]
            print outString
        print
#####################################
class vertexPrinter(analysisStep) :
    def uponAcceptance(self, eventVars) :
        for i in range(eventVars["vertexNdof"].size()) :
            good = "*" if i in eventVars["vertexIndices"] else "-"
            print "%s vertex %d: sumPt %g GeV; z = %g cm"%(good,i,eventVars["vertexSumPt"].at(i),eventVars["vertexPosition"].at(i).z())
        print
#####################################
class htMhtPrinter(analysisStep) :

    def __init__(self, cs, etRatherThanPt = False ) :
        self.cs = cs
        self.htName = "%sSumPt%s"%self.cs if not etRatherThanPt else  "%sSumEt%s"%self.cs
        self.mhtName = "%sSumP4%s"%self.cs
    def uponAcceptance(self,eventVars) :
        outString ="HT %#6.3f GeV"   %eventVars[self.htName]
        outString+="; MHT %#6.3f GeV"%eventVars[self.mhtName].pt()
        print outString
#####################################
class diJetAlphaPrinter(analysisStep) :

    def __init__(self,jets) :
        self.jetCollection=jets[0]
        self.jetSuffix=jets[1]
        
    def uponAcceptance(self,eventVars) :
        outString="di-jet alpha  %#6.3f"%eventVars[self.jetCollection+"DiJetAlpha"+self.jetSuffix]
        print outString
#####################################
class alphaTPrinter(analysisStep) :
    def __init__(self,jets,etRatherThanPt) :
        fixes = (jets[0], ("Et" if etRatherThanPt else "Pt")+jets[1])
        for var in ["AlphaT","DeltaPseudoJet"] : setattr(self,var,("%s"+var+"%s")%fixes)
    def uponAcceptance(self,eV) :
        print "n-jet deltaHT %#6.3f;  n-jet alphaT %#6.3f" % (ev[self.DeltaPseudoJet],ev[self.AlphaT])
#####################################
class particleP4Printer(analysisStep) :

    def __init__(self,cs) :
        self.cs = cs
        self.moreName="%s %s" %self.cs
        self.nHyphens=56
        self.p4Name = "%sP4%s"%self.cs
    def select (self,eventVars) :
        p4Vector=eventVars[self.p4Name]

        nParticles=len(p4Vector)
        for iParticle in range(nParticles) :
            particle=p4Vector[iParticle]

            outString = "%s%s %2d" %(self.cs[0],self.cs[1],iParticle)
            outString+="; pT %#6.1f GeV"      %particle.pt()
            outString+="; eta %#6.3f"         %particle.eta()
            outString+="; phi %#6.3f"         %particle.phi()
            print outString

        if nParticles>0 : print
        else :            print "no %s%s found"%self.cs

        return True
#####################################
class metPrinter(analysisStep) :

    def __init__(self,collections) :
        self.collections=collections
        self.moreName = str(self.collections)
        self.nHyphens=56

    def select (self,eventVars) :
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

    def __init__(self,algoType,detector,nFlagged) :
        self.algoType=algoType
        self.detector=detector
        self.nFlagged=nFlagged
        self.p4String="rechit"+self.algoType+"P4"+self.detector

    def select(self,eventVars) :
        return len(eventVars[self.p4String])>=self.nFlagged
#####################################
class recHitPrinter(analysisStep) :

    def __init__(self,algoType,detector) :
        self.algoType=algoType
        self.detector=detector

        self.sum=utils.LorentzV()
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
        outString+="               %#7.4f"%p4.eta()
        outString+=" %#5.2f"%p4.phi()

        for i in range(len(self.bitInfo)) :
            outString+="%14d"%self.bitSet(word,self.bitInfo[i][1])
        return outString
    
    def uponAcceptance(self,eventVars) :
        flaggedP4s=eventVars["rechit"+self.algoType+"P4"+self.detector]

        print "flagged "+self.detector+" RecHits"
        someString="   i      pT (GeV)                  eta   phi"
        hyphens    ="---------------------------------------------"
        for tuple in self.bitInfo :
            someString+=tuple[0].rjust(15)
            hyphens+="".rjust(15,"-")
        print someString
        print hyphens

        self.sum.SetCoordinates(0.0,0.0,0.0,0.0)
        nFlagged=len(flaggedP4s)
        for i in range(nFlagged) :
            flaggedP4=flaggedP4s[i]
            flagWord=0
            if (self.algoType=="Calo") : flagWord=eventVars["rechitCaloFlagWord"+self.detector][i]
            print self.makeString(i,flaggedP4,flagWord)
            self.sum+=flaggedP4

        if (nFlagged>1) :
            print "(sum)",self.makeString(0,self.sum,0)[6:50]
#####################################
class recHitHistogrammer(analysisStep) :

    def __init__(self,algoType,detector,jetCollection,jetSuffix) :
        self.algoType=algoType
        self.detector=detector
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
    
    def select(self,eventVars) :
        flaggedP4s=eventVars["rechit"+self.algoType+"P4"+self.detector]
        leadingJetPt=eventVars[self.jetCollection+"CorrectedP4"+self.jetSuffix][0].pt()
        
        pTs=[]
        nFlagged=len(flaggedP4s)
        for i in range(nFlagged) :
            pTs.append(flaggedP4s[i].pt())

        if len(pTs)==0 : pTs=[0.0]
        maxPt=max(pTs)
        sumPt=sum(pTs)

        self.sumVsPtHisto.Fill
        self.sumVsPtHisto=r.TH2D((leadingJetPt,sumPt),"sumVsPtHisto"+self.algoType+self.detector,
                                 (100,100),
                                 (0.0,0.0),
                                 (200.0,200.0),
                                 "sumVsPtHisto"+self.algoType+self.detector,
                                 )
        
        if leadingJetPt<30.0 :
            self.book.fill(maxPt,"ptMaxHisto1"+self.algoType+self.detector,100,0.0,200.0,"ptMaxHisto1"+self.algoType+self.detector)
            self.book.fill(sumPt,"ptSumHisto1"+self.algoType+self.detector,100,0.0,200.0,"ptSumHisto1"+self.algoType+self.detector)
            self.ptSumHisto1.Fill(sumPt)
        elif leadingJetPt>60.0 :
            self.book.fill(maxPt,"ptMaxHisto2"+self.algoType+self.detector,100,0.0,200.0,"ptMaxHisto2"+self.algoType+self.detector)
            self.book.fill(sumPt,"ptSumHisto2"+self.algoType+self.detector,100,0.0,200.0,"ptSumHisto2"+self.algoType+self.detector)

        #special silliness
        if leadingJetPt<70.0 : return False
        if sumPt<70.0 : return False

        return True
        #for i in range(nFlagged) :
        #    hit=flaggedP4s[i]
        #    print "hit:",i,hit.pt(),hit.eta(),hit.phi()
        #
        #jets=eventVars[self.jetCollection+"CorrectedP4"+self.jetSuffix]
        #for iJet in range(len(jets)) :
        #    jet=jets[iJet]
        #    print "jet:",iJet,jet.pt(),jet.eta(),jet.phi()

#####################################
