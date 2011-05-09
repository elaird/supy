import copy,array,os,collections
import ROOT as r
from analysisStep import analysisStep
import stepsMaster
import utils
#####################################
class histogrammer(analysisStep) :

    def __init__(self,var,N,low,up,title="", funcString = "lambda x:x" , suffix = "") :
        for item in ["var","N","low","up","title","funcString"] : setattr(self,item,eval(item))
        self.oneD = type(var) != tuple
        self.hName = (var if self.oneD else "_vs_".join(reversed(var)))+suffix
        self.moreName = "%s(%s)"% ("(%s)"%funcString if funcString!="lambda x:x" else "", str(self.hName))
        self.funcStringEvaluated = False

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True
            
        value = eventVars[self.var] if self.oneD else \
                tuple(map(eventVars.__getitem__,self.var))
        if value is None or (not self.oneD and not all(value)) : return #temporary bug

        self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class iterHistogrammer(histogrammer) :

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True

        values = eventVars[self.var] if self.oneD else \
                 zip(*map(eventVars.__getitem__,self.var))

        for i in range(len(values)) :
            value = values[i]
            if value is None or (not self.oneD and None in value) : continue
            self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class passFilter(analysisStep) :
    def __init__(self,title) : self.moreName = title
    def select(self,eventVars) : return True
#####################################
class multiplicityFilter(analysisStep) :

    def __init__(self,var, nMin = 0, nMax = None ) :
        self.moreName = "%d <= %s"%(nMin,var) + (" <= %d" % nMax if nMax!=None else "")
        self.var = var
        self.nMin = nMin
        self.nMax = nMax if nMax!=None else 1e6
    def select(self,eventVars) :
        return self.nMin <= len(eventVars[self.var]) <= self.nMax
#####################################
def multiplicityPlotFilter(var, nMin=0, nMax=None, xlabel="") :
    return ([ histogrammer(var, 20, -0.5, 19.5, title=";%s;events / bin"%xlabel, funcString="lambda x:len(x)")] if xlabel else []) + \
           [ multiplicityFilter(var, nMin = nMin , nMax = nMax) ]
#####################################
class orFilter(analysisStep) :
    def __init__(self, listOfSelectorSteps = []) :
        self.steps = listOfSelectorSteps
        self.moreName = '|'.join(["%s:%s"%(step.name(),step.moreName) for step in self.steps])
    def select(self,eventVars) :
        for step in self.steps :
            if step.select(eventVars) : return True
        return False
#####################################
class assertNotYetCalculated(analysisStep) :
    def __init__(self,var) : self.var = var
    def uponAcceptance(self, eV) : assert not dict.__getitem__(eV, self.var).updated
