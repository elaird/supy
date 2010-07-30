import copy,array,os
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class skimmer(analysisStep) :
    #special __doc__ assignment below
    
    def __init__(self,outputDir,alsoWriteExtraTree=False) :
        self.__doc__=self.skimmerStepName
        self.outputDir=outputDir
        self.outputTree=0
        self.moreName="(see below)"
        self.alsoWriteExtraTree=alsoWriteExtraTree
        self.outputTreeExtraIsSetup=False

    def setup(self,chain,fileDir,name) :
        self.fileDir=fileDir
        self.outputFileName=self.outputDir+"/"+name+"_skim.root"
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        self.outputTree=chain.CloneTree(0)        #clone structure of tree (but no entries)
        self.outputTree.SetDirectory(r.gDirectory)#put output tree in correct place
        chain.CopyAddresses(self.outputTree)      #associate branch addresses

        if self.alsoWriteExtraTree :
            self.arrayDictionary={}
            self.supportedBuiltInTypes=[type(True),type(0),type(0L),type(0.0)]
            self.supportedOtherTypes=[type(r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0))]
            
            extraName=self.outputTree.GetName()+"Extra"
            self.outputTreeExtra=r.TTree(extraName,extraName)
            self.outputTreeExtra.SetDirectory(r.gDirectory)

        r.gROOT.cd()

    def select(self,eventVars,extraVars) :
        #read all the data for this event
        if eventVars._wrappedChain__chain.GetEntry(extraVars.entry,1)<=0 :
            return False #skip this event in case of i/o error
        #fill the skim tree
        self.outputTree.Fill()
        
        #optionally fill an extra tree
        if self.alsoWriteExtraTree :
            if not self.outputTreeExtraIsSetup : self.setupExtraTree(extraVars)
            self.fillExtraVariables(extraVars)
            self.outputTreeExtra.Fill()
            
        return True

    def setupExtraTree(self,extraVars) :
        extraVarsCopy=copy.deepcopy(extraVars)
        branchNameList=dir(extraVarsCopy)
        skipList=['__doc__','__init__','__module__']

        #set up remaining suitable branches as doubles
        for branchName in branchNameList :
            if (branchName in skipList) : continue

            thisType=type(getattr(extraVars,branchName))
            if (thisType in self.supportedBuiltInTypes) :
                self.arrayDictionary[branchName]=array.array('d',[0.0])
                self.outputTreeExtra.Branch(branchName,self.arrayDictionary[branchName],branchName+"/D")
            elif (thisType in self.supportedOtherTypes) :
                self.outputTreeExtra.Branch(branchName,getattr(extraVars,branchName))                
            else :
                #print "The variable \""+branchName+"\" has been rejected from the extra tree."
                continue
            
        self.outputTreeExtraIsSetup=True

    def fillExtraVariables(self,extraVars) :
        for key in self.arrayDictionary :
            self.arrayDictionary[key][0]=getattr(extraVars,key)
        
    def endFunc(self,chain,hyphens,nEvents,xs) :
        print hyphens
        self.outputFile.cd(self.fileDir)
        self.outputTree.Write()
        if (self.alsoWriteExtraTree) :
            self.outputTreeExtra.Write()
        self.outputFile.Close()
        print "The skim file \""+self.outputFileName+"\" has been written."
        effXs=0.0
        if nEvents>0 : effXs=(xs+0.0)*self.nPass/nEvents
        print "The effective XS =",xs,"*",self.nPass,"/",nEvents,"=",effXs
