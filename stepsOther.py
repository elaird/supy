import copy,array
import ROOT as r
from base import analysisStep
#####################################
class skimmer(analysisStep) :
    #special __doc__ assignment below
    
    def __init__(self,outputDir,alsoWriteExtraTree) :
        self.__doc__=self.skimmerStepName
        self.outputDir=outputDir
        self.outputTree=0
        self.moreName="(see below)"
        self.alsoWriteExtraTree=alsoWriteExtraTree
        self.outputTreeExtraIsSetup=False
        self.neededBranches=[]

    def setup(self,chain,fileDir,name) :
        self.fileDir=fileDir
        self.outputFileName=self.outputDir+"/"+name+"_skim.root"
        self.outputFile=r.TFile(self.outputFileName,"RECREATE")
        self.outputFile.mkdir(self.fileDir)
        self.outputFile.cd(self.fileDir)
        self.outputTree=chain.CloneTree(0)        #clone structure of tree (but no entries)
        self.outputTree.SetDirectory(r.gDirectory)#put output tree in correct place
        chain.CopyAddresses(self.outputTree)      #associate branch addresses

        if (self.alsoWriteExtraTree) :
            self.arrayDictionary={}
            self.supportedBuiltInTypes=[type(True),type(0),type(0L),type(0.0)]
            self.supportedOtherTypes=[type(r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0))]
            
            extraName=self.outputTree.GetName()+"Extra"
            self.outputTreeExtra=r.TTree(extraName,extraName)
            self.outputTreeExtra.SetDirectory(r.gDirectory)

        r.gROOT.cd()

    def select(self,chain,chainVars,extraVars) :
        #read all the data for this event
        if (chain.GetEntry(extraVars.entry,1)<=0) :
            return False #skip this event in case of i/o error
        #fill the skim tree
        self.outputTree.Fill()
        
        #optionally fill an extra tree
        if (self.alsoWriteExtraTree) :
            if (not self.outputTreeExtraIsSetup) : self.setupExtraTree(extraVars)
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
        
    def endFunc(self,hypens) :
        print hypens
        self.outputFile.cd(self.fileDir)
        self.outputTree.Write()
        if (self.alsoWriteExtraTree) :
            self.outputTreeExtra.Write()
        print "The skim file \""+self.outputFileName+"\" has been written."
#####################################
class extraVariableGreaterFilter(analysisStep) :
    """extraVariableGreaterFilter"""

    def __init__(self,threshold,variable):
        self.threshold=threshold
        self.variable=variable
        self.moreName="("+self.variable
        self.moreName+=">="
        self.moreName+=str(self.threshold)
        self.moreName+=")"
        self.neededBranches=[]

    def select (self,chain,chainVars,extraVars) :
        return (getattr(extraVars,self.variable)>=self.threshold)
#####################################
class vertexRequirementFilterOld(analysisStep) :
    """vertexRequirementFilterOld"""
    
    def __init__(self,minVertexNtracks,maxVertexChi2Ndf,maxVertexZ) :
        self.neededBranches=["vertexChi2","vertexNdof","vertexNtrks","vertexPosition"]
        self.minVertexNtracks=minVertexNtracks
        self.maxVertexChi2Ndf=maxVertexChi2Ndf
        self.maxVertexZ=maxVertexZ
        self.moreName="("
        self.moreName+=">="+str(self.minVertexNtracks)+" ve.tr.; "
        self.moreName+="chi2/ndf<"+str(self.maxVertexChi2Ndf)+"; "
        self.moreName+="abs(z)<"+str(self.maxVertexZ)
        self.moreName+=")"

    def select(self,chain,chainVars,extraVars) :
        nVertices=len(chain.vertexPosition)
        for i in range(nVertices) :
            if (chain.vertexNtrks[i]>=self.minVertexNtracks
                and chain.vertexNdof[i]>0.0
                and chain.vertexChi2[i] / chain.vertexNdof[i] < self.maxVertexChi2Ndf
                and r.TMath.Abs(chain.vertexPosition[i].Z()) < self.maxVertexZ) :
                return True
        return False
