import time
import ROOT as r
from base import analysisStep
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

    def uponAcceptance (self,chain,chainVars,extraVars) :
        if (self.nTotal==self.num) :
            self.num=self.factor*self.num
            toPrint="event "+str(self.nTotal).rjust(self.integerWidth," ")
            toPrint=toPrint.ljust(self.docWidth+self.moreWidth+1)+time.ctime()
            if (self.num==self.factor or self.num>self.cut) :
                print toPrint
#####################################
class eventPrinter(analysisStep) :
    """eventPrinter"""

    def __init__(self) :
        self.neededBranches=["run","event","lumiSection","bx"]
        self.nHyphens=56

    def uponAcceptance(self,chain,chainVars,extraVars) :
        print
        print "".ljust(self.nHyphens,"-")
        outString ="run %7d"%chain.run
        outString+="; event %10d"%chain.event
        outString+="; ls %#5d"%chain.lumiSection
        outString+="; bx %4d"%chain.bx
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

        self.neededBranches=[]
        self.neededBranches.append(self.jetCollection+'CorrectedP4'     +self.jetSuffix)
        self.neededBranches.append(self.jetCollection+'CorrFactor'      +self.jetSuffix)
        self.neededBranches.append(self.jetCollection+'EmEnergyFraction'+self.jetSuffix)
        self.neededBranches.append(self.jetCollection+'JetIDFHPD'       +self.jetSuffix)
        self.neededBranches.append(self.jetCollection+"JetIDN90Hits"    +self.jetSuffix)

    def uponAcceptance (self,chain,chainVars,extraVars) :
        p4Vector        =getattr(chainVars,self.jetCollection+'CorrectedP4'     +self.jetSuffix)
        corrFactorVector=getattr(chainVars,self.jetCollection+'CorrFactor'      +self.jetSuffix)
        jetEmfVector    =getattr(chainVars,self.jetCollection+'EmEnergyFraction'+self.jetSuffix)
        jetFHpdVector   =getattr(chainVars,self.jetCollection+'JetIDFHPD'       +self.jetSuffix)
        jetN90Vector    =getattr(chainVars,self.jetCollection+'JetIDN90Hits'    +self.jetSuffix)

        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)

        for iJet in range(len(p4Vector)) :
            jet=p4Vector[iJet]

            outString=" "
            if (iJet in otherJetIndices) : outString="-"
            if (iJet in cleanJetIndices) : outString="*"
            
            outString+=" j%2d"                %iJet
            outString+="; pT %#6.1f GeV"      %jet.pt()
            outString+="; eta %#4.1f"         %jet.eta()
            outString+="; phi %#4.1f"         %jet.phi()
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
        
    def uponAcceptance(self,chain,chainVars,extraVars) :
        outString ="HT %#6.1f GeV"   %getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        outString+="; MHT %#6.1f GeV"%getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix).pt()
        print outString
#####################################
class diJetAlphaPrinter(analysisStep) :
    """diJetAlphaPrinter"""

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        
    def uponAcceptance(self,chain,chainVars,extraVars) :
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
        
    def uponAcceptance(self,chain,chainVars,extraVars) :
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
        p4Vector=getattr(chainVars,self.collection+'P4'+self.suffix)

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
            metVector=getattr(chainVars,met)
            outString=met.ljust(15)
            outString+=" pT %#6.1f GeV"%metVector.pt()
            outString+="; phi %#4.1f"  %metVector.phi()
            print outString
        print
        return True
#####################################