#####################################
class skimmer2(analysisStep) :
    """skimmer2"""
    
    def __init__(self,outputDir,alsoWriteExtraTree=False) :
        self.outputDir=outputDir
        self.moreName="(see below)"
        self.alsoWriteExtraTree=alsoWriteExtraTree
        self.outputTreeExtraIsSetup=False

    def setup(self,chain,fileDir,name) :
        self.eventList=r.TEventList("eventList")
        self.eventList.SetDirectory(chain.GetDirectory())
        
        self.fileDir=fileDir
        self.outputFileName=self.outputDir+"/"+name+"_skim.root"
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)

        if self.alsoWriteExtraTree :
            self.arrayDictionary={}
            self.supportedBuiltInTypes=[type(True),type(0),type(0L),type(0.0)]
            self.supportedOtherTypes=[type(r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0))]
            
            extraName=chain.GetName()+"Extra"
            self.outputTreeExtra=r.TTree(extraName,extraName)
            self.outputTreeExtra.SetDirectory(r.gDirectory)

        r.gROOT.cd()

    def uponAcceptance(self,eventVars,extraVars) :
        self.eventList.Enter(extraVars.entry)

        #optionally fill an extra tree
        if self.alsoWriteExtraTree :
            if not self.outputTreeExtraIsSetup : self.setupExtraTree(extraVars)
            self.fillExtraVariables(extraVars)
            self.outputTreeExtra.Fill()

    def setupExtraTree(self,extraVars) :
        extraVarsCopy=copy.deepcopy(extraVars)
        branchNameList=dir(extraVarsCopy)
        skipList=['__doc__','__init__','__module__']

        #set up remaining suitable branches as doubles
        for branchName in branchNameList :
            if (branchName in skipList) : continue

            thisType=type(getattr(extraVars,branchName))
            if (thisType in self.supportedBuiltInTypes) :
                self.arrayDictionary[branchName]=array.array('d',[0.0])
                self.outputTreeExtra.Branch(branchName,self.arrayDictionary[branchName],branchName+"/D")
            elif (thisType in self.supportedOtherTypes) :
                self.outputTreeExtra.Branch(branchName,getattr(extraVars,branchName))                
            else :
                #print "The variable \""+branchName+"\" has been rejected from the extra tree."
                continue
            
        self.outputTreeExtraIsSetup=True

    def fillExtraVariables(self,extraVars) :
        for key in self.arrayDictionary :
            self.arrayDictionary[key][0]=getattr(extraVars,key)
        
    def endFunc(self,chain,hyphens,nEvents,xs) :
        print hyphens
        self.eventList.Print("all")
        chain.SetEventList(self.eventList)
        self.outputFile.cd(self.fileDir)

        print "writing skim file..."
        tree=chain.CopyTree("")
        tree.Write()
        if self.alsoWriteExtraTree :
            self.outputTreeExtra.Write()

        self.outputFile.Close()
        print "The skim file \""+self.outputFileName+"\" has been written."
        effXs=0.0
        if nEvents>0 : effXs=(xs+0.0)*self.nPass/nEvents
        print "The effective XS =",xs,"*",self.nPass,"/",nEvents,"=",effXs
#####################################
class skimmer3(analysisStep) :
    """skimmer3"""
    
    def __init__(self,outputDir) :
        self.outputDir=outputDir
        self.moreName="(see below)"

    def setup(self,chain,fileDir,name) :
        self.eventLists=[ r.TEventList("eventList%d"%iTree) for iTree in range(chain.GetNtrees()) ]
        
        self.fileDir=fileDir
        self.outName=name

    def uponAcceptance(self,eventVars,extraVars) :
        self.eventLists[eventVars._wrappedChain__chain.GetTreeNumber()].Enter(extraVars.localEntry)

    def endFunc(self,inChain,hyphens,nEvents,xs) :
        #for eventList in self.eventLists :
        #    eventList.Print("all")
        chain=inChain.Clone("newChain")
        iTreeFirstEntry = 0
        for iTree in range(chain.GetNtrees()) :
            chain.LoadTree(iTreeFirstEntry)
            if iTree!=chain.GetTreeNumber() : continue

            inTree=chain.GetTree()
            nEntries=inTree.GetEntries()
            iTreeFirstEntry+=nEntries

            #make and output file for this tree
            outputFileName=self.outputDir+"/"+self.outName+"_skim_"+str(iTree)+".root"
            print hyphens
            print "writing skim file",outputFileName
            self.outputFile=r.TFile(outputFileName,"RECREATE")
            self.outputFile.mkdir(self.fileDir).cd()

            #make a skimmed tree
            inTree.SetEventList(self.eventLists[iTree])
            tree=inTree.CopyTree("")
            #r.gDirectory.pwd()
            tree.SetDirectory(r.gDirectory)
            tree.Write()
            self.outputFile.Close()

            effXs=0.0
            if nEvents>0 : effXs=(xs+0.0)*self.nPass/nEvents
            print "The effective XS =",xs,"*",self.nPass,"/",nEvents,"=",effXs
        del chain