#####################################
class vertexRequirementFilter(analysisStep) :
    """vertexRequirementFilter"""
    
    def __init__(self,minVertexNdof,maxVertexZ) :
        self.neededBranches=["vertexIsFake","vertexNdof","vertexPosition"]
        self.minVertexNdof=minVertexNdof
        self.maxVertexZ=maxVertexZ
        self.moreName="(any v: !fake; "
        self.moreName+="ndf>="+str(self.minVertexNdof)+"; "
        self.moreName+="abs(z)<"+str(self.maxVertexZ)
        self.moreName+=")"

    def select(self,chain,chainVars,extraVars) :
        nVertices=len(chainVars.vertexPosition)
        for i in range(nVertices) :
            if (chainVars.vertexIsFake[i]) : continue
            if (chainVars.vertexNdof[i]<self.minVertexNdof) : continue
            if (r.TMath.Abs(chainVars.vertexPosition[i].Z()) >= self.maxVertexZ) : continue
            return True
        return False
#####################################
class monsterEventFilter(analysisStep) :
    """monsterEventFilter"""
    
    def __init__(self,maxNumTracks,minGoodTrackFraction) :
        self.neededBranches=["tracksNEtaLT0p9AllTracks"       ,"tracksNEta0p9to1p5AllTracks"       ,"tracksNEtaGT1p5AllTracks",
                             "tracksNEtaLT0p9HighPurityTracks","tracksNEta0p9to1p5HighPurityTracks","tracksNEtaGT1p5HighPurityTracks"
                             ]
        self.maxNumTracks=maxNumTracks
        self.minGoodTrackFraction=minGoodTrackFraction
        self.moreName="("
        self.moreName+="<="+str(maxNumTracks)+" tracks or "
        self.moreName+=">"+str(minGoodTrackFraction)+" good fraction"
        self.moreName+=")"

    def select (self,chain,chainVars,extraVars) :
        nTracks    =chain.tracksNEtaLT0p9AllTracks        + chain.tracksNEta0p9to1p5AllTracks        + chain.tracksNEtaGT1p5AllTracks
        nGoodTracks=chain.tracksNEtaLT0p9HighPurityTracks + chain.tracksNEta0p9to1p5HighPurityTracks + chain.tracksNEtaGT1p5HighPurityTracks
        return (nTracks <= self.maxNumTracks or nGoodTracks > self.minGoodTrackFraction*nTracks)
#####################################
class runNumberFilter(analysisStep) :
    """runNumberFilter"""

    def __init__(self,runList,acceptRatherThanReject) :
        self.neededBranches=["run"]
        self.runList=runList
        self.accept=acceptRatherThanReject
        self.moreName="run "
        if (not self.accept) : self.moreName+="not "
        self.moreName+="in list ["
        for i in range(len(self.runList)) :
            self.moreName+=str(self.runList[i])
            if (i!=len(self.runList)-1) : self.moreName+=","
            else : self.moreName+="]"
        
    def select (self,chain,chainVars,extraVars) :
        thisRun=chain.run
        return not ((thisRun in self.runList) ^ self.accept)

#####################################
class goodRunsOnly2009(analysisStep) :
    """goodRunsOnly2009"""

    def __init__(self,energyString,version) :
        self.neededBranches=["run","lumiSection"]
        self.moreName="("+energyString+" "+version+")"
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
        
    def select (self,chain,chainVars,extraVars) :
        run=chain.run
        #run=chainVars.run[0]
        if (not run in self.runDict) : return False
        ls=chain.lumiSection
        #ls=chainVars.lumiSection[0]
        if (ls<self.runDict[run][0]) : return False
        if (ls>self.runDict[run][1]) : return False
        return True

