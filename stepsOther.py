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
            if eventVar[var] < cut: return True
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

        if xs==None : return
        effXs=0.0
        if nEvents>0 : effXs=(xs+0.0)*self.nPass/nEvents
        if not self.quietMode : print "The effective XS =",xs,"*",self.nPass,"/",nEvents,"=",effXs
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
    """monsterEventFilter"""
    
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
        l = []
        file = open(fileName)
        l = [ line.replace("\n","").split(":") for line in file]
        file.close()

        self.tuples = []
        for item in l :
            self.tuples.append( (int(item[0]),int(item[1]),int(item[2])) )

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
class goodRunsOnly2009(analysisStep) :

    def __init__(self,energyString,version) :
        self.moreName = "%s %s" % (energyString,version)
        self.runList=[]
        self.runLsList=[]

        #http://indico.cern.ch/getFile.py/access?contribId=4&resId=0&materialId=slides&confId=81465
        #assume "12732" means 123732
        self.runLsList_900GeV_v1=[123596,123615,123732,123815,
                                 123818,123906,123908,123909,
                                 124006,124008,124009,124017,
                                 124020,124022,124023,124024,
                                 124025,124027,124030
                                 ]

        self.bogusLsRequirements(self.runLsList_900GeV_v1)
        #http://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=76798
        self.runLsList_900GeV_v2=[123596,123615,123732,123815,
                                  123818,123906,123908,124008,
                                  124009,124020,124022,124023,
                                  124024,124025,124027,124030
                                  ]
        self.bogusLsRequirements(self.runLsList_900GeV_v2)

        #2 TeV
        self.runLsList_2TeV=[124120]
        self.bogusLsRequirements(self.runLsList_2TeV)

        #format is (run, first good ls, last good ls)
        self.runLsList_900GeV_v3=[
            (123596,  2, 9999),
            (123615, 70, 9999),
            (123732, 62,  109),
            (123815,  8, 9999),
            (123818,  2,   42),
            (123908,  2,   12),
            (124008,  1,    1),
            (124009,  1,   68),
            (124020, 12,   94),
            (124022, 66,  179),
            (124023, 38, 9999),
            (124024,  2,   83),
            (124025,  5,   13),
            (124027, 24, 9999),
            (124030,  2, 9999),
            ]
        
        if (energyString=="2 TeV") :
            self.runLsList=self.runLsList_2TeV
        elif (energyString=="900 GeV") :
            self.runLsList=getattr(self,"runLsList_900GeV_"+version)

        self.buildRunDict()
        
    def bogusLsRequirements(self,someList) :
        for i in range(len(someList)) :
            someList[i]=(someList[i],0,9999)

    def buildRunDict(self) :
        self.runDict={}
        for tuple in self.runLsList :
            self.runDict[tuple[0]]=[tuple[1],tuple[2]]
        
    def select (self,eventVars) :
        if eventVars["run"] not in self.runDict : return False
        ls = eventVars["lumiSection"]
        if ls < self.runDict[run][0] or \
           ls > self.runDict[run][1] : return False
        return True

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
class metGroupNoiseEventFilter(analysisStep) :

    def __init__(self,version) :
        self.version=version
        self.moreName=self.version
        self.setupStuff()

    def setupStuff(self) :
        self.setOfBadTuples = set([])

        inFile = open("/afs/cern.ch/user/e/elaird/public/susypvt/misc/cleaned_events/cleaned_events_"+self.version+".txt")
        for line in inFile :
            varList = line.split()
            run = int(varList[1])
            ls = int(varList[3])
            event = int(varList[5])
            self.setOfBadTuples.add( (run,ls,event) )
        inFile.close()
        
    def select (self,eventVars) :
        return  (eventVars["run"],eventVars["lumiSection"],eventVars["event"])   not in   self.setOfBadTuples
#####################################
class bxFilter(analysisStep) :
    """bxFilter"""

    def __init__(self,bxList) :
        self.bxList = bxList
        self.moreName = "[%s]" % ",".join(bxList)

    def select (self,eventVars) :
        return eventVars["bunch"] in self.bxList