#####################################
class hbheNoiseFilter(analysisStep) :
    """hbheNoiseFilter"""

    def select (self,eventVars,extraVars) :
        return eventVars["hbheNoiseFilterResult"]
#####################################
class extraVariableGreaterFilter(analysisStep) :
    """extraVariableGreaterFilter"""

    def __init__(self,threshold,variable):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "(%s>=%.1f)" % (variable,threshold)

    def select (self,eventVars,extraVars) :
        return (getattr(extraVars,self.variable)>=self.threshold)
#####################################
class extraVariablePtGreaterFilter(analysisStep) :
    """extraVariablePtGreaterFilter"""

    def __init__(self,threshold,variable):
        self.threshold = threshold
        self.variable = variable
        self.moreName = "(%s>=%.1f)" % (variable,threshold)

    def select (self,eventVars,extraVars) :
        return (getattr(extraVars,self.variable).pt()>=self.threshold)
#####################################
class objectPtVetoer(analysisStep) :
    """objectPtVetoer"""

    def __init__(self, collection, p4String, suffix, ptThreshold, index):
        self.index = index
        self.ptThreshold = ptThreshold
        self.varName = collection + p4String + suffix
        self.moreName = "(%s; %s; corr. pT[%d]< %.1f GeV)" % (collection, suffix, index, ptThreshold )

    def select (self,eventVars,extraVars) :
        p4s = eventVars[self.varName]
        if p4s.size() <= self.index : return True
        return p4s.at(self.index).pt() < self.ptThreshold

#    def bookHistos(self) :
#        nBins=100
#        etaMin=-5.0
#        etaMax=5.0
#        title=";#eta;events / bin"
#        self.etaRejected=r.TH1D(self.objectCollection+"Eta"+self.objectSuffix,title,nBins,etaMin,etaMax)

#    def uponRejection(self,eventVars,extraVars) :
#        p4Vector=eventVars[self.objectCollection+self.objectP4String+self.objectSuffix]
#        self.etaRejected.Fill(p4Vector[self.objectIndex].eta())
#####################################
class soloObjectPtSelector(analysisStep) :
    """soloObjectPtSelector"""

    def __init__(self, collection, p4String, suffix, ptThreshold):
        self.ptThreshold = ptThreshold
        self.varName = collection + p4String + suffix        
        self.moreName = "(%s; %s; corr. pT> %.1f GeV)" % (collection, suffix, ptThreshold )

    def select (self,eventVars,extraVars) :
        return self.ptThreshold <= eventVars[self.varName].pt()
#####################################
class vertexRequirementFilterOld(analysisStep) :
    """vertexRequirementFilterOld"""
    
    def __init__(self, minVertexNtracks, maxVertexChi2Ndf, maxVertexZ) :
        self.minVertexNtracks = minVertexNtracks
        self.maxVertexChi2Ndf = maxVertexChi2Ndf
        self.maxVertexZ = maxVertexZ

        self.moreName = "(>=%d ve.tr.; chi2/ndf<%.1f; abs(z)<%.1f)" % (minVertexNtracks, maxVertexChi2Ndf, maxVertexZ )

    def select(self,eventVars,extraVars) :
        pos = eventVars["vertexPosition"]
        for i in range(pos.size()) :
            if eventVars["vertexNtrks"].at(i) >= self.minVertexNtracks and \
               eventVars["vertexNdof"].at(i) > 0.0 and \
               eventVars["vertexChi2"].at(i) / eventVars["vertexNdof"].at(i) < self.maxVertexChi2Ndf and \
               abs(pos.at(i).Z()) < self.maxVertexZ :
                return True
        return False
