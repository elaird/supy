def getCommandOutput2(command):
    import os
    child = os.popen(command)
    data = child.read()
    err = child.close()
    #if err: raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data
                        
class sampleDictionaryHolder :
    """sampleDictionaryHolder"""

    def __init__(self) :
        self.fileListDict={}#string mapped to [file1,file2,...]
        self.xsDict={}      #string mapped to xs (pb)
    
    def getFileListDictionary(self) :
        return self.fileListDict
    
    def getXsDictionary(self) :
        return self.xsDict
    
    def buildDictionaries(self) :
        #call all member functions starting with specialPrefix
        specialPrefix="add"
        for member in dir(self) :
            if member[:len(specialPrefix)]!=specialPrefix : continue
            getattr(self,member)()

    def add_met_pas_skims(self) :
        baseDir="/vols/cms02/elaird1/03_skims/cleaned/"

        subDirs=[
            "JetMETTau.Run2010A-May27thReReco_v1.RECO",
            "MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO",
            "MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO",
            "QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            "QCD_Pt-15_7TeV-pythia6.Spring10-START3X_V26B-v1.GEN-SIM-RECO",
            ]

        furtherSubDirs=["leading_uncorr_ak5CaloJet.gt.40"]
        
        for subDir in subDirs :
            self.fileListDict[subDir+"_cleanEvent"]=getCommandOutput2("ls "+baseDir+"/"+subDir+"/*.root").split()
            for furtherSubDir in furtherSubDirs :
                self.fileListDict[subDir+"."+furtherSubDir]=getCommandOutput2("ls "+baseDir+"/"+subDir+"/"+furtherSubDir+"/*.root").split()

    def add_Burt1(self) :
        prefix="dcap://gfe02.hep.ph.ic.ac.uk:22128"
        dir="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_08_03_27_37/"

        files=[
            prefix+"/"+dir+"/"+"SusyCAF_Tree_2_2.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_22_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_10_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_4_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_32_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_15_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_5_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_29_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_14_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_19_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_28_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_30_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_6_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_23_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_20_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_26_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_16_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_31_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_17_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_25_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_12_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_21_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_27_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_7_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_13_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_8_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_11_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_1_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_3_1.root",
            prefix+"/"+dir+"/"+"SusyCAF_Tree_9_1.root",
            ]

        self.fileListDict["JetMETTau.Run2010A-May27thReReco_v1.RECO"]=files
        return
    
    def add_Burt2(self) :
        prefix="dcap://gfe02.hep.ph.ic.ac.uk:22128"
        dir="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_08_04_00_40/"

        files=[
            prefix+"/"+dir+"/SusyCAF_Tree_18_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_8_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_6_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_27_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_40_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_15_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_45_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_28_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_24_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_2_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_55_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_26_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_14_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_21_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_65_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_61_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_20_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_33_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_68_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_31_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_32_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_9_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_30_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_44_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_4_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_66_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_51_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_13_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_10_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_11_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_23_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_60_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_12_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_35_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_56_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_52_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_25_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_54_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_69_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_38_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_53_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_22_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_36_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_49_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_1_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_58_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_67_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_59_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_3_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_37_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_34_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_39_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_19_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_41_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_48_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_47_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_64_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_7_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_43_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_17_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_62_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_63_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_5_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_46_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_50_1.root",
            ]

        self.fileListDict["MinimumBias.Commissioning10-May6thPDSkim2_SD_JetMETTau-v1.RECO"]=files
        return

    def add_Burt3(self) :
        prefix="dcap://gfe02.hep.ph.ic.ac.uk:22128"
        dir="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_08_03_44_12/"

        files=[
            prefix+"/"+dir+"/SusyCAF_Tree_9_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_58_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_31_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_38_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_20_1.root",
            #prefix+"/"+dir+"/SusyCAF_Tree_10_1.root",#not finished
            prefix+"/"+dir+"/SusyCAF_Tree_151_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_51_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_1_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_14_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_99_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_2_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_37_1.root",
            #prefix+"/"+dir+"/SusyCAF_Tree_28_1.root",#not finished
            prefix+"/"+dir+"/SusyCAF_Tree_154_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_8_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_30_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_13_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_95_1.root",
            #prefix+"/"+dir+"/SusyCAF_Tree_26_1.root",#not finished
            prefix+"/"+dir+"/SusyCAF_Tree_29_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_132_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_74_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_15_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_16_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_105_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_7_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_72_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_45_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_62_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_68_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_24_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_130_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_70_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_60_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_55_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_76_1.root",
            #prefix+"/"+dir+"/SusyCAF_Tree_56_2.root",#broken
            prefix+"/"+dir+"/SusyCAF_Tree_103_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_104_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_102_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_25_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_5_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_150_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_67_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_93_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_27_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_42_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_18_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_86_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_23_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_43_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_96_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_22_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_82_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_40_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_89_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_50_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_144_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_64_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_153_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_47_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_146_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_21_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_98_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_110_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_11_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_129_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_75_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_118_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_48_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_155_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_73_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_54_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_19_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_61_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_78_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_35_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_71_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_119_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_52_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_109_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_90_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_128_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_143_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_101_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_91_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_83_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_115_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_139_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_126_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_65_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_127_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_107_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_36_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_133_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_122_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_134_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_116_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_69_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_131_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_121_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_100_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_84_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_87_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_148_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_80_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_125_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_85_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_152_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_59_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_124_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_156_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_113_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_112_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_111_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_123_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_138_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_120_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_108_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_46_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_147_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_117_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_17_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_142_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_44_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_136_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_141_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_106_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_145_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_66_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_137_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_114_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_140_1.root",
            ]
        
        self.fileListDict["MinimumBias.Commissioning10-SD_JetMETTau-v9.RECO"]=files
        return

    def add_Burt4(self) :
        prefix="dcap://gfe02.hep.ph.ic.ac.uk:22128"
        dir="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/elaird//ICF/automated/2010_06_04_18_22_38/"

        files=[
            prefix+"/"+dir+"/SusyCAF_Tree_3_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_49_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_11_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_9_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_29_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_33_0.root",
            prefix+"/"+dir+"/SusyCAF_Tree_35_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_51_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_45_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_34_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_36_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_50_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_28_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_2_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_22_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_46_2.root",
            prefix+"/"+dir+"/SusyCAF_Tree_37_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_25_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_6_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_5_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_55_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_18_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_17_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_52_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_20_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_4_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_1_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_53_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_47_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_41_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_8_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_44_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_12_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_23_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_19_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_21_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_26_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_54_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_15_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_42_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_38_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_7_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_27_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_16_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_31_0.root",
            prefix+"/"+dir+"/SusyCAF_Tree_39_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_43_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_48_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_14_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_30_0.root",
            prefix+"/"+dir+"/SusyCAF_Tree_13_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_32_0.root",
            prefix+"/"+dir+"/SusyCAF_Tree_40_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_24_1.root",
            prefix+"/"+dir+"/SusyCAF_Tree_56_1.root",
            ]
        
        self.fileListDict["QCD_Pt-15_7TeV-pythia8.Spring10-START3X_V26B-v1.GEN-SIM-RECO"]=files
        return

    def add_Burt5(self) :
        prefix="dcap://gfe02.hep.ph.ic.ac.uk:22128"
        dir="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20/"
        files=[
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_3_2.root",
            "1187184130 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_17_2.root",
            "1188420629 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_37_3.root",
            "645399087 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_13_2.root",
            "1189025467 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_16_3.root",
            "1185401408 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_19_2.root",
            "1190250788 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_15_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_23_1.root",
            "1192505109 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_43_3.root",
            "1185930578 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_45_4.root",
            "1190634664 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_24_3.root",
            "1190793685 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_11_3.root",
            "1188110942 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_52_2.root",
            "1189104854 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_48_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_26_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_9_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_38_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_5_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_27_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_7_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_53_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_25_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_56_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_12_3.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_58_2.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_33_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_54_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_4_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_6_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_29_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_57_1.root",
            "0 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_35_2.root",
            "1190351962 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_46_2.root",
            "62632488 /pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bbetchar//ICF/automated/2010_06_12_02_55_20//SusyCAF_Tree_40_1.root",
            ]

        outFiles=[]
        for fileStuff in files :
            list=fileStuff.split()
            size=int(list[0])
            name=list[1]
            if size>0 :
                outFiles.append(prefix+name)
        
        self.fileListDict["QCD_Pt-15_7TeV.pythia6.Spring10-START3X_V26B-v1.GEN-SIM-RECO"]=outFiles
        return
    
    def add_Burt(self) :
        #self.fileListDict["Burt"]=getCommandOutput2('find /tmp/bbetchar/SusyCAF/2010_05_18_19_26_19/OUTPUT/ | grep .root').split()
        return

    def add_test(self) :
        #self.fileListDict["test"]=["~/public/susypvt/CMSSW_3_5_6/src/SusyCAF_Tree.root"]
        self.fileListDict["test"]=["/tmp/elaird/SusyCAF_Tree.root"]
        #self.fileListDict["test"]=["/tmp/elaird/CMSSW_3_5_7/src/SUSYBSMAnalysis/SusyCAF/SusyCAF_Tree.root"]
        #self.fileListDict["test"]=["~/public/susypvt/CMSSW_3_5_7/src/SUSYBSMAnalysis/SusyCAF/SusyCAF_Tree.root"]
    
    def add_LM_points(self) :
        baseDir="/data0/elaird/susyTree/07_susy_mc/"
        for name in ["LM0","LM1","LM2","PYTHIA6_QCDpt_1000_1400"] :
            self.fileListDict["GEN_"+name]=[baseDir+"/"+name+"_SusyCAF_Tree.root"]

        self.xsDict["GEN_LM0"                    ]=  110.00
        self.xsDict["GEN_LM1"                    ]=   16.06
        self.xsDict["GEN_LM2"                    ]=    2.42
        self.xsDict["GEN_PYTHIA6_QCDpt_1000_1400"]=10000.0
        
    
    def add_icfV7Ntuples(self) :
        baseDir="/data0/elaird/icfNtuple/nt7/"
        self.fileListDict["NT7_LM0"         ]=[baseDir+"LM0_229_PATV5_NT7.root"              ]
        self.fileListDict["NT7_LM1"         ]=[baseDir+"LM1_229_PATV5_NT7.root"              ]
        self.fileListDict["NT7_MG_QCD_bin1" ]=[baseDir+"QCD_MG_HT100to250_229_PATV5_NT7.root"]
        self.fileListDict["NT7_MG_QCD_bin2" ]=[baseDir+"MadQCD250to500_NT7.root"             ]
        self.fileListDict["NT7_MG_QCD_bin3" ]=[baseDir+"MadQCD500to1000_NT7.root"            ]
        self.fileListDict["NT7_MG_QCD_bin4" ]=[baseDir+"MadQCD1000toInf_NT7.root"            ]
        self.fileListDict["NT7_MG_TT_jets"  ]=[baseDir+"TTJets_madgraph_NT7.root"            ]
        self.fileListDict["NT7_MG_Z_jets"   ]=[baseDir+"ZJetsMG_229_PATV5_NT7.root"          ]
        self.fileListDict["NT7_MG_W_jets"   ]=[baseDir+"WJetsMG_229_PATV5_NT7.root"          ]
        self.fileListDict["NT7_MG_Z_inv"    ]=[baseDir+"ZtoInvMG_229_PATV5_NT7.root"         ]

        self.xsDict["NT7_LM0"        ]=     110.00
        self.xsDict["NT7_LM1"        ]=      16.06
        self.xsDict["NT7_MG_QCD_bin1"]=15000000.0
        self.xsDict["NT7_MG_QCD_bin2"]=  400000.0
        self.xsDict["NT7_MG_QCD_bin3"]=   14000.0
        self.xsDict["NT7_MG_QCD_bin4"]=     370.0
        self.xsDict["NT7_MG_TT_jets" ]=     317.0
        self.xsDict["NT7_MG_Z_jets"  ]=    3700.0
        self.xsDict["NT7_MG_W_jets"  ]=   40000.0
        self.xsDict["NT7_MG_Z_inv"   ]=    2000.0


    def add_icfV2Ntuples(self) :
        self.fileListDict["LM0"                ]=["/data1/elaird/susyTree/08_icf/LM0_7TeV_V00-08-04-04.root"   ]
        self.fileListDict["LM1"                ]=["/data1/elaird/susyTree/08_icf/LM1_7TeV_V00-08-04-04.root"   ]
        self.fileListDict["PY_QCD_bin3"        ]=["/data0/elaird/susyTree/08_icf/QCDJets_Pythia_80.root"       ]
        self.fileListDict["PY_QCD_bin4"        ]=["/data1/elaird/susyTree/08_icf/QCDJets_Pythia_170.root"      ]
        self.fileListDict["PY_QCD_bin5"        ]=["/data1/elaird/susyTree/08_icf/QCDJets_Pythia_300.root"      ]
        self.fileListDict["PY_QCD_bin6"        ]=["/data0/elaird/susyTree/08_icf/QCDJets_Pythia_470.root"      ]
        self.fileListDict["PY_QCD_bin7"        ]=["/data0/elaird/susyTree/08_icf/QCDJets_Pythia_800.root"      ]
        self.fileListDict["PY_QCD_bin8"        ]=["/data0/elaird/susyTree/08_icf/QCDJets_Pythia_1400.root"     ]
        self.fileListDict["TTbar_jets_madgraph"]=["/data0/elaird/susyTree/08_icf/TTbarJets-madgraph_ICFv2.root"]
        self.fileListDict["W_jets_madgraph"    ]=["/data0/elaird/susyTree/08_icf/WJets-madgraph_ICFv2.root"    ]
        self.fileListDict["Z_jets_madgraph"    ]=["/data0/elaird/susyTree/08_icf/ZJets-madgraph_ICFv2.root"    ]

        self.xsDict["LM0"         ]= 38.93
        self.xsDict["LM1"         ]=  4.888
        self.xsDict["PY_QCD_bin1" ]=8.762e+08
        self.xsDict["PY_QCD_bin2" ]=6.041e+07
        self.xsDict["PY_QCD_bin3" ]=9.238e+05
        self.xsDict["PY_QCD_bin4" ]=2.547e+04
        self.xsDict["PY_QCD_bin5" ]=1.256e+03
        self.xsDict["PY_QCD_bin6" ]=8.798e+01
        self.xsDict["PY_QCD_bin7" ]=2.186e+00
        self.xsDict["PY_QCD_bin8" ]=1.122e-02
        self.xsDict["TTbar_jets_madgraph"]=95
        self.xsDict["W_jets_madgraph"]=24170#NLO (17830 LO)
        self.xsDict["Z_jets_madgraph"]=2350#LO

    def add_icfV2Ntuples_may26skim(self) :
        someDir="/data0/elaird/susyTree/08_icf/may26skim/"
        labelList=["LM0",
                   "LM1",    
                   "PY_QCD_bin3",    
                   "PY_QCD_bin4",
                   "PY_QCD_bin5",
                   "PY_QCD_bin6",
                   "PY_QCD_bin7",
                   "PY_QCD_bin8",
                   "TTbar_jets_madgraph",
                   "W_jets_madgraph",
                   "Z_jets_madgraph",
                   ]
        for item in labelList :
            self.fileListDict[item+"_may26skim"]=[someDir+"/"+item+"_skim.root"]
            if item in ["PY_QCD_bin3","PY_QCD_bin4","PY_QCD_bin5"] :
                self.fileListDict[item+"_may26skim"]=[someDir+"/"+item+"_may22skim_skim.root"]

        self.xsDict["LM0_may26skim"                 ]=6.898
        self.xsDict["LM1_may26skim"                 ]=1.8679
        self.xsDict["PY_QCD_bin3_may26skim"         ]=0.576
        self.xsDict["PY_QCD_bin4_may26skim"         ]=0.20253
        self.xsDict["PY_QCD_bin5_may26skim"         ]=0.04119
        self.xsDict["PY_QCD_bin6_may26skim"         ]=0.005278
        self.xsDict["PY_QCD_bin7_may26skim"         ]=0.00039348
        self.xsDict["PY_QCD_bin8_may26skim"         ]=6.0588e-06
        self.xsDict["TTbar_jets_madgraph_may26skim" ]=0.854999
        self.xsDict["W_jets_madgraph_may26skim"     ]=14.5020
        self.xsDict["Z_jets_madgraph_may26skim"     ]=0.1081