#####################################
class skimmer(analysisStep) :
    
    def __init__(self) :
        self.outputTree=0
        self.moreName="(see below)"
        self.alsoWriteExtraTree=False #hard-code until this functionality is fixed
        self.outputTreeExtraIsSetup=False

    def requiresNoSetBranchAddress(self) :
        return True

    def setup(self, chain, fileDir) :
        self.fileDir = fileDir
        self.outputFile = r.TFile(self.outputFileName(), "RECREATE")
        self.setupMainChain(chain)
        self.initExtraTree()

    def setupMainChain(self, chain) :
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        if chain and chain.GetEntry(0)>0 :
            self.outputTree = chain.CloneTree(0)  #clone structure of tree (but no entries)
        if not self.outputTree :                  #in case the chain has 0 entries
            r.gROOT.cd()
            return
        self.outputTree.SetDirectory(r.gDirectory)#put output tree in correct place
        chain.CopyAddresses(self.outputTree)      #associate branch addresses

    def writeOtherChains(self, otherChainDict) :
        for (dirName,treeName),chain in otherChainDict.iteritems() :
            self.outputFile.mkdir(dirName).cd()
            if chain and chain.GetEntry(0)>0 :
                outChain = chain.CloneTree()
                if outChain :
                    outChain.SetName(treeName)
                    outChain.SetDirectory(r.gDirectory)
                    outChain.Write()

    def initExtraTree(self) :
        if self.alsoWriteExtraTree :
            raise Exception("at the moment, adding the extra tree with the skimmer is broken")
            self.arrayDictionary={}
            self.supportedBuiltInTypes=[type(True),type(0),type(0L),type(0.0)]
            self.supportedOtherTypes=[type(utils.LorentzV())]
            
            extraName=self.outputTree.GetName()+"Extra"
            self.outputTreeExtra=r.TTree(extraName,extraName)
            self.outputTreeExtra.SetDirectory(r.gDirectory)
        r.gROOT.cd()


    def select(self,eventVars) :
        #read all the data for this event
        if eventVars["chain"].GetEntry(eventVars["entry"],1)<=0 :
            return False #skip this event in case of i/o error
        #fill the skim tree
        self.outputTree.Fill()
        
        #optionally fill an extra tree
        if self.alsoWriteExtraTree :
            if not self.outputTreeExtraIsSetup : self.setupExtraTree(eventVars)
            self.fillExtraVariables(eventVars)
            self.outputTreeExtra.Fill()
            
        return True

    def setupExtraTree(self,eventVars) :
        crockCopy=copy.deepcopy(eventVars["crock"])
        branchNameList=dir(crockCopy)
        skipList=['__doc__','__init__','__module__']

        #set up remaining suitable branches as doubles
        for branchName in branchNameList :
            if (branchName in skipList) : continue

            thisType=type(eventVars["crock"][branchName])
            if (thisType in self.supportedBuiltInTypes) :
                self.arrayDictionary[branchName]=array.array('d',[0.0])
                self.outputTreeExtra.Branch(branchName,self.arrayDictionary[branchName],branchName+"/D")
            elif (thisType in self.supportedOtherTypes) :
                self.outputTreeExtra.Branch(branchName,eventVars["crock"][branchName])
            else :
                #print "The variable \""+branchName+"\" has been rejected from the extra tree."
                continue
            
        self.outputTreeExtraIsSetup=True

    def fillExtraVariables(self,eventVars) :
        for key in self.arrayDictionary :
            self.arrayDictionary[key][0]=eventVars["crock"][key]
        
    def endFunc(self, otherChainDict) :
        self.outputFile.cd(self.fileDir)                          #cd to file
        if self.outputTree :         self.outputTree.Write()      #write main tree
        if self.alsoWriteExtraTree : self.outputTreeExtra.Write() #write a tree with "extra" variables
        self.writeOtherChains(otherChainDict)
        self.outputFile.Close()

    def outputSuffix(self) :
        return "_skim.root"
    
    def mergeFunc(self, products) :
        print "The %d skim files have been written."%len(products["outputFileName"])
        print "( e.g. %s )"%products["outputFileName"][0]
        print utils.hyphens
#####################################
class hbheNoiseFilter(analysisStep) :
    def __init__(self, invert = False) :
        self.invert = invert
        if self.invert : self.moreName = "[INVERTED]"

    def select (self,eventVars) :
        return eventVars["hbheNoiseFilterResult"]^self.invert
#####################################
class productGreaterFilter(analysisStep) :

    def __init__(self, threshold, variables, suffix = ""):
        self.threshold = threshold
        self.variables = variables
        self.moreName = "%s>=%.3f %s" % ("*".join(variables),threshold,suffix)

    def select (self,eventVars) :
        product = 1
        for var in self.variables : product *= eventVars[var]
        return product >= self.threshold
