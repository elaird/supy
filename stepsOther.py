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

        self.book(eventVars).fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
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
            self.book(eventVars).fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
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

    def setup(self,chain,fileDir,name,outputDir) :
        self.fileDir = fileDir
        self.outputFileName=outputDir+"/"+name+"_skim.root"
        os.system("mkdir -p "+outputDir)
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        if chain and chain.GetEntry(0)>0 :
            self.outputTree=chain.CloneTree(0)    #clone structure of tree (but no entries)
        if not self.outputTree :                  #in case the chain has 0 entries
            r.gROOT.cd()
            return
        self.outputTree.SetDirectory(r.gDirectory)#put output tree in correct place
        chain.CopyAddresses(self.outputTree)      #associate branch addresses

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
        
    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        if not self.quietMode : print utils.hyphens

        self.outputFile.cd(self.fileDir)                          #cd to file
        if self.outputTree :         self.outputTree.Write()      #write main tree
        if self.alsoWriteExtraTree : self.outputTreeExtra.Write() #write a tree with "extra" variables

        #store other chains
        for (dirName,treeName),chain in otherChainDict.iteritems() :
            self.outputFile.mkdir(dirName).cd()
            if chain and chain.GetEntry(0)>0 :
                outChain=chain.CloneTree()
                if outChain :
                    outChain.SetName(treeName)
                    outChain.SetDirectory(r.gDirectory)
                    outChain.Write()
        
        self.outputFile.Close()
        if not self.quietMode : print "The skim file \""+self.outputFileName+"\" has been written."
#####################################
class hbheNoiseFilter(analysisStep) :

    def select (self,eventVars) :
        return eventVars["hbheNoiseFilterResult"]
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
#        self.book(eventVars).fill(p4Vector[self.objectIndex].eta(),self.objectCollection+"Eta"+self.objectSuffix,100,-5.0,5.0,";#eta;events / bin")
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
        book = self.book(ev).fill(value,"ptRatio", 50, 0.0, 2.0, title = ";%s / %s;events / bin"%(self.numVar,self.denVar) )
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
        print self.name(),printList
#####################################
class bxFilter(analysisStep) :

    def __init__(self,bxList) :
        self.bxList = bxList
        self.moreName = "[%s]" % ",".join(bxList)

    def select (self,eventVars) :
        return eventVars["bunch"] in self.bxList
