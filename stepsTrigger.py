import ROOT as r
from analysisStep import analysisStep
import stepsMaster
import math,collections,os,utils,re
#####################################
class physicsDeclaredFilter(analysisStep) :

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
class NameDump(analysisStep) :

    def __init__(self,triggerLevel = ""):
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
        outFile = open(self.outputFileName,"w")

        maxNameLength = max([len(key) for key in counts.keys()])
        maxCountLength = max([len(str(value)) for value in counts.values()])
        for key in sorted(counts.keys()) :
            outFile.write("%s    %s\n"%(key.ljust(maxNameLength), str(counts[key]).ljust(maxCountLength)))
        outFile.close()
        print "The trigger counts file %s has been written."%self.outputFileName
        print utils.hyphens
#####################################
class lowestUnPrescaledTriggerFilter(analysisStep) :
    def __init__(self) :
        self.moreName = "lowest unprescaled of triggers in calculable"
        
    def select (self,eventVars) :
        return eventVars["triggered"][eventVars["lowestUnPrescaledTrigger"]]
#####################################
class lowestUnPrescaledTriggerHistogrammer(analysisStep) :
    def __init__(self) :
        self.key = "lowestUnPrescaledTrigger"
        
    def uponAcceptance(self, eventVars) :
        if not hasattr(self,"listOfPaths") :
            self.listOfPaths = dict.__getitem__(eventVars,self.key).sortedListOfPaths
            self.nPaths = len(self.listOfPaths)
        i = self.listOfPaths.index(eventVars[self.key])
        self.book.fill( i, self.key, self.nPaths, 0.0, self.nPaths, title = ";lowest un-prescaled path;events / bin", xAxisLabels = self.listOfPaths)
#####################################
class l1Filter(analysisStep) :

    def __init__(self, bitName):
        self.bitName = bitName
        self.moreName = self.bitName

    def select (self,eventVars) :
        return eventVars["L1triggered"][self.bitName]
#####################################
class hltFilter(analysisStep) :

    def __init__(self,hltPathName):
        self.hltPathName = hltPathName
        self.moreName = self.hltPathName

    def select (self,eventVars) :
        return eventVars["triggered"][self.hltPathName]