#    def add_icfV2Ntuples_may8skim(self) :
#        someDir="/data1/elaird/misc/may8skim/"
#        labelList=["LM0",
#                   "LM1",    
#                   "PY_QCD_bin3",    
#                   "PY_QCD_bin4",
#                   "PY_QCD_bin5",
#                   "PY_QCD_bin6",
#                   "PY_QCD_bin7",
#                   "PY_QCD_bin8",
#                   "TTbar_jets_madgraph"
#                   ]
#        for item in labelList :
#            self.fileListDict[item+"_may8skim"]=[someDir+"/"+item+"_skim.root"]
#
#        self.xsDict["LM0_may8skim"                ]=350.47 /100.0
#        self.xsDict["LM1_may8skim"                ]=127.80 /100.0
#        self.xsDict["PY_QCD_bin3_may8skim"        ]=  0.00 /100.0
#        self.xsDict["PY_QCD_bin4_may8skim"        ]=  3.25 /100.0
#        self.xsDict["PY_QCD_bin5_may8skim"        ]=  0.77 /100.0
#        self.xsDict["PY_QCD_bin6_may8skim"        ]=  0.45 /100.0
#        self.xsDict["PY_QCD_bin7_may8skim"        ]=  0.02 /100.0
#        self.xsDict["PY_QCD_bin8_may8skim"        ]=  0.005/100.0  #just a guess (reported as 0.00)
#        self.xsDict["TTbar_jets_madgraph_may8skim"]= 10.63 /100.0

    def add_icfV2Ntuples_may22skim(self) :
        someDir="/data0/elaird/misc/may22skim/"
        labelList=["PY_QCD_bin3",    
                   "PY_QCD_bin4",
                   "PY_QCD_bin5",
                   ]
        for item in labelList :
            self.fileListDict[item+"_may22skim"]=[someDir+"/"+item+"_skim.root"]

        self.xsDict["PY_QCD_bin3_may22skim"]=9.238e+05 * 259161.0/3203440
        self.xsDict["PY_QCD_bin4_may22skim"]=2.547e+04 * 498233.0/3132800
        self.xsDict["PY_QCD_bin5_may22skim"]=1.256e+03 * 894898.0/3274202

    def add_mSugraScan(self) :
        #just tests
        #self.fileListDict["mSugraScan_TB3"]=["rfio:///castor/cern.ch/user/e/elaird/SusyCAF/automated/2010_05_14_jetmettausd_take1/SusyCAF_Tree_10_1.root"]
        #self.fileListDict["mSugraScan_TB3"]=["rfio:///castor/cern.ch/user/t/trommers/7TeV/V00-08-04-XX/TANB3/SusyCAF_Tree_10_1.root"]
        #self.fileListDict["mSugraScan_TB3"]=["/data0/elaird/susyTree/08_icf/mSugraScan/TB3/SusyCAF_Tree_10_1.root"]

        #relevant files
        #self.fileListDict["mSugraScan_TB10"]=["/data0/elaird/susyTree/08_icf/mSugraScan/mSugraScan_TB10_skim.root"]
        self.fileListDict["mSugraScan_TB10"]=["rfio:///castor/cern.ch/user/t/trommers/7TeV/V00-08-04-XX/TANB10/SusyCAF_Tree_TANB10.root"]

    def add_2010_Data_v1(self) :
        self.fileListDict["2010_Data_v1"]=["/data1/elaird/susyTree/09_susycaf/2010_04_24_23_38_50_TwoCaloJets_pt10.root"]
        self.xsDict["2010_Data_v1"]= 1.0e3 * 430613 #1 / 1 nb-1 (written in pb) * nEventsInFile
        
    def add_2010_Data_v2(self) :
        someDir="/data0/elaird/susyTree/09_susycaf/2010_05_14_jetmettausd_take1/"
        fileList=[]
        for i in range(1,86) :
            fileList.append(someDir+"SusyCAF_Tree_"+str(i)+"_1.root")

        fileList[fileList.index(someDir+"SusyCAF_Tree_70_1.root")]=someDir+"SusyCAF_Tree_70_2.root"
        self.fileListDict["2010_Data_v2"]=fileList

    def add_2010_MC_v1(self) :
        self.fileListDict["2010_MC_v1"]=["/data0/elaird/susyTree/09_susycaf/2010_04_26_02_57_56_Skims_TwoCaloJets_pt10.root"]

    def add_2009_Data_v7(self) :
        baseLocation0="/data0/elaird/susyTree/06_reprocessed_2009_data/"
        inputFiles=[]
        for i in range(1,97) :
            inputFiles.append(baseLocation0+"/05_v7/data_niklas/SusyCAF_Tree_"+str(i)+".root")
        self.fileListDict["2009_Data_v7"]=inputFiles

    def add_2009_Data_v6(self) :
        baseLocation0="/data0/elaird/susyTree/06_reprocessed_2009_data/"
        inputFiles=[]
        for i in range(1,69) :
            inputFiles.append(baseLocation0+"/04_hannes/dataAllMinBias/SusyCAF_Tree_numEvent100_"+str(i)+".root")
        self.fileListDict["2009_Data_v6"]=inputFiles
        self.fileListDict["2009_Data_v6_skimmed"]=[baseLocation0+"/04_hannes/dataAllMinBias/skim/v3-1/skim_runLsV3_l1_vertex_1jet.root"]
        self.fileListDict["2009_Data_v6_skimmed_ge2jet"]=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]

    def add_900_GeV_MC_v6(self) :
        baseLocation0="/data0/elaird/susyTree/06_reprocessed_2009_data/"
        inputFiles=[]
        for i in range(1,51) :
            inputFiles.append(baseLocation0+"/04_hannes/mcMinBias900GeV/SusyCAF_Tree_numEvent100_"+str(i)+".root")
        self.fileListDict["900_GeV_MC_v6"]=inputFiles
        self.fileListDict["900_GeV_MC_v6_skimmed"]=[baseLocation0+"/04_hannes/mcMinBias900GeV/skim/skim_l1_vertex_1jet.root"]
        self.fileListDict["900_GeV_MC_v6_skimmed_ge2jet"]=[baseLocation0+"/04_hannes/mcMinBias900GeV/skim/skim_l1_vertex_1jet_ge2jet.root"]

    def add_example_skimmed_900_GeV_Data(self) :
        inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]
        self.fileListDict["Example_Skimmed_900_GeV_Data"]=inputFiles

    def add_example_skimmed_900_GeV_MC(self) :
        inputFiles=["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]
        self.fileListDict["Example_Skimmed_900_GeV_MC"]=inputFiles
