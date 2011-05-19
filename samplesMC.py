import samples
from configuration import srm
mc = samples.SampleHolder()

mgKFactor = 3048.0/2400.0 #Z+jets NNLO/LO

######## QCD ##########
mgQcdLoc = '/bbetchar//ICF/automated/2011_04_07_20_30_16/'
mgQcdDset = "QCD_TuneD6T_HT-%s_7TeV-madgraph.Spring11-PU_S1_START311_V1G1-v1.AODSIM"

mc.add("qcd_mg_ht_100_250",  '%s/%s/%s")'%(srm,mgQcdLoc,mgQcdDset%"100To250"), xs = {"LO":7e+06, "fakeNLO":7e+06*mgKFactor}["fakeNLO"])
mc.add("qcd_mg_ht_250_500",  '%s/%s/%s")'%(srm,mgQcdLoc,mgQcdDset%"250To500"), xs = {"LO":171e+03, "fakeNLO":171e+03*mgKFactor}["fakeNLO"])
mc.add("qcd_mg_ht_500_1000", '%s/%s/%s")'%(srm,mgQcdLoc,mgQcdDset%"500To1000"),xs = {"LO":5200, "fakeNLO":5200*mgKFactor}["fakeNLO"])
mc.add("qcd_mg_ht_1000_inf", '%s/%s/%s")'%(srm,mgQcdLoc,mgQcdDset%"1000"),     xs = {"LO":83, "fakeNLO":83*mgKFactor}["fakeNLO"])

py6Loc = '/bbetchar//ICF/automated/2011_04_07_19_50_45/'
py6Dset = "/QCD_Pt_%s_TuneZ2_7TeV_pythia6.Spring11-PU_S1_START311_V1G1-v1.AODSIM"

mc.add("qcd_py6_pt_15_30",     '%s/%s/%s")'%(srm,py6Loc,py6Dset%"15to30"),     xs = 8.159e+08)
mc.add("qcd_py6_pt_30_50",     '%s/%s/%s")'%(srm,py6Loc,py6Dset%"30to50"),     xs = 5.312e+07)
mc.add("qcd_py6_pt_50_80",     '%s/%s/%s")'%(srm,py6Loc,py6Dset%"50to80"),     xs = 6.359e+06)
mc.add("qcd_py6_pt_80_120",    '%s/%s/%s")'%(srm,py6Loc,py6Dset%"80to120"),    xs = 7.843e+05)
mc.add("qcd_py6_pt_120_170",   '%s/%s/%s")'%(srm,py6Loc,py6Dset%"120to170"),   xs = 1.151e+05)
mc.add("qcd_py6_pt_170_300",   '%s/%s/%s")'%(srm,py6Loc,py6Dset%"170to300"),   xs = 2.426e+04)
mc.add("qcd_py6_pt_300_470",   '%s/%s/%s")'%(srm,py6Loc,py6Dset%"300to470"),   xs = 1.168e+03)
mc.add("qcd_py6_pt_470_600",   '%s/%s/%s")'%(srm,py6Loc,py6Dset%"470to600"),   xs = 7.022e+01)
mc.add("qcd_py6_pt_600_800",   '%s/%s/%s")'%(srm,py6Loc,py6Dset%"600to800"),   xs = 1.555e+01)
mc.add("qcd_py6_pt_800_1000",  '%s/%s/%s")'%(srm,py6Loc,py6Dset%"800to1000"),  xs = 1.844e+00)
mc.add("qcd_py6_pt_1000_1400", '%s/%s/%s")'%(srm,py6Loc,py6Dset%"1000to1400"), xs = 3.321e-01)
mc.add("qcd_py6_pt_1400_1800", '%s/%s/%s")'%(srm,py6Loc,py6Dset%"1400to1800"), xs = 1.087e-02)
mc.add("qcd_py6_pt_1800",      '%s/%s/%s")'%(srm,py6Loc,py6Dset%"1800"),       xs = 3.575e-04)

######### TT / EWK ############
burt_ttbar = '/bbetchar//ICF/automated/2011_04_07_19_30_01/'
burt_ewk = '/bbetchar//ICF/automated/2011_04_07_19_40_51/'
spring11pu = "Spring11-PU_S1_START311_V1G1-v1.AODSIM"

#MG
mc.add("tt_tauola_mg",'%s%s/TTJets_TuneZ2_7TeV-madgraph-tauola.%s")'%(srm,burt_ttbar,spring11pu), xs = {"LO":121, "BurtGuessNLO":157.5}["BurtGuessNLO"])
mc.add("w_jets_mg",'%s%s/WJetsToLNu_TuneZ2_7TeV-madgraph-tauola.%s")'%(srm,burt_ewk,spring11pu), xs = {"LO":24640, "BurtGuessNNLO": 31924}["BurtGuessNNLO"])
mc.add("zinv_jets_mg",'%s/henning//ICF/automated/2011_04_13_12_16_30/")'%srm, xs = {"LO":4500.0,"fakeNLO":4500.0*mgKFactor}["fakeNLO"])

