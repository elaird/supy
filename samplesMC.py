import samples

mc = samples.SampleHolder()
srm = 'utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user'

#PY 6 QCD
mc.add("qcd_py6_pt15",  '%s/gouskos//ICF/automated/2010_06_24_18_00_11/")'%srm, xs = 8.762e+08, ptHatMin =   15 )
mc.add("qcd_py6_pt30",  '%s/gouskos//ICF/automated/2010_06_24_18_09_51/")'%srm, xs = 6.041e+07, ptHatMin =   30 )
mc.add("qcd_py6_pt80",  '%s/gouskos//ICF/automated/2010_07_06_00_55_17/")'%srm, xs = 9.238e+05, ptHatMin =   80 )
mc.add("qcd_py6_pt170", '%s/gouskos//ICF/automated/2010_07_06_01_33_23/")'%srm, xs = 2.547e+04, ptHatMin =  170 )
mc.add("qcd_py6_pt300", '%s/gouskos//ICF/automated/2010_07_09_19_13_09/")'%srm, xs = 1.256e+03, ptHatMin =  300 )
mc.add("qcd_py6_pt470", '%s/gouskos//ICF/automated/2010_07_10_04_22_06/")'%srm, xs = 8.798e+01, ptHatMin =  470 )
mc.add("qcd_py6_pt800", '%s/gouskos//ICF/automated/2010_07_10_04_37_56/")'%srm, xs = 2.186e+00, ptHatMin =  800 )
mc.add("qcd_py6_pt1400",'%s/gouskos//ICF/automated/2010_07_10_04_47_48/")'%srm, xs = 1.122e-02, ptHatMin = 1400 )
mc.adjustOverlappingSamples( ["qcd_py6_pt%d"%i for i in [15,30,80,170,300,470,800,1400] ] )

