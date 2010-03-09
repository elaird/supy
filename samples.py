baseLocation0="/data0/elaird/susyTree/06_reprocessed_2009_data/"
baseLocation1="/data1/elaird/susyTree/06_reprocessed_2009_data/"

def buildSampleDictionary() :
    d={}

    add_2009_Data_v6(d)

    add_2009_Data_v5(d)
    add_900_GeV_MC_v5(d)

    add_example_skimmed_900_GeV_Data(d)
    add_example_skimmed_900_GeV_MC(d)

    return d

def add_2009_Data_v6(d) :
    inputFiles=[]
    for i in range(1,69) :
        inputFiles.append(baseLocation0+"/04_hannes/dataAllMinBias/SusyCAF_Tree_numEvent100_"+str(i)+".root")
    d["2009_Data_v6"]=inputFiles
    d["2009_Data_v6_skimmed"]=[baseLocation0+"/04_hannes/dataAllMinBias/skim/skim_runLsV3_l1_vertex_1jet.root"]

def add_2009_Data_v5(d) :
    inputFiles=[]
    for i in range(1,29) :
        inputFiles.append(baseLocation1+"/03_hannes/dataAllMinBias/nTuple_"+str(i)+".root")
    d["2009_Data_v5"]=inputFiles

def add_900_GeV_MC_v5(d) :
    inputFiles=[]
    for i in range(1,104) :
        inputFiles.append(baseLocation1+"/03_hannes/mcMinBias900GeV/nTuple_"+str(i)+".root")
    d["900_GeV_MC_v5"]=inputFiles

def add_example_skimmed_900_GeV_Data(d) :
    inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]
    d["Example_Skimmed_900_GeV_Data"]=inputFiles

def add_example_skimmed_900_GeV_MC(d) :
    inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]
    d["Example_Skimmed_900_GeV_MC"]=inputFiles