#####################################
class displayer(analysisStep) :
    
    def __init__(self,jets = ("",""), met = "", muons = "", electrons = "", photons = "", recHits = "",
                 recHitPtThreshold = -1.0, scale = 200.0, etRatherThanPt = False, doGenParticles = False,
                 doEtaPhiPlot = True, hotTpThreshold = 63.5, deltaPhiStarExtraName = "",
                 printOtherJetAlgoQuantities = False, markusMode = False, tipToTail = False) :

        self.moreName = "(see below)"

        for item in ["scale","jets","met","muons","electrons","photons",
                     "recHits","recHitPtThreshold","doGenParticles",
                     "doEtaPhiPlot","hotTpThreshold","deltaPhiStarExtraName","printOtherJetAlgoQuantities",
                     "tipToTail"] :
            setattr(self,item,eval(item))

        self.jetRadius = 0.7 if "ak7Jet" in self.jets[0] else 0.5
        self.genJets = self.jets
        self.genMet  = self.met.replace("P4","GenMetP4")
        self.deltaHtName = "%sDeltaPseudoJetEt%s"%self.jets if etRatherThanPt else "%sDeltaPseudoJetPt%s"%self.jets
        
        self.doGen = False
        self.doReco = not self.doGenParticles
        self.doLeptons = True
        self.helper = r.displayHelper()

        self.titleSizeFactor = 1.0
        
        self.legendDict = collections.defaultdict(int)
        self.legendList = []
        

    def switchGenOn(self) :
        self.doGen=True

    def setup(self,chain,fileDir,name,outputDir) :
        someDir=r.gDirectory
        self.outputFileName=outputDir+"/"+name+"_displays.root"
        os.system("mkdir -p "+outputDir)
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        someDir.cd()

        self.canvas = utils.canvas("canvas")
        self.canvas.SetFixedAspectRatio()
        self.canvasIndex = 0

        self.ellipse = r.TEllipse()
        self.ellipse.SetFillStyle(0)

        self.deadBox = r.TBox()
        self.deadBox.SetFillColor(r.kBlack)
        self.deadBox.SetLineColor(r.kBlack)

        self.coldBox = r.TBox()
        self.coldBox.SetFillColor(r.kOrange-6)
        self.coldBox.SetLineColor(r.kOrange-6)

        self.hotBox = r.TBox()
        self.hotBox.SetFillColor(r.kRed)
        self.hotBox.SetLineColor(r.kRed)
        
        self.hcalBox = r.TBox()
        self.hcalBox.SetFillColor(r.kGreen)
        self.hcalBox.SetLineColor(r.kGreen)
        
        self.line = r.TLine()
        self.arrow = r.TArrow()
        self.text = r.TText()
        self.latex = r.TLatex()

        self.alphaFuncs=[
            self.makeAlphaTFunc(0.55,r.kBlack),
            self.makeAlphaTFunc(0.50,r.kOrange+3),
            self.makeAlphaTFunc(0.45,r.kOrange+7)
            ]

        epsilon=1.0e-6
        self.mhtLlHisto=r.TH2D("mhtLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashH_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        self.metLlHisto=r.TH2D("metLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashE_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        self.mhtLlHisto.SetDirectory(0)
        self.metLlHisto.SetDirectory(0)

    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        self.outputFile.Write()
        self.outputFile.Close()
        #if not self.quietMode : print "The display file \""+self.outputFileName+"\" has been written."
        if not self.splitMode :
            if not self.quietMode : print utils.hyphens
            psFileName=self.outputFileName.replace(".root",".ps")
            utils.psFromRoot([self.outputFileName],psFileName,self.quietMode)
        del self.canvas

    def prepareText(self, params, coords) :
        self.text.SetTextSize(params["size"])
        self.text.SetTextFont(params["font"])
        self.text.SetTextColor(params["color"])
        self.textSlope = params["slope"]

        self.textX = coords["x"]
        self.textY = coords["y"]
        self.textCounter = 0

    def printText(self, message) :
        self.text.DrawText(self.textX, self.textY - self.textCounter * self.textSlope, message)
        self.textCounter += 1

    def printEvent(self, eventVars, params, coords) :
        self.prepareText(params, coords)
        for message in ["Run   %#10d"%eventVars["run"],
                        "Ls    %#10d"%eventVars["lumiSection"],
                        "Event %#10d"%eventVars["event"]
                        ] :
            self.printText(message)
        
    def printVertices(self, eventVars, params, coords, nMax) :
        self.prepareText(params, coords)
        self.printText("Vertices")
        self.printText("ID   Z(cm) sumPt(GeV)")
        self.printText("---------------------")

        nVertices = eventVars["vertexNdof"].size()
        for i in range(nVertices) :
            if nMax<=i :
                self.printText("[%d more not listed]"%(nVertices-nMax))
                break
            
            out = "%2s %6.2f  %5.0f"%("G " if i in eventVars["vertexIndices"] else "  ", eventVars["vertexPosition"].at(i).z(), eventVars["vertexSumPt"].at(i))
            self.printText(out)

    def printJets(self, eventVars, params, coords, jets, nMax) :
        self.prepareText(params, coords)
        jets2 = (jets[0].replace("xc",""),jets[1])
        isPf = "PF" in jets[0]
        p4Vector         = eventVars['%sCorrectedP4%s'     %jets2]
        corrFactorVector = eventVars['%sCorrFactor%s'      %jets2]

        if not isPf :
            jetEmfVector  = eventVars['%sEmEnergyFraction%s'%jets2]
            jetFHpdVector = eventVars['%sJetIDFHPD%s'       %jets2]
            jetN90Vector  = eventVars['%sJetIDN90Hits%s'    %jets2]

            loose = eventVars["%sJetIDloose%s"%jets2]
            tight = eventVars["%sJetIDtight%s"%jets2]
            
        else :
            chf = eventVars["%sFchargedHad%s"%jets2]
            nhf = eventVars["%sFneutralHad%s"%jets2]

            cef = eventVars["%sFchargedEm%s"%jets2]
            nef = eventVars["%sFneutralEm%s"%jets2]

            cm  = eventVars["%sNcharged%s"%jets2]
            nm  = eventVars["%sNneutral%s"%jets2]
            
            loose = eventVars["%sPFJetIDloose%s"%jets2]
            tight = eventVars["%sPFJetIDtight%s"%jets2]
            
        jetIndices = eventVars["%sIndices%s"%jets]
        jetIndicesOther = eventVars["%sIndicesOther%s"%jets]

        self.printText(jets[0]+jets[1])
        self.printText("ID   pT  eta  phi%s"%("   EMF  fHPD N90" if not isPf else "  CHF  NHF  CEF  NEF CM"))
        self.printText("-----------------%s"%("----------------" if not isPf else "-----------------------"))

        nJets = p4Vector.size()
        for iJet in range(nJets) :
            if nMax<=iJet :
                self.printText("[%d more not listed]"%(nJets-nMax))
                break
            jet=p4Vector[iJet]

            outString = "%1s%1s"% ("L" if loose.at(iJet) else " ", "T" if tight.at(iJet) else " ")
            outString+="%5.0f %4.1f %4.1f"%(jet.pt(), jet.eta(), jet.phi())

            if not isPf :
                outString+=" %5.2f %5.2f %3d"%(jetEmfVector.at(iJet), jetFHpdVector.at(iJet), jetN90Vector.at(iJet))
            else :
                outString+=" %4.2f %4.2f %4.2f %4.2f%3d"%(chf.at(iJet), nhf.at(iJet), cef.at(iJet), nef.at(iJet), cm.at(iJet))
            self.printText(outString)

    def printKinematicVariables(self, eventVars, params, coords, jets, jets2) :
        self.prepareText(params, coords)
        
        def go(j) :
            l = [eventVars["%s%s%s"  %(j[0], "SumEt",        j[1])],
                 eventVars["%s%s%s"  %(j[0], "SumP4",        j[1])].pt() if eventVars["%s%s%s"%(j[0], "SumP4",  j[1])] else 0,
                 eventVars["%s%s%s"  %(j[0], "AlphaTEt",     j[1])],
                 eventVars["%s%s%s%s"%(j[0], "DeltaPhiStar", j[1], self.deltaPhiStarExtraName)]["DeltaPhiStar"],
                 ]
            self.printText("%14s %4.0f %4.0f %6.3f %4.2f"%tuple([j[0]+j[1]]+l))

        self.printText("jet collection   HT  MHT alphaT Dphi*")
        self.printText("-------------------------------------")
        
        go(jets)
        if jets2!=None :
            go(jets2)
        
    def passBit(self, var) :
        return " p" if var else " f"

    def printCutBits(self, eventVars, params, coords, jets, jets2, met, met2) :
        self.prepareText(params, coords)

        def go(j, m) :
            J2 = None if len(eventVars["%sIndices%s"%j])<2 else eventVars['%sCorrectedP4%s'%j].at(eventVars["%sIndices%s"%j][1]).pt()
            HT = eventVars["%sSumEt%s"%j]
            aT = eventVars["%sAlphaTEt%s"%j]
            MM = eventVars["%sMht%s_Over_%s"%(j[0], j[1], m)]
            DE = eventVars["%sDeltaPhiStar%s%s"%(j[0], j[1], self.deltaPhiStarExtraName)]["DeltaPhiStar"]>0.5 or \
                 eventVars["%sDeadEcalDR%s%s"  %(j[0], j[1], self.deltaPhiStarExtraName)]                >0.3

            all = (J2!=None and J2 > 100.0) and \
                  (HT!=None and HT > 350.0) and \
                  (aT!=None and aT > 0.550) and \
                  (DE!=None and DE        ) and \
                  (MM!=None and MM < 1.250)
            
            self.printText("%14s  %s %s %s %s %s  %s"%(j[0]+j[1],
                                                       self.passBit(J2!=None and J2 > 100.0),
                                                       self.passBit(HT!=None and HT > 350.0),
                                                       self.passBit(aT!=None and aT > 0.550),
                                                       self.passBit(DE!=None and DE),
                                                       self.passBit(MM!=None and MM < 1.250),
                                                       "candidate" if all else "",
                                                       )
                           )

        self.printText("jet collection  J2 HT aT DE MM")
        self.printText("------------------------------")

        go(jets, met)
        if jets2!=None and met2!=None :
            go(jets2, met2)
        
    def drawSkeleton(self, coords, color) :
        r.gPad.AbsCoordinates(False)
        
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(1)
        self.ellipse.SetLineStyle(1)
        self.ellipse.DrawEllipse(coords["x0"], coords["y0"], coords["radius"], coords["radius"], 0.0, 360.0, 0.0, "")

        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-coords["radius"], coords["y0"]                 , coords["x0"]+coords["radius"], coords["y0"]                 )
        self.line.DrawLine(coords["x0"]                 , coords["y0"]-coords["radius"], coords["x0"]                 , coords["y0"]+coords["radius"])

    def drawScale(self, color, size, scale, point) :
        self.latex.SetTextSize(size)
        self.latex.SetTextColor(color)
        self.latex.DrawLatex(point["x"], point["y"],"radius = "+str(scale)+" GeV p_{T}")

    def drawP4(self, c, p4, color, lineWidth, arrowSize, p4Initial = None) :
        x0 = c["x0"]+p4Initial.px()*c["radius"]/c["scale"] if p4Initial else c["x0"]
        y0 = c["y0"]+p4Initial.py()*c["radius"]/c["scale"] if p4Initial else c["y0"]
        x1 = x0+p4.px()*c["radius"]/c["scale"]
        y1 = y0+p4.py()*c["radius"]/c["scale"]

        #self.line.SetLineColor(color)
        #self.line.SetLineWidth(lineWidth)
        #self.line.DrawLine(x0,y0,x1,y1)

        self.arrow.SetLineColor(color)
        self.arrow.SetLineWidth(lineWidth)
        self.arrow.SetArrowSize(arrowSize)
        self.arrow.SetFillColor(color)
        self.arrow.DrawArrow(x0,y0,x1,y1)
        
    def drawCircle(self, p4, color, lineWidth, circleRadius, lineStyle = 1) :
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(lineWidth)
        self.ellipse.SetLineStyle(lineStyle)
        self.ellipse.DrawEllipse(p4.eta(), p4.phi(), circleRadius, circleRadius, 0.0, 360.0, 0.0, "")

    def legendFunc(self, color, name, desc) :
        if not self.legendDict[name] :
            self.legendDict[name] = True
            self.legendList.append( (color, desc, "l") )

    def drawGenJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "genJet", desc = "GEN jets (%s%s)"%self.genJets)

        genJets = "%sGenJetP4%s"%self.genJets
        if genJets[:2] == "xc": genJets = genJets[2:]
        p4s = eventVars[genJets]
        if self.tipToTail :
            phiOrder = utils.phiOrder(p4s, range(len(p4s)))
            partials = utils.partialSumP4(p4s, phiOrder)
            mean = utils.partialSumP4Centroid(partials)
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, 0.3*arrowSize, partials[i]-mean)
            return
        for jet in p4s :
            self.drawP4(coords, jet, color, lineWidth, arrowSize)
            
    def drawGenParticles(self, eventVars, coords, color, lineWidth, arrowSize, statusList = None, pdgIdList = None, motherList = None, label = "", circleRadius = None) :
        self.legendFunc(color, name = "genParticle"+label, desc = label)

        for iParticle,particle in enumerate(eventVars["genP4"]) :
            if statusList!=None and eventVars["genStatus"].at(iParticle) not in statusList : continue
            if pdgIdList!=None and eventVars["genPdgId"].at(iParticle) not in pdgIdList : continue
            if motherList!=None and eventVars["genMotherPdgId"][iParticle] not in motherList : continue
            if circleRadius==None :
                self.drawP4(coords, particle, color, lineWidth, arrowSize)
            else :
                self.drawCircle(particle, color, lineWidth, circleRadius)
            
    def drawCleanJets(self, eventVars, coords, jets, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%scleanJet%s"%jets, desc = "clean jets (%s%s)"%jets)

        p4s = eventVars['%sCorrectedP4%s'%jets]
        if self.tipToTail :
            phiOrder = eventVars["%sIndicesPhi%s"%self.jets]
            partials = eventVars["%sPartialSumP4%s"%self.jets]
            mean = utils.partialSumP4Centroid(partials)
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, 0.3*arrowSize, partials[i]-mean)
            return

        cleanJetIndices = eventVars["%sIndices%s"%jets]
        for iJet in cleanJetIndices :
            self.drawP4(coords, p4s.at(iJet), color, lineWidth, arrowSize)
            
    def drawOtherJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sotherJet%s"%self.jets, desc = "\"other\" jets (%s%s)"%self.jets)

        p4Vector = eventVars["%sCorrectedP4%s"%self.jets]
        otherJetIndices = eventVars["%sIndicesOther%s"%self.jets]
        for index in otherJetIndices :
            self.drawP4(coords, p4Vector.at(index), color, lineWidth, arrowSize)
            
    def drawIgnoredJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%signoredJet%s"%self.jets, desc = "ignored jets (%s%s)"%self.jets)

        p4s = eventVars["%sCorrectedP4%s"%self.jets]
        ignoredJetIndices = set(range(len(p4s))) \
                            - set(eventVars["%sIndices%s"%self.jets]) \
                            - set(eventVars["%sIndicesOther%s"%self.jets])
        if self.tipToTail :
            phiOrder = utils.phiOrder(p4s, ignoredJetIndices)
            partials = utils.partialSumP4(p4s, phiOrder)
            goodPartials = eventVars["%sPartialSumP4%s"%self.jets]
            offset = goodPartials[-1] - eventVars["%sPartialSumP4Centroid%s"%self.jets]
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, arrowSize, partials[i]+offset)
            return
        for iJet in ignoredJetIndices :
            self.drawP4(coords, p4s.at(iJet), color, lineWidth, arrowSize)
            
    def drawMht(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%smht%s"%self.jets, desc = "MHT (%s%s)"%self.jets)

        sump4 = eventVars["%sSumP4%s"%self.jets]
        if self.tipToTail :
            phiOrder = eventVars["%sIndicesPhi%s"%self.jets]
            partials = eventVars["%sPartialSumP4%s"%self.jets]
            mean = eventVars["%sPartialSumP4Centroid%s"%self.jets]
            if sump4 : self.drawP4(coords, -sump4,color,lineWidth,arrowSize, partials[-1]-mean)
            return
        if sump4 : self.drawP4(coords, -sump4, color, lineWidth, arrowSize)
            
    def drawHt(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sht%s"%self.jets, desc = "H_{T} (%s%s)"%self.jets)

        ht = eventVars["%sSumPt%s"%self.jets]
            
        y = coords["y0"]-coords["radius"]-0.05
        l = ht*coords["radius"]/coords["scale"]
        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-l/2.0, y, coords["x0"]+l/2.0, y)
        
    def drawNJetDeltaHt(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sdeltaHt%s"%self.jets, desc = "#DeltaH_{T} (%s%s)"%self.jets)

        y = coords["y0"]-coords["radius"]-0.03
        l=eventVars[self.deltaHtName]*coords["radius"]/coords["scale"]
        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-l/2.0, y, coords["x0"]+l/2.0, y)

    def drawMet(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "met%s"%self.met, desc = "MET (%s)"%self.met)
        self.drawP4(coords, eventVars[self.met], color, lineWidth, arrowSize)
            
    def drawGenMet(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "genMet", desc = "GEN MET (%s)"%self.genMet)
        self.drawP4(coords, eventVars[self.genMet], color, lineWidth, arrowSize)
            
    def drawMuons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%smuon%s"%self.muons, desc = "muons (%s%s)"%self.muons)
        p4Vector=eventVars["%sP4%s"%self.muons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawElectrons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%selectron%s"%self.electrons, desc = "electrons (%s%s)"%self.electrons)
        p4Vector=eventVars["%sP4%s"%self.electrons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawPhotons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sphoton%s"%self.photons, desc = "photons (%s%s)"%self.photons)
        p4Vector=eventVars["%sP4%s"%self.photons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawTaus(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%stau%s"%self.taus, desc = "taus (%s%s)"%self.taus)
        p4Vector=eventVars[self.tauCollection+'P4'+self.tauSuffix]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawCleanedRecHits(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "cleanedRecHits%s"%self.recHits, desc = "cleaned RecHits (%s)"%self.recHits)

        subDetectors=[]
        if self.recHits=="Calo" :
            subDetectors=["Eb","Ee","Hbhe","Hf"]
        if self.recHits=="PF" :
            subDetectors=["Ecal","Hcal","Hfem","Hfhad","Ps"]

        for detector in subDetectors :
            for collectionName in ["","cluster"] :
                varName = "rechit"+collectionName+self.recHits+"P4"+detector
                if varName not in eventVars : continue
                for hit in eventVars[varName] :
                    if hit.pt()<self.recHitPtThreshold : continue
                    self.drawP4(coords, hit, color, lineWidth, arrowSize)
            
    def makeAlphaTFunc(self,alphaTValue,color) :
        alphaTFunc=r.TF1("#alpha_{T} = %#4.2g"%alphaTValue,
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(color)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc

    def drawEtaPhiPlot (self, eventVars, corners) :
        pad=r.TPad("etaPhiPad", "etaPhiPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetTickx()
        pad.SetTicky()

        etaPhiPlot = r.TH2D("etaPhi",";#eta;#phi;",1, -3.0, 3.0, 1, -r.TMath.Pi(), r.TMath.Pi() )
        etaPhiPlot.SetStats(False)
        etaPhiPlot.Draw()

        ebEe = 1.479
        self.line.SetLineColor(r.kBlack)
        self.line.DrawLine(-ebEe, etaPhiPlot.GetYaxis().GetXmin(), -ebEe, etaPhiPlot.GetYaxis().GetXmax() )
        self.line.DrawLine( ebEe, etaPhiPlot.GetYaxis().GetXmin(),  ebEe, etaPhiPlot.GetYaxis().GetXmax() )
        suspiciousJetColor = r.kBlack
        suspiciousJetStyle = 2
        
        def drawEcalBox(fourVector, nBadXtals, maxStatus) :
            value = (0.087/2) * nBadXtals / 25
            args = (fourVector.eta()-value, fourVector.phi()-value, fourVector.eta()+value, fourVector.phi()+value)
            if maxStatus==14 :
                self.deadBox.DrawBox(*args)
            elif fourVector.Et()>=self.hotTpThreshold :
                self.hotBox.DrawBox(*args)
            else :
                self.coldBox.DrawBox(*args)
                
        def drawHcalBox(fourVector) :
            value = 0.087/2
            args = (fourVector.eta()-value, fourVector.phi()-value, fourVector.eta()+value, fourVector.phi()+value)
            self.hcalBox.DrawBox(*args)
                
        #draw dead ECAL regions
        nRegions = eventVars["ecalDeadTowerTrigPrimP4"].size()
        for iRegion in range(nRegions) :
            drawEcalBox(fourVector = eventVars["ecalDeadTowerTrigPrimP4"].at(iRegion),
                        nBadXtals  = eventVars["ecalDeadTowerNBadXtals"].at(iRegion),
                        maxStatus  = eventVars["ecalDeadTowerMaxStatus"].at(iRegion),
                        )

        #draw masked HCAL regions
        nBadHcalChannels = eventVars["hcalDeadChannelP4"].size()
        for iChannel in range(nBadHcalChannels) :
            drawHcalBox(fourVector = eventVars["hcalDeadChannelP4"].at(iChannel))

        if self.doGenParticles :
            self.drawGenParticles(eventVars,r.kMagenta, lineWidth = 1, arrowSize = -1.0, statusList = [1], pdgIdList = [22],
                                  motherList = [1,2,3,4,5,6,-1,-2,-3,-4,-5,-6], label = "status 1 photon w/quark as mother", circleRadius = 0.15)
            self.drawGenParticles(eventVars,r.kOrange, lineWidth = 1, arrowSize = -1.0, statusList = [1], pdgIdList = [22],
                                  motherList = [22], label = "status 1 photon w/photon as mother", circleRadius = 0.15)
        else :
            d = eventVars["%sDeltaPhiStar%s%s"%(self.jets[0],self.jets[1],self.deltaPhiStarExtraName)]
            suspiciousJetIndex = d["DeltaPhiStarJetIndex"]
            #title = "#Delta#phi * = %6.4f"%d["DeltaPhiStar"]
            #title+= "#semicolon index = %d"%suspiciousJetIndex
            etaPhiPlot.SetTitle("")

            jets = eventVars["%sCorrectedP4%s"%self.jets]
            for index in range(jets.size()) :
                jet = jets.at(index)
                if index in eventVars["%sIndices%s"%self.jets] :
                    self.drawCircle(jet, r.kBlue, lineWidth = 1, circleRadius = self.jetRadius)
                else :
                    self.drawCircle(jet, r.kCyan, lineWidth = 1, circleRadius = self.jetRadius)
                if index==suspiciousJetIndex :
                    self.drawCircle(jet, suspiciousJetColor, lineWidth = 1, circleRadius = self.jetRadius - 0.04, lineStyle = suspiciousJetStyle)
                    

        legend1 = r.TLegend(0.02, 0.9, 0.72, 1.0)
        legend1.SetFillStyle(0)
        legend1.SetBorderSize(0)
        legend1.AddEntry(self.deadBox,"dead ECAL cells","f")
        legend1.AddEntry(self.coldBox,"dead ECAL cells w/TP link","f")
        legend1.AddEntry(self.hotBox, "dead ECAL cells w/TP ET>%4.1f GeV"%self.hotTpThreshold,"f")
        legend1.Draw()

        legend2 = r.TLegend(0.58, 0.933, 0.98, 1.0)
        legend2.SetFillStyle(0)
        legend2.SetBorderSize(0)
        legend2.AddEntry(self.hcalBox,"masked HCAL cells","f")
        self.ellipse.SetLineColor(suspiciousJetColor)
        self.ellipse.SetLineStyle(suspiciousJetStyle)
        legend2.AddEntry(self.ellipse,"jet determining #Delta#phi*","l")
        legend2.Draw()

        self.canvas.cd()
        pad.Draw()
        return [pad, etaPhiPlot, legend1, legend2]

    def drawAlphaPlot (self, eventVars, color, showAlphaTMet, corners) :
        pad = r.TPad("alphaTpad", "alphaTpad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetTickx()
        pad.SetTicky()

        title = ";"
        if showAlphaTMet :
            title +="#color[%d]{MET/HT}              "%r.kGreen
        title+= "#color[%d]{MHT/HT};#DeltaHT/HT"%r.kBlue
        alphaTHisto = r.TH2D("alphaTHisto",title,100,0.0,1.0,100,0.0,1.0)
        alphaTMetHisto = alphaTHisto.Clone("alphaTMetHisto")

        mht = eventVars["%sSumP4%s"%self.jets].pt() if eventVars["%sSumP4%s"%self.jets] else 0
        met = eventVars[self.met].pt()
        ht  = eventVars["%sSumPt%s"%self.jets]
        deltaHt   = eventVars[self.deltaHtName]
        alphaT    = eventVars["%sAlphaTEt%s"%self.jets]    #hack: hard-coded Et
        alphaTMet = eventVars["%sAlphaTMetEt%s"%self.jets] #hack: hard-coded Et
        
        if ht : alphaTHisto.Fill(mht/ht,deltaHt/ht)
        alphaTHisto.SetStats(False)
        alphaTHisto.SetMarkerStyle(29)
        alphaTHisto.GetYaxis().SetTitleOffset(1.15)
        alphaTHisto.SetMarkerColor(r.kBlue)
        alphaTHisto.GetXaxis().SetTitleSize(self.titleSizeFactor*alphaTHisto.GetXaxis().GetTitleSize())
        alphaTHisto.GetYaxis().SetTitleSize(self.titleSizeFactor*alphaTHisto.GetYaxis().GetTitleSize())
        alphaTHisto.Draw("p")

        if showAlphaTMet :
            if ht : alphaTMetHisto.Fill(met/ht,deltaHt/ht)
            alphaTMetHisto.SetStats(False)
            alphaTMetHisto.SetMarkerStyle(29)
            alphaTMetHisto.GetYaxis().SetTitleOffset(1.25)
            alphaTMetHisto.SetMarkerColor(r.kGreen)
            alphaTMetHisto.Draw("psame")

        legend1 = r.TLegend(0.1, 0.6, 1.0, 0.9)
        legend1.SetBorderSize(0)
        legend1.SetFillStyle(0)
        
        for func in self.alphaFuncs :
            func.Draw("same")
            legend1.AddEntry(func,func.GetName(),"l")

        legend1.Draw()

        #legend2 = r.TLegend(0.1, 0.4, 1.0, 0.6)
        #legend2.SetBorderSize(0)
        #legend2.SetFillStyle(0)
        #legend2.AddEntry(alphaTHisto,"this event","p")
        #if showAlphaTMet :
        #    legend2.AddEntry(alphaTMetHisto,"this event","p")
        #legend2.Draw()
        
        self.canvas.cd()
        pad.Draw()
        return [pad, alphaTHisto, alphaTMetHisto, legend1]

    def fillHisto(self,histo,lls,mhts) :
        for i in range(len(mhts)) :
            histo.Fill(lls[i],mhts[i])
        
    def drawMhtLlPlot (self, eventVars, color, corners) :
        stuffToKeep=[]
        pad = r.TPad("mhtLlPad","mhtLlPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetLeftMargin(0.3)
        pad.SetRightMargin(0.15)

        mets       =eventVars[self.jetCollection+"mets"+self.jetSuffix]
        mhts       =eventVars[self.jetCollection+"mhts"+self.jetSuffix]
        lls        =eventVars[self.jetCollection+"lls"+self.jetSuffix]
        nVariedJets=eventVars[self.jetCollection+"nVariedJets"+self.jetSuffix]
        
        self.mhtLlHisto.Reset()
        self.metLlHisto.Reset()
        self.helper.Fill(self.mhtLlHisto,lls,mhts,nVariedJets)
        self.helper.Fill(self.metLlHisto,lls,mets,nVariedJets)

        histo=self.metLlHisto

        #histo.SetStats(False)
        histo.GetYaxis().SetTitleOffset(1.25)
        histo.SetMarkerColor(r.kBlack)
        histo.Draw("colz")

        stats=histo.GetListOfFunctions().FindObject("stats")
        if (stats!=None) :
            stats.SetX1NDC(0.01);
            stats.SetX2NDC(0.25);
            stats.SetY1NDC(0.51);
            stats.SetY2NDC(0.75);
            pad.Modified()
            pad.Update()
            stuffToKeep.append(stats)

        #legend=r.TLegend(0.1,0.9,0.6,0.6)
        #legend.SetFillStyle(0)
        #
        #legend.AddEntry(mhtLlHisto,"this event","p")
        #legend.Draw()
        #stuffToKeep.append(legend)
        #stuffToKeep.extend([pad,mhtLlHisto])
        stuffToKeep.append(pad)
        self.canvas.cd()
        pad.Draw()
        return stuffToKeep

    def drawRhoPhiPlot(self, eventVars, coords, corners) :
        pad = r.TPad("rhoPhiPad", "rhoPhiPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()

        skeletonColor = r.kYellow+1
        self.drawSkeleton(coords, skeletonColor)
        self.drawScale(color = skeletonColor, size = 0.03, scale = coords["scale"], point = {"x":0.0, "y":coords["radius"]+coords["y0"]+0.03})

        defArrowSize=0.5*self.arrow.GetDefaultArrowSize()
        defWidth=1
        #                                  color      , width   , arrow size
        if self.doGen :
            if self.doGenParticles :
                self.drawGenParticles(eventVars, coords,r.kBlack  , defWidth, defArrowSize,       label = "all GEN particles")
                self.drawGenParticles(eventVars, coords,r.kBlue   , defWidth, defArrowSize*4/6.0, statusList = [1], label = "status 1")
                self.drawGenParticles(eventVars, coords,r.kGreen  , defWidth, defArrowSize*2/6.0, statusList = [1], pdgIdList = [22], label = "status 1 photon")
                self.drawGenParticles(eventVars, coords,r.kMagenta, defWidth, defArrowSize*1/6.0, statusList = [1], pdgIdList = [22],
                                      motherList = [1,2,3,4,5,6,-1,-2,-3,-4,-5,-6], label = "status 1 photon w/quark as mother")
                self.drawGenParticles(eventVars, coords,r.kOrange, defWidth, defArrowSize*1/6.0, statusList = [1], pdgIdList = [22],
                                      motherList = [22], label = "status 1 photon w/photon as mother")
            else :
                self.drawGenJets    (eventVars, coords,r.kBlack   , defWidth, defArrowSize)
                self.drawGenMet     (eventVars, coords,r.kMagenta , defWidth, defArrowSize*2/6.0)
            
        if self.doReco : 
            #self.drawP4(eventVars["%sLongP4%s"%self.jets],r.kGray,defWidth,defArrowSize*1/100.0)
            #self.drawP4(-eventVars["%sLongP4%s"%self.jets],r.kGray,defWidth,defArrowSize*1/100.0)
            self.drawCleanJets      (eventVars, coords, self.jets, r.kBlue    , defWidth, defArrowSize)
                                     
            #self.drawCleanJets      (eventVars, coords,
            #                         (self.jets[0].replace("xc","")+"JPT","Pat"),896,defWidth, defArrowSize*3/4.0)
            #self.drawCleanJets      (eventVars, coords,
            #                         (self.jets[0].replace("xc","")+"PF","Pat"), 38,defWidth, defArrowSize*1/2.0)
        
            self.drawIgnoredJets    (eventVars, coords,r.kCyan    , defWidth, defArrowSize*1/6.0)
            #self.drawOtherJets      (eventVars, coords,r.kBlack  )
            self.drawHt             (eventVars, coords,r.kBlue+3  , defWidth, defArrowSize*1/6.0)
            self.drawNJetDeltaHt    (eventVars, coords,r.kBlue-9  , defWidth, defArrowSize*1/6.0)
            self.drawMht            (eventVars, coords,r.kRed     , defWidth, defArrowSize*3/6.0)
            self.drawMet            (eventVars, coords,r.kGreen   , defWidth, defArrowSize*2/6.0)
            
            if self.doLeptons :
                self.drawMuons      (eventVars, coords,r.kYellow  , defWidth, defArrowSize*2/6.0)
                self.drawElectrons  (eventVars, coords,r.kOrange+7, defWidth, defArrowSize*2.5/6.0)
                self.drawPhotons    (eventVars, coords,r.kOrange  , defWidth, defArrowSize*1.8/6.0)
                #self.drawTaus       (eventVars, coords,r.kYellow  , defWidth, defArrowSize*2/6.0)
            
            self.drawCleanedRecHits (eventVars, coords,r.kOrange-6, defWidth, defArrowSize*2/6.0)

        self.canvas.cd()
        pad.Draw()
        return [pad]

    def drawLegend(self, corners) :
        pad = r.TPad("legendPad", "legendPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        
        legend = r.TLegend(0.0, 0.0, 1.0, 1.0)
        for item in self.legendList :
            self.line.SetLineColor(item[0])
            someLine = self.line.DrawLine(0.0,0.0,0.0,0.0)
            legend.AddEntry(someLine, item[1], item[2])
        legend.Draw("same")
        self.canvas.cd()
        pad.Draw()
        return [pad,legend]

    def printEventText(self, eventVars, corners) :
        pad = r.TPad("textPad", "textPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()

        defaults = {}
        defaults["size"] = 0.04
        defaults["font"] = 80
        defaults["color"] = r.kBlack
        defaults["slope"] = 0.02

        x0 = 0.015
        x1 = 0.45
        self.printEvent(   eventVars, params = defaults, coords = {"x":x0, "y":0.98})
        self.printVertices(eventVars, params = defaults, coords = {"x":x1, "y":0.98}, nMax = 3)

        if self.printOtherJetAlgoQuantities :
            y0 = 0.44
            jetsOtherAlgo = (self.jets[0]+"PF" if "PF" not in self.jets[0] else self.jets[0].replace("PF",""), self.jets[1])
            metOtherAlgo  = "metP4AK5TypeII" if "PF" in self.met else "metP4PF"
            self.printJets(          eventVars, params = defaults, coords = {"x":x0, "y":0.64}, jets = jetsOtherAlgo, nMax = 5)            
        else :
            y0 = 0.64            
            jetsOtherAlgo = None
            metOtherAlgo  = None
        
        self.printJets(              eventVars, params = defaults, coords = {"x":x0, "y":   0.84}, jets = self.jets, nMax = 5)
        self.printKinematicVariables(eventVars, params = defaults, coords = {"x":x0, "y":y0     }, jets = self.jets, jets2 = jetsOtherAlgo)
        self.printCutBits(           eventVars, params = defaults, coords = {"x":x0, "y":y0-0.10}, jets = self.jets, jets2 = jetsOtherAlgo, met = self.met, met2 = metOtherAlgo)

        self.canvas.cd()
        pad.Draw()
        return [pad]

    def uponAcceptance(self, eventVars) :
        self.canvas.Clear()

        rhoPhiPadYSize = 0.50*self.canvas.GetAspectRatio()
        rhoPhiPadXSize = 0.50
        radius = 0.4
        g1 = self.drawRhoPhiPlot(eventVars,
                                 coords = {"scale":400.0, "radius":radius, "x0":radius, "y0":radius+0.05},
                                 corners = {"x1":0.0, "y1":0.0, "x2":rhoPhiPadXSize, "y2":rhoPhiPadYSize},
                                 )
        l = self.drawLegend(corners = {"x1":0.0, "y1":rhoPhiPadYSize, "x2":1.0-rhoPhiPadYSize, "y2":1.0})

        r.gStyle.SetOptStat(110011)        
        if self.doGenParticles or self.doEtaPhiPlot :
            gg = self.drawEtaPhiPlot(eventVars, corners = {"x1":rhoPhiPadXSize - 0.18,
                                                           "y1":rhoPhiPadYSize - 0.08*self.canvas.GetAspectRatio(),
                                                           "x2":rhoPhiPadXSize + 0.12,
                                                           "y2":rhoPhiPadYSize + 0.22*self.canvas.GetAspectRatio()})
        
        if self.doReco :
            g3 = self.drawAlphaPlot(eventVars, r.kBlack, showAlphaTMet = True,
                                    corners = {"x1":rhoPhiPadXSize - 0.08,
                                               "y1":0.0,
                                               "x2":rhoPhiPadXSize + 0.12,
                                               "y2":0.55})
            #g4 = self.drawMhtLlPlot(eventVars, r.kBlack, corners = {"x1":0.63, "y1":0.63, "x2":0.95, "y2":0.95})

        t = self.printEventText(eventVars,
                                corners = {"x1":rhoPhiPadXSize + 0.12,
                                           "y1":0.0,
                                           "x2":1.0,
                                           "y2":1.0})
        
        someDir=r.gDirectory
        self.outputFile.cd()
        self.canvas.Write("canvas_%d"%self.canvasIndex)
        self.canvasIndex+=1
        someDir.cd()
#####################################
class counter(analysisStep) :

    def __init__(self,label) :
        self.label = label
        self.moreName = '("%s")' % label

    def uponAcceptance(self,eventVars) :
        self.book(eventVars).fill(0.0,"countsHisto_"+self.label,1,-0.5,0.5,";dummy axis;number of events")
#####################################
class pickEventSpecMaker(analysisStep) :
    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/WorkBookPickEvents

    def setup(self,chain,fileDir,name,outputDir) :
        self.outputFileName = outputDir+"/"+name+"_pickEvents.txt"
        self.outputFile = open(self.outputFileName,"w")
        
    def uponAcceptance(self,eventVars) :
        line="%14d:%6d:%14d\n"%(eventVars["run"], eventVars["lumiSection"], eventVars["event"])
        self.outputFile.write(line) #slow: faster to buffer output, write less frequently

    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        print utils.hyphens
        self.outputFile.close()
        print "The pick events spec. file \""+self.outputFileName+"\" has been written."
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
    
    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        if self.splitMode : return
        if not self.quietMode : print utils.hyphens
        sillyDict={}
        sillyDict[1]=[self.runLsDict]
        utils.mergeRunLsDicts(sillyDict,self.outputFileName)
#####################################
class duplicateEventCheck(analysisStep) :

    def __init__(self) :
        self.events = collections.defaultdict(set)

    def uponAcceptance(self,ev) :
        runLs = self.events[(ev["run"],ev["lumiSection"])]
        event = ev["event"]
        assert event not in runLs, "You have a duplicate event: run %d, lumiSection %d, event %d"%(ev["run"],ev["lumiSection"],event)
        runLs.add(event)
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
        book = self.book(eV)

        index = eV["vertexIndices"]
        sump3 = eV["vertexSumP3"]
        sumpt = eV["vertexSumPt"]
        if not len(index) : return
        
        #coord = reduce(lambda v,u: (v[0]+u[0],v[1]+u[1],v[2]+u[2]), [(sump3[i].x(),sump3[i].y(),sump3[i].z()) for i in index][1:], (0,0,0))
        #sump3Secondaries = type(sump3[0])(coord[0],coord[1],coord[2])

        book.fill( sumpt[index[0]], "vertex0SumPt", 40, 0, 1200, title = ";primary vertex #Sigma p_{T} (GeV); events / bin")
        book.fill( sump3[index[0]].rho(), "vertex0MPT%d", 40, 0, 400, title = ";primary vertex MPT (GeV);events / bin")

        book.fill( sum(map(sumpt.__getitem__,index[1:])), "vertexGt0SumPt", 100, 0, 400, title = ";secondary vertices #Sigma p_{T};events / bin")
        #book.fill( (sumpt[index[0]], sum(map(sumpt.__getitem__,index[1:]))), "vertexSumPt_0_all", (100,100), (0,0), (1200,400), title = ";primary vertex #Sigma p_{T};secondary vertices #Sigma p_{T};events / bin")
        #book.fill( (sump3[index[0]].rho(), sump3Secondaries.rho()), "vertexMPT_0_all", (100,100), (0,0), (400,200), title = ";primary vertex MPT;secondary verticies MPT;events / bin")
