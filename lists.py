import copy
from stepsOther import *
from stepsJet import *
from stepsTrigger import *
from stepsJetAlgoComparison import *
from stepsPrint import *
from stepsGen import *
from stepsIcf import *

def removeStepsForMc(inSteps) :
    dummyBX=bxFilter([])
    dummyPhysDecl=physicsDeclared()
    dummyTechBit0=techBitFilter([0],True)
    dummyRunList=goodRunsOnly2009("900 GeV","v2")
    dummyMetGroupFilter=metGroupNoiseEventFilter("v1")
    outSteps=[]
    for step in inSteps :
        if (step.__doc__==dummyBX.__doc__) : continue
        if (step.__doc__==dummyPhysDecl.__doc__) : continue
        if (step.moreName==dummyTechBit0.moreName) : continue
        if (step.__doc__==dummyRunList.__doc__) : continue
        if (step.__doc__==dummyMetGroupFilter.__doc__) : continue        
        outSteps.append(copy.deepcopy(step))
    return outSteps

class listDictionaryHolder :
    """listDictionaryHolder"""

    def __init__(self) :
        self.listDict={}
    
    def getDictionary(self) :
        return self.listDict
    
    def buildDictionary(self) :
        #call all member functions starting with specialPrefix
        specialPrefix="add"
        for member in dir(self) :
            if member[:len(specialPrefix)]!=specialPrefix : continue
            getattr(self,member)()

    def addListTriggerSkim(self) :
        steps=[
            progressPrinter(2,300),
            
            techBitFilter([40,41],True),
            techBitFilter([0],True),
            techBitFilter([36,37,38,39],False),
            physicsDeclared(),
            goodRunsOnly2009("900 GeV","v3"),
            metGroupNoiseEventFilter("v1"),
            vertexRequirementFilter(5.0,15.0),
            jetPtSelector("ak5Jet","Pat",5.0,0),
            jetPtSelector("ak5Jet","Pat",5.0,1),
            #runHistogrammer(),
            skimmer("/tmp/",False),
            ]

        self.listDict["triggerSkimSteps_data"]=steps
        self.listDict["triggerSkimSteps_mc"]=removeStepsForMc(steps)

    def addListMetPasFilter(self) :
        steps=[
            progressPrinter(2,300),
            techBitFilter([0],True),
            physicsDeclared(),
            vertexRequirementFilter(5.0,15.0),
            monsterEventFilter(10,0.25),
            hltFilter("HLT_Jet15U"),
            skimmer("/tmp/bbetchar/SusyCAF/2010_05_18_19_26_19/OUTPUT/",False)
            ]
        self.listDict["metPasFilter_data"]=steps
        self.listDict["metPasFilter_mc"]=removeStepsForMc(steps)

    def addListRecHitTest(self) :
        jetCollection="ak5Jet"
        jetSuffix="Pat"
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        jetEtaMax=50.0
        
        #algoType="Calo"
        #detector="Eb"
        #detector="Ee"
        #detector="Hbhe"
        #detector="Hf"

        algoType="PF"
        detector="Ecal"
    
        steps=[
            progressPrinter(2,300),
            nFlaggedRecHitFilter(algoType,detector,1),
            eventPrinter(),
            recHitPrinter(algoType,detector),
            cleanJetIndexProducerOld(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            jetPrinter(jetCollection,jetSuffix),
            ]
        self.listDict["RecHitTestSteps"]=steps

    def addHcalTechTriggerCheck(self) :
        branch1List=[eventPrinter()]

        branch2List=[physicsDeclared(),
                     techBitFilter([0],True)
                     ]
    
        steps=[
            progressPrinter(2,300),
            techBitFilter([12],True),
            #eventPrinter()
            #branchStep([branch1List,branch2List])
            ]
        self.listDict["HcalTechTriggerCheckSteps"]=steps

    def addMSugraLook(self) :
        tanBeta=10.0
        steps=[
            progressPrinter(2,300),
            #skimmer("/tmp/",False),
            #eventPrinter(),
            #genParticlePrinter(),
            genParticleCounter(tanBeta),
            #susyScanPointPrinter(),
            ]
        self.listDict["mSugraLookSteps"]=steps

    def addListDeltaPhiLook(self) :
        #jetCollection="ic5Jet"
        jetCollection="ak5Jet"
        #jetCollection="ak7Jet"
        jetSuffix="Pat"
        #jetPtThreshold=8.0
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        nCleanJets=2
        jetEtaMax=3.0
    
        #metCollection="metnohfP4Calo"
        #metCollection="metP4Calo"
        metCollection="metP4AK5"
        
        steps=[
            progressPrinter(2,300),
            
            #these already addressed in the skim
            #goodRunsOnly2009("900 GeV","v3"),
            #
            #techBitFilter([40,41],True),
            #techBitFilter([0],True),
            #techBitFilter([36,37,38,39],False),
            #physicsDeclared(),
            vertexRequirementFilter(5.0,15.0),
            #monsterEventFilter(10,0.25),
            
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
            jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet
            
            metGroupNoiseEventFilter("v1"),
            
            cleanJetIndexProducerOld(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
            nOtherJetEventFilter(jetCollection,jetSuffix,1),
            cleanJetPtHistogrammer(jetCollection,jetSuffix),
            
            cleanJetHtMhtProducer(jetCollection,jetSuffix),
            #extraVariableGreaterFilter(25.0,jetCollection+"Ht"+jetSuffix),
            
            cleanDiJetAlphaProducer(jetCollection,jetSuffix),
            cleanNJetAlphaProducer(jetCollection,jetSuffix),
            #alphaHistogrammer(jetCollection,jetSuffix),
            
            deltaPhiProducer(jetCollection,jetSuffix),
            deltaPhiSelector(jetCollection,jetSuffix,0.4,1.0),
            deltaPhiHistogrammer(jetCollection,jetSuffix),
            mHtOverHtSelector(jetCollection,jetSuffix,0.9,1.1),
            cleanJetHtMhtHistogrammer(jetCollection,jetSuffix,corrRatherThanUnCorr),
            
            #skimmer("/tmp/",True),
            
            ##extraVariableGreaterFilter(0.6,jetCollection+"diJetAlpha_pT"+jetSuffix),
            #extraVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
            
            eventPrinter(),
            jetPrinter(jetCollection,jetSuffix),
            metPrinter(["metP4Calo","metP4AK5","metnohfP4Calo"]),
            particleP4Printer("muon","Pat"),
            particleP4Printer("electron","Pat"),
            particleP4Printer("photon","Pat"),
            ]
        
        self.listDict["deltaPhiSteps_data"]=steps
        self.listDict["deltaPhiSteps_mc"]=removeStepsForMc(steps)

    def addListJetKineLook(self) :
        jetCollection="ak5Jet"
        jetSuffix="Pat"
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        nCleanJets=2
        jetEtaMax=3.0
        skimmerAlsoWritesExtraTree=False
        
        #metCollection="metnohfP4Calo"
        #metCollection="metP4Calo"
        metCollection="metP4AK5"

        steps=[
            progressPrinter(2,300),
            
            #these already addressed in the skim
            #goodRunsOnly2009("900 GeV","v3"),
            #
            #techBitFilter([40,41],True),
            #techBitFilter([0],True),
            #techBitFilter([36,37,38,39],False),
            #physicsDeclared(),
            vertexRequirementFilter(5.0,15.0),
            #monsterEventFilter(10,0.25),
            
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
            #jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet
            
            metGroupNoiseEventFilter("v1"),
            
            cleanJetIndexProducerOld(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
            nOtherJetEventFilter(jetCollection,jetSuffix,1),
            cleanJetPtHistogrammer(jetCollection,jetSuffix),
            
            cleanJetHtMhtProducer(jetCollection,jetSuffix),
            cleanJetHtMhtHistogrammer(jetCollection,jetSuffix,corrRatherThanUnCorr),
            #extraVariableGreaterFilter(25.0,jetCollection+"Ht"+jetSuffix),
            
            cleanDiJetAlphaProducer(jetCollection,jetSuffix),
            cleanNJetAlphaProducer(jetCollection,jetSuffix),
            alphaHistogrammer(jetCollection,jetSuffix),
            
            deltaPhiProducer(jetCollection,jetSuffix),
            deltaPhiHistogrammer(jetCollection,jetSuffix),
            
            ##extraVariableGreaterFilter(0.6,jetCollection+"diJetAlpha_pT"+jetSuffix),
            #extraVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
            
            #skimmer("/tmp/",skimmerAlsoWritesExtraTree),
            
            #eventPrinter(),
            #jetPrinter(jetCollection,jetSuffix),
            #metPrinter(["metP4Calo","metP4AK5","metnohfP4Calo"]),
            #particleP4Printer("muon","Pat"),
            #particleP4Printer("electron","Pat"),
            #particleP4Printer("photon","Pat"),
            ]
        
        self.listDict["jetKineSteps_data"]=steps
        self.listDict["jetKineSteps_mc"]=removeStepsForMc(steps)

    def addListMetDistLook(self) :
        jetCollection="ak5Jet"
        jetSuffix="Pat"
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        nCleanJets=2
        jetEtaMax=3.0
        skimmerAlsoWritesExtraTree=False
        
        #metCollection="metnohfP4Calo"
        metCollection="metP4Calo"
        #metCollection="metP4AK5"

        steps=[
            progressPrinter(2,300),
            
            #these already addressed in the skim
            #goodRunsOnly2009("900 GeV","v3"),
            
            techBitFilter([40,41],True),
            techBitFilter([0],True),
            techBitFilter([36,37,38,39],False),
            physicsDeclared(),
            vertexRequirementFilter(5.0,15.0),
            #monsterEventFilter(10,0.25),
            
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
            #jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet
            
            metHistogrammer(metCollection,"ge2jets no jetID"),
            
            cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,jetEtaMax),
            #cleanJetIndexProducerOld(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            #nCleanJetHistogrammer(jetCollection,jetSuffix),
            nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
            metHistogrammer(metCollection,"ge2jets at least 2 clean"),
            
            nOtherJetEventFilter(jetCollection,jetSuffix,1),
            metHistogrammer(metCollection,"ge2jets all clean"),
            
            #metGroupNoiseEventFilter("v1"),
            #metHistogrammer(metCollection,"ge2jets all clean plus group filter"),        
            ]
        
        self.listDict["metDistSteps_data"]=steps
        self.listDict["metDistSteps_mc"]=removeStepsForMc(steps)
        
    def addListMetGroupCleanupLook(self) :
        jetCollection="ak5Jet"
        jetSuffix="Pat"
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        nCleanJets=2
        jetEtaMax=3.0
        skimmerAlsoWritesExtraTree=False
        
        #metCollection="metnohfP4Calo"
        #metCollection="metP4Calo"
        metCollection="metP4AK5"
        
        steps=[
            progressPrinter(2,300),
            
            #these already addressed in the skim
            goodRunsOnly2009("900 GeV","v3"),
            
            techBitFilter([40,41],True),
            techBitFilter([0],True),
            techBitFilter([36,37,38,39],False),
            physicsDeclared(),
            vertexRequirementFilter(2.0,15.0),
            monsterEventFilter(10,0.25),
            
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
            ##jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet
            
            metGroupNoiseEventFilter("v1"),
            
            cleanJetIndexProducerOld(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
            nOtherJetEventFilter(jetCollection,jetSuffix,1),
            
            eventPrinter(),
            jetPrinter(jetCollection,jetSuffix),
            metPrinter(["metP4Calo","metP4AK5"]),
            ]
        
        self.listDict["metGroupCleanupLookSteps_data"]=steps
        self.listDict["metGroupCleanupLookSteps_mc"]=removeStepsForMc(steps)
        
    def addListJetAlgoComparison(self) :
        jetCollection1="ak5Jet"
        jetCollection2="ic5Jet"
        jetSuffix1="Pat"
        jetSuffix2="Pat"
        jetPtThreshold=10.0
        corrRatherThanUnCorr=True
        nCleanJets=2
        jetEtaMax=3.0
        
        steps=[
            progressPrinter(2,300),
            
            goodRunsOnly2009("900 GeV","v3"),
            
            #di-jet sample according to algo 1
            jetPtSelector(jetCollection1,jetSuffix1,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection1,jetSuffix1,jetPtThreshold,1),#next corrected jet
            jetPtVetoer(jetCollection1,jetSuffix1,jetPtThreshold,2),#next corrected jet
            cleanJetIndexProducerOld(jetCollection1,jetSuffix1,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            nCleanJetEventFilter(jetCollection1,jetSuffix1,nCleanJets),
            nOtherJetEventFilter(jetCollection1,jetSuffix1,1),
            
            #di-jet sample according to algo 2
            jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,0),#leading corrected jet
            jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,1),#next corrected jet
            jetPtVetoer(jetCollection2,jetSuffix2,jetPtThreshold,2),#next corrected jet
            cleanJetIndexProducerOld(jetCollection2,jetSuffix2,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
            nCleanJetEventFilter(jetCollection2,jetSuffix2,nCleanJets),
            nOtherJetEventFilter(jetCollection2,jetSuffix2,1),
            
            #now we have some sort of "clean" di-jet sample
            #produce some variables and make some histograms
            
            cleanJetPtHistogrammer(jetCollection1,jetSuffix1),
            cleanJetPtHistogrammer(jetCollection2,jetSuffix2),
            
            leadingJetPtHistogrammer(jetCollection1,jetSuffix1,jetCollection2,jetSuffix2),
            
            cleanJetHtMhtProducer(jetCollection1,jetSuffix1),
            cleanJetHtMhtProducer(jetCollection2,jetSuffix2),
            
            cleanJetHtMhtHistogrammer(jetCollection1,jetSuffix1,corrRatherThanUnCorr),
            cleanJetHtMhtHistogrammer(jetCollection2,jetSuffix2,corrRatherThanUnCorr),
            
            cleanDiJetAlphaProducer(jetCollection1,jetSuffix1),
            cleanDiJetAlphaProducer(jetCollection2,jetSuffix2),
            
            cleanNJetAlphaProducer(jetCollection1,jetSuffix1),
            cleanNJetAlphaProducer(jetCollection2,jetSuffix2),
            
            alphaHistogrammer(jetCollection1,jetSuffix1),
            alphaHistogrammer(jetCollection2,jetSuffix2),
            
            #skimmer("/tmp/",True),
            
            #extraVariableGreaterFilter(0.6,jetCollection1+"nJetAlphaT"+jetSuffix1),
            #extraVariableGreaterFilter(25.0,jetCollection1+"Ht"+jetSuffix1),
            #
            #eventPrinter(),
            #jetPrinter(jetCollection1,jetSuffix1),
            #htMhtPrinter(jetCollection1,jetSuffix1),
            #diJetAlphaPrinter(jetCollection1,jetSuffix1),
            #nJetAlphaTPrinter(jetCollection1,jetSuffix1),
            ]
        
        self.listDict["jetAlgoComparison_data"]=steps
        self.listDict["jetAlgoComparison_mc"]=removeStepsForMc(steps)
        
    def addListIcfRa1_DiJet(self) :
        #jetPtThreshold=100.0
        #jetPtThresholdVeto=50.0
        #jetPtThresholdClean=50.0

        jetPtThreshold=100.0
        jetPtThresholdVeto=50.0
        jetPtThresholdClean=20.0
        
        nCleanJets=2
        jetEtaMax=3.0
        
        muonPtThreshold=10.0
        elecPtThreshold=10.0
        photPtThreshold=25.0
        
        minLogLikelihood=-6.0
        
        steps=[
            progressPrinter(2,300),
            
            icfJetPtSorter(),
            
            icfAnyJetPtSelector(jetPtThreshold,0),
            icfAnyJetPtSelector(jetPtThreshold,1),
            icfAnyJetPtVetoer  (jetPtThresholdVeto,2),
            
            icfCleanJetProducer(jetPtThresholdClean,jetEtaMax),
            icfNCleanJetHistogrammer(),
            icfNCleanJetEventFilter(nCleanJets),
            
            icfCleanJetPtSelector(jetPtThreshold,0),
            icfCleanJetPtSelector(jetPtThreshold,1),
            icfCleanJetPtVetoer(jetPtThresholdVeto,2),
            icfCleanJetEtaSelector(2.5,0),
            #skimmer("/tmp/",False),        
            icfNOtherJetEventFilter(1),
            
            icfMuonVetoer(muonPtThreshold),
            icfElecVetoer(elecPtThreshold),
            icfPhotVetoer(photPtThreshold),
            
            icfCleanJetHtMhtProducer(),
            extraVariableGreaterFilter(250.0,"Ht"),
            #extraVariableGreaterFilter(500.0,"Ht"),
            icfCleanDiJetAlphaProducer(),
            icfCleanNJetAlphaProducer(),
            icfDeltaPhiProducer(),
            
            #icfMhtAllProducer(30.0),
            #icfMhtRatioSelector(1.25),
            
            icfCleanJetPtEtaHistogrammer(),
            icfCleanJetHtMhtHistogrammer(),
            icfAlphaHistogrammer(),
            #icfDeltaPhiHistogrammer(),
            
            #devMhtOld("","",True),
            #devMhtHistogrammerOld("","",minLogLikelihood),
            
            #devMht("","",minLogLikelihood,True),
            #devMhtHistogrammer("","",minLogLikelihood),
            #displayer("","","/tmp/",400.0,True),
            
            #extraVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
            #extraVariableGreaterFilter(25.0,jetCollection+"Ht"+jetSuffix),
            ]

        self.listDict["Icf_Ra1_DiJet_Steps_data"]=steps
        self.listDict["Icf_Ra1_DiJet_Steps_mc"]=removeStepsForMc(steps)
    
    def addListIcfRa1_NJet(self) :
        jetPtLeadingThreshold=100.0
        jetPtThreshold=50.0
        nCleanJets=2
        jetEtaMax=3.0
        
        muonPtThreshold=10.0
        elecPtThreshold=10.0
        photPtThreshold=25.0
        
        steps=[
            progressPrinter(2,300),
            
            #icfGenPrinter(),
            #icfGenP4Producer(),
            #icfGenP4Histogrammer(),
            
            icfJetPtSorter(),
            
            icfAnyJetPtSelector(jetPtLeadingThreshold,0),
            icfAnyJetPtSelector(jetPtLeadingThreshold,1),
            
            #icfCleanJetFromGenProducer(jetPtThreshold,jetEtaMax),
            icfCleanJetProducer(jetPtThreshold,jetEtaMax),
            icfNCleanJetHistogrammer(),
            icfNCleanJetEventFilter(nCleanJets),
            
            icfCleanJetPtSelector(jetPtLeadingThreshold,0),
            icfCleanJetPtSelector(jetPtLeadingThreshold,1),
            #icfCleanJetPtVetoer(jetPtLeadingThreshold,2),
            icfCleanJetEtaSelector(2.0,0),
            #skimmer("/tmp/",False),
            icfNOtherJetEventFilter(1),
            
            icfOtherJetHistogrammer(0.0),
            
            icfMuonVetoer(muonPtThreshold),
            icfElecVetoer(elecPtThreshold),
            icfPhotVetoer(photPtThreshold),
            
            icfCleanJetHtMhtProducer(),
            extraVariableGreaterFilter(350.0,"Ht"),
            icfCleanDiJetAlphaProducer(),
            icfCleanNJetAlphaProducer(),
            icfDeltaPhiProducer(),
            
            icfMhtAllProducer(30.0),
            icfMhtRatioSelector(1.25),
            
            icfCleanJetPtEtaHistogrammer(),
            icfCleanJetHtMhtHistogrammer(),
            icfAlphaHistogrammer(),
            icfDeltaPhiHistogrammer(),
            
            #extraVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
            #extraVariableGreaterFilter(25.0,jetCollection+"Ht"+jetSuffix),
            ]
        
        self.listDict["Icf_Ra1_NJet_Steps_data"]=steps
        self.listDict["Icf_Ra1_NJet_Steps_mc"]=removeStepsForMc(steps)
        