#####################################
class vertexRequirementFilter(analysisStep) :
    """vertexRequirementFilter"""
    
    def __init__(self,minVertexNdof,maxVertexZ) :
        self.minVertexNdof = minVertexNdof
        self.maxVertexZ = maxVertexZ
        self.moreName = "(any v: !fake; ndf>=%.1f;abs(z)<%.1f)" % (minVertexNdof,maxVertexZ)

    def select(self,eventVars,extraVars) :
        fake,ndof,pos = eventVars["vertexIsFake"], eventVars["vertexNdof"], eventVars["vertexPosition"]
        
        for i in range(pos.size()) :
            if fake.at(i) : continue
            if ndof.at(i) < self.minVertexNdof : continue
            if abs(pos.at(i).Z()) >= self.maxVertexZ : continue
            return True
        return False
#####################################
class monsterEventFilter(analysisStep) :
    """monsterEventFilter"""
    
    def __init__(self,maxNumTracks,minGoodTrackFraction) :
        self.maxNumTracks=maxNumTracks
        self.minGoodTrackFraction=minGoodTrackFraction

        self.moreName = "(<=%d tracks or >%.1f good fraction)" % (maxNumTracks, minGoodTrackFraction)

    def select (self,eventVars,extraVars) :
        nTracks    = eventVars["tracksNEtaLT0p9AllTracks"] + eventVars["tracksNEta0p9to1p5AllTracks"] + eventVars["tracksNEtaGT1p5AllTracks"]
        nGoodTracks = eventVars["tracksNEtaLT0p9HighPurityTracks"] + eventVars["tracksNEta0p9to1p5HighPurityTracks"] + eventVars["tracksNEtaGT1p5HighPurityTracks"]
        return (nTracks <= self.maxNumTracks or nGoodTracks > self.minGoodTrackFraction*nTracks)
#####################################
class runNumberFilter(analysisStep) :
    """runNumberFilter"""

    def __init__(self,runList,acceptRatherThanReject) :
        self.runList = runList
        self.accept = acceptRatherThanReject

        self.moreName = "run%s in list %s" % ( ("" if self.accept else " not"),str(runList) )
        
    def select (self,eventVars,extraVars) :
        return not ((eventVars["run"] in self.runList) ^ self.accept)

#####################################
class goodRunsOnly2009(analysisStep) :
    """goodRunsOnly2009"""

    def __init__(self,energyString,version) :
        self.moreName = "(%s %s)" % (energyString,version)
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
        
    def select (self,eventVars,extraVars) :
        if eventVars["run"] not in self.runDict : return False
        ls = eventVars["lumiSection"]
        if ls < self.runDict[run][0] or \
           ls > self.runDict[run][1] : return False
        return True

#####################################
class runHistogrammer(analysisStep) :
    """runHistogrammer"""

    def __init__(self) :
        self.runDict={}
        
    def select (self,eventVars,extraVars) :
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
    """metGroupNoiseEventFilter"""

    def __init__(self,version) :
        self.version=version
        self.moreName="("+self.version+")"
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
        
    def select (self,e,extraVars) :
        return  (e["run"],e["lumiSection"],e["event"])   not in   self.setOfBadTuples
#####################################
class bxFilter(analysisStep) :
    """bxFilter"""

    def __init__(self,bxList) :
        self.bxList = bxList
        self.moreName = "[%s]" % ",".join(bxList)

    def select (self,eventVars,extraVars) :
        return eventVars["bunch"] in self.bxList
