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
        
    def writeTree(self) :
        self.outputFile.cd(self.fileDir)
        self.outputTree.Write()
        if (self.alsoWriteExtraTree) :
            self.outputTreeExtra.Write()
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
