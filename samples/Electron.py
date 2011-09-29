import samples
from core.configuration import srm
electron = samples.SampleHolder()

# 2011
electron.add("ElectronHad.Run2011A-PromptReco-v1.Burt",    '%s/bbetchar//ICF/automated/2011_04_02_22_49_42/")'%srm, lumi = 5.81) #/pb
electron.add("SingleElectron.Run2011A-PromptReco-v1.Burt", '%s/bbetchar//ICF/automated/2011_04_02_23_01_32/")'%srm, lumi = 5.81) #/pb

#Skims
electron.add("EG.2010A_skim", #Lumi lower than expected: check
             'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/EG.Run2010A-Nov4ReReco_v1.RECO.Sparrow/")', lumi = 1.619)
electron.add("Electron.Run2010B_skim",
             'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/Electron.Run2010B-Nov4ReReco_v1.RECO.Sparrow")', lumi = 32.884)


#38X ORIGINALS
electron.add("Electron.Run2010B-Nov4ReReco_v1.RECO.Sparrow",'%s/as1604//ICF/automated/2011_01_07_14_15_11/")'%srm, lumi = 9999)
electron.add("EG.Run2010A-Nov4ReReco_v1.RECO.Sparrow",'%s/as1604//ICF/automated/2011_01_07_14_21_29/")'%srm, lumi = 9999)