#####################################
class objectEtaSelector(analysisStep) :

    def __init__(self, cs, etaThreshold, index, p4String):
        self.index = index
        self.etaThreshold = etaThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%s%s%s" % (self.cs[0], p4String, self.cs[1])
        self.moreName = "%s%s; |eta[index[%d]]|<=%.1f" % (self.cs[0], self.cs[1], index, etaThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.index : return False
        p4s = eventVars[self.p4sName]
        return self.etaThreshold > abs(p4s.at(indices[self.index]).eta())
#####################################
class ptRatioLessThanSelector(analysisStep) :

    def __init__(self,numVar = None, denVar = None, threshold = None):
        for item in ["numVar","denVar","threshold"] :
            setattr(self,item,eval(item))
        self.moreName = "%s.pt() / %s.pt() < %.3f" % (numVar,denVar,threshold)

    def select (self,ev) :
        value = ev[self.numVar].pt() / ev[self.denVar].pt()
        return value<self.threshold
#####################################
class ptRatioHistogrammer(analysisStep) :

    def __init__(self,numVar = None, denVar = None):
        for item in ["numVar","denVar"] :
            setattr(self,item,eval(item))
        self.moreName = "%s.pt() / %s.pt()" % (self.numVar,self.denVar)

    def uponAcceptance (self,ev) :
        value = ev[self.numVar].pt() / ev[self.denVar].pt()
        self.book.fill(value,"ptRatio", 50, 0.0, 2.0, title = ";%s / %s;events / bin"%(self.numVar,self.denVar) )
#####################################
class monsterEventFilter(analysisStep) :
    
    def __init__(self,maxNumTracks=10,minGoodTrackFraction=0.25) :
        self.maxNumTracks=maxNumTracks
        self.minGoodTrackFraction=minGoodTrackFraction

        self.moreName = "<=%d tracks or >%.2f good fraction" % (maxNumTracks, minGoodTrackFraction)

    def select (self,eventVars) :
        nTracks    = eventVars["tracksNEtaLT0p9AllTracks"] + eventVars["tracksNEta0p9to1p5AllTracks"] + eventVars["tracksNEtaGT1p5AllTracks"]
        nGoodTracks = eventVars["tracksNEtaLT0p9HighPurityTracks"] + eventVars["tracksNEta0p9to1p5HighPurityTracks"] + eventVars["tracksNEtaGT1p5HighPurityTracks"]
        return (nTracks <= self.maxNumTracks or nGoodTracks > self.minGoodTrackFraction*nTracks)
#####################################
class touchstuff(analysisStep) :

    def __init__(self,stuff) :
        self.stuff = stuff
        self.moreName = "touch all in %s" % str(stuff)
        
    def uponAcceptance(self,eventVars) :
        for s in self.stuff : eventVars[s]
#####################################
class printstuff(analysisStep) :
    def __init__(self,stuff) :
        self.stuff = stuff
        self.moreName = "touch all in %s" % str(stuff)
    def uponAcceptance(self,eventVars) :
        for s in self.stuff : print s.rjust(20), eventVars[s]
#####################################
class runLsEventFilter(analysisStep) :

    def __init__(self, fileName) :
        self.moreName = "run:ls:event in %s"%fileName
        file = open(fileName)
        self.tuples = [ eval("(%s,%s,%s)"%tuple(line.replace("\n","").split(":"))) for line in file]
        file.close()

    def select (self,eventVars) :
        return (eventVars["run"], eventVars["lumiSection"], eventVars["event"]) in self.tuples
#####################################
class runNumberFilter(analysisStep) :

    def __init__(self,runList,acceptRatherThanReject) :
        self.runList = runList
        self.accept = acceptRatherThanReject

        self.moreName = "run%s in list %s" % ( ("" if self.accept else " not"),str(runList) )
        
    def select (self,eventVars) :
        return not ((eventVars["run"] in self.runList) ^ self.accept)
#####################################
class runHistogrammer(analysisStep) :

    def __init__(self) :
        self.runDict={}
        
    def select (self,eventVars) :
        run = eventVars["run"]
        if run in self.runDict :
            self.runDict[run] += 1
        else :
            self.runDict[run] = 1
        return True

    def printStatistics(self) :
        printList=[]
        for key in sorted(self.runDict) :
            printList.append( (key,self.runDict[key]) )
        print self.name1(),printList
#####################################
class bxFilter(analysisStep) :

    def __init__(self,bxList) :
        self.bxList = bxList
        self.moreName = "[%s]" % ",".join(bxList)

    def select (self,eventVars) :
        return eventVars["bunch"] in self.bxList
#####################################
class counter(analysisStep) :

    def __init__(self,label) :
        self.label = label
        self.moreName = '("%s")' % label

    def uponAcceptance(self,eventVars) :
        self.book.fill(0.0,"countsHisto_"+self.label,1,-0.5,0.5,";dummy axis;number of events")
#####################################
class pickEventSpecMaker(analysisStep) :
    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/WorkBookPickEvents

    def __init__(self) :
        self.events = []
        
    def outputSuffix(self) :
        return "_pickEvents.txt"
    
    def uponAcceptance(self, eventVars) :
        self.events.append( (eventVars["run"], eventVars["lumiSection"], eventVars["event"]) )
        
    def varsToPickle(self) :
        return ["events"]

    def mergeFunc(self, products) :
        out = open(self.outputFileName(), "w")
        for events in products["events"] :
            for event in events :
                out.write("%14d:%6d:%14d\n"%event)
        out.close()
        print "The pick events spec. file %s has been written."%self.outputFileName()
#####################################
class jsonMaker(analysisStep) :

    def __init__(self) :
        self.runLsDict=collections.defaultdict(list)
        self.moreName="see below"

    def uponAcceptance(self,eventVars) :
        self.runLsDict[eventVars["run"]].append(eventVars["lumiSection"])
    
    def varsToPickle(self) :
        return ["runLsDict"]

    def outputSuffix(self) :
        return ".json"
    
    def mergeFunc(self, products) :
        def mergedDict(runLsDicts) :
            #merge results into one dictionary
            out = collections.defaultdict(list)
            for d in runLsDicts :
                for run,lsList in d.iteritems() :
                    out[run].extend(lsList)
            return out

        def trimmedList(run, lsList) :
            #check for duplicates
            out = list(set(lsList))
            nDuplicates = len(lsList)-len(out)
            if nDuplicates!=0 :
                for ls in out :
                    lsList.remove(ls)
                lsList.sort()
                print "In run %d, these lumi sections appear multiple times in the lumiTree: %s"%(run, str(lsList))
            return sorted(out)

        def aJson(inDict) :
            #make a json
            outDict = {}
            for run,lsList in inDict.iteritems() :
                trimList = trimmedList(run, lsList)

                newList = []
                lowerBound = trimList[0]
                for iLs in range(len(trimList)-1) :
                    thisLs = trimList[iLs  ]
                    nextLs = trimList[iLs+1]
                    if nextLs!=thisLs+1 :
                        newList.append([lowerBound, thisLs])
                        lowerBound = nextLs
                    if iLs==len(trimList)-2 :
                        newList.append([lowerBound, nextLs])
                outDict[str(run)] = newList
            return str(outDict).replace("'",'"')

        outFile = open(self.outputFileName(),"w")
        outFile.write(aJson(mergedDict(products["runLsDict"])))
        outFile.close()
        print "The json file %s has been written."%self.outputFileName()
        print utils.hyphens
#####################################
class duplicateEventCheck(analysisStep) :
    def __init__(self) :
        self.events = collections.defaultdict(list)

    def uponAcceptance(self,ev) :
        self.events[(ev["run"], ev["lumiSection"])].append(ev["event"])

    def varsToPickle(self) :
        return ["events"]

    def mergeFunc(self, products) :
        def mergedEventDicts(l) :
            out = collections.defaultdict(list)
            for d in l :
                for key,value in d.iteritems() :
                    out[key] += value
            return out

        def duplicates(l) :
            s = set(l)
            for item in s :
                l.remove(item)
            return list(set(l))

        anyDups = False
        events = mergedEventDicts(products["events"])
        for runLs in sorted(events.keys()) :
            d = duplicates(events[runLs])
            if d :
                print "DUPLICATE EVENTS FOUND in run %d ls %d: %s"%(runLs[0], runLs[1], d)
                anyDups = True
        if not anyDups :
            print "No duplicate events were found."
#####################################
class deadEcalFilter(analysisStep) :
    def __init__(self, jets = None, extraName = "", dR = None, dPhiStarCut = None) :
        for item in ["jets","extraName","dR","dPhiStarCut"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStar%s%s"%(self.jets[0], self.jets[1], self.extraName)
        self.deadEcalDR = "%sDeadEcalDR%s%s"%(self.jets[0], self.jets[1], self.extraName)
        self.moreName = "%s%s; dR>%5.3f when deltaPhiStar<%5.3f"%(self.jets[0], self.jets[1], self.dR, self.dPhiStarCut)
        
    def select(self, eventVars) :
        return (eventVars[self.dps]["DeltaPhiStar"]>self.dPhiStarCut or eventVars[self.deadEcalDR]>self.dR)
#####################################
class deadHcalFilter(analysisStep) :
    def __init__(self, jets = None, extraName = "", dR = None, dPhiStarCut = None, nXtalThreshold = None) :
        for item in ["jets","dR","dPhiStarCut"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStar%s%s"%(self.jets[0],self.jets[1],extraName)
        self.badJet = utils.LorentzV()
        self.moreName = "%s%s; dR>%5.3f when deltaPhiStar<%5.3f"%(self.jets[0], self.jets[1], self.dR, self.dPhiStarCut)
        
    def select(self, eventVars) :
        d = eventVars[self.dps]
        index = d["DeltaPhiStarJetIndex"]
        if d["DeltaPhiStar"]>self.dPhiStarCut :
            return True
        jet = eventVars["%sCorrectedP4%s"%self.jets].at(index)
        self.badJet.SetCoordinates(jet.pt(),jet.eta(),jet.phi(),jet.mass())
        for channel in eventVars["hcalDeadChannelP4"] :
            if r.Math.VectorUtil.DeltaR(self.badJet,channel) < self.dR :
                return False
        return True
#####################################
class deadEcalFilterIncludingPhotons(analysisStep) :
    def __init__(self, jets = None, extraName = "", photons = None, dR = None, dPhiStarCut = None, nXtalThreshold = None) :
        for item in ["jets","photons","dR","dPhiStarCut","nXtalThreshold"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStarIncludingPhotons%s%s"%(self.jets[0],self.jets[1],extraName)
        self.badThing = utils.LorentzV()
        self.moreName = "%s%s; %s%s; dR>%5.3f when deltaPhiStar<%5.3f and nXtal>%d"%(self.jets[0], self.jets[1],
                                                                                     self.photons[0], self.photons[1],
                                                                                     self.dR, self.dPhiStarCut, self.nXtalThreshold)
        
    def select(self, eventVars) :
        d = eventVars[self.dps]
        if d["DeltaPhiStar"]>self.dPhiStarCut :
            return True

        jetIndex = d["DeltaPhiStarJetIndex"]
        photonIndex = d["DeltaPhiStarPhotonIndex"]
        if jetIndex!=None :
            thing = eventVars["%sCorrectedP4%s"%self.jets].at(jetIndex)
        elif photonIndex!=None :
            thing = eventVars["%sP4%s"%self.photons].at(photonIndex)

        self.badThing.SetCoordinates(thing.pt(),thing.eta(),thing.phi(),thing.mass())
        for iRegion,region in enumerate(eventVars["ecalDeadTowerTrigPrimP4"]) :
            if eventVars["ecalDeadTowerNBadXtals"].at(iRegion)<self.nXtalThreshold : continue
            if r.Math.VectorUtil.DeltaR(self.badThing,region) < self.dR :
                return False
        return True
#####################################
class vertexHistogrammer(analysisStep) :
    def uponAcceptance(self,eV) :
        index = eV["vertexIndices"]
        sump3 = eV["vertexSumP3"]
        sumpt = eV["vertexSumPt"]
        if not len(index) : return
        
        #coord = reduce(lambda v,u: (v[0]+u[0],v[1]+u[1],v[2]+u[2]), [(sump3[i].x(),sump3[i].y(),sump3[i].z()) for i in index][1:], (0,0,0))
        #sump3Secondaries = type(sump3[0])(coord[0],coord[1],coord[2])

        self.book.fill( sumpt[index[0]], "vertex0SumPt", 40, 0, 1200, title = ";primary vertex #Sigma p_{T} (GeV); events / bin")
        self.book.fill( sump3[index[0]].rho(), "vertex0MPT%d", 40, 0, 400, title = ";primary vertex MPT (GeV);events / bin")

        self.book.fill( sum(map(sumpt.__getitem__,index[1:])), "vertexGt0SumPt", 100, 0, 400, title = ";secondary vertices #Sigma p_{T};events / bin")
        #self.book.fill( (sumpt[index[0]], sum(map(sumpt.__getitem__,index[1:]))), "vertexSumPt_0_all", (100,100), (0,0), (1200,400), title = ";primary vertex #Sigma p_{T};secondary vertices #Sigma p_{T};events / bin")
        #self.book.fill( (sump3[index[0]].rho(), sump3Secondaries.rho()), "vertexMPT_0_all", (100,100), (0,0), (400,200), title = ";primary vertex MPT;secondary verticies MPT;events / bin")

#####################################
class cutSorter(analysisStep) :
    def __init__(self, listOfSteps = [], applySelections = True ) :
        self.selectors = filter(lambda s: hasattr(s,"select") and type(s)!=passFilter, listOfSteps)
        self.applySelections = applySelections
        self.moreName = "Applied" if applySelections else "Not Applied"
        self.bins = 1 << len(self.selectors)

    def select(self,eventVars) :
        selections = [s.select(eventVars) for s in self.selectors]
        self.book.fill( utils.intFromBits(selections), "cutSorterConfigurationCounts", 
                                  self.bins, -0.5, self.bins-0.5, title = ";cutConfiguration;events / bin")
        return (not self.applySelections) or all(selections)
        
    def endFunc(self, otherChainDict) :
        bins = len(self.selectors)
        self.book.fill(1, "cutSorterNames", bins, 0, bins, title = ";cutName", xAxisLabels = [sel.__class__.__name__ for sel in self.selectors])
        self.book.fill(1, "cutSorterMoreNames", bins, 0, bins, title = ";cutMoreName", xAxisLabels = [sel.moreName for sel in self.selectors])
#####################################
class compareMissing(analysisStep) :
    def __init__(self, missings, bins = 50, min = 0, max = 500) :
        self.missings = missings
        self.missingPairs = [(a,b) for a in missings for b in missings[missings.index(a)+1:]]
        for item in ["bins","min","max"] :
            setattr(self,item,eval(item))
            setattr(self,"%sPair"%item,(eval(item),eval(item)))
    def uponAcceptance(self,eV) :
        for m in self.missings :
            self.book.fill(eV[m].pt(), "%s.pt"%m, self.bins,self.min,self.max, title = ";%s.pt;events / bin"%m)
        for pair in self.missingPairs :
            self.book.fill((eV[pair[0]].pt(),eV[pair[1]].pt()), "%s.pt_vs_%s.pt"%pair, self.binsPair, self.minPair, self.maxPair,
                           title = ";%s.pt;%s.pt;events / bin"%pair)
#####################################
class collector(analysisStep) :
    def __init__(self, vars) :
        self.vars = vars
        self.collection = set([])
    def uponAcceptance(self, eventVars) :
        self.collection.add(tuple([eventVars[var] for var in self.vars]))
    def varsToPickle(self) :
        return ["collection"]
    def mergeFunc(self, products) :
        print "These points %s have been found:"%str(self.vars)
        s = set([]).union(*products["collection"])
        print sorted(list(s))
#####################################
class handleChecker(analysisStep) :
    def __init__(self, matches = ["handle", "Handle", "valid", "Valid"]) :
        self.run = False
        self.matches = matches

    def ofInterest(self, eventVars) :
        out = []
        for var in eventVars :
            for item in self.matches :
                if item in var :
                    out.append(var)
        return list(set(out))
    
    def uponAcceptance(self, eventVars) :
        if self.run : return
        self.run = True

        true = []
        false = []
        for var in self.ofInterest(eventVars) :
            if eventVars[var] :
                true.append(var)
            else :
                false.append(var)
        print "True:",sorted(true)
        print
        print "False:",sorted(false)
#####################################
class smsMedianHistogrammer(analysisStep) :
    def __init__(self, cs) :
        self.cs = cs

        self.nBinsX = 12
        self.xLo =  400.0
        self.xHi = 1000.0

        self.nBinsY = 36
        self.yLo =  100.0
        self.yHi = 1000.0

        self.nBinsZ = 100
        self.zLo =    0.0
        self.zHi = 1000.0

    def nEvents(self, eventVars) :
        self.book.fill((eventVars["susyScanM0"], eventVars["susyScanM12"]), "nEvents",
                       (self.nBinsX, self.nBinsY), (self.xLo, self.yLo), (self.xHi, self.yHi),
                       title = ";m_{mother} (GeV);m_{LSP} (GeV);N events")

    def ht(self, eventVars) :
        var = "%sSumEt%s"%self.cs
        value = eventVars[var] if eventVars[var] else 0.0
        self.book.fill((eventVars["susyScanM0"], eventVars["susyScanM12"], value), var,
                       (self.nBinsX, self.nBinsY, self.nBinsZ), (self.xLo, self.yLo, self.zLo), (self.xHi, self.yHi, self.zHi),
                       title = ";m_{mother} (GeV);m_{LSP} (GeV);%s"%var)

    def mht(self, eventVars) :
        var = "%sSumP4%s"%self.cs
        value = eventVars[var].pt() if eventVars[var] else 0.0
        self.book.fill((eventVars["susyScanM0"], eventVars["susyScanM12"], value), var,
                       (self.nBinsX, self.nBinsY, self.nBinsZ), (self.xLo, self.yLo, self.zLo), (self.xHi, self.yHi, self.zHi),
                       title = ";m_{mother} (GeV);m_{LSP} (GeV);%s"%var)
        

    def jets(self, eventVars) :
        jets = eventVars["%sCorrectedP4%s"%self.cs] if eventVars["%sCorrectedP4%s"%self.cs] else []
        for i in range(2) :
            var = "%sJet%dPt%s"%(self.cs[0], i, self.cs[1])
            if len(jets)<i+1 : value = 0.0
            else :             value = jets.at(i).pt()
            self.book.fill((eventVars["susyScanM0"], eventVars["susyScanM12"], value), var,
                           (self.nBinsX, self.nBinsY, self.nBinsZ), (self.xLo, self.yLo, self.zLo), (self.xHi, self.yHi, self.zHi),
                           title = ";m_{mother} (GeV);m_{LSP} (GeV);%s"%var)

    def forwardJets(self, eventVars) :
        jets = eventVars["%sCorrectedP4%s"%self.cs] if eventVars["%sCorrectedP4%s"%self.cs] else []        
        forwardJets = filter(lambda x:abs(x.eta())>3.0, jets)
        value = max([jet.pt() for jet in forwardJets]) if forwardJets else 0.0
        var = "%sMaxForwardJetPt%s"%self.cs
        self.book.fill((eventVars["susyScanM0"], eventVars["susyScanM12"], value), var,
                       (self.nBinsX, self.nBinsY, self.nBinsZ), (self.xLo, self.yLo, self.zLo), (self.xHi, self.yHi, self.zHi),
                       title = ";m_{mother} (GeV);m_{LSP} (GeV);%s"%var)


    def uponAcceptance(self, eventVars) :
        self.nEvents(eventVars)
        self.ht(eventVars)
        self.mht(eventVars)
        self.jets(eventVars)
        self.forwardJets(eventVars)
        
    def outputSuffix(self) : return stepsMaster.Master.outputSuffix()

    def oneHisto(self, name, zAxisTitle) :
        f = r.TFile(self.outputFileName(), "UPDATE")
        h = f.Get("Master/orFilter/%s"%name)
        outName = "%s_median"%name
        out = r.TH2D(outName, h.GetTitle(),
                     h.GetNbinsX(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax(),
                     h.GetNbinsY(), h.GetYaxis().GetXmin(), h.GetYaxis().GetXmax())
        out.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
        out.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
        out.GetZaxis().SetTitle(zAxisTitle)
        oneD = r.TH1D("%s_oneD"%name, h.GetTitle(), h.GetNbinsZ(), h.GetZaxis().GetXmin(), h.GetZaxis().GetXmax())
        
        for iBinX in range(1, 1+h.GetNbinsX()) :
            for iBinY in range(1, 1+h.GetNbinsY()) :
                oneD.Reset()
                for iBinZ in range(1, 1+h.GetNbinsZ()) :
                    oneD.SetBinContent(iBinZ, h.GetBinContent(iBinX, iBinY, iBinZ))
                if not oneD.Integral() : continue
                probSum = array.array('d', [0.5])
                q = array.array('d', [0.0]*len(probSum))
                oneD.GetQuantiles(len(probSum), q, probSum)
                out.SetBinContent(iBinX, iBinY, q[0])

        f.cd("Master/orFilter")
        out.Write()
        r.gROOT.cd()
        f.Close()
        print "Output updated with %s."%name
        
    def mergeFunc(self, products) :
        self.oneHisto("%sSumEt%s"%self.cs, "Median HT (GeV)")
        self.oneHisto("%sSumP4%s"%self.cs, "Median MHT (GeV)")
        self.oneHisto("%sMaxForwardJetPt%s"%self.cs, "Median pT of (highest pT jet with |#eta| > 3.0) (GeV)")
        for i in range(2) :
            self.oneHisto("%sJet%dPt%s"%(self.cs[0], i, self.cs[1]), "Median pT of jet %d (GeV)"%(i+1))
#####################################


###   Obsolete   ####
#####################################
class variablePtGreaterFilter(analysisStep) :
    '''Obsolete: use ptFilter'''

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s.pt()>=%.1f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable].pt()>=self.threshold
#####################################
class variablePtLessFilter(analysisStep) :
    '''Obsolete: use ptFilter'''

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s.pt()<=%.1f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable].pt()<=self.threshold
#####################################
class vertexRequirementFilter(analysisStep) :
    '''Obsolete: use vertexIndices + multiplicityFilter'''

    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Collisions2010Recipes#Good_Vertex_selection
    def __init__(self, minNdof = 5.0, maxAbsZ = 24.0, maxD0 = 2.0) :
        for item in ["minNdof","maxAbsZ","maxD0"]: setattr(self,item,eval(item))
        self.moreName = "any v: !fake; ndf>=%.1f; |z|<=%.1f cm; d0<=%.1f cm" % (minNdof,maxAbsZ,maxD0)

    def select(self,eventVars) :
        fake,ndof,pos = eventVars["vertexIsFake"], eventVars["vertexNdof"], eventVars["vertexPosition"]
        
        for i in range(pos.size()) :
            if fake.at(i) : continue
            if ndof.at(i) < self.minNdof : continue
            if abs(pos.at(i).Z()) > self.maxAbsZ : continue
            if abs(pos.at(i).Rho()) > self.maxD0 : continue
            return True
        return False
#####################################
class variableGreaterFilter(analysisStep) :
    '''Obsolete: use valueFilter'''

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s>=%.3f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable]>=self.threshold
#####################################
class variableLessFilter(analysisStep) :
    '''Obsolete: use valueFilter'''

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s<%.3f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable]<self.threshold
#####################################