mc.add("dyll_jets_mg", '%s/gouskos//ICF/automated/2011_05_02_12_39_53/DYJetsToLL_TuneZ2_M-50_7TeV-madgraph-tauola.Spring11-PU_S1_START311_V1G1-v1.AODSIM ")'%srm,
       xs = {"LO":2321.0, "NNLO":3048}["NNLO"])

#PYTHIA
mc.add("tt_tauola_pythia",'%s%s/TT_TuneZ2_7TeV-pythia6-tauola.%s")'%(srm,burt_ttbar,spring11pu), xs = {"LO":94, "BurtGuessNLO":122}["BurtGuessNLO"])
mc.add("w_enu", '%s%s/WToENu_TuneZ2_7TeV-pythia6.%s)'%(srm,burt_ewk,spring11pu),            xs = {"LO": 7899, "BurtGuessNNLO": 10234}["BurtGuessNNLO"])
mc.add("w_munu", '%s%s/WToMuNu_TuneZ2_7TeV-pythia6.%s)'%(srm,burt_ewk,spring11pu),          xs = {"LO": 7899, "BurtGuessNNLO": 10234}["BurtGuessNNLO"])
mc.add("w_taunu", '%s%s/WToTauNu_TuneZ2_7TeV-pythia6-tauola.%s)'%(srm,burt_ewk,spring11pu), xs = {"LO": 7899, "BurtGuessNNLO": 10234}["BurtGuessNNLO"])
mc.add("z_nunu",  '%s/henning//ICF/automated/2011_04_15_10_55_57/")'%srm, xs = 4292)

##### G + jets #########
#MG
gJetMg = "/elaird//ICF/automated/2011_04_04_11_45_04/"
mc.add("g_jets_mg_ht_40_100",'%s/%s/GJets_TuneD6T_HT-40To100_7TeV-madgraph.Spring11-PU_S1_START311_V1G1-v1.AODSIM")'%(srm, gJetMg),
       xs = {"LO":23620, "fakeNLO":23620*mgKFactor}["fakeNLO"])
mc.add("g_jets_mg_ht_100_200",'%s/%s/GJets_TuneD6T_HT-100To200_7TeV-madgraph.Spring11-PU_S1_START311_V1G1-v1.AODSIM")'%(srm, gJetMg),
       xs = {"LO":3476, "fakeNLO":3476*mgKFactor}["fakeNLO"])
mc.add("g_jets_mg_ht_200_inf"   ,'%s/%s/GJets_TuneD6T_HT-200_7TeV-madgraph.Spring11-PU_S1_START311_V1G1-v1.AODSIM")'%(srm, gJetMg),
       xs = {"LO":485, "fakeNLO":485*mgKFactor}["fakeNLO"])