#####################################
class displayer(analysisStep) :
    
    def __init__(self,jets = ("",""), met = "", muons = "", electrons = "", photons = "",
                 recHits = "", recHitPtThreshold = -1.0, scale = 200.0, etRatherThanPt = False, doGenParticles = False) :

        self.moreName = "(see below)"

        for item in ["scale","jets","met","muons","electrons","photons","recHits","recHitPtThreshold","doGenParticles"] :
            setattr(self,item,eval(item))

        self.genJets = self.jets
        self.genMet  = self.met.replace("P4","GenMetP4")
        self.deltaHtName = "%sDeltaPseudoJetEt%s"%self.jets if etRatherThanPt else "%sDeltaPseudoJetPt%s"%self.jets
        
        self.doGen=False
        self.doReco = not self.doGenParticles
        self.doLeptons=True
        self.helper=r.displayHelper()

    def switchGenOn(self) :
        self.doGen=True

    def setup(self,chain,fileDir,name,outputDir) :
        someDir=r.gDirectory
        self.outputFileName=outputDir+"/"+name+"_displays.root"
        os.system("mkdir -p "+outputDir)
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        someDir.cd()
        
        self.canvas=r.TCanvas("canvas","canvas",500,500)
        self.canvasIndex=0

        self.ellipse=r.TEllipse()
        self.ellipse.SetFillStyle(0)
        self.line=r.TLine()
        self.arrow=r.TArrow()
        self.radius=0.3
        self.x0=self.radius
        self.y0=self.radius+0.05
        self.text=r.TText()
        self.latex=r.TLatex()
        self.legend=r.TLegend(0.01+2.0*self.radius,self.radius,0.95,0.05)

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

    def drawEventInfo(self,eventVars,color) :
        self.text.SetTextSize(0.02)
        self.text.SetTextFont(80)
        self.text.SetTextColor(color)
        x=0.1
        self.text.DrawText(x,0.80,"Run   %#10d"%eventVars["run"])
        self.text.DrawText(x,0.78,"Ls    %#10d"%eventVars["lumiSection"])
        self.text.DrawText(x,0.76,"Event %#10d"%eventVars["event"])
        #self.text.DrawText(x,0.74,"Bx    %#10d"%eventVars["bunch"])
        
    def drawSkeleton(self,color) :
        #self.canvas.cd(2)
        r.gPad.AbsCoordinates(False)
        
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(1)
        self.ellipse.DrawEllipse(self.x0,self.y0,self.radius,self.radius,0.0,360.0,0.0,"")

        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-self.radius,self.y0            ,self.x0+self.radius,self.y0            )
        self.line.DrawLine(self.x0            ,self.y0-self.radius,self.x0            ,self.y0+self.radius)

        self.latex.SetTextSize(0.04)
        self.latex.SetTextColor(color)
        self.latex.DrawLatex(0.6,0.01,"radius = "+str(self.scale)+" GeV p_{T}")

        return []

    def drawP4(self,p4,color,lineWidth,arrowSize) :
        x1=self.x0+p4.px()*self.radius/self.scale
        y1=self.y0+p4.py()*self.radius/self.scale

        #self.line.SetLineColor(color)
        #self.line.SetLineWidth(lineWidth)
        #self.line.DrawLine(self.x0,self.y0,x1,y1)

        self.arrow.SetLineColor(color)
        self.arrow.SetLineWidth(lineWidth)
        self.arrow.SetArrowSize(arrowSize)
        self.arrow.SetFillColor(color)
        self.arrow.DrawArrow(self.x0,self.y0,x1,y1)
        
    def drawGenJets (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"genJetEntryInLegend") :
            self.genJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"GEN jets (%s%s)"%self.genJets,"l")

        genJets = "%sGenJetP4%s"%self.genJets
        if genJets[:2] == "xc": genJets = genJets[2:]
        p4Vector = eventVars[genJets]
        for jet in p4Vector :
            self.drawP4(jet,color,lineWidth,arrowSize)
            
    def drawGenParticles (self, eventVars, color, lineWidth, arrowSize, statusList = None, pdgIdList = None, motherList = None ,label = "") :
        self.line.SetLineColor(color)
        if not hasattr(self,"genParticleEntryInLegend"+label) :
            setattr(self,"genParticleEntryInLegend"+label,True)
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,label,"l")

        for iParticle,particle in enumerate(eventVars["genP4"]) :
            if statusList!=None and eventVars["genStatus"].at(iParticle) not in statusList : continue
            if pdgIdList!=None and eventVars["genPdgId"].at(iParticle) not in pdgIdList : continue
            if motherList!=None and eventVars["genMotherPdgId"][iParticle] not in motherList : continue
            self.drawP4(particle,color,lineWidth,arrowSize)
            
    def drawCleanJets (self,eventVars,jets,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        legString = "%scleanJetEntryInLegend%s"%jets
        if not hasattr(self,legString) :
            setattr(self,legString,True)
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"clean jets (%s%s)"%jets,"l")

        p4Vector=eventVars['%sCorrectedP4%s'%self.jets]
        cleanJetIndices = eventVars["%sIndices%s"%self.jets]
        for iJet in cleanJetIndices :
            self.drawP4(p4Vector.at(iJet),color,lineWidth,arrowSize)
            
    def drawOtherJets (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"otherJetEntryInLegend") :
            self.otherJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"\"other\" jets","l")

        p4Vector=eventVars["%sCorrectedP4%s"%self.jets]
        otherJetIndices = eventVars["%sIndicesOther%s"%self.jets]
        for index in otherJetIndices :
            self.drawP4(p4Vector.at(index),color,lineWidth,arrowSize)
            
    def drawIgnoredJets (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"ignoredJetEntryInLegend")) :
            self.ignoredJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"ignored jets (%s%s)"%self.jets,"l")

        p4Vector=eventVars["%sCorrectedP4%s"%self.jets]
        cleanJetIndices = eventVars["%sIndices%s"%self.jets]
        otherJetIndices = eventVars["%sIndicesOther%s"%self.jets]
        for iJet in range(len(p4Vector)) :
            if (iJet in cleanJetIndices) : continue
            if (iJet in otherJetIndices) : continue
            self.drawP4(p4Vector.at(iJet),color,lineWidth,arrowSize)
            
    def drawMht (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"mhtEntryInLegend") :
            self.mhtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"MHT (%s%s)"%self.jets,"l")

        mh = -eventVars["%sSumP4%s"%self.jets]
        self.drawP4(mh,color,lineWidth,arrowSize)
            
    def drawHt (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"htEntryInLegend") :
            self.htEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"H_{T} (%s%s)"%self.jets,"l")

        ht = eventVars["%sSumPt%s"%self.jets]
            
        y=self.y0-self.radius-0.05
        l=ht*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)
        
    def drawNJetDeltaHt (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"deltaHtEntryInLegend") :
            self.deltaHtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#DeltaH_{T} (%s%s)"%self.jets,"l")

        y=self.y0-self.radius-0.03
        l=eventVars[self.deltaHtName]*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)

    def drawMet (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"metEntryInLegend")) :
            self.metEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"MET (%s)"%self.met,"l")

        self.drawP4(eventVars[self.met],color,lineWidth,arrowSize)
            
    def drawGenMet (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"genMetEntryInLegend") :
            self.genMetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"GEN MET (%s)"%self.genMet,"l")

        self.drawP4(eventVars[self.genMet],color,lineWidth,arrowSize)
            
    def drawMuons (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"muonEntryInLegend") :
            self.muonEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"muons (%s%s)"%self.muons,"l")
        p4Vector=eventVars["%sP4%s"%self.muons]
        for i in range(len(p4Vector)) :
            self.drawP4(p4Vector.at(i),color,lineWidth,arrowSize)
            
    def drawElectrons (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"electronEntryInLegend") :
            self.electronEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"electrons (%s%s)"%self.electrons,"l")
        p4Vector=eventVars["%sP4%s"%self.electrons]
        for i in range(len(p4Vector)) :
            self.drawP4(p4Vector.at(i),color,lineWidth,arrowSize)
            
    def drawPhotons (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"photonEntryInLegend") :
            self.photonEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"photons (%s%s)"%self.photons,"l")
        p4Vector=eventVars["%sP4%s"%self.photons]
        for i in range(len(p4Vector)) :
            self.drawP4(p4Vector.at(i),color,lineWidth,arrowSize)
            
    def drawTaus (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"tauEntryInLegend") :
            self.tauEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"taus ("+self.tauSuffix+")","l")
        p4Vector=eventVars[self.tauCollection+'P4'+self.tauSuffix]
        for i in range(len(p4Vector)) :
            self.drawP4(p4Vector.at(i),color,lineWidth,arrowSize)
            
    def drawCleanedRecHits (self,eventVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if not hasattr(self,"cleanedRecHitEntryInLegend") :
            self.cleanedRecHitEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"cleaned RecHits (%s)"%self.recHits,"l")

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
                    self.drawP4(hit,color,lineWidth,arrowSize)
            
    def makeAlphaTFunc(self,alphaTValue,color) :
        alphaTFunc=r.TF1(("alphaTCurve ( %#5.3g"%alphaTValue)+" )",
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(color)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc

    def drawAlphaPlot (self, eventVars, color, useMet = False) :
        mhtVar = "%sSumP4%s"%self.jets if not useMet else self.met
        mhtLabel = "MHT"               if not useMet else "MET"
        alphaTVar = "AlphaT"           if not useMet else "AlphaTMet"
        padYOffset = 0.0               if not useMet else 0.3

        stuffToKeep=[]
        pad=r.TPad(alphaTVar+"pad",alphaTVar+"pad",
                   0.01 + 2.0*self.radius, padYOffset + 0.01 + self.radius,
                   0.95,                   padYOffset + 0.63)
        pad.cd()
        pad.SetRightMargin(0.01)
        title=";%s/H_{T};#DeltaH_{T}/H_{T}"%mhtLabel
        alphaHisto=r.TH2D(alphaTVar+"Histo",title,100,0.0,1.0,100,0.0,0.7)

        mht=eventVars[mhtVar].pt()
        ht = eventVars["%sSumPt%s"%self.jets]
        deltaHt=eventVars[self.deltaHtName]
        alphaT =eventVars[ "%s%s%s"%(self.jets[0],alphaTVar,self.jets[1]) ]
        
        alphaHisto.Fill(mht/ht,deltaHt/ht)
        alphaHisto.SetStats(False)
        alphaHisto.SetMarkerStyle(29)
        alphaHisto.GetYaxis().SetTitleOffset(1.25)
        alphaHisto.SetMarkerColor(r.kBlue)
        alphaHisto.Draw("p")

        legend=r.TLegend(0.1,0.9,0.6,0.6)
        legend.SetFillStyle(0)
        
        for func in self.alphaFuncs :
            func.Draw("same")
            legend.AddEntry(func,func.GetName(),"l")

        legend.AddEntry(alphaHisto,"this event ( %#5.3g )"%alphaT,"p")
        legend.Draw()
        stuffToKeep.extend([pad,alphaHisto,legend])
        self.canvas.cd()
        pad.Draw()
        return stuffToKeep

    def fillHisto(self,histo,lls,mhts) :
        for i in range(len(mhts)) :
            histo.Fill(lls[i],mhts[i])
        
    def drawMhtLlPlot (self,eventVars,color) :
        stuffToKeep=[]
        pad=r.TPad("pad","pad",self.x0+0.37*self.radius,0.63,0.95,0.95)
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
        
    def uponAcceptance (self,eventVars) :
        self.canvas.Clear()

        g1=self.drawSkeleton(r.kYellow+1)
        self.drawEventInfo(eventVars,r.kBlack)

        defArrowSize=0.5*self.arrow.GetDefaultArrowSize()
        defWidth=1
        #                                  color      , width   , arrow size
        if self.doGen :
            if self.doGenParticles :
                self.drawGenParticles(eventVars,r.kBlack  , defWidth, defArrowSize,       label = "all GEN particles")
                self.drawGenParticles(eventVars,r.kBlue   , defWidth, defArrowSize*4/6.0, statusList = [1], label = "status 1")
                self.drawGenParticles(eventVars,r.kGreen  , defWidth, defArrowSize*2/6.0, statusList = [1], pdgIdList = [22], label = "status 1 photon")
                self.drawGenParticles(eventVars,r.kMagenta, defWidth, defArrowSize*1/6.0, statusList = [1], pdgIdList = [22],
                                      motherList = [1,2,3,4,5,6,-1,-2,-3,-4,-5,-6], label = "status 1 photon w/quark as mother")
                
            else :
                self.drawGenJets    (eventVars,r.kBlack   , defWidth, defArrowSize)
                self.drawGenMet     (eventVars,r.kMagenta , defWidth, defArrowSize*2/6.0)
            
        if self.doReco : 
            self.drawCleanJets      (eventVars,
                                     self.jets,r.kBlue    , defWidth, defArrowSize)
            #self.drawCleanJets      (eventVars,
            #                         (self.jets[0]+"JPT","Pat"),896,defWidth, defArrowSize*3/4.0)
            #self.drawCleanJets      (eventVars,
            #                         (self.jets[0]+"PF","Pat"), 38,defWidth, defArrowSize*1/2.0)
            self.drawIgnoredJets    (eventVars,r.kCyan    , defWidth, defArrowSize*1/6.0)
            #self.drawOtherJets      (eventVars,r.kBlack  )
            self.drawHt             (eventVars,r.kBlue+3  , defWidth, defArrowSize*1/6.0)
            self.drawNJetDeltaHt    (eventVars,r.kBlue-9  , defWidth, defArrowSize*1/6.0)
            self.drawMht            (eventVars,r.kRed     , defWidth, defArrowSize*3/6.0)
            self.drawMet            (eventVars,r.kGreen   , defWidth, defArrowSize*2/6.0)

            if self.doLeptons :
                self.drawMuons      (eventVars,r.kYellow  , defWidth, defArrowSize*2/6.0)
                self.drawElectrons  (eventVars,r.kOrange+7, defWidth, defArrowSize*2.5/6.0)
                self.drawPhotons    (eventVars,r.kOrange  , defWidth, defArrowSize*1.8/6.0)
                #self.drawTaus       (eventVars,r.kYellow  , defWidth, defArrowSize*2/6.0)

            self.drawCleanedRecHits (eventVars,r.kOrange-6, defWidth, defArrowSize*2/6.0)

        self.legend.Draw("same")
        r.gStyle.SetOptStat(110011)

        if self.doReco :
            g2=self.drawAlphaPlot(eventVars,r.kBlack)
            g3=self.drawAlphaPlot(eventVars,r.kBlack, useMet = True)
            #g4=self.drawMhtLlPlot(eventVars,r.kBlack)

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

    #https://twiki.cern.ch/twiki/bin/view/CMS/PickEvents
    def __init__(self,dataSetName) :
        self.dataSetName = dataSetName

    def setup(self,chain,fileDir,name,outputDir) :
        self.outputFileName = outputDir+"/"+name+"_pickEvents.txt"
        self.outputFile = open(self.outputFileName,"w")
        
    def uponAcceptance(self,eventVars) :
        line=""
        line+="%14d"%eventVars["run"]
        line+="%14d"%eventVars["event"]
        line+="%14d"%eventVars["lumiSection"]
        line+="   "+self.dataSetName+"\n"
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
