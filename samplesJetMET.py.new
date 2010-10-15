import samples

jetmet = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#38X SKIMS
jetmet.add("Run2010B_J_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt/")', lumi = 3.897) #/pb
jetmet.add("Run2010A_JM_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/JetMET.Run2010A-Sep17ReReco_v2.RECO.RAW.Burt/")', lumi = 2.889) #/pb
jetmet.add("Run2010A_JMT_skim",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/12_skims/JetMETTau.Run2010A-Sep17ReReco_v2.RECO.RAW.Henning/")', lumi = 0.172) #/pb

#deprecated; use the above instead
#jetmet.add("Run2010B_J_skim1",
#           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/10_skims/Jet.Run2010B-PromptReco-v2.RECO.Burt/")', lumi = 1.372) #/pb
#jetmet.add("Run2010B_J_skim2",
#           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/10_skims/Jet.Run2010B-PromptReco-v2.RECO.Burt2/")', lumi = 2.246) #/pb
#jetmet.add("Run2010A_JM_skim",
#           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/10_skims/JetMET.Run2010A-Sep17ReReco_v2.RECO.Burt/")', lumi = 2.889) #/pb
#jetmet.add("Run2010A_JMT_skim",
#           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/10_skims/JetMETTau.Run2010A-Sep17ReReco_v2.RECO.Burt/")', lumi = 0.172) #/pb

#38X ORIGINALS
jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.RAW.Burt",          '%s/bbetchar//ICF/automated/2010_10_12_09_56_12/")'%srm, lumi = 99999.9 )
jetmet.add("JetMET.Run2010A-Sep17ReReco_v2.RECO.RAW.Burt",      '%s/bbetchar//ICF/automated/2010_10_12_10_01_47/")'%srm, lumi = 99999.9 )
jetmet.add("JetMETTau.Run2010A-Sep17ReReco_v2.RECO.RAW.Henning",'%s/henning//ICF/automated/2010_10_14_11_50_11/")'%srm,  lumi = 99999.9 )

#deprecated; use the above instead
#jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.Burt",          '%s/bbetchar//ICF/automated/2010_10_05_22_57_38/")'%srm, lumi = 99999.9 )
#jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.Burt2",         '%s/bbetchar//ICF/automated/2010_10_08_18_56_52/")'%srm, lumi = 99999.9 )
#jetmet.add("JetMET.Run2010A-Sep17ReReco_v2.RECO.Burt",      '%s/bbetchar//ICF/automated/2010_10_05_23_25_55/", alwaysUseLastAttempt = True)'%srm, lumi = 99999.9 )
#jetmet.add("JetMETTau.Run2010A-Sep17ReReco_v2.RECO.Burt",   '%s/bbetchar//ICF/automated/2010_10_05_23_30_00/", alwaysUseLastAttempt = True)'%srm, lumi = 99999.9 )

#36X SKIM
jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 2.601 ) #/pb

#TEST
jetmet.add("JetMET_test_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/03_jetmet/")', lumi = 2.601 ) #/pb
jetmet.add("JetMET_test_skim2", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/04_38_recipe/")', lumi = 2.601 ) #/pb
jetmet.add("test", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/tmp//hadronicLook/defaultMht_pythia6_ge2_caloAK5/config00/Run2010B_skim_*_skim.root", isDirectory = False)', lumi = 1.372 ) #/pb
jetmet.add("2010_data_skim_calo",'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/06_highAlphaT/2010_data_skim_calo.root", isDirectory = False)', lumi = 6.68 )
jetmet.add("2010_data_skim_pf",  'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/06_highAlphaT/2010_data_skim_pf.root", isDirectory = False)', lumi = 6.68 )
#jetmet.add("Bryn_request",'eval(utils.getCommandOutput2("cat /home/hep/elaird1/ForTed.txt"))', lumi = 9999999.9)
jetmet.add("2010_data_photons_high_met",  'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/08_photons_high_met/")', lumi = 6.68 )
jetmet.add("Tanja_sync",
           'utils.fileListFromDisk(location = "/vols/cms02/elaird1/10_skims/Jet.Run2010B-PromptReco-v2.RECO.Burt2/Jet.Run2010B-PromptReco-v2.RECO.Burt2_[6-9]_skim.root", isDirectory = False)', lumi = 9999999.9) #/pb