#####################################
class hltFail(analysisStep) :

    def __init__(self, paths):
        self.paths = paths
        self.moreName = str(self.paths)

    def select (self,eventVars) :
        fired = False
        inMenu = False
        for path in self.paths :
            if path not in eventVars["triggered"] : continue
            inMenu = True
            if eventVars["triggered"][path] : fired = True
        return inMenu and (not fired)
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

    def __init__(self, var = None, binsMinMax = None, probe = None, tags = None, permissive = False) :
        for item in ["var","binsMinMax","probe","tags","permissive"] :
            setattr(self,item,eval(item))

        tags = "{%s}"%(','.join([t.replace("HLT_","") for t in self.tags]))
        probe = self.probe.replace("HLT_","")
        
        self.tagTitle   = ( "tag_%s_%s_%s" % (probe,tags,var), "pass %s;%s;events / bin" % (tags,var))
        self.probeTitle = ( "probe_%s_%s_%s" % (probe,tags,var), "pass %s given %s;%s;events / bin" % (probe, tags, var) )
        self.effTitle   = ( "turnon_%s_%s_%s" % (probe,tags,var), "%s Turn On;%s;P(%s | %s)" % (probe,var,probe,tags))

        self.moreName = "%s by %s, given %s;" % (probe, var, tags)

    def uponAcceptance(self,eventVars) :
        if not any([eventVars["triggered"][t] for t in self.tags]) : return
        if (not self.permissive) and 1 != eventVars["prescaled"][self.probe] : return
        
        for t in ([self.tagTitle] if not eventVars["triggered"][self.probe] else [self.tagTitle,self.probeTitle]) :
            self.book.fill( eventVars[self.var], t[0], self.binsMinMax[0],self.binsMinMax[1],self.binsMinMax[2], title = t[1] )
    
    def outputSuffix(self) : return stepsMaster.Master.outputSuffix()

    def mergeFunc(self, products) :
        file = r.TFile.Open(self.outputFileName, "UPDATE")
        probe = file.FindObjectAny(self.probeTitle[0])
        if not probe : return
        probe.GetDirectory().cd()
        tag = file.FindObjectAny(self.tagTitle[0])
        if tag.GetDirectory() != probe.GetDirectory() :
            print "Warning: hltTurnOnHistogrammer could not complete mergeFunc"
            print self.tagTitle[0]
            return
        efficiency = probe.Clone(self.effTitle[0])
        efficiency.SetTitle(self.effTitle[1])
        efficiency.Divide(probe,tag,1,1,"B")
        for bin in [0,self.binsMinMax[0]+1] :
            efficiency.SetBinContent(bin,0)
            efficiency.SetBinError(bin,0)
        efficiency.Write()
        r.gROOT.cd()
        file.Close()
        print "Output updated with TurnOn %s."%self.effTitle[0]
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
class triggerScan(analysisStep) :
    def __init__(self, pattern = r".*", prescaleRequirement = "True", tag = "") :
        self.tag = tag
        self.pattern = pattern
        self.prescaleRequirement = prescaleRequirement
        self.moreName = "%s; %s"%(pattern, prescaleRequirement)

        self.triggerNames = collections.defaultdict(set)
        self.counts = collections.defaultdict(int)

    def uponAcceptance(self,eventVars) :
        key = (eventVars["run"],eventVars["lumiSection"])
        self.counts[key] += 1
        if key not in self.triggerNames :
            for name,prescale in eventVars["prescaled"] :
                if re.match(self.pattern,name) and eval(self.prescaleRequirement) :
                    self.triggerNames[key].add(name)

    def varsToPickle(self) : return ["triggerNames","counts"]
        
    def outputSuffix(self) : return stepsMaster.Master.outputSuffix()

    def mergeFunc(self,products) :
        def update(a,b) : a.update(b); return a;
        self.triggerNames = reduce(update, products["triggerNames"], dict())
        self.counts = reduce(update, products["counts"], dict())

        names = sorted(list(reduce(lambda a,b: a|b, self.triggerNames.values(), set())))

        reducedNames = []
        reducedCounts = []
        order = sorted(self.triggerNames.keys())
        for key in order :
            if (not reducedNames) or reducedNames[-1] != self.triggerNames[key] :
                reducedNames.append(self.triggerNames[key])
                reducedCounts.append(self.counts[key])
            else : reducedCounts[-1] += self.counts[key]

        hist = r.TH2D(self.tag if self.tag else "triggerScan",
                      "(%s) with (%s);epochs of %s;;events"%(self.pattern, self.prescaleRequirement, self._analysisStep__outputFileStem.split('/')[-1]),
                      len(reducedNames),0,len(reducedNames),len(names),0,len(names))
        for i,name in enumerate(names) : hist.GetYaxis().SetBinLabel(i+1,name.replace("HLT_",""))
        for i in range(len(reducedNames)) : hist.GetXaxis().SetBinLabel(i+1,"%d"%(i+1))
        
        for i, iNames, iCount in zip(range(len(reducedNames)), reducedNames, reducedCounts) :
            for name in iNames :
                j = names.index(name)
                hist.SetBinContent(i+1,j+1,iCount)

        file = r.TFile.Open(self.outputFileName,"UPDATE")
        if not file.FindKey("triggerScan") : file.mkdir("triggerScan")
        file.cd("triggerScan")
        hist.Write()
        r.gROOT.cd()
        file.Close()
        print "Output updated with triggerScans %s."%self.tag
#####################################
class prescaleScan(analysisStep) :
    def __init__(self, trigger = None, ptMin = None, triggeringPt = "") :
        self.trigger = trigger
        self.triggeringPt = triggeringPt
        self.ptMin = ptMin
        self.moreName = "%s; %.1f<pt mu"%(trigger, ptMin)

    def uponAcceptance(self,ev) :
        if not self.ptMin < ev[self.triggeringPt] : return
        prescale = ev["prescaled"][self.trigger]
        if not prescale : return
        name = self.trigger+"_p%d"%prescale
        self.book.fill( ev['triggered'][self.trigger], name, 2,0,1, title = '%s;Fail / Pass;event / bin'%(name))
#####################################
class anyTrigger(analysisStep) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.moreName = "any of "+','.join(self.sortedListOfPaths).replace("HLT_","")
        
    def select(self, ev) :
        return any(ev['triggered'][item] for item in self.sortedListOfPaths)
