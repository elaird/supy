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