#####################################
class runHistogrammer(analysisStep) :
    """runHistogrammer"""

    def __init__(self) :
        self.neededBranches=["run"]
        self.runDict={}
        
    def select (self,chain,chainVars,extraVars) :
        run=chain.run
        if (run in self.runDict) :
            self.runDict[run]+=1
        else :
            self.runDict[run]=1
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
        self.neededBranches=["run","lumiSection","event"]
        self.version=version
        self.moreName="("+self.version+")"
        self.setupStuff()

    def setupStuff(self) :
        self.setOfBadTuples=set([])

        inFile=open("/afs/cern.ch/user/e/elaird/public/susypvt/misc/cleaned_events/cleaned_events_"+self.version+".txt")
        for line in inFile :
            varList=line.split()
            run=int(varList[1])
            ls=int(varList[3])
            event=int(varList[5])
            self.setOfBadTuples.add( (run,ls,event) )
        inFile.close()
        
    def select (self,chain,chainVars,extraVars) :
        run=chain.run
        ls=chain.lumiSection
        event=chain.event
        tuple=(run,ls,event)
        return not (tuple in self.setOfBadTuples)
#####################################
class bxFilter(analysisStep) :
    """bxFilter"""

    def __init__(self,bxList) :
        self.neededBranches=["bunch"]
        self.bxList=bxList
        self.moreName="["
        for i in range(len(self.bxList)) :
            self.moreName+=str(self.bxList[i])
            if (i!=len(self.bxList)-1) : self.moreName+=","
            else : self.moreName+="]"
        
    def select (self,chain,chainVars,extraVars) :
        bunch=chain.bunch
        for bx in self.bxList:
            if (bx==bunch) : return True
