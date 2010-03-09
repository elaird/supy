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
    addListJetAlgoComparison(d)
    return d

def removeStepsForMc(inSteps) :
    dummyBX=bxFilter([])
    dummyPhysDecl=physicsDeclared()
    dummyTechBit0=techBitFilter([0],True)
    dummyRunList=goodRunsOnly2009("900 GeV","v2")
    
    outSteps=[]
    for step in inSteps :
        if (step.__doc__==dummyBX.__doc__) : continue
        if (step.__doc__==dummyPhysDecl.__doc__) : continue
        if (step.moreName==dummyTechBit0.moreName) : continue
        if (step.__doc__==dummyRunList.__doc__) : continue
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

        vertexRequirementFilter(2.0,15.0),        
        jetPtSelector("ak5Jet","Pat",5.0,0),
        #runHistogrammer(),

        skimmer("/tmp/",False),
        ]

    d["triggerSkimSteps_data"]=steps
    d["triggerSkimSteps_mc"]=removeStepsForMc(steps)

def addListJetKineLook(d) :
    #jetCollection="ic5Jet"
    jetCollection="ak5Jet"
    jetSuffix="Pat"
    flagInsteadOfByHand=False
    jetPtThreshold=8.0
    #jetPtThreshold=10.0
    corrRatherThanUnCorr=True
    nCleanJets=2
    jetEtaMax=3.0
    skimmerAlsoWritesExtraTree=False
    
    steps=[
        progressPrinter(2,300),

        goodRunsOnly2009("900 GeV","v3"),

        techBitFilter([40,41],True),
        techBitFilter([0],True),
        techBitFilter([36,37,38,39],False),
        physicsDeclared(),
        vertexRequirementFilter(2.0,15.0),
        monsterEventFilter(10,0.2),

        jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,0),#leading corrected jet
        jetPtSelector(jetCollection,jetSuffix,jetPtThreshold,1),#next corrected jet
        #jetPtVetoer(jetCollection,jetSuffix,jetPtThreshold,2),#next corrected jet

        #skimmer("/tmp/",skimmerAlsoWritesExtraTree),

        cleanJetIndexProducer(jetCollection,jetSuffix,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax,flagInsteadOfByHand),
        nCleanJetEventFilter(jetCollection,jetSuffix,nCleanJets),
        nOtherJetEventFilter(jetCollection,jetSuffix,1),
        cleanJetPtHistogrammer(jetCollection,jetSuffix),
        
        cleanJetHtMhtProducer(jetCollection,jetSuffix),
        #extraVariableGreaterFilter(25.0,jetCollection+"Ht"+jetSuffix),
        cleanJetHtMhtHistogrammer(jetCollection,jetSuffix,corrRatherThanUnCorr),
        
        cleanDiJetAlphaProducer(jetCollection,jetSuffix),
        cleanNJetAlphaProducer(jetCollection,jetSuffix),
        alphaHistogrammer(jetCollection,jetSuffix),

        ##extraVariableGreaterFilter(0.6,jetCollection+"diJetAlpha_pT"+jetSuffix),
        #extraVariableGreaterFilter(0.6,jetCollection+"nJetAlphaT"+jetSuffix),
        #jetPrinter(jetCollection,jetSuffix),
        #metPrinter(["metP4Calo","metP4AK5","metnohfP4Calo"]),
        #particleP4Printer("muon","Pat"),
        #particleP4Printer("electron","Pat"),
        #particleP4Printer("photon","Pat"),
        ]

    d["jetKineSteps_data"]=steps
    d["jetKineSteps_mc"]=removeStepsForMc(steps)

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
        cleanJetIndexProducer(jetCollection1,jetSuffix1,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax,False),
        nCleanJetEventFilter(jetCollection1,jetSuffix1,nCleanJets),
        nOtherJetEventFilter(jetCollection1,jetSuffix1,1),

        #di-jet sample according to algo 2
        jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,0),#leading corrected jet
        jetPtSelector(jetCollection2,jetSuffix2,jetPtThreshold,1),#next corrected jet
        jetPtVetoer(jetCollection2,jetSuffix2,jetPtThreshold,2),#next corrected jet
        cleanJetIndexProducer(jetCollection2,jetSuffix2,jetPtThreshold,corrRatherThanUnCorr,jetEtaMax,False),
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

        skimmer("/tmp/",True),
        
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
