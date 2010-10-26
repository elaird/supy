import samples

muon = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#38X SKIMS
muon.add("Mu.Run2010_skim", 'utils.fileListFromDisk(location = "/vols/cms02/elaird1/11_skims/17_markus_mu_dataset/")', lumi = 999999.9) #/pb

#38X ORIGINALS
muon.add("Mu.Run2010A-Sep17ReReco_v2.RECO.Robin",             '%s/rnandi//ICF/automated/2010_10_13_14_30_58/")'%srm, lumi = 99999.9 )
muon.add("Mu.Run2010B-PromptReco-v2.RECO.Arlo1",              '%s/arlogb//ICF/automated/2010_10_13_14_09_24/")'%srm, lumi = 99999.9 )
muon.add("Mu.Run2010B-PromptReco-v2.RECO.Arlo2",              '%s/arlogb//ICF/automated/2010_10_24_16_41_15/")'%srm, lumi = 99999.9 )
muon.add("Mu.Run2010B-PromptReco-v2.RECO.Martyn",             '%s/mjarvis//ICF/automated/2010_10_22_16_11_58/")'%srm, lumi = 99999.9 )