#####################################
class displayer(analysisStep) :
    """displayer"""

    def __init__(self,jetCollection,jetSuffix,outputDir) :
        self.outputDir=outputDir
        self.moreName="(see below)"
        self.scale=500 #GeV
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.neededBranches=[self.jetCollection+'CorrectedP4'+self.jetSuffix]
        self.neededBranches.extend(["run","lumiSection","event","bunch"])
        
    def setup(self,chain,fileDir,name) :
        self.fileDir=fileDir
        self.outputFileName=self.outputDir+"/"+name+"_displays.ps"
        self.canvas=r.TCanvas("canvas","canvas",500,500)
        self.printCanvas("[")
        self.ellipse=r.TEllipse()
        self.ellipse.SetFillStyle(0)
        self.line=r.TLine()
        self.radius=0.3
        self.x0=self.radius
        self.y0=self.radius
        self.text=r.TText()
        self.latex=r.TLatex()
        self.legend=r.TLegend(0.01+2.0*self.radius,self.radius,0.95,0.05)

    def endFunc(self,hypens) :
        print hypens
        self.printCanvas("]")
        print "The display file \""+self.outputFileName+"\" has been written."

    def printCanvas(self,extraStuff="") :
        self.canvas.Print(self.outputFileName+extraStuff,"Landscape")

    def drawEventInfo(self,chainVars,extraVars,color) :
        self.text.SetTextSize(0.02)
        self.text.SetTextFont(80)
        self.text.SetTextColor(color)
        x=0.78
        self.text.DrawText(x,0.80,"Run   %#10d"%chainVars.run[0])
        self.text.DrawText(x,0.78,"Ls    %#10d"%chainVars.lumiSection[0])
        self.text.DrawText(x,0.76,"Event %#10d"%chainVars.event[0])
        self.text.DrawText(x,0.74,"Bx    %#10d"%chainVars.bunch[0])
        
    def drawSkeleton(self,color) :
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(1)
        self.ellipse.DrawEllipse(self.x0,self.y0,self.radius,self.radius,0.0,360.0,0.0,"")

        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-self.radius,self.y0            ,self.x0+self.radius,self.y0            )
        self.line.DrawLine(self.x0            ,self.y0-self.radius,self.x0            ,self.y0+self.radius)

        self.latex.SetTextSize(0.04)
        self.latex.SetTextColor(color)
        self.latex.DrawLatex(0.6,0.01,"radius = "+str(self.scale)+" GeV p_{T}")

    def drawP4(self,p4,color) :
        x1=self.x0+p4.px()*self.radius/self.scale
        y1=self.y0+p4.py()*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0,self.y0,x1,y1)
        
    def drawCleanJets (self,chainVars,extraVars,color) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"jetEntryInLegend")) :
            self.jetEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"jets","l")
            
        p4Vector=getattr(chainVars,self.jetCollection+'CorrectedP4'+self.jetSuffix)
        cleanJetIndices=getattr(extraVars,self.jetCollection+"cleanJetIndices"+self.jetSuffix)

        for iJet in cleanJetIndices :
            self.drawP4(p4Vector[iJet],color)
            
    def drawMht (self,chainVars,extraVars,color) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"mhtEntryInLegend")) :
            self.mhtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#slashH_{T}","l")

        mht=getattr(extraVars,self.jetCollection+"Mht"+self.jetSuffix)
        self.drawP4(mht,color)
        
    def drawHt (self,chainVars,extraVars,color) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"htEntryInLegend")) :
            self.htEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"H_{T}","l")

        ht=getattr(extraVars,self.jetCollection+"Ht"+self.jetSuffix)
        y=2.0*self.radius+0.10
        l=ht*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)
        
    def drawNJetDeltaHt (self,chainVars,extraVars,color) :
        self.line.SetLineColor(color)
        if (not hasattr(self,"deltaHtEntryInLegend")) :
            self.deltaHtEntryInLegend=True
            someLine=self.line.DrawLine(0.0,0.0,0.0,0.0)
            self.legend.AddEntry(someLine,"#DeltaH_{T}","l")

        deltaHt=getattr(extraVars,self.jetCollection+"nJetDeltaHt"+self.jetSuffix)
        y=2.0*self.radius+0.06
        l=deltaHt*self.radius/self.scale
        self.line.SetLineColor(color)
        self.line.DrawLine(self.x0-l/2.0,y,self.x0+l/2.0,y)


    def makeAlphaTFunc(self,alphaTValue,color) :
        alphaTFunc=r.TF1(("alphaTCurve ( %#5.3g"%alphaTValue)+" )",
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(color)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc

    def drawAlphaPlot (self,chainVars,extraVars,color) :
        stuffToKeep=[]
        pad=r.TPad("pad","pad",0.01+2.0*self.radius,0.01+self.radius,0.95,0.70)
        pad.cd()
        pad.SetRightMargin(0.0)
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
        
        funcs=[
            self.makeAlphaTFunc(0.55,r.kBlack),
            self.makeAlphaTFunc(0.50,r.kOrange+3),
            self.makeAlphaTFunc(0.45,r.kOrange+7)
            ]
        stuffToKeep.extend(funcs)
        for func in funcs :
            func.Draw("same")
            legend.AddEntry(func,func.GetName(),"l")

        legend.AddEntry(alphaHisto,"this event ( %#5.3g )"%alphaT,"p")
        legend.Draw()
        stuffToKeep.extend([pad,alphaHisto,legend])
        self.canvas.cd()
        pad.Draw()
        return stuffToKeep
        
    def uponAcceptance (self,chain,chainVars,extraVars) :
        self.canvas.Clear()
        self.drawSkeleton(r.kYellow+1)
        self.drawEventInfo(chainVars,extraVars,r.kBlack)
        self.drawCleanJets(chainVars,extraVars,r.kBlue)
        self.drawMht(chainVars,extraVars,r.kRed)
        self.drawHt(chainVars,extraVars,r.kBlue+3)
        self.drawNJetDeltaHt(chainVars,extraVars,r.kBlue-9)

        graphicalStuff=self.drawAlphaPlot(chainVars,extraVars,r.kBlack)
        
        self.legend.Draw("same")
        self.printCanvas()


#####################################
#class bxHistogrammer(analysisStep) :
#    """bxHistogrammer"""
#
#    def __init__(self) :
#        self.neededBranches=["bunch"]
#
#    def bookHistos(self) :
#        nBx=3564+1 #one extra in case count from 1
#        self.bxHisto=r.TH1D("bx",";bx of event;events / bin",nBx,-0.5,nBx-0.5)
#
#    def uponAcceptance(self,chain,chainVars,extraVars) :
#        self.bxHisto.Fill(chain.bunch)
#####################################
