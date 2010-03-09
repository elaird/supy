import copy
from stepsOther import *
from stepsJet import *
from stepsTrigger import *
from stepsJetAlgoComparison import *
from stepsPrint import *

def buildListDictionary() :
    d={}
    addListTriggerSkim(d)
    addListJetKineLook(d)
    addListDeltaPhiLook(d)
    addListJetAlgoComparison(d)
    addListMetGroupCleanupLook(d)
    addListMetDistLook(d)
    return d

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

def addListTriggerSkim(d) :
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

    d["triggerSkimSteps_data"]=steps
    d["triggerSkimSteps_mc"]=removeStepsForMc(steps)

def addListDeltaPhiLook(d) :
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
        
        cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
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

    d["deltaPhiSteps_data"]=steps
    d["deltaPhiSteps_mc"]=removeStepsForMc(steps)

def addListJetKineLook(d) :
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

        #skimmer("/tmp/",skimmerAlsoWritesExtraTree),
        metGroupNoiseEventFilter("v1"),
        
        cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
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

        #eventPrinter(),
        #jetPrinter(jetCollection,jetSuffix),
        #metPrinter(["metP4Calo","metP4AK5","metnohfP4Calo"]),
        #particleP4Printer("muon","Pat"),
        #particleP4Printer("electron","Pat"),
        #particleP4Printer("photon","Pat"),
        ]

    d["jetKineSteps_data"]=steps
    d["jetKineSteps_mc"]=removeStepsForMc(steps)

def addListMetDistLook(d) :
    jetCollection="ak5Jet"
    jetSuffix="Pat"
    jetPtThreshold=8.0
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

        metHistogrammer(metCollection,"ge2jets no jetID"),

        cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
        #nCleanJetHistogrammer(jetCollection,jetSuffix),
        nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
        metHistogrammer(metCollection,"ge2jets at least 2 clean"),

        nOtherJetEventFilter(jetCollection,jetSuffix,1),
        metHistogrammer(metCollection,"ge2jets all clean"),
        
        metGroupNoiseEventFilter("v1"),
        metHistogrammer(metCollection,"ge2jets all clean plus group filter"),        
        ]

    d["metDistSteps_data"]=steps
    d["metDistSteps_mc"]=removeStepsForMc(steps)

def addListMetGroupCleanupLook(d) :
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

        cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
        nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
        nOtherJetEventFilter(jetCollection,jetSuffix,1),

        eventPrinter(),
        jetPrinter(jetCollection,jetSuffix),
        metPrinter(["metP4Calo","metP4AK5"]),
        ]

    d["metGroupCleanupLookSteps_data"]=steps
    d["metGroupCleanupLookSteps_mc"]=removeStepsForMc(steps)

def addListJetAlgoComparison(d) :
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
        cleanJetIndexProducer(jetCollection1,jetSuffix1,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
        nCleanJetEventFilter(jetCollection1,jetSuffix1,nCleanJets),
        nOtherJetEventFilter(jetCollection1,jetSuffix1,1),

        #di-jet sample according to algo 2
        jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,0),#leading corrected jet
        jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,1),#next corrected jet
        jetPtVetoer(jetCollection2,jetSuffix2,jetPtThreshold,2),#next corrected jet
        cleanJetIndexProducer(jetCollection2,jetSuffix2,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax),
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

    d["jetAlgoComparison_data"]=steps
    d["jetAlgoComparison_mc"]=removeStepsForMc(steps)
