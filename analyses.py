import base,copy

class analysisDictionaryHolder :
    """analysisDictionaryHolder"""

    def __init__(self,fileListDict,xsDict,listDict) :
        self.fileListDict=fileListDict
        self.xsDict=xsDict
        self.listDict=listDict
        self.analysisDict={}
    
    def getDictionary(self) :
        return self.analysisDict
    
    def buildDictionary(self) :
        #call all member functions starting with specialPrefix
        specialPrefix="add"
        for member in dir(self) :
            if member[:len(specialPrefix)]!=specialPrefix : continue
            getattr(self,member)()

    def splitUpSpecs(self,inListOfSpecs) :
        outListOfSpecs=[]
        for spec in inListOfSpecs :
            fileIndex=0
            for iFileName in range(len(self.fileListDict[spec.name])) :
                suffix="_"+str(iFileName)
                newName=spec.name+suffix
                if newName in self.fileListDict :
                    raise NameError(newName," already in fileListDict")
                self.fileListDict[newName]=[self.fileListDict[spec.name][iFileName]]
                outListOfSpecs.append(base.sampleSpecification(self.fileListDict,
                                                               newName,
                                                               spec.nEvents,
                                                               spec.outputPrefix,
                                                               copy.deepcopy(spec.steps),
                                                               spec.xs
                                                               )
                                      )
                outListOfSpecs[-1].doSplitMode(spec.name)
                
        return outListOfSpecs

    def addMetPasSkim1(self) :
        outputPrefix="MetPasSkim1"

        subDirsData=[
            "JetMETTau.Run2010A-May27thReReco_v1.RECO",
            "MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO",
            "MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO",
            ]

        subDirsMc=[
            #"QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            "QCD_Pt-15_7TeV-pythia6.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            ]

        #jetType=""
        #jetType="PF"
        jetType="JPT"
        nEvents=-1
        specs=[]

        #for subDir in subDirsData :
        #    specs.append( base.sampleSpecification(self.fileListDict,subDir+"_cleanEvent",nEvents,outputPrefix,self.listDict["metPasFilterJet1"+jetType+"_data"]) )

        #for subDir in subDirsMc :
        #    specs.append( base.sampleSpecification(self.fileListDict,subDir+"_cleanEvent",nEvents,outputPrefix,self.listDict["metPasFilterJet1"+jetType+"_mc"]) )
        #specs.append( base.sampleSpecification(self.fileListDict,"QcdSkim",nEvents,outputPrefix,self.listDict["metPasFilterJet1"+jetType+"_data"]) )
        #specs.append( base.sampleSpecification(self.fileListDict,"PYQCD_HLTJet",nEvents,outputPrefix,self.listDict["metPasFilterJet1"+jetType+"_mc"]) )
        #specs.append( base.sampleSpecification(self.fileListDict,"361_v12_11_jetmet_v9_skim",nEvents,outputPrefix,self.listDict["metPasFilterJet1"+jetType+"_mc"]) )
        #self.analysisDict[outputPrefix]=specs
        self.analysisDict[outputPrefix]=self.splitUpSpecs(specs)
        
    def addMetPasSkim2(self) :
        outputPrefix="MetPasSkim2"

        subDirsData=[
            "JetMETTau.Run2010A-May27thReReco_v1.RECO",
            "MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO",
            "MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO",
            ]

        subDirsMc=[
            #"QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            "QCD_Pt-15_7TeV-pythia6.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            ]

        #jetType=""
        #jetType="PF"
        jetType="JPT"
        nEvents=-1
        specs=[]

        #for subDir in subDirsData :
        #    specs.append( base.sampleSpecification(self.fileListDict,subDir+"_cleanEvent",nEvents,outputPrefix,self.listDict["metPasFilterJet2"+jetType+"_data"]) )

        for subDir in subDirsMc :
            specs.append( base.sampleSpecification(self.fileListDict,subDir+"_cleanEvent",nEvents,outputPrefix,self.listDict["metPasFilterJet2"+jetType+"_mc"]) )

        #self.analysisDict[outputPrefix]=specs
        self.analysisDict[outputPrefix]=self.splitUpSpecs(specs)
        
    def addMetPasSkim(self) :
        outputPrefix="MetPasSkim"
        nEvents=-1
        specs=[
            #base.sampleSpecification(self.fileListDict,"361_v12_11_jetmet_v9",nEvents,outputPrefix,self.listDict["metPasFilter_data"]),
            #base.sampleSpecification(self.fileListDict,"JetMETTau.Run2010A-May27thReReco_v1.RECO",nEvents,outputPrefix,self.listDict["metPasFilter_data"]),
            #base.sampleSpecification(self.fileListDict,"MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO",nEvents,outputPrefix,self.listDict["metPasFilter_data"]),
            #base.sampleSpecification(self.fileListDict,"MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO",nEvents,outputPrefix,self.listDict["metPasFilter_data"]),
            #base.sampleSpecification(self.fileListDict,"QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO",nEvents,outputPrefix,self.listDict["metPasFilter_mc"]),
            base.sampleSpecification(self.fileListDict,"QCD_Pt-15_7TeV.pythia6.Spring10-START3X_V26B-v1.GEN-SIM-RECO",nEvents,outputPrefix,self.listDict["metPasFilter_mc"]),
            ]
        #self.analysisDict[outputPrefix]=specs
        self.analysisDict[outputPrefix]=self.splitUpSpecs(specs)
        #print self.splitUpSpecs(specs)
        
    def addMetPasSpeedTest(self) :
        outputPrefix="MetPasSpeedTest"

        dataDirs=["JetMETTau.Run2010A-May27thReReco_v1.RECO","MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO",
                  "MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO"]
        mcDirs=["QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO"]

        #dataDirs=[]
        #mcDirs=[]
        
        nEvents=-1
        specs=[]

        for dir in dataDirs :
            specs.append( base.sampleSpecification(self.fileListDict,dir+".leading_uncorr_ak5CaloJet.gt.40",nEvents,outputPrefix,self.listDict["metPasSpeedTest_data"]) )
        for dir in mcDirs :
            specs.append( base.sampleSpecification(self.fileListDict,dir+".leading_uncorr_ak5CaloJet.gt.40",nEvents,outputPrefix,self.listDict["metPasSpeedTest_mc"]) )
            
        self.analysisDict[outputPrefix]=specs
        #self.analysisDict[outputPrefix]=self.splitUpSpecs(specs)
        
    def addRecHitTest(self) :
        outputPrefix="RecHitTest"
        nEvents=-1
        specs=[
            base.sampleSpecification(self.fileListDict,"test",nEvents,outputPrefix,self.listDict["RecHitTestSteps"]),
            ]
        self.analysisDict[outputPrefix]=specs
    
    def addHcalTechTriggerCheck(self) :
        outputPrefix="HcalTechTriggerCheck"
        nEvents=10000
        specs=[
            base.sampleSpecification(self.fileListDict,"2010_Data_v2",nEvents,outputPrefix,self.listDict["HcalTechTriggerCheckSteps"]),
            ]
        self.analysisDict[outputPrefix]=specs

    def addMSugraLook(self) :
        outputPrefix="mSugraLook"
        nEvents=-1
        specs=[
            base.sampleSpecification(self.fileListDict,"mSugraScan_TB10",nEvents,outputPrefix,self.listDict["mSugraLookSteps"]),
            ]
        self.analysisDict[outputPrefix]=specs
    
    def addTriggerSkim(self) :
        outputPrefix="triggerSkim"

        steps_data=self.listDict["triggerSkimSteps_data"]
        steps_mc  =self.listDict["triggerSkimSteps_mc"  ]

        specs=[
            base.sampleSpecification(self.fileListDict,"2009_Data_v7", -1,outputPrefix,steps_data),
            
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6", -1,outputPrefix,steps_mc),
            
            #base.sampleSpecification(self.fileListDict,"2009_Data_v5", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v5", -1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addMetGroupCleanupLook(self) :
        outputPrefix="metGroupCleanupLook"

        steps_data=self.listDict["metGroupCleanupLookSteps_data"]
        steps_mc  =self.listDict["metGroupCleanupLookSteps_mc"  ]

        specs=[
            #900 GeV data
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
            base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),
            
            #900 GeV MC
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addMetDistLook(self) :
        outputPrefix="metDistLook"

        steps_data=self.listDict["metDistSteps_data"]
        steps_mc  =self.listDict["metDistSteps_mc"  ]

        specs=[
            ##900 GeV data
            ##base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),
            #
            ##900 GeV MC
            ##base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
            
            #2010 data
            base.sampleSpecification(self.fileListDict,"2010_Data_v1",-1,outputPrefix,steps_data),
            
            #7TeV min-bias MC
            base.sampleSpecification(self.fileListDict,"2010_MC_v1",-1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addDeltaPhiLook(self) :
        outputPrefix="deltaPhiLook"

        steps_data=self.listDict["deltaPhiSteps_data"]
        steps_mc  =self.listDict["deltaPhiSteps_mc"  ]

        specs=[
            #2 TeV data
            #base.sampleSpecification(self.fileListDict,"2_TeV_Data",      -1,outputPrefix,steps_data),
            
            #2 TeV MC
            #base.sampleSpecification(self.fileListDict,"2_TeV_MC",   2000000,outputPrefix,steps_mc),
            
            #900 GeV data (test)
            #base.sampleSpecification(self.fileListDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6", -1,outputPrefix,steps_data),
            
            #900 GeV data
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
            base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),
            
            #900 GeV MC
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
            base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addJetKineLook(self) :
        outputPrefix="jetKineLook"

        steps_data=self.listDict["jetKineSteps_data"]
        steps_mc  =self.listDict["jetKineSteps_mc"  ]
        
        specs=[
            #2 TeV data
            #base.sampleSpecification(self.fileListDict,"2_TeV_Data",      -1,outputPrefix,steps_data),
            
            #2 TeV MC
            #base.sampleSpecification(self.fileListDict,"2_TeV_MC",   2000000,outputPrefix,steps_mc),
            
            #900 GeV data (test)
            #base.sampleSpecification(self.fileListDict,"2009_Data_v5_skimmed", -1,outputPrefix,steps_data),
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6", -1,outputPrefix,steps_data),
            
            #900 GeV data
            #base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed", -1,outputPrefix,steps_data),
            base.sampleSpecification(self.fileListDict,"2009_Data_v6_skimmed_ge2jet", -1,outputPrefix,steps_data),
            
            #900 GeV MC
            #base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed",   -1,outputPrefix,steps_mc),
            base.sampleSpecification(self.fileListDict,"900_GeV_MC_v6_skimmed_ge2jet",-1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addExample(self) :
        outputPrefix="example"

        steps_data=self.listDict["jetKineSteps_data"]
        steps_mc  =self.listDict["jetKineSteps_mc"  ]

        specs=[
            base.sampleSpecification(self.fileListDict,"Example_Skimmed_900_GeV_Data",      -1,outputPrefix,steps_data),
            base.sampleSpecification(self.fileListDict,"Example_Skimmed_900_GeV_MC",       100,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addJetAlgoComparison(self) :
        outputPrefix="jetAlgoComparison"
        
        steps_data=self.listDict["jetAlgoComparison_data"]
        steps_mc  =self.listDict["jetAlgoComparison_mc"  ]
        
        specs=[
            base.sampleSpecification(self.fileListDict,"Example_Skimmed_900_GeV_Data",      -1,outputPrefix,steps_data),
            base.sampleSpecification(self.fileListDict,"Example_Skimmed_900_GeV_MC",        -1,outputPrefix,steps_mc),
            ]
        self.analysisDict[outputPrefix]=specs

    def addIcfRa1_DiJet(self) :
        outputPrefix="Icf_Ra1_DiJet"

        steps_data=self.listDict["Icf_Ra1_DiJet_Steps_data"]
        steps_mc  =self.listDict["Icf_Ra1_DiJet_Steps_mc"]

        sampleNames=[
            #"data"       ,
            "NT7_LM0"        ,
            #"NT7_LM1"        ,
            ##"NT7_MG_QCD_bin1",
            #"NT7_MG_QCD_bin2",
            "NT7_MG_QCD_bin3",
            #"NT7_MG_QCD_bin4",
            #"NT7_MG_TT_jets" ,
            #"NT7_MG_Z_jets"  ,
            #"NT7_MG_W_jets"  ,
            #"NT7_MG_Z_inv"   ,
            ]
        
        nEventsBase=10000

        nEventsDict={}
        nEventsDict["NT7_LM0"        ]=nEventsBase
        nEventsDict["NT7_LM1"        ]=nEventsBase
        nEventsDict["NT7_MG_QCD_bin1"]=nEventsBase
        nEventsDict["NT7_MG_QCD_bin2"]=nEventsBase*3
        nEventsDict["NT7_MG_QCD_bin3"]=nEventsBase*3
        nEventsDict["NT7_MG_QCD_bin4"]=nEventsBase
        nEventsDict["NT7_MG_TT_jets" ]=nEventsBase
        nEventsDict["NT7_MG_W_jets"  ]=nEventsBase*50
        nEventsDict["NT7_MG_Z_jets"  ]=nEventsBase*50
        nEventsDict["NT7_MG_Z_inv"   ]=nEventsBase*5
        
        specs=[]
        for sampleName in sampleNames :
            specs.append(base.sampleSpecification(self.fileListDict,sampleName,nEventsDict[sampleName],outputPrefix,steps_mc,self.xsDict[sampleName]))

        for spec in specs :
            spec.fileDirectory="dijet"
            spec.treeName="allData"

        self.analysisDict[outputPrefix]=specs

    def addIcfRa1_NJet(self) :
        outputPrefix="Icf_Ra1_NJet"

        steps_data=self.listDict["Icf_Ra1_NJet_Steps_data"]
        steps_mc  =self.listDict["Icf_Ra1_NJet_Steps_mc"]

        sampleNames=[
            #"data"       ,
            "NT7_LM0"        ,
            "NT7_LM1"        ,
            "NT7_MG_QCD_bin1",
            "NT7_MG_QCD_bin2",
            "NT7_MG_QCD_bin3",
            "NT7_MG_QCD_bin4",
            "NT7_MG_TT_jets" ,
            "NT7_MG_W_jets"  ,
            "NT7_MG_Z_jets"  ,
            "NT7_MG_Z_inv"   ,
            ]

        nEventsBase=20000

        nEventsDict={}
        nEventsDict["NT7_LM0"        ]=nEventsBase
        nEventsDict["NT7_LM1"        ]=nEventsBase
        nEventsDict["NT7_MG_QCD_bin1"]=nEventsBase
        nEventsDict["NT7_MG_QCD_bin2"]=nEventsBase*3
        nEventsDict["NT7_MG_QCD_bin3"]=nEventsBase*3
        nEventsDict["NT7_MG_QCD_bin4"]=nEventsBase
        nEventsDict["NT7_MG_TT_jets" ]=nEventsBase
        nEventsDict["NT7_MG_W_jets"  ]=nEventsBase*50
        nEventsDict["NT7_MG_Z_jets"  ]=nEventsBase*50
        nEventsDict["NT7_MG_Z_inv"   ]=nEventsBase*5

        specs=[]
        for sampleName in sampleNames :
            specs.append(base.sampleSpecification(self.fileListDict,sampleName,nEventsDict[sampleName],outputPrefix,steps_mc,self.xsDict[sampleName]))

        for spec in specs :
            spec.fileDirectory="dijet"
            spec.treeName="allData"

        self.analysisDict[outputPrefix]=specs

#    def addRa1Gen_NJet(self) :
#        outputPrefix="Ra1_NJet"
#    
#        steps_data=self.listDict["Ra1_NJet_Steps_data"]
#        steps_mc  =self.listDict["Ra1_NJet_Steps_mc"  ]
#
#        sampleNames=[
#            #"data"       ,
#            "LM0"        ,
#            "LM1"        ,
#            #"LM2"        ,
#            #"PYTHIA6_QCDpt_1000_1400",
#            ]
#
#        nEventsBase=-1
#
#        nEventsDict={}
#        nEventsDict["LM0"                    ]=nEventsBase
#        nEventsDict["LM1"                    ]=nEventsBase
#        nEventsDict["LM2"                    ]=nEventsBase
#        nEventsDict["PYTHIA6_QCDpt_1000_1400"]=nEventsBase
#    
#        specs=[]
#        for sampleName in sampleNames :
#            specs.append(base.sampleSpecification(self.fileListDict,sampleName,nEventsDict[sampleName],outputPrefix,steps_mc,self.xsDict[sampleName]))
#
#        self.analysisDict[outputPrefix]=specs