#PYTHIA
GPyLoc = "/dburton//ICF/automated/2011_04_15_14_36_55/"
GPyDset = "G_Pt_%s_TuneZ2_7TeV_pythia6.Spring11-PU_S1_START311_V1G1-v1.AODSIM"
mc.add("g_jets_py6_pt_0_15",      '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"0to15"),      xs = 8.420e+07)
mc.add("g_jets_py6_pt_15_30",     '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"15to30"),     xs = 1.717e+05)
mc.add("g_jets_py6_pt_30_50",     '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"30to50"),     xs = 1.669e+04)
mc.add("g_jets_py6_pt_50_80",     '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"50to80"),     xs = 2.722e+03)
mc.add("g_jets_py6_pt_80_120",    '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"80to120"),    xs = 4.472e+02)
mc.add("g_jets_py6_pt_120_170",   '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"120to170"),   xs = 8.417e+01)
mc.add("g_jets_py6_pt_170_300",   '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"170to300"),   xs = 2.264e+01)
mc.add("g_jets_py6_pt_300_470",   '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"300to470"),   xs = 1.493e+00)
mc.add("g_jets_py6_pt_470_800",   '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"470to800"),   xs = 1.323e-01)
mc.add("g_jets_py6_pt_800_1400",  '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"800to1400"),  xs = 3.481e-03)
mc.add("g_jets_py6_pt_1400_1800", '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"1400to1800"), xs = 1.270e-05)
mc.add("g_jets_py6_pt_1800_inf",  '%s/%s/%s")'%(srm,GPyLoc,GPyDset%"1800"),       xs = 2.936e-07)

##### SUSY LM  ##########
lmDir = "/henning//ICF/automated/2011_04_12_14_13_06/"
lmTag = "_SUSY_sftsht_7TeV-pythia6.Spring11-PU_S1_START311_V1G1-v1.AODSIM"
mc.add("lm0" ,'%s/%s/LM0%s")' %(srm, lmDir, lmTag), xs = 38.93  )
mc.add("lm1" ,'%s/%s/LM1%s")' %(srm, lmDir, lmTag), xs = 4.888  )
mc.add("lm2" ,'%s/%s/LM2%s")' %(srm, lmDir, lmTag), xs = 0.6027 )
mc.add("lm3" ,'%s/%s/LM3%s")' %(srm, lmDir, lmTag), xs = 3.438  )
mc.add("lm4" ,'%s/%s/LM4%s")' %(srm, lmDir, lmTag), xs = 1.879  )
mc.add("lm5" ,'%s/%s/LM5%s")' %(srm, lmDir, lmTag), xs = 0.4734 )
mc.add("lm6" ,'%s/%s/LM6%s")' %(srm, lmDir, lmTag), xs = 0.3104 )
mc.add("lm7" ,'%s/%s/LM7%s")' %(srm, lmDir, lmTag), xs = 1.209  )
mc.add("lm8" ,'%s/%s/LM8%s")' %(srm, lmDir, lmTag), xs = 0.7300 )
mc.add("lm9" ,'%s/%s/LM9%s")' %(srm, lmDir, lmTag), xs = 7.134  )
mc.add("lm11",'%s/%s/LM11%s")'%(srm, lmDir, lmTag), xs = 0.8236 )
mc.add("lm12",'%s/%s/LM12%s")'%(srm, lmDir, lmTag), xs = 4.414  )
mc.add("lm13",'%s/%s/LM13%s")'%(srm, lmDir, lmTag), xs = 6.899  )

#SMS
mc.add("t1", '%s/bbetchar/ICF/automated/2011_01_24_18_09_42/")'%srm, lumi = 1.0) #dummy xs
mc.add("t11",'%s/bainbrid//ICF/automated/2011_03_09_08_57_50/")'%srm, lumi = 1.0) #dummy xs
mc.add("t2", '%s/elaird/ICF/automated/2011_03_08_23_04_26/")'%srm, lumi = 1.0) #dummy xs
mc.add("t21",'%s/bainbrid//ICF/automated/2011_03_08_20_30_30/")'%srm, lumi = 1.0) #dummy xs
mc.add("t3", '%s/bbetchar/ICF/automated/2011_01_25_21_33_22/")'%srm, lumi = 1.0) #dummy xs
mc.add("t4", '%s/henning/ICF/automated/2011_01_27_12_39_13/")'%srm, lumi = 1.0) #dummy xs

#MSUGRA SCANS
mc.add("scan_tanbeta3_tanja1",'%s/trommers//ICF/automated/2010_12_03_15_28_38/")'%srm, xs = 100000.0 ) #dummy xs
mc.add("scan_tanbeta3_tanja2",'%s/trommers//ICF/automated/2010_12_17_20_09_06/")'%srm, xs = 100000.0 ) #dummy xs
mc.add("scan_tanbeta10",('%s/trommers//ICF/automated/2011_02_24_16_41_52/")'%srm).replace("user","user_old"), xs = 1.0) #fake xs
dead = str(["_43_1_vfJ", "_109_1_K7V", "_648_1_SNq", "_19_1_P2A", '_106_1_5y9', '_107_1_xWu', '_116_1_GYJ', '_157_1_P2J', '_163_1_zG0', '_171_1_mkQ', '_173_1_gew', '_177_1_8Ew', '_191_1_Kdf', '_226_1_21E', '_266_1_ygR', '_295_1_BNB', '_311_1_Thz', '_319_1_UoK', '_328_2_Pn2', '_333_1_6tK', '_369_1_NG4', '_378_1_Nhp', '_413_1_IrU', '_42_1_h0i', '_446_1_5vP', '_449_1_a7D', '_487_1_VjZ', '_509_1_SiQ', '_547_1_hG9', '_559_1_Jjs', '_579_1_GaN', '_599_1_7Fs', '_644_1_1Zq', '_67_1_glp']).replace("'",'"')
mc.add("scan_tanbeta3_burt1", '%s/bbetchar//ICF/automated/2010_11_10_19_34_17/", itemsToSkip = %s)'%(srm, dead), xs = 100000.0 ) #dummy xs
mc.add("scan_tanbeta3_skim200", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/33_m12_200/")', xs = 1.0 ) #dummy xs
mc.add("scan_tanbeta3_skim100", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/34_m12_100/")', xs = 1.0 ) #dummy xs
