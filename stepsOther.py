import copy,array,os,collections
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class histogrammer(analysisStep) :

    def __init__(self,var,N,low,up,title="", funcString = "lambda x:x" ) :
        for item in ["var","N","low","up","title","funcString"] : setattr(self,item,eval(item))
        self.oneD = type(var) != tuple
        self.hName = var if self.oneD else "_vs_".join(reversed(var))
        self.moreName = "%s(%s)"% ("(%s)"%funcString if funcString!="lambda x:x" else "", str(self.hName))
        self.funcStringEvaluated = False

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True
            
        value = eventVars[self.var] if self.oneD else \
                tuple(map(eventVars.__getitem__,self.var))
        if value is None or (not self.oneD and None in value) : return

        self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class iterHistogrammer(histogrammer) :

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True
            
        values = eventVars[self.var] if self.oneD else \
                 tuple(map(eventVars.__getitem__,self.var))
        for value in values:
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
    return ([ histogrammer(var,10,-0.5,9.5, title=";%s;events / bin"%xlabel, funcString="lambda x:len(x)")] if xlabel else []) + \
           [ multiplicityFilter(var, nMin = nMin , nMax = nMax) ]
#####################################
class orFilter(analysisStep) :

    def __init__(self, varGreaterCutList = [], varLessCutList = []) :
        self.varGreaterCutList = varGreaterCutList
        self.varLessCutList = varLessCutList
        self.moreName = '|'.join(["%s>%.2f"%i for i in varGreaterCutList]+\
                                 ["%s<%.2f"%i for i in varLessCutList])
        
    def select(self,eventVars) :
        for var,cut in self.varGreaterCutList:
            if eventVars[var] > cut: return True
        for var,cut in self.varLessCutList:
            if eventVars[var] < cut: return True
        return False
#####################################
class skimmer(analysisStep) :
    
    def __init__(self) :
        self.outputTree=0
        self.moreName="(see below)"
        self.alsoWriteExtraTree=False #hard-code until this functionality is fixed
        self.outputTreeExtraIsSetup=False

    def requiresNoSetBranchAddress(self) :
        return True

    def setup(self, chain, fileDir, name, outputDir) :
        self.fileDir = fileDir
        self.outputFileName = "%s/%s_skim.root"%(outputDir, name)
        os.system("mkdir -p "+outputDir)
        self.outputFile = r.TFile(self.outputFileName,"RECREATE")

        self.setupMainChain(chain, fileDir)
        self.initExtraTree()

    def setupMainChain(self, chain, fileDir) :
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        if chain and chain.GetEntry(0)>0 :
            self.outputTree=chain.CloneTree(0)    #clone structure of tree (but no entries)
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
            self.supportedOtherTypes=[type(r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0))]
            
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

    def varsToPickle(self) :
        return ["outputFileName"]

    def mergeFunc(self, productList, someLooper) :
        print "The %d skim files have been written."%len(productList)
        print "( e.g. %s )"%productList[0]["outputFileName"]
        print utils.hyphens
#####################################
class hbheNoiseFilter(analysisStep) :
    def __init__(self, invert = False) :
        self.invert = invert

    def select (self,eventVars) :
        return eventVars["hbheNoiseFilterResult"]^self.invert
#####################################
class variableGreaterFilter(analysisStep) :

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s>=%.3f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable]>=self.threshold
#####################################
class variableLessFilter(analysisStep) :

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s<%.3f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable]<self.threshold
#####################################
class variablePtGreaterFilter(analysisStep) :

    def __init__(self, threshold, variable, suffix = ""):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "%s.pt()>=%.1f %s" % (variable,threshold,suffix)

    def select (self,eventVars) :
        return eventVars[self.variable].pt()>=self.threshold
