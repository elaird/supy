#!/usr/bin/env python

import analysis,utils
        
a=analysis.analysis(name="metPasLook",
                    outputDir="/vols/cms02/elaird1/tmp/"
                    )


a.addSampleSpec(sampleName="qcd_py_pt30",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/",
                                                        nMaxFiles=6),
                listName="metPasLook",
                isMc=True,
                nEvents=-1,
                xs=6.041e+07#pb
                )
    
#a.addSampleSpec(sampleName="tt_tauola_mg",
#                listOfFileNames=utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n")[:6],
#                listName="metPasLook",
#                isMc=True,
#                nEvents=-1,
#                xs=95.0#pb
#                )
#
a.addSampleSpec(sampleName="lm0",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
                                                        nMaxFiles=6),
                listName="metPasLook",
                isMc=True,
                nEvents=-1,
                xs=38.93#pb
                )

a.addSampleSpec(sampleName="lm1",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
                                                        nMaxFiles=6),
                listName="metPasLook",
                isMc=True,
                nEvents=-1,
                xs=4.888#pb
                )

dataList=        utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn",pruneList=False,nMaxFiles=-1)
dataList.extend( utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",pruneList=False,nMaxFiles=-1) )

a.addSampleSpec(sampleName="JetMETTau.Run2010A",
                listOfFileNames=dataList,
                listName="metPasLook",
                isMc=False,
                nEvents=-1,
                lumi=0.132,#/pb
                )

a.splitJobsByInputFile()

#a.loop(profile=False,nCores=6)
a.plot()
