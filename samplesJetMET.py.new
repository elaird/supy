import samples

jetmet = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#NOV.4 RE-RECO SKIMS
dir = "/vols/cms02/elaird1/16_skims/"
jetmet.add("Nov4_MJ_skim",  'utils.fileListFromDisk(location = "%s/MultiJet.Run2010B-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,    lumi = 27.907) #/pb
jetmet.add("Nov4_J_skim",   'utils.fileListFromDisk(location = "%s/Jet.Run2010B-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,         lumi =  2.853) #/pb
jetmet.add("Nov4_J_skim2",  'utils.fileListFromDisk(location = "%s/Jet.Run2010B-Nov4ReReco_v1.RECO.Henning_*_skim.root", isDirectory = False)'%dir,      lumi =  2.181) #/pb
jetmet.add("Nov4_JM_skim",  'utils.fileListFromDisk(location = "%s/JetMET.Run2010A-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,      lumi =  2.895) #/pb
jetmet.add("Nov4_JMT_skim", 'utils.fileListFromDisk(location = "%s/JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,   lumi =  0.167) #/pb
jetmet.add("Nov4_JMT_skim2",'utils.fileListFromDisk(location = "%s/JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Henning_*_skim.root", isDirectory = False)'%dir,lumi =  0.117) #/pb

#NOV.4 RE-RECO ORIGINALS
jetmet.add("MultiJet.Run2010B-Nov4ReReco_v1.RECO.Burt", '%s/bbetchar//ICF/automated/2010_11_21_18_35_30/")'%srm, lumi = 27.907) #/pb
jetmet.add("Jet.Run2010B-Nov4ReReco_v1.RECO.Burt",      '%s/bbetchar//ICF/automated/2010_11_20_02_58_06/", alwaysUseLastAttempt = True)'%srm, lumi =  2.853) #/pb
jetmet.add("JetMET.Run2010A-Nov4ReReco_v1.RECO.Burt",   '%s/bbetchar//ICF/automated/2010_11_20_02_53_00/", alwaysUseLastAttempt = True)'%srm, lumi =  2.895) #/pb
jetmet.add("JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt",'%s/bbetchar//ICF/automated/2010_11_20_02_46_12/")'%srm, lumi =  0.167) #/pb

jetmet.add("Jet.Run2010B-Nov4ReReco_v1.RECO.Henning",      '%s/henning//ICF/automated/2010_12_03_19_00_17/")'%srm, lumi =  2.181)
jetmet.add("JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Henning",'%s/henning//ICF/automated/2010_12_06_10_21_14/")'%srm, lumi =  0.117)

#38X SKIMS
jetmet.add("Run2010B_MJ_skim5",
           'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt3/")', lumi=0.651)#/pb
jetmet.add("Run2010B_MJ_skim4",
           'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Robin/")', lumi=12.832)#/pb
jetmet.add("Run2010B_MJ_skim3",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/14_skims/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Bryn/")', lumi = 6.807) #/pb
jetmet.add("Run2010B_MJ_skim2",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/14_skims/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt2/")', lumi = 4.1508) #/pb
jetmet.add("Run2010B_MJ_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/14_skims/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt/")', lumi = 3.467) #/pb
jetmet.add("Run2010B_J_skim2",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/14_skims/Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt2/")', lumi = 0.5107) #/pb
jetmet.add("Run2010B_J_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt/")', lumi = 3.897) #/pb
jetmet.add("Run2010A_JM_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/JetMET.Run2010A-Sep17ReReco_v2.RECO.RAW.Burt/")', lumi = 2.889) #/pb
jetmet.add("Run2010A_JMT_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/JetMETTau.Run2010A-Sep17ReReco_v2.RECO.RAW.Henning/")', lumi = 0.172) #/pb

#38X ORIGINALS
jetmet.add("MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt3",    '%s/bbetchar//ICF/automated/2010_11_13_18_52_56/")'%srm,    lumi = 0.651) #/pb
jetmet.add("MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Robin",    '%s/rnandi//ICF/automated/2010_11_05_20_27_38/")'%srm,    lumi = 12.832) #/pb
jetmet.add("MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Bryn",     '%s/bm409//ICF/automated/2010_10_29_17_39_47/")'%srm,    lumi = 6.807) #/pb
jetmet.add("MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt2",    '%s/bbetchar//ICF/automated/2010_10_22_17_46_53/")'%srm, lumi = 4.1508 )
jetmet.add("MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Burt",     '%s/bbetchar//ICF/automated/2010_10_18_00_39_32/")'%srm, lumi = 3.467 )
jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt2",         '%s/bbetchar//ICF/automated/2010_10_18_00_34_11/")'%srm, lumi = 0.5107 )
jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt",          '%s/bbetchar//ICF/automated/2010_10_12_09_56_12/")'%srm, lumi = 3.897 )
jetmet.add("JetMET.Run2010A-Sep17ReReco_v2.RECO.RAW.Burt",      '%s/bbetchar//ICF/automated/2010_10_12_10_01_47/")'%srm, lumi = 2.889 )
jetmet.add("JetMETTau.Run2010A-Sep17ReReco_v2.RECO.RAW.Henning",'%s/henning//ICF/automated/2010_10_14_11_50_11/")'%srm,  lumi = 0.172 )

#TEST
jetmet.add("2010_data_calo_skim", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/22_hadronicLook/caloAK5_mix.root", isDirectory = False)', lumi = 34.724)
jetmet.add("2010_data_pf_skim", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/22_hadronicLook/pfAK5_mix.root", isDirectory = False)', lumi = 34.724)
jetmet.add("tanjas14", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/22_hadronicLook/tanjas14.root", isDirectory = False)', lumi = 34.724)
jetmet.add("markus38", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/25_markus38/markus38_0_skim.root", isDirectory = False)', lumi = 34.724)
jetmet.add("toms17", 'utils.fileListFromDisk(location=  "/vols/cms02/elaird1/11_skims/26_tom17/toms17_0_skim.root", isDirectory = False)', lumi = 34.724)
jetmet.add('hennings38','utils.fileListFromDisk(location = "/vols/cms02/bbetchar/thirtyEight/")', lumi = 35.38)
jetmet.add('markusVeto','utils.fileListFromDisk(location = "/home/hep/elaird1/48_markus_veto_events/v1/events.root", isDirectory = False)', lumi = 35.38)
jetmet.add("pfSkim_partialResCorr", 'utils.fileListFromDisk(location = "/home/hep/elaird1/pfSkim_partialResCorr_0_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("pfSkim_fullResCorr", 'utils.fileListFromDisk(location = "/home/hep/elaird1/pfSkim_fullResCorr_0_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("bryns15", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/tmp//eventSkim//config/*_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("hbheNoise_calo", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/31_hbheNoise/hbheNoise_calo_0_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("hbheNoise_pf", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/31_hbheNoise/hbheNoise_pf_0_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("markus5_old", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/32_markus5/old/markus5_old_0_skim.root", isDirectory = False)', lumi = 35.38)
jetmet.add("markus5_new", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/32_markus5/new/markus5_new_0_skim.root", isDirectory = False)', lumi = 35.38)#Burt's 4 ReReco samples
