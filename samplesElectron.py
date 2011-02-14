import samples
from configuration import srm
electron = samples.SampleHolder()

#Skims
electron.add("EG.2010A_skim", #Lumi lower than expected: check
             'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/EG.Run2010A-Nov4ReReco_v1.RECO.Sparrow/")', lumi = 1.619)
electron.add("Electron.Run2010B_skim",
             'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/Electron.Run2010B-Nov4ReReco_v1.RECO.Sparrow")', lumi = 32.884)


#38X ORIGINALS
electron.add("Electron.Run2010B-Nov4ReReco_v1.RECO.Sparrow",'%s/as1604//ICF/automated/2011_01_07_14_15_11/")'%srm, lumi = 9999)
electron.add("EG.Run2010A-Nov4ReReco_v1.RECO.Sparrow",'%s/as1604//ICF/automated/2011_01_07_14_21_29/")'%srm, lumi = 9999)


