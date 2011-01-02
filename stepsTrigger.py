import ROOT as r
from analysisStep import analysisStep
import math
#####################################
class physicsDeclared(analysisStep) :

    def select (self,eventVars) :
        return eventVars["physicsDeclared"]
#####################################
class techBitFilter(analysisStep) :

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

    def __init__(self,triggerLevel):
        self.varName = triggerLevel + "triggered"
        self.moreName = self.varName

    def select (self,eventVars) :
        for pair in eventVars[self.varName] :
            print pair.first
        return True
#####################################
class triggerCounts(analysisStep) :

    def __init__(self, pathMatches = []) :
        self.key = "triggerCounts"
        self.pathMatches = pathMatches
        self.pathMatches.append("HLTriggerFinalPath")
        
    def uponAcceptance(self, eventVars) :
        for pair in eventVars["triggered"] :
            self.book(eventVars).fill( pair.first, self.key, 1, 1.0, -1.0, w = pair.second, title = ";;events / bin")

    def prunedHisto(self, inHisto) :
        list = []
        max = inHisto.GetMaximum()
        for iBin in range(0,inHisto.GetNbinsX()+2) :
            content = inHisto.GetBinContent(iBin)
            label = inHisto.GetXaxis().GetBinLabel(iBin)
            for match in self.pathMatches :
                if match in label :
                    list.append( (label, content) )

        dir = inHisto.GetDirectory()
        name = inHisto.GetName()
        title = "%s;%s;%s"%(inHisto.GetTitle(), inHisto.GetXaxis().GetTitle(), inHisto.GetYaxis().GetTitle())
        inHisto.Delete()

        outHisto = r.TH1D(name, title, len(list), 0.0, len(list))
        outHisto.SetDirectory(dir)
        
        for iItem,item in enumerate(list) :
            outHisto.Fill(iItem, item[1])
            outHisto.GetXaxis().SetBinLabel(iItem+1, item[0])
        return outHisto
        
    def endFunc(self, otherChainDict) :
        for book in self.books.values() :
            if self.key in book :
                book[self.key] = self.prunedHisto(book[self.key])
#####################################
class lowestUnPrescaledTrigger(analysisStep) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.moreName = "lowest unprescaled of "+','.join(self.sortedListOfPaths).replace("HLT_","")
        
    def select (self,eventVars) :
        for path in self.sortedListOfPaths :
            if eventVars["prescaled"][path]==1 : return eventVars["triggered"][path]
        return False
#####################################
class lowestUnPrescaledTriggerHistogrammer(analysisStep) :
    def __init__(self, listOfPaths = []) :
        self.listOfPaths = listOfPaths
        self.key = "lowestUnPrescaledTrigger"
        self.n = len(self.listOfPaths)
        
    def uponAcceptance(self, eventVars) :
        i = self.listOfPaths.index(eventVars["lowestUnPrescaledTrigger"])
        self.book(eventVars).fill( i, self.key, self.n, 0.0, self.n, title = ";lowest un-prescaled path;events / bin")

    def endFunc(self, otherChainDict) :
        for book in self.books.values() :
            if self.key in book :
                for iPath in range(self.n) :
                    book[self.key].GetXaxis().SetBinLabel(iPath+1,self.listOfPaths[iPath])
#####################################
class hltFilter(analysisStep) :

    def __init__(self,hltPathName):
        self.hltPathName = hltPathName
        self.moreName = self.hltPathName

    def select (self,eventVars) :
        return eventVars["triggered"][self.hltPathName]
#####################################
class hltFilterList(analysisStep) :

    def __init__(self,hltPathNames):
        self.hltPathNames = hltPathNames
        self.moreName = "any of "+str(self.hltPathNames)

    def select (self,eventVars) :
        for path in self.hltPathNames :
            if eventVars["triggered"][path] : return True
        return False
#####################################
class hltPrescaleHistogrammer(analysisStep) :

    def __init__(self,listOfHltPaths) :
        self.listOfHltPaths = listOfHltPaths
        self.moreName = ','.join(self.listOfHltPaths).replace("HLT_","")
        self.nBinsX = len(self.listOfHltPaths)
        self.key = "HltPrescaleHisto"

    def uponAcceptance(self,eventVars) :
        for iPath in range(len(self.listOfHltPaths)) :
            value = eventVars["prescaled"][self.listOfHltPaths[iPath]]
            if value<=0.0 : continue
            self.book(eventVars).fill( (iPath,math.log10(value)), self.key, (self.nBinsX,100), (-0.5,-0.5), (self.nBinsX-0.5,4,5),
                                       title="hltPrescaleHisto;;log_{10}(prescale value);events / bin")

    def endFunc(self, otherChainDict) :
        for book in self.books.values() :
            if self.key in book :
                for iPath in range(self.nBinsX) :
                    book[self.key].GetXaxis().SetBinLabel(iPath+1,self.listOfHltPaths[iPath])
