import ROOT as r
from base import analysisStep
import math
#####################################
class physicsDeclared(analysisStep) :
    """physicsDeclared"""

    def __init__(self) :
        self.neededBranches=["physicsDeclared"]

    def select (self,chain,chainVars,extraVars) :
        return chain.physicsDeclared
#####################################
class techBitFilter(analysisStep) :
    """techBitFilter"""

    def __init__(self,bitList,acceptRatherThanReject) :
        self.neededBranches=["l1techbits"]
        self.bitList=bitList
        self.accept=acceptRatherThanReject

        self.moreName=""
        if (self.accept) : self.moreName+="any "
        else :             self.moreName+="no  "
        self.moreName+="tech. bit in ["
        for i in range(len(self.bitList)) :
            self.moreName+=str(self.bitList[i])
            if (i!=len(self.bitList)-1) : self.moreName+=","
            else : self.moreName+="]"
        
    def select (self,chain,chainVars,extraVars) :
        l1techbits=chainVars.l1techbits
        anyBitInList=False
        for bit in self.bitList:
            if l1techbits[bit] :
                anyBitInList=True
                break

        return not (anyBitInList ^ self.accept)
#####################################
class triggerTest(analysisStep) :
    """triggerTest"""

    def __init__(self) :
        self.neededBranches=["l1physbits","l1techbits","L1triggered"]

    def select (self,chain,chainVars,extraVars) :
        #print chain.l1techbits[9],chain.L1triggered["L1Tech_HCAL_HF_totalOR_minBias.v0"]
        print "bit 9=",chain.l1techbits[9],"; v0=",chain.L1triggered["L1Tech_HCAL_HF_coincidence_PM.v0"],"; v1=",chain.L1triggered["L1Tech_HCAL_HF_coincidence_PM.v1"]
        return True
#####################################
class triggerNameDump(analysisStep) :
    """triggerNameDump"""

    def __init__(self,triggerLevel):
        self.var=""
        if (triggerLevel=="L1") : self.var="L1"
        self.neededBranches=[self.var+"triggered"]
        self.moreName="("+triggerLevel+")"

    def select (self,chain,chainVars,extraVars) :
        chain.Scan(self.var+"triggered.first.c_str()","","colsize=40",1,extraVars.entry)
        return True
#####################################
class hltFilter(analysisStep) :
    """hltFilter"""

    def __init__(self,hltPathName):
        self.neededBranches=["triggered"]
        self.hltPathName=hltPathName
        self.moreName="("+self.hltPathName+")"

    def select (self,chain,chainVars,extraVars) :
        return chain.triggered[self.hltPathName]
#####################################
class hltPrescaleHistogrammer(analysisStep) :
    """hltPrescaleHistogrammer"""

    def __init__(self,listOfHltPaths) :
        self.neededBranches=["prescaled"]
        self.listOfHltPaths=listOfHltPaths
        self.moreName="("+str(self.listOfHltPaths)+")"

    def bookHistos(self) :
        nBinsX=len(self.listOfHltPaths)
        self.prescaleHisto=r.TH2D("hltPrescaleHisto","hltPrescaleHisto;;log_{10}(prescale value);events / bin",
                                  nBinsX,-0.5,nBinsX-0.5,
                                  100,-0.5,4.5)
        for iPath in range(len(self.listOfHltPaths)) :
            self.prescaleHisto.GetXaxis().SetBinLabel(iPath+1,self.listOfHltPaths[iPath])
        
    def uponAcceptance(self,chain,chainVars,extraVars) :
        for iPath in range(len(self.listOfHltPaths)) :
            value=chainVars.prescaled.find(self.listOfHltPaths[iPath]).second
            if value<=0.0 : continue
            self.prescaleHisto.Fill(iPath,math.log10(value))
#####################################
