#!/usr/bin/env python

import analysis,utils
        
a=analysis.analysis(name="hadronicLook",
                    outputDir="/vols/cms02/elaird1/tmp/",
                    listName="metPasLook"
                    )


a.addSample(sampleName="qcd_py_pt30",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/",
                                                        nMaxFiles=1),
                nEvents=100,
                xs=6.041e+07#pb
                )

a.addSample(sampleName="qcd_py_pt80",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_00_55_17/",
                                                        nMaxFiles=1),
                nEvents=100,
                xs=9.238e+05#pb
                )

a.addSample(sampleName="qcd_py_pt170",
                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_01_33_23/",
                                                        nMaxFiles=1),
                nEvents=100,
                xs=2.547e+04#pb
                )

a.combineSamples(ptHatLowerThresholdsAndSampleNames=[(30,"qcd_py_pt30"),(80,"qcd_py_pt80"),(170,"qcd_py_pt170")])

#a.addSample(sampleName="tt_tauola_mg",
#                listOfFileNames=utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n")[:1],
#                nEvents=10,
#                xs=95.0#pb
#                )

#a.addSample(sampleName="lm0",
#                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
#                                                        nMaxFiles=6),
#                nEvents=-1,
#                xs=38.93#pb
#                )
#
#a.addSample(sampleName="lm1",
#                listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/",
#                                                        nMaxFiles=6),
#                nEvents=-1,
#                xs=4.888#pb
#                )
#
#a.addSample(sampleName="JetMETTau.Run2010A",
#                listOfFileNames=utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/take2/JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn",pruneList=False,nMaxFiles=-1),
#                nEvents=-1,
#                lumi=0.120,#/pb
#                )

#a.splitJobsByInputFile()

a.loop(profile=False,nCores=1)
a.plot()
