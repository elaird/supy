baseLocation0="/data0/elaird/susyTree/06_reprocessed_2009_data/"
baseLocation1="/data1/elaird/susyTree/06_reprocessed_2009_data/"

def buildSampleDictionary() :
    d={}

    add_2009_Data_v7(d)

    add_2009_Data_v6(d)
    add_900_GeV_MC_v6(d)
    
    add_2009_Data_v5(d)
    add_900_GeV_MC_v5(d)

    add_example_skimmed_900_GeV_Data(d)
    add_example_skimmed_900_GeV_MC(d)

    add_icfV7Ntuples(d)
    add_Burt(d)
    
    return d

def getCommandOutput2(command):
    import os
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data
                        
def add_Burt(d) :
    d["Burt"] = getCommandOutput2('find /tmp/bbetchar/SusyCAF/2010_05_18_19_26_19/OUTPUT/ | grep .root').split()


def add_icfV7Ntuples(d) :
    baseDir="/data0/elaird/icfNtuple/nt7/"
    d["LM0"         ]=[baseDir+"LM0_229_PATV5_NT7.root"              ]
    d["LM1"         ]=[baseDir+"LM1_229_PATV5_NT7.root"              ]
    d["MG_QCD_bin1" ]=[baseDir+"QCD_MG_HT100to250_229_PATV5_NT7.root"]
    d["MG_QCD_bin2" ]=[baseDir+"MadQCD250to500_NT7.root"             ]
    d["MG_QCD_bin3" ]=[baseDir+"MadQCD500to1000_NT7.root"            ]
    d["MG_QCD_bin4" ]=[baseDir+"MadQCD1000toInf_NT7.root"            ]
    d["MG_TT_jets"  ]=[baseDir+"TTJets_madgraph_NT7.root"            ]
    d["MG_Z_jets"   ]=[baseDir+"ZJetsMG_229_PATV5_NT7.root"          ]
    d["MG_W_jets"   ]=[baseDir+"WJetsMG_229_PATV5_NT7.root"          ]
    d["MG_Z_inv"    ]=[baseDir+"ZtoInvMG_229_PATV5_NT7.root"         ]

def add_2009_Data_v7(d) :
    inputFiles=[]
    for i in range(1,97) :
        inputFiles.append(baseLocation0+"/05_v7/data_niklas/SusyCAF_Tree_"+str(i)+".root")
    d["2009_Data_v7"]=inputFiles

def add_2009_Data_v6(d) :
    inputFiles=[]
    for i in range(1,69) :
        inputFiles.append(baseLocation0+"/04_hannes/dataAllMinBias/SusyCAF_Tree_numEvent100_"+str(i)+".root")
    d["2009_Data_v6"]=inputFiles
    d["2009_Data_v6_skimmed"]=[baseLocation0+"/04_hannes/dataAllMinBias/skim/v3-1/skim_runLsV3_l1_vertex_1jet.root"]
    d["2009_Data_v6_skimmed_ge2jet"]=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]

def add_2009_Data_v5(d) :
    inputFiles=[]
    for i in range(1,29) :
        inputFiles.append(baseLocation1+"/03_hannes/dataAllMinBias/nTuple_"+str(i)+".root")
    d["2009_Data_v5"]=inputFiles
    d["2009_Data_v5_skimmed"]=[baseLocation1+"/03_hannes/ted_skim/data_V00-05-00_V3-1_skim_runLsV3_l1_vertex_1jet.root"]

def add_900_GeV_MC_v6(d) :
    inputFiles=[]
    for i in range(1,51) :
        inputFiles.append(baseLocation0+"/04_hannes/mcMinBias900GeV/SusyCAF_Tree_numEvent100_"+str(i)+".root")
    d["900_GeV_MC_v6"]=inputFiles
    d["900_GeV_MC_v6_skimmed"]=[baseLocation0+"/04_hannes/mcMinBias900GeV/skim/skim_l1_vertex_1jet.root"]
    d["900_GeV_MC_v6_skimmed_ge2jet"]=[baseLocation0+"/04_hannes/mcMinBias900GeV/skim/skim_l1_vertex_1jet_ge2jet.root"]

def add_900_GeV_MC_v5(d) :
    inputFiles=[]
    for i in range(1,104) :
        inputFiles.append(baseLocation1+"/03_hannes/mcMinBias900GeV/nTuple_"+str(i)+".root")
    d["900_GeV_MC_v5"]=inputFiles
    d["900_GeV_MC_v5_skimmed"]=[baseLocation1+"/03_hannes/ted_skim/mc_V00-05-00_V3-1_skim_l1_vertex_1jet.root"]
    
def add_example_skimmed_900_GeV_Data(d) :
    inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]
    d["Example_Skimmed_900_GeV_Data"]=inputFiles

def add_example_skimmed_900_GeV_MC(d) :
    inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]
    d["Example_Skimmed_900_GeV_MC"]=inputFiles