#PY 8 QCD
py8Dir = "/bm409//ICF/automated/2010_07_26_10_23_33/"
py8Gt1  = "Summer10-START36_V10_S09-v1.GEN-SIM-RECO"
py8Gt2  = "Summer10-START36_V10_S09-v2.GEN-SIM-RECO"
mc.add("qcd_py8_pt0to15",       '%s/%s/QCD_Pt-0to15_7TeV-pythia8.%s/")'     %(srm,py8Dir,py8Gt1), xs = 2.117e+12)
mc.add("qcd_py8_pt15to20",      '%s/%s/QCD_Pt-15to20_7TeV-pythia8.%s/")'    %(srm,py8Dir,py8Gt1), xs = 5.638e+08)
mc.add("qcd_py8_pt20to30",      '%s/%s/QCD_Pt-20to30_7TeV-pythia8.%s/")'    %(srm,py8Dir,py8Gt1), xs = 2.264e+08)
mc.add("qcd_py8_pt30to50",      '%s/%s/QCD_Pt-30to50_7TeV-pythia8.%s/")'    %(srm,py8Dir,py8Gt2), xs = 5.018e+07)
mc.add("qcd_py8_pt50to80",      '%s/%s/QCD_Pt-50to80_7TeV-pythia8.%s/")'    %(srm,py8Dir,py8Gt1), xs = 6.035e+06)
mc.add("qcd_py8_pt80to120",     '%s/%s/QCD_Pt-80to120_7TeV-pythia8.%s/")'   %(srm,py8Dir,py8Gt1), xs = 7.519e+05)
mc.add("qcd_py8_pt120to170",    '%s/%s/QCD_Pt-120to170_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt1), xs = 1.120e+05)
mc.add("qcd_py8_pt170to230",    '%s/%s/QCD_Pt-170to230_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt2), xs = 1.994e+04)
mc.add("qcd_py8_pt230to300",    '%s/%s/QCD_Pt-230to300_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt2), xs = 4.123e+03)
mc.add("qcd_py8_pt300to380",    '%s/%s/QCD_Pt-300to380_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt1), xs = 9.593e+02)
mc.add("qcd_py8_pt380to470",    '%s/%s/QCD_Pt-380to470_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt1), xs = 2.434e+02)
mc.add("qcd_py8_pt470to600",    '%s/%s/QCD_Pt-470to600_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt1), xs = 7.410e+01)
mc.add("qcd_py8_pt600to800",    '%s/%s/QCD_Pt-600to800_7TeV-pythia8.%s/")'  %(srm,py8Dir,py8Gt1), xs = 1.657e+01)
mc.add("qcd_py8_pt800to1000",   '%s/%s/QCD_Pt-800to1000_7TeV-pythia8.%s/")' %(srm,py8Dir,py8Gt2), xs = 1.997e+00)
mc.add("qcd_py8_pt1000to1400",  '%s/%s/QCD_Pt-1000to1400_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 3.621e-01)
mc.add("qcd_py8_pt1400to1800",  '%s/%s/QCD_Pt-1400to1800_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 1.179e-02)
mc.add("qcd_py8_pt1800to2200",  '%s/%s/QCD_Pt-1800to2200_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 3.743e-04)
mc.add("qcd_py8_pt2200to2600",  '%s/%s/QCD_Pt-2200to2600_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 7.590e-06)
mc.add("qcd_py8_pt2600to3000",  '%s/%s/QCD_Pt-2600to3000_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 5.458e-08)
mc.add("qcd_py8_pt3000to3500",  '%s/%s/QCD_Pt-3000to3500_7TeV-pythia8.%s/")'%(srm,py8Dir,py8Gt2), xs = 3.283e-11)

#MG QCD
mgDir = "/as1604/ICF/automated/2010_08_15_23_34_33/"
mc.add("qcd_mg_ht_50_100",  '%s/%s/QCD_Pt-50To100_7TeV-madgraph.Spring10-START3X_V26-v1.GEN-SIM-RECO/")'%(srm,mgDir), xs =  30e+06)
mc.add("qcd_mg_ht_100_250", '%s/%s/QCD_Pt100to250-madgraph.Spring10-START3X_V26_S09-v2.GEN-SIM-RECO/ ")'%(srm,mgDir), xs =   7e+06)
mc.add("qcd_mg_ht_250_500", '%s/%s/QCD_Pt250to500-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/ ")'%(srm,mgDir), xs = 171e+03)
mc.add("qcd_mg_ht_500_1000",'%s/%s/QCD_Pt500to1000-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%(srm,mgDir), xs = 5200)
mc.add("qcd_mg_ht_1000_inf",'%s/%s/QCD_Pt1000toInf-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%(srm,mgDir), xs = 83)
#mc.add("qcd_mg_ht_250_500_old",'%s/as1604//ICF/automated/2010_07_27_14_33_00//QCD_Pt250to500-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm, xs = 171e+03 )

#ALPGEN QCD
#efficiences from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/851.html
agDir = "/elaird/ICF/automated/2010_08_26_19_33_35/"
mc.add("qcd_ag_2jets_Pt40to120"  ,'%s/%s/QCD2Jets_Pt40to120-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'  %(srm,agDir), xs = 0.571 * 1.67E+07 )
mc.add("qcd_ag_2jets_Pt120to280" ,'%s/%s/QCD2Jets_Pt120to280-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.279 * 1.23E+05 )
mc.add("qcd_ag_2jets_Pt280to500" ,'%s/%s/QCD2Jets_Pt280to500-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.204 * 1.57E+03 )
mc.add("qcd_ag_2jets_Pt500to5000",'%s/%s/QCD2Jets_Pt500to5000-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'%(srm,agDir), xs = 0.192 * 5.23E+01 )

mc.add("qcd_ag_3jets_Pt40to120"  ,'%s/%s/QCD3Jets_Pt40to120-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'  %(srm,agDir), xs = 0.299 * 1.13E+07 )
mc.add("qcd_ag_3jets_Pt120to280" ,'%s/%s/QCD3Jets_Pt120to280-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.207 * 2.22E+05 )
mc.add("qcd_ag_3jets_Pt280to500" ,'%s/%s/QCD3Jets_Pt280to500-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.144 * 3.52E+03 )
mc.add("qcd_ag_3jets_Pt500to5000",'%s/%s/QCD3Jets_Pt500to5000-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'%(srm,agDir), xs = 0.134 * 1.23E+02 )

mc.add("qcd_ag_4jets_Pt40to120"  ,'%s/%s/QCD4Jets_Pt40to120-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'  %(srm,agDir), xs = 0.184 * 2.34E+06 )
mc.add("qcd_ag_4jets_Pt120to280" ,'%s/%s/QCD4Jets_Pt120to280-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.147 * 1.47E+05 )
mc.add("qcd_ag_4jets_Pt280to500" ,'%s/%s/QCD4Jets_Pt280to500-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.106 * 3.30E+03 )
mc.add("qcd_ag_4jets_Pt500to5000",'%s/%s/QCD4Jets_Pt500to5000-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'%(srm,agDir), xs = 0.103 * 1.27E+02 )

mc.add("qcd_ag_5jets_Pt40to120"  ,'%s/%s/QCD5Jets_Pt40to120-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'  %(srm,agDir), xs = 0.115 * 4.71E+05 )
mc.add("qcd_ag_5jets_Pt120to280" ,'%s/%s/QCD5Jets_Pt120to280-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.101 * 6.30E+04 )
mc.add("qcd_ag_5jets_Pt280to500" ,'%s/%s/QCD5Jets_Pt280to500-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.075 * 2.01E+03 )
mc.add("qcd_ag_5jets_Pt500to5000",'%s/%s/QCD5Jets_Pt500to5000-alpgen.Summer10-START36_V9_S09-v1.GEN-SIM-RECO/")'%(srm,agDir), xs = 0.076 * 8.49E+01 )

mc.add("qcd_ag_6jets_Pt40to120"  ,'%s/%s/QCD6Jets_Pt40to120-alpgen.Summer10-START36_V9_S09-v2.GEN-SIM-RECO/")'  %(srm,agDir), xs = 0.095 * 8.33E+04 )
mc.add("qcd_ag_6jets_Pt120to280" ,'%s/%s/QCD6Jets_Pt120to280-alpgen.Summer10-START36_V9_S09-v2.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.102 * 2.02E+04 )
mc.add("qcd_ag_6jets_Pt280to500" ,'%s/%s/QCD6Jets_Pt280to500-alpgen.Summer10-START36_V9_S09-v2.GEN-SIM-RECO/")' %(srm,agDir), xs = 0.099 * 9.05E+02 )
mc.add("qcd_ag_6jets_Pt500to5000",'%s/%s/QCD6Jets_Pt500to5000-alpgen.Summer10-START36_V9_S09-v2.GEN-SIM-RECO/")'%(srm,agDir), xs = 0.099 * 4.20E+01 )


#MG GAMMA + JETS
mc.add("g_jets_mg_pt40_100", '%s/arlogb//ICF/automated/2010_07_26_15_14_40//PhotonJets_Pt40to100-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm, xs = 23620 )
mc.add("g_jets_mg_pt100_200",'%s/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt100to200-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm,  xs = 3476 )
mc.add("g_jets_mg_pt200",    '%s/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt200toInf-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm,  xs = 485 )
            
#MG TT/EWK
mc.add("tt_tauola_mg",'utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\\n")',
       xs = {"LO":95.0,"NLO":157.5}["LO"] )
mc.add("z_inv_mg",'%s/zph04/ICF/automated/2010_07_14_11_52_58/",itemsToSkip=["14_3.root"])'%srm, xs = 4500.0 )
mc.add("z_jets_mg",'%s/jad/ICF/automated//2010_07_05_22_43_20/", pruneList=False)'%srm,
       xs = {"LO":2400.0,"NNLO":3048.0}["LO"] )
mc.add("w_jets_mg",'%s/jad/ICF/automated//2010_06_18_22_33_23/")'%srm,
       xs = {"LO":24170.0,"NNLO":31314.0}["LO"] )

#SUSY
mc.add("lm0",'%s/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm, xs = 38.93 )
mc.add("lm1",'%s/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")'%srm, xs = 4.888 )

#MG EWK SKIMS
mc.add("z_inv_mg_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/z_inv_mg/")', xs = 50.2 )
mc.add("z_jets_mg_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/z_jets_mg/")', xs = 55.4 )
mc.add("w_jets_mg_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/w_jets_mg/")', xs = 332.4 )

#PY QCD SKIMS
mc.add("qcd_py_pt80_skim", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt80/")',  xs = 0.894,    ptHatMin =  80 )
mc.add("qcd_py_pt170_skim",'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt170/")', xs = 0.377,    ptHatMin = 170 )
mc.add("qcd_py_pt300_skim",'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt300/")', xs = 0.0409,   ptHatMin = 300 )
mc.add("qcd_py_pt470_skim",'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/qcd_high_alphaT/pt470/")', xs = 0.002362, ptHatMin = 470 )
mc.adjustOverlappingSamples( ["qcd_py_pt80_skim",
                              "qcd_py_pt170_skim",
                              "qcd_py_pt300_skim",
                              "qcd_py_pt470_skim"] )

#PY QCD SKIMS2
mc.add("qcd_py_pt30_skim2", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/alphaT.gt.0.525/pt30/")', xs = 12.56, ptHatMin = 30 )
mc.add("qcd_py_pt80_skim2", 'utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/alphaT.gt.0.525/pt80/")', xs = 4.9,   ptHatMin = 80 )
mc.adjustOverlappingSamples( ["qcd_py_pt30_skim2",
                              "qcd_py_pt80_skim2"] )

