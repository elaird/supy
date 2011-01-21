import ROOT as r
from analysisStep import analysisStep
import math,collections,os,utils
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
class Counts(analysisStep) :

    def __init__(self) :
        self.counts = collections.defaultdict(int)
        
    def uponAcceptance(self, eventVars) :
        for pair in eventVars["triggered"] :
            if pair.second : 
                self.counts[pair.first] += 1

    def outputSuffix(self) :
        return "_triggerCounts.txt"

    def varsToPickle(self) :
        return ["counts"]

    def mergeFunc(self, products) :
        def mergedCounts(l) :
            out = collections.defaultdict(int)
            for d in l :
                for key,value in d.iteritems() :
                    out[key] += value
            return out

        counts = mergedCounts(products["counts"])
        outFile = open(self.outputFileName(),"w")

        maxNameLength = max([len(key) for key in counts.keys()])
        maxCountLength = max([len(str(value)) for value in counts.values()])
        for key in sorted(counts.keys()) :
            outFile.write("%s    %s\n"%(key.ljust(maxNameLength), str(counts[key]).ljust(maxCountLength)))
        outFile.close()
        print "The trigger counts file %s has been written."%self.outputFileName()
        print utils.hyphens
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
        self.book.fill( i, self.key, self.n, 0.0, self.n, title = ";lowest un-prescaled path;events / bin", xAxisLabels = self.listOfPaths)
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
            self.book.fill( (iPath,math.log10(value)), self.key, (self.nBinsX,100), (-0.5,-0.5), (self.nBinsX-0.5,4,5),
                            title="hltPrescaleHisto;;log_{10}(prescale value);events / bin", xAxisLabels = self.listOfHltPaths)
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
            self.book.fill( value, t[0], self.bmm[0],self.bmm[1],self.bmm[2], title = t[1] )
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
        
        self.book.fill( (triggerJetPt,triggerMet), "TriggerMet_vs_TriggerJetPt", (100,100), (0.0,0.0), (200.0,100.0),
                        title=";leading un-corr. %s p_{T} (GeV);%s p_{T} (GeV);events / bin"%(self.triggerJets,self.triggerMet))
        
        self.book.fill( (offlineMht,triggerMet),   "TriggerMet_vs_OfflineMht",   (100,100), (0.0,0.0), (400.0,100.0),
                        title=";%s MHT (GeV);%s (GeV);events / bin"%(self.offlineMht,self.triggerMet))

        self.book.fill( (triggerJetPt,offlineJetPt), "OfflineJetPt_vs_TriggerJetPt", (100,100), (0.0,0.0), (200.0,200.0),
                        title=";leading un-corr. %s p_{T} (GeV);%s p_{T} (GeV);events / bin"%(self.triggerJets,self.offlineJets))
#####################################
