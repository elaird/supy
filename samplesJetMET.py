import samples

jetmet = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#DATA SKIM
jetmet.add("JetMET_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 0.8267 ) #/pb
#jetmet.add("JetMET.Run2010A", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data2/")', lumi = 0.293 ) #/pb (old lumi value)
#jetmet.add("JetMETTau.Run2010A_old", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data1/")', lumi = 0.012+0.120+0.1235 ) #/pb

#ORIGINALS
jetmet.add("MinimumBias.Commissioning10-SD_JetMETTau-Jun14thSkim_v1.RECO.Bryn", '%s/bm409/ICF/automated/2010_07_06_22_18_07/")'%srm, lumi = 999999.9 )
jetmet.add("JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", '%s/bm409//ICF/automated/2010_07_20_16_52_06/")'%srm,   lumi = 0.012 )
jetmet.add("JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn", '%s/bm409//ICF/automated/2010_07_20_17_20_35/")'%srm,   lumi = 0.120 )
jetmet.add("JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn",    '%s/bm409//ICF/automated/2010_07_20_15_40_06/")'%srm,   lumi = 0.1235)
jetmet.add("JetMETTau.Run2010A-PromptReco-v4.RECO.Loukas",  '%s/gouskos//ICF/automated/2010_08_05_01_38_58/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Loukas",     '%s/gouskos//ICF/automated/2010_08_05_01_56_12/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Martyn",     '%s/mjarvis//ICF/automated/2010_08_13_15_36_08/")'%srm, lumi = 999999.9 )
jetmet.add("JetMET.Run2010A-PromptReco-v4.RECO.Bryn",       '%s/bm409//ICF/automated/2010_08_21_18_15_19/")'%srm,   lumi = 999999.9 )