#####################################
class objectPtSelector(analysisStep) :

    def __init__(self, cs, ptThreshold, index, p4String):
        self.index = index
        self.ptThreshold = ptThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%s%s%s" % (self.cs[0], p4String, self.cs[1])
        self.moreName = "%s%s; pT[index[%d]]>=%.1f GeV" % (self.cs[0], self.cs[1], jetIndex, jetPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.index : return False
        p4s = eventVars[self.p4sName]
        return self.ptThreshold <= p4s.at(indices[self.index]).pt()
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
class objectPtVetoer(analysisStep) :

    def __init__(self, collection, p4String, suffix, ptThreshold, index):
        self.index = index
        self.ptThreshold = ptThreshold
        self.varName = collection + p4String + suffix
        self.moreName = "%s; %s; pT[%d]< %.1f GeV" % (collection, suffix, index, ptThreshold )

    def select (self,eventVars) :
        p4s = eventVars[self.varName]
        if p4s.size() <= self.index : return True
        return p4s.at(self.index).pt() < self.ptThreshold

#    def uponRejection(self,eventVars) :
#        p4Vector=eventVars[self.objectCollection+self.objectP4String+self.objectSuffix]
#        self.book.fill(p4Vector[self.objectIndex].eta(),self.objectCollection+"Eta"+self.objectSuffix,100,-5.0,5.0,";#eta;events / bin")
#####################################
class soloObjectPtSelector(analysisStep) :

    def __init__(self, collection, p4String, suffix, ptThreshold):
        self.ptThreshold = ptThreshold
        self.varName = collection + p4String + suffix        
        self.moreName = "%s; %s; pT> %.1f GeV" % (collection, suffix, ptThreshold )

    def select (self,eventVars) :
        return self.ptThreshold <= eventVars[self.varName].pt()
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
class vertexRequirementFilter(analysisStep) :

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

    def setup(self,chain,fileDir,name,outputDir) :
        self.outputFileName = outputDir+"/"+name+"_pickEvents.txt"
        self.outputFile = open(self.outputFileName,"w")
        
    def uponAcceptance(self,eventVars) :
        line="%14d:%6d:%14d\n"%(eventVars["run"], eventVars["lumiSection"], eventVars["event"])
        self.outputFile.write(line) #slow: faster to buffer output, write less frequently

    def endFunc(self, otherChainDict) :
        print utils.hyphens
        self.outputFile.close()
        print "The pick events spec. file \""+self.outputFileName+"\" has been written."

    def varsToPickle(self) :
        return ["outputFileName"]
    
#####################################
class bxHistogrammer(analysisStep) :

    def __init__(self) :
        self.nBx=3564+1 #one extra in case count from 1

    def uponAcceptance(self,eventVars) :
        self.book.fill(eventVars["bunch"],"bx",self.nBx,-0.5,0.5,";bx of event;events / bin")
#####################################
class jsonMaker(analysisStep) :

    def __init__(self) :
        self.runLsDict=collections.defaultdict(list)
        self.moreName="see below"

    def setup(self,chain,fileDir,name,outputDir) :
        self.outputFileName=outputDir+"/"+name+".json"
        os.system("mkdir -p "+outputDir)
        
    def uponAcceptance(self,eventVars) :
        self.runLsDict[eventVars["run"]].append(eventVars["lumiSection"])
    
    def varsToPickle(self) :
        return ["outputFileName", "runLsDict"]

    def mergeFunc(self, productList, someLooper) :
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

        outFileName = [p["outputFileName"] for p in productList][0]
        runLsDicts = [p["runLsDict"] for p in productList]
        
        outFile = open(outFileName,"w")
        outFile.write(aJson(mergedDict(runLsDicts)))
        outFile.close()
        print "The json file %s has been written."%outFileName
        print utils.hyphens
#####################################
class duplicateEventCheck(analysisStep) :
    def __init__(self) :
        self.events = collections.defaultdict(list)

    def uponAcceptance(self,ev) :
        self.events[(ev["run"], ev["lumiSection"])].append(ev["event"])

    def varsToPickle(self) :
        return ["events"]

    def mergeFunc(self, productList, someLooper) :
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
        events = mergedEventDicts([p["events"] for p in productList])
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
        self.badJet = r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,0.0,0.0,0.0)
        self.moreName = "%s%s; dR>%5.3f when deltaPhiStar<%5.3f"%(self.jets[0], self.jets[1], self.dR, self.dPhiStarCut)
        
    def select(self, eventVars) :
        d = eventVars[self.dps]
        index = d["DeltaPhiStarJetIndex"]
        if d["DeltaPhiStar"]>self.dPhiStarCut :
            return True
        jet = eventVars["%sCorrectedP4%s"%self.jets].at(index)
        self.badJet.SetCoordinates(jet.pt(),jet.eta(),jet.phi(),jet.E())
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
        self.badThing = r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,0.0,0.0,0.0)
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

        self.badThing.SetCoordinates(thing.pt(),thing.eta(),thing.phi(),thing.E())
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
    def __init__(self, listOfSteps, applySelections = True ) :
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