#####################################
class displayer(analysisStep) :
    #special __doc__ assignment below
    
    def __init__(self,jetCollection="",jetSuffix="",metCollection="",metSuffix="",leptonSuffix="",genJetCollection="",outputDir="",scale=200.0,fakerMode=False) :
        self.__doc__=self.displayerStepName
        self.outputDir=outputDir
        self.moreName="(see below)"
        self.scale=scale #GeV
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.metCollection=metCollection
        self.metSuffix=metSuffix
        self.leptonSuffix=leptonSuffix
        self.genJetCollection=genJetCollection
        
        self.fakerMode=fakerMode

        self.doGen=False
        self.doLeptons=True

        if (self.doLeptons) :
            listOfTuples=[("muon",self.leptonSuffix),("electron",self.leptonSuffix),("photon","Pat"),("tau","Pat")]
            for tuple in listOfTuples :
                particle=tuple[0]
                suffix=tuple[1]
                setattr(self,particle+"Collection",particle)
                setattr(self,particle+"Suffix",suffix)

        self.helper=r.displayHelper()

    def switchGenOn(self) :
        self.doGen=True

    def bookHistos(self) :
        epsilon=1.0e-6
        self.mhtLlHisto=r.TH2D("mhtLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashH_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        self.metLlHisto=r.TH2D("metLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashE_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        
    def setup(self,chain,fileDir,name) :
        someDir=r.gDirectory
        self.outputFileName=self.outputDir+"/"+name+"_displays.root"
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

    def endFunc(self,chain,hyphens,nEvents,xs) :
        self.outputFile.Write()
        self.outputFile.Close()
        #if not self.quietMode : print "The display file \""+self.outputFileName+"\" has been written."
        if not self.splitMode :
            if not self.quietMode : print hyphens
            psFileName=self.outputFileName.replace(".root",".ps")
            utils.psFromRoot([self.outputFileName],psFileName,self.quietMode)
        del self.canvas

    def drawEventInfo(self,eventVars,extraVars,color) :
        self.text.SetTextSize(0.02)
        self.text.SetTextFont(80)
        self.text.SetTextColor(color)
        x=0.1
        self.text.DrawText(x,0.80,"Run   %#10d"%eventVars["run"])
        if (not self.fakerMode) : self.text.DrawText(x,0.78,"Ls    %#10d"%eventVars["lumiSection"])
        self.text.DrawText(x,0.76,"Event %#10d"%eventVars["event"])
        if (not self.fakerMode) : self.text.DrawText(x,0.74,"Bx    %#10d"%eventVars["bunch"])
        
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
        
    def drawGenJets (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"genJetEntryInLegend")) :
            self.genJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"GEN jets ("+self.genJetCollection+")","l")

        p4Vector=eventVars[self.genJetCollection+'GenJetP4'+self.jetSuffix]
        for jet in p4Vector :
            self.drawP4(jet,color,lineWidth,arrowSize)
            
    def drawCleanJets (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"cleanJetEntryInLegend")) :
            self.cleanJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"clean jets ("+self.jetCollection+")","l")

        if (not self.fakerMode) :
            p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
            cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
            for iJet in cleanJetIndices :
                self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
        else :
            for jet in extraVars.icfCleanJets :
                self.drawP4(jet,color,lineWidth,arrowSize)
            
    def drawOtherJets (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"otherJetEntryInLegend")) :
            self.otherJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"\"other\" jets","l")

        if (self.fakerMode) : return

        p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)
        for index in otherJetIndices :
            self.drawP4(p4Vector[index],color,lineWidth,arrowSize)
            
    def drawLowPtJets (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"lowPtJetEntryInLegend")) :
            self.lowPtJetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"low p_{T} jets ("+self.jetCollection+")","l")

        if (self.fakerMode) : return

        p4Vector=eventVars[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)
        otherJetIndices=getattr(extraVars,self.jetCollection+"otherJetIndices"+self.jetSuffix)
        for iJet in range(len(p4Vector)) :
            if (iJet in cleanJetIndices) : continue
            if (iJet in otherJetIndices) : continue
            self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
            
    def drawMht (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"mhtEntryInLegend")) :
            self.mhtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#slashH_{T} ("+self.jetCollection+")","l")

        mht=getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix)
        self.drawP4(mht,color,lineWidth,arrowSize)
            
    def drawHt (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"htEntryInLegend")) :
            self.htEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"H_{T} ("+self.jetCollection+")","l")

        ht=getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
            
        y=self.y0-self.radius-0.05
        l=ht*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)
        
    def drawNJetDeltaHt (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"deltaHtEntryInLegend")) :
            self.deltaHtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#DeltaH_{T} ("+self.jetCollection+")","l")

        deltaHt=getattr(extraVars,self.jetCollection+"nJetDeltaHt"+self.jetSuffix)
        y=self.y0-self.radius-0.03
        l=deltaHt*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)


    def drawMet (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"metEntryInLegend")) :
            self.metEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#slashE_{T} ("+self.metSuffix+")","l")

        met=eventVars[self.metCollection+"P4"+self.metSuffix]
        self.drawP4(met,color,lineWidth,arrowSize)
            
    def drawGenMet (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"genMetEntryInLegend")) :
            self.genMetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"GEN #slashE_{T} ("+self.metSuffix+")","l")

        genMet=eventVars[self.metCollection+"GenMetP4"+self.metSuffix]
        self.drawP4(genMet,color,lineWidth,arrowSize)
            
    def drawMuons (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"muonEntryInLegend")) :
            self.muonEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"muons ("+self.muonSuffix+")","l")
        if (self.fakerMode) : return
        p4Vector=eventVars[self.muonCollection+'P4'+self.muonSuffix]
        for iJet in range(len(p4Vector)) :
            self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
            
    def drawElectrons (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"electronEntryInLegend")) :
            self.electronEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"electrons ("+self.electronSuffix+")","l")
        if (self.fakerMode) : return
        p4Vector=eventVars[self.electronCollection+'P4'+self.electronSuffix]
        for iJet in range(len(p4Vector)) :
            self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
            
    def drawPhotons (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        #temporary hack
        if self.leptonSuffix=="PF" : return

        self.line.SetLineColor(color)
        if (not hasattr(self,"photonEntryInLegend")) :
            self.photonEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"photons ("+self.photonSuffix+")","l")
        if (self.fakerMode) : return
        p4Vector=eventVars[self.photonCollection+'P4'+self.photonSuffix]
        for iJet in range(len(p4Vector)) :
            self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
            
    def drawTaus (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"tauEntryInLegend")) :
            self.tauEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"taus ("+self.tauSuffix+")","l")
        if (self.fakerMode) : return
        p4Vector=eventVars[self.tauCollection+'P4'+self.tauSuffix]
        for iJet in range(len(p4Vector)) :
            self.drawP4(p4Vector[iJet],color,lineWidth,arrowSize)
            
    def drawCleanedRecHits (self,eventVars,extraVars,color,lineWidth,arrowSize) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"cleantedRecHitEntryInLegend")) :
            self.cleanedRecHitEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"cleaned RecHits (hack)","l")

        algoType="Calo"
        detector="Hf"
        flaggedP4s=eventVars["rechit"+algoType+"P4"+detector]
        for hit in range(len(flaggedP4s)) :
            self.drawP4(hit,color,lineWidth,arrowSize)
            
    def makeAlphaTFunc(self,alphaTValue,color) :
        alphaTFunc=r.TF1(("alphaTCurve ( %#5.3g"%alphaTValue)+" )",
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(color)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc

    def drawAlphaPlot (self,eventVars,extraVars,color) :
        stuffToKeep=[]
        pad=r.TPad("pad","pad",0.01+2.0*self.radius,0.01+self.radius,0.95,0.63)
        pad.cd()
        pad.SetRightMargin(0.01)
        title=";#slashH_{T}/H_{T};#DeltaH_{T}/H_{T}"
        alphaHisto=r.TH2D("alphaHisto",title,100,0.0,1.0,100,0.0,0.7)

        mht=getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix).pt()
        ht=getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        deltaHt=getattr(extraVars,self.jetCollection+"nJetDeltaHt"+self.jetSuffix)
        alphaT=getattr(extraVars,self.jetCollection+"nJetAlphaT"+self.jetSuffix)
        
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
        
    def drawMhtLlPlot (self,eventVars,extraVars,color) :
        stuffToKeep=[]
        pad=r.TPad("pad","pad",self.x0+0.37*self.radius,0.63,0.95,0.95)
        pad.cd()
        pad.SetLeftMargin(0.3)
        pad.SetRightMargin(0.15)

        mets=getattr(extraVars,self.jetCollection+"mets"+self.jetSuffix)
        mhts=getattr(extraVars,self.jetCollection+"mhts"+self.jetSuffix)
        lls=getattr(extraVars,self.jetCollection+"lls"+self.jetSuffix)
        nVariedJets=getattr(extraVars,self.jetCollection+"nVariedJets"+self.jetSuffix)
        
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
        
    def uponAcceptance (self,eventVars,extraVars) :
        self.canvas.Clear()

        g1=self.drawSkeleton(r.kYellow+1)
        self.drawEventInfo  (eventVars,extraVars,r.kBlack)

        defArrowSize=0.5*self.arrow.GetDefaultArrowSize()
        defWidth=1
        #                                        color     , width   , arrow size

        if self.doGen :
            self.drawGenJets    (eventVars,extraVars,r.kBlack  , defWidth, defArrowSize      )
        self.drawCleanJets      (eventVars,extraVars,r.kBlue   , defWidth, defArrowSize*2/3.0)
        self.drawLowPtJets      (eventVars,extraVars,r.kCyan   , defWidth, defArrowSize*1/6.0)
        #self.drawOtherJets      (eventVars,extraVars,r.kBlack  )
        self.drawHt             (eventVars,extraVars,r.kBlue+3 , defWidth, defArrowSize*1/6.0)
        self.drawNJetDeltaHt    (eventVars,extraVars,r.kBlue-9 , defWidth, defArrowSize*1/6.0)
        self.drawMht            (eventVars,extraVars,r.kRed    , defWidth, defArrowSize*3/6.0)
        self.drawMet            (eventVars,extraVars,r.kGreen  , defWidth, defArrowSize*2/6.0)
        #self.drawCleanedRecHits (eventVars,extraVars,r.kBrown  , defWidth, defArrowSize*2/6.0)
        if (self.doGen) : self.drawGenMet     (eventVars,extraVars,r.kMagenta, defWidth, defArrowSize*2/6.0)

        if (self.doLeptons) :
            self.drawMuons      (eventVars,extraVars,r.kYellow  , defWidth, defArrowSize*2/6.0)
            self.drawElectrons  (eventVars,extraVars,r.kOrange+7, defWidth, defArrowSize*2/6.0)
            self.drawPhotons    (eventVars,extraVars,r.kOrange  , defWidth, defArrowSize*2/6.0)
            #self.drawTaus       (eventVars,extraVars,r.kYellow , defWidth, defArrowSize*2/6.0)

        self.legend.Draw("same")        
        g2=self.drawAlphaPlot(eventVars,extraVars,r.kBlack)
        
        r.gStyle.SetOptStat(110011)
        #g3=self.drawMhtLlPlot(eventVars,extraVars,r.kBlack)

        someDir=r.gDirectory
        self.outputFile.cd()
        self.canvas.Write("canvas_%d"%self.canvasIndex)
        self.canvasIndex+=1
        someDir.cd()
