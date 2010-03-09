import base,samples,lists

sampleDict=samples.buildSampleDictionary()
listDict=lists.buildListDictionary()

def buildAnalysisDictionary() :
    d={}
    addTriggerSkim(d)
    addJetKineLook(d)
    addDeltaPhiLook(d)
    addExample(d)
    addJetAlgoComparison(d)
    addMetDistLook(d)
    addMetGroupCleanupLook(d)
    addRA1_DiJet(d)
    addRA1_NJet(d)
    return d
    
def addTriggerSkim(d) :
    outputPrefix="triggerSkim"

    steps_data=listDict["triggerSkimSteps_data"]
    steps_mc  =listDict["triggerSkimSteps_mc"  ]

    specs=[
        base.sampleSpecification(sampleDict,"2009_Data_v7", -1,outputPrefix,steps_data),

        #base.sampleSpecification(sampleDict,"2009_Data_v6", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6", -1,outputPrefix,steps_mc),

        #base.sampleSpecification(sampleDict,"2009_Data_v5", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v5", -1,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addMetGroupCleanupLook(d) :
    outputPrefix="metGroupCleanupLook"

    steps_data=listDict["metGroupCleanupLookSteps_data"]
    steps_mc  =listDict["metGroupCleanupLookSteps_mc"  ]

    specs=[
        #900 GeV data
        #base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),

        #900 GeV MC
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addMetDistLook(d) :
    outputPrefix="metDistLook"

    steps_data=listDict["metDistSteps_data"]
    steps_mc  =listDict["metDistSteps_mc"  ]

    specs=[
        #900 GeV data
        #base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),

        #900 GeV MC
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
        base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
        ]
    d[outputPrefix]=specs

def addDeltaPhiLook(d) :
    outputPrefix="deltaPhiLook"

    steps_data=listDict["deltaPhiSteps_data"]
    steps_mc  =listDict["deltaPhiSteps_mc"  ]

    specs=[
        #2 TeV data
        #base.sampleSpecification(sampleDict,"2_TeV_Data",      -1,outputPrefix,steps_data),

        #2 TeV MC
        #base.sampleSpecification(sampleDict,"2_TeV_MC",   2000000,outputPrefix,steps_mc),

        #900 GeV data (test)
        #base.sampleSpecification(sampleDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"2009_Data_v6", -1,outputPrefix,steps_data),

        #900 GeV data
        #base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),

        #900 GeV MC
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
        base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addJetKineLook(d) :
    outputPrefix="jetKineLook"

    steps_data=listDict["jetKineSteps_data"]
    steps_mc  =listDict["jetKineSteps_mc"  ]

    specs=[
        #2 TeV data
        #base.sampleSpecification(sampleDict,"2_TeV_Data",      -1,outputPrefix,steps_data),

        #2 TeV MC
        #base.sampleSpecification(sampleDict,"2_TeV_MC",   2000000,outputPrefix,steps_mc),

        #900 GeV data (test)
        #base.sampleSpecification(sampleDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
        #base.sampleSpecification(sampleDict,"2009_Data_v6", -1,outputPrefix,steps_data),

        #900 GeV data
        #base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),

        #900 GeV MC
        #base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
        base.sampleSpecification(sampleDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addExample(d) :
    outputPrefix="example"

    steps_data=listDict["jetKineSteps_data"]
    steps_mc  =listDict["jetKineSteps_mc"  ]

    specs=[
        base.sampleSpecification(sampleDict,"Example_Skimmed_900_GeV_Data",      -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"Example_Skimmed_900_GeV_MC",       500,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addJetAlgoComparison(d) :
    outputPrefix="jetAlgoComparison"

    steps_data=listDict["jetAlgoComparison_data"]
    steps_mc  =listDict["jetAlgoComparison_mc"  ]

    specs=[
        base.sampleSpecification(sampleDict,"Example_Skimmed_900_GeV_Data",      -1,outputPrefix,steps_data),
        base.sampleSpecification(sampleDict,"Example_Skimmed_900_GeV_MC",        -1,outputPrefix,steps_mc),
        ]

    d[outputPrefix]=specs

def addRA1_DiJet(d) :
    outputPrefix="RA1_DiJet"

    steps_data=listDict["RA1_DiJet_Steps_data"]
    steps_mc  =listDict["RA1_DiJet_Steps_mc"]

    xsDict={}

    sampleNames=[
        #"data"       ,
        "LM0"        ,
        "LM1"        ,
        #"MG_QCD_bin1",
        "MG_QCD_bin2",
        "MG_QCD_bin3",
        "MG_QCD_bin4",
        #"MG_TT_jets" ,
        #"MG_Z_jets"  ,
        #"MG_W_jets"  ,
        #"MG_Z_inv"   ,
        ]

    #pb
    xsDict["LM0"        ]=     110.00
    xsDict["LM1"        ]=      16.06
    xsDict["MG_QCD_bin1"]=15000000.0
    xsDict["MG_QCD_bin2"]=  400000.0
    xsDict["MG_QCD_bin3"]=   14000.0
    xsDict["MG_QCD_bin4"]=     370.0
    xsDict["MG_TT_jets" ]=     317
    xsDict["MG_Z_jets"  ]=    3700.0
    xsDict["MG_W_jets"  ]=   40000.0
    xsDict["MG_Z_inv"   ]=    2000.0

    nEventsEach=20000

    specs=[]
    for sampleName in sampleNames :
        specs.append(base.sampleSpecification(sampleDict,sampleName,nEventsEach,outputPrefix,steps_mc,xsDict[sampleName]))

    for spec in specs :
        spec.useSetBranchAddress=False
        spec.fileDirectory="dijet"
        spec.treeName="allData"

    d[outputPrefix]=specs

def addRA1_NJet(d) :
    outputPrefix="RA1_NJet"

    steps_data=listDict["RA1_NJet_Steps_data"]
    steps_mc  =listDict["RA1_NJet_Steps_mc"]

    xsDict={}

    sampleNames=[
        #"data"       ,
        "LM0"        ,
        "LM1"        ,
        #"MG_QCD_bin1",
        "MG_QCD_bin2",
        "MG_QCD_bin3",
        "MG_QCD_bin4",
        #"MG_TT_jets" ,
        #"MG_Z_jets"  ,
        #"MG_W_jets"  ,
        #"MG_Z_inv"   ,
        ]

    #pb
    xsDict["LM0"        ]=     110.00
    xsDict["LM1"        ]=      16.06
    xsDict["MG_QCD_bin1"]=15000000.0
    xsDict["MG_QCD_bin2"]=  400000.0
    xsDict["MG_QCD_bin3"]=   14000.0
    xsDict["MG_QCD_bin4"]=     370.0
    xsDict["MG_TT_jets" ]=     317
    xsDict["MG_Z_jets"  ]=    3700.0
    xsDict["MG_W_jets"  ]=   40000.0
    xsDict["MG_Z_inv"   ]=    2000.0

    nEventsEach=10000

    specs=[]
    for sampleName in sampleNames :
        specs.append(base.sampleSpecification(sampleDict,sampleName,nEventsEach,outputPrefix,steps_mc,xsDict[sampleName]))

    for spec in specs :
        spec.useSetBranchAddress=False
        spec.fileDirectory="dijet"
        spec.treeName="allData"

    d[outputPrefix]=specs

