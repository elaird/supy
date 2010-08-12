import samples

jetmet = SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#DATA SKIM
jetmet.add("JetMETTau.Run2010A", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/data1/")', lumi = 0.012+0.120+0.1235 ) #/pb


#ORIGINALS
jetmet.add("JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn", '%s/bm409//ICF/automated/2010_07_20_16_52_06/")'%srm, lumi = 0.012 )
jetmet.add("JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",'%s/bm409//ICF/automated/2010_07_20_17_20_35/")'%srm, lumi = 0.120 )
jetmet.add("JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn",'%s/bm409//ICF/automated/2010_07_20_15_40_06/")'%srm,lumi = 0.1235)