#####################################
class counter(analysisStep) :
    """counter"""

    def __init__(self,label) :
        self.label = label
        self.moreName = '("%s")' % label
    def bookHistos(self) :
        self.countsHisto = r.TH1D("countsHisto_"+self.label,";dummy axis;number of events",1,-0.5,0.5)

    def uponAcceptance(self,eventVars,extraVars) :
        self.countsHisto.Fill(0.0)
#####################################
class pickEventSpecMaker(analysisStep) :
    """pickEventSpecMaker"""
    #https://twiki.cern.ch/twiki/bin/view/CMS/PickEvents
    def __init__(self,outputFileName,dataSetName) :
        self.outputFileName = outputFileName
        self.dataSetName = dataSetName

    def bookHistos(self) :
        self.outputFile = open(self.outputFileName,"w")
        
    def uponAcceptance(self,eventVars,extraVars) :
        line=""
        line+="%14d"%eventVars["run"]
        line+="%14d"%eventVars["event"]
        line+="%14d"%eventVars["lumiSection"]
        line+="   "+self.dataSetName+"\n"
        self.outputFile.write(line) #slow: faster to buffer output, write less frequently

    def endFunc(self,chain,hyphens,nEvents,xs) :
        print hyphens
        self.outputFile.close()
        print "The pick events spec. file \""+self.outputFileName+"\" has been written."
#####################################
#class bxHistogrammer(analysisStep) :
#    """bxHistogrammer"""
#
#    def bookHistos(self) :
#        nBx=3564+1 #one extra in case count from 1
#        self.bxHisto=r.TH1D("bx",";bx of event;events / bin",nBx,-0.5,nBx-0.5)
#
#    def uponAcceptance(self,eventVars,extraVars) :
#        self.bxHisto.Fill(eventVars["bunch"])
#####################################
