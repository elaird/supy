import ROOT as r
from base import analysisStep
import math
#####################################
class physicsDeclared(analysisStep) :
    """physicsDeclared"""

    def select (self,eventVars,extraVars) :
        return eventVars["physicsDeclared"]
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
        
    def select (self,eventVars,extraVars) :
        l1techbits = eventVars["l1techbits"]
        anyBitInList=False
        for bit in self.bitList:
            if l1techbits.at(bit) :
                anyBitInList=True
                break

        return not (anyBitInList ^ self.accept)
#####################################
class triggerTest(analysisStep) :
    """triggerTest"""

    def select (self,eventVars,extraVars) :
        #print chain.l1techbits[9],chain.L1triggered["L1Tech_HCAL_HF_totalOR_minBias.v0"]
        L1 = eventVars["L1triggered"]
        print "bit 9=%d; v0=%d; v1=%d" % \
              ( eventVars["l1techbits"].at(9), \
                L1["L1Tech_HCAL_HF_coincidence_PM.v0"], \
                L1["L1Tech_HCAL_HF_coincidence_PM.v1"] )
        return True
#####################################
class triggerNameDump(analysisStep) :
    """triggerNameDump"""

    def __init__(self,triggerLevel):
        self.varName = triggerLevel + "triggered"
        self.moreName = "("+self.varName+")"

    def select (self,eventVars,extraVars) :
        for pair in eventVars[self.varName] :
            print pair.first
        return True
#####################################
class hltFilter(analysisStep) :
    """hltFilter"""

    def __init__(self,hltPathName):
        self.hltPathName = hltPathName
        self.moreName="("+self.hltPathName+")"

    def select (self,eventVars,extraVars) :
        return eventVars["triggered"][self.hltPathName]
#####################################
class hltPrescaleHistogrammer(analysisStep) :
    """hltPrescaleHistogrammer"""

    def __init__(self,listOfHltPaths) :
        self.listOfHltPaths = listOfHltPaths
        self.moreName = "("+str(self.listOfHltPaths)+")"

    def bookHistos(self) :
        nBinsX = len(self.listOfHltPaths)
        self.prescaleHisto = r.TH2D("hltPrescaleHisto","hltPrescaleHisto;;log_{10}(prescale value);events / bin",
                                    nBinsX,-0.5,nBinsX-0.5,
                                    100,-0.5,4.5)
        for iPath in range(nBinsX) :
            self.prescaleHisto.GetXaxis().SetBinLabel(iPath+1,self.listOfHltPaths[iPath])
        
    def uponAcceptance(self,eventVars,extraVars) :
        for iPath in range(len(self.listOfHltPaths)) :
            value = eventVars["prescaled"][self.listOfHltPaths[iPath]]
            if value<=0.0 : continue
            self.prescaleHisto.Fill(iPath,math.log10(value))
#####################################