#####################################
class hltTurnOnHistogrammer(analysisStep) :

    def __init__(self, probeTrig = None, var = None, tagTrigs = None, binsMinMax = None) :
        self.var = var
        self.bmm = binsMinMax
        self.probeTrigger = probeTrig
        self.tagTriggers = tagTrigs

        tagString = '-'.join(map(lambda s: s.lstrip("HLT_"),tagTrigs))
        probeString = probeTrig.lstrip("HLT_")
        
        self.probeTitle = ( "%s_given_%s_and_%s" % (var, tagString, probeString),
                            "pass %s given %s;%s; events / bin" % (probeString, tagString, var) )
        self.tagTitle = ( "%s_given_%s"% (var, tagString),
                          "pass %s;%s; events / bin" % (tagString,var))

        self.moreName = "%s given; %s; and %s" % (var, ", ".join(tagString.split('-')), probeString)

    def uponAcceptance(self,eventVars) :
        tag = any([eventVars["triggered"][t] for t in self.tagTriggers])
        probe = eventVars["triggered"][self.probeTrigger]
        types = [] if not tag else \
                [self.tagTitle] if not probe else \
                [self.tagTitle, self.probeTitle]
        value = eventVars[self.var]
        if value==None : return
        for t in types :
            self.book(eventVars).fill( value, t[0], self.bmm[0],self.bmm[1],self.bmm[2], title = t[1] )
        
#     def endFunc(self, otherChainDict) :
#         for book in self.books.values() :
#             tag = self.tagTitle[0]
#             probe = self.probeTitle[0]
#             efficiency = "%s-%s-%s"%(self.probeTrigger,str(self.tagTriggers),self.var)

#             if not (tag in book and \
#                     probe in book) : continue
            
#             book[efficiency] = book[probe].Clone(efficiency)
#             book[efficiency].SetTitle("Efficiency;%s;n%s / n%s"%(self.var,self.probeTrigger,str(self.tagTriggers)))
#             book[efficiency].Divide(book[tag])
#             book[efficiency].SetBit(r.TH1.kIsAverage)
#####################################
class jetMetTriggerHistogrammer(analysisStep) :

    def __init__(self,triggerJets,triggerMet,offlineJets,offlineMht) :
        self.triggerJets = triggerJets
        self.triggerMet = triggerMet
        self.offlineJets = offlineJets
        self.offlineMht = offlineMht
        self.moreName  = "trigger: %s,%s"%(self.triggerJets,self.triggerMet)
        self.moreName2 = " offline: %s,%s"%(self.offlineJets,self.offlineMht)
        self.triggerJetsP4String = "%sCorrectedP4%s"%self.triggerJets
        self.triggerJetsCorrFactorString = "%sCorrFactor%s"%self.triggerJets
        self.triggerMetString = "%sP4%s"%self.triggerMet

        self.offlineJetsP4String = "%sCorrectedP4%s"%self.offlineJets
        self.offlineSumP4String = "%sSumP4%s"%self.offlineJets
        
    def uponAcceptance(self,eventVars) :
        nTriggerJets = eventVars[self.triggerJetsP4String].size()
        if not nTriggerJets : return
        triggerJetPt = max( [eventVars[self.triggerJetsP4String].at(i).pt()/eventVars[self.triggerJetsCorrFactorString].at(i) for i in range(nTriggerJets)] )
        triggerMet = eventVars[self.triggerMetString].pt()

        nOfflineJets = eventVars[self.offlineJetsP4String].size()
        offlineJetPt = eventVars[self.offlineJetsP4String].at(0).pt() if nOfflineJets else 0.0
        offlineMht   = eventVars[self.offlineSumP4String].pt() if eventVars[self.offlineSumP4String] else 0.0
        
        self.book(eventVars).fill( (triggerJetPt,triggerMet), "TriggerMet_vs_TriggerJetPt", (100,100), (0.0,0.0), (200.0,100.0),
                                   title=";leading un-corr. %s p_{T} (GeV);%s p_{T} (GeV);events / bin"%(self.triggerJets,self.triggerMet))
        
        self.book(eventVars).fill( (offlineMht,triggerMet),   "TriggerMet_vs_OfflineMht",   (100,100), (0.0,0.0), (400.0,100.0),
                                   title=";%s MHT (GeV);%s (GeV);events / bin"%(self.offlineMht,self.triggerMet))

        self.book(eventVars).fill( (triggerJetPt,offlineJetPt), "OfflineJetPt_vs_TriggerJetPt", (100,100), (0.0,0.0), (200.0,200.0),
                                   title=";leading un-corr. %s p_{T} (GeV);%s p_{T} (GeV);events / bin"%(self.triggerJets,self.offlineJets))
#####################################
