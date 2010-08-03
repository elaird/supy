import ROOT as r
from analysisStep import analysisStep
import math
#####################################
class physicsDeclared(analysisStep) :
    """physicsDeclared"""

    def select (self,eventVars) :
        return eventVars["physicsDeclared"]
#####################################
class techBitFilter(analysisStep) :
    """techBitFilter"""

    def __init__(self,bitList,acceptRatherThanReject) :
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
        
    def select (self,eventVars) :
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

    def select (self,eventVars) :
        #print eventVars["l1techbits"][9],eventVars["L1triggered"]["L1Tech_HCAL_HF_totalOR_minBias.v0"]
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

    def select (self,eventVars) :
        for pair in eventVars[self.varName] :
            print pair.first
        return True
#####################################
class hltFilter(analysisStep) :
    """hltFilter"""

    def __init__(self,hltPathName):
        self.hltPathName = hltPathName
        self.moreName="("+self.hltPathName+")"

    def select (self,eventVars) :
        return eventVars["triggered"][self.hltPathName]
#####################################
class hltPrescaleHistogrammer(analysisStep) :
    """hltPrescaleHistogrammer"""

    def __init__(self,listOfHltPaths) :
        self.listOfHltPaths = listOfHltPaths
        self.moreName = "("+str(self.listOfHltPaths)+")"
        self.nBinsX = len(self.listOfHltPaths)

    def uponAcceptance(self,eventVars) :
        for iPath in range(len(self.listOfHltPaths)) :
            value = eventVars["prescaled"][self.listOfHltPaths[iPath]]
            if value<=0.0 : continue
            self.book(eventVars).fill( (iPath,math.log10(value)), "hltPrescaleHisto", (self.nBinsX,100), (-0.5,-0.5), (self.nBinsX-0.5,4,5),
                                       title="hltPrescaleHisto;;log_{10}(prescale value);events / bin")

    def endFunc(self,chain,otherChainDict,hyphens,nEvents,xs) :
        key="hltPrescaleHisto"
        for book in self.books.values() :
            if key in book :
                for iPath in range(self.nBinsX) :
                    book[key].GetXaxis().SetBinLabel(iPath+1,self.listOfHltPaths[iPath])
#####################################
class hltTurnOnHistogrammer(analysisStep) :
    """hltTurnOnHistogrammer"""

    def __init__(self, probeTrigger = None, var = None, tagTriggers = None, binsMinMax = None) :
        self.var = var
        self.bmm = binsMinMax
        self.probeTrigger = probeTrigger
        self.tagTriggers = tagTriggers
        self.tagString = reduce(lambda x,y: "%s%s"%(x,y.strip('HLT')), self.tagTriggers, "")

        self.moreName = "(%s turnon vs. %s" % (probeTrigger,var)
        self.moreName2 = "given one of %s )" % (str(tagTriggers))

    def uponAcceptance(self,eventVars) :
        tag = reduce(lambda x,y: x or y, [eventVars["triggered"][t] for t in self.tagTriggers], False)
        probe = eventVars["triggered"][self.probe]
        types = [] if not tag else \
                [self.tagString] if not probe else \
                [self.tagString, self.probeTrigger]
        for t in types :
            self.book(eventVars).fill( eventVars[self.var], "%s-%s"%(t,self.var), self.bmm[0],self.bmm[1],self.bmm[2],
                                       title = "pass %s;%s; events / bin" % (t,self.var) )
        
#     def endFunc(self,chain,otherChainDict,hyphens,nEvents,xs) :
#         book = self.book(eventVars)
#         tag = book["%s-%s"%(self.tagString,self.var)]
#         probe = book["%s-%s"%(self.probeTrigger,self.var)]

#         efficiencyName = "%s-%s-%s"%(self.probeTrigger,self.tagString,self.var)
#         book[efficiencyName] = probe.Clone(efficiencyName)
#         book[efficiencyName].SetTitle("Efficiency;%s;N%s/N%s"%(self.var,self.probeTrigger,self.tagString))
#         book[efficiencyName].Divide(tag)
        
#####################################
