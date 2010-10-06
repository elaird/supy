import samples

jetmet = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#DATA SKIM
jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 2.601 ) #/pb
#jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 1.068+0.223 ) #/pb (old lumi value)
#jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 1.068 ) #/pb (old lumi value)
#jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 0.8267 ) #/pb (old lumi value)
#jetmet.add("JetMET.Run2010A", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 0.293 ) #/pb (old lumi value)
#jetmet.add("JetMETTau.Run2010A_old", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data1/")', lumi = 0.012+0.120+0.1235 ) #/pb

#ORIGINALS
#36X
jetmet.add("MinimumBias.Commissioning10-SD_JetMETTau-Jun14thSkim_v1.RECO.Bryn", '%s/bm409/ICF/automated/2010_07_06_22_18_07/")'%srm, lumi = 999999.9 )
jetmet.add("JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", '%s/bm409//ICF/automated/2010_07_20_16_52_06/")'%srm,   lumi = 0.012 )
jetmet.add("JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", '%s/bm409//ICF/automated/2010_07_20_17_20_35/")'%srm,   lumi = 0.120 )
jetmet.add("JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn",    '%s/bm409//ICF/automated/2010_07_20_15_40_06/")'%srm,   lumi = 0.1235)
jetmet.add("JetMETTau.Run2010A-PromptReco-v4.RECO.Loukas",  '%s/gouskos//ICF/automated/2010_08_05_01_38_58/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Loukas",     '%s/gouskos//ICF/automated/2010_08_05_01_56_12/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Martyn",     '%s/mjarvis//ICF/automated/2010_08_13_15_36_08/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Bryn",       '%s/bm409//ICF/automated/2010_08_21_18_15_19/")'%srm,   lumi = 0.2416 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Bryn2",      '%s/bm409//ICF/automated/2010_08_25_22_01_16/")'%srm,   lumi = 0.223 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Alex",       '%s/as1604//ICF/automated/2010_09_04_22_37_49/")'%srm,  lumi = 999999.9 )
#jetmet.add("Bryn.test.data", 'utils.getCommandOutput2("cat /home/hep/elaird1/LumiToOutput2.txt").replace(\'"\',"").replace("\\n","").split(",")[0:3]',   lumi = 999999.9 )
#jetmet.add("PF_skim", '["~/public_html/23_high_alphaT_events/pf/SusyCAF_Tree.root"]',   lumi = 999999.9 )
#jetmet.add("PF_skim_skim", '["~/public_html/23_high_alphaT_events/pf/PF_skim_skim.root"]',   lumi = 999999.9 )

#38X
jetmet.add("Jet.Run2010B-PromptReco-v2.RECO.Burt",          '%s/bbetchar//ICF/automated/2010_10_05_22_57_38/")'%srm, lumi = 99999.9 )

#TEST
jetmet.add("JetMET_test_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/03_jetmet/")', lumi = 2.601 ) #/pb
jetmet.add("JetMET_test_skim2", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/11_skims/04_38_recipe/")', lumi = 2.601 ) #/pb
