import samples
from configuration import srm
photon = samples.SampleHolder()

photon.add("Photon.Run2011A-PromptReco-v1.AOD.Henning1", '%s/henning//ICF/automated/2011_04_11_22_38_56/")'%srm, lumi = 11.88)
photon.add("Photon.Run2011A-PromptReco-v1.AOD.Henning2", '%s/henning//ICF/automated/2011_04_13_15_50_13/")'%srm, lumi =  5.07)
photon.add("Photon.Run2011A-PromptReco-v2.AOD.Arlo",     '%s/arlogb//ICF/automated/2011_04_20_15_08_17/")'%srm, lumi = 3.0) #guess lumi

dir = "/vols/cms02/elaird1/29_skims/04_photons/v1"
photon.add("Photon.Run2011A-PromptReco-v1.AOD.Henning1_noIsoReqSkim",
           'utils.fileListFromDisk(location = "%s/Photon.Run2011A-PromptReco-v1.AOD.Henning1_*_skim.root", isDirectory = False)'%dir,lumi = 1.188000e+01)
photon.add("Photon.Run2011A-PromptReco-v1.AOD.Henning2_noIsoReqSkim",
           'utils.fileListFromDisk(location = "%s/Photon.Run2011A-PromptReco-v1.AOD.Henning2_*_skim.root", isDirectory = False)'%dir,lumi = 5.070000e+00)
photon.add("HT.Run2011A-PromptReco-v1.AOD.Henning_noIsoReqSkim",
           'utils.fileListFromDisk(location = "%s/HT.Run2011A-PromptReco-v1.AOD.Henning_*_skim.root", isDirectory = False)'%dir, lumi = 5.07)
photon.add("HT.Run2011A-PromptReco-v1.AOD.Georgia_noIsoReqSkim",
           'utils.fileListFromDisk(location = "%s/HT.Run2011A-PromptReco-v1.AOD.Georgia_*_skim.root", isDirectory = False)'%dir, lumi = 1.188000e+01)
photon.add("g_jets_mg_ht_100_200_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/g_jets_mg_ht_100_200_*_skim.root", isDirectory = False)'%dir,
           xs = 8.158440e-02 * 4.414520e+03)
photon.add("g_jets_mg_ht_200_inf_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/g_jets_mg_ht_200_inf_*_skim.root", isDirectory = False)'%dir,
           xs = 1.554971e-01 * 6.159500e+02)
photon.add("g_jets_mg_ht_40_100_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/g_jets_mg_ht_40_100_*_skim.root", isDirectory = False)'%dir,
           xs = 4.606359e-03 * 2.999740e+04)
photon.add("qcd_mg_ht_1000_inf_noIsoReqSkim",   'utils.fileListFromDisk(location = "%s/qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir,
           xs = 4.445170e-03 * 1.054100e+02)
photon.add("qcd_mg_ht_100_250_noIsoReqSkim",    'utils.fileListFromDisk(location = "%s/qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,
           xs = 1.111370e-04 * 8.890000e+06)
photon.add("qcd_mg_ht_250_500_noIsoReqSkim",    'utils.fileListFromDisk(location = "%s/qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,
           xs = 4.298156e-03 * 2.171700e+05)
photon.add("qcd_mg_ht_500_1000_noIsoReqSkim",   'utils.fileListFromDisk(location = "%s/qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir,
           xs = 5.889124e-03 * 6.604000e+03)

####### only 2010 below ######

#this one sample copied from samplesMCOld.py to avoid importing that file
photon.add("z_inv_mg_v12_skim",  'utils.fileListFromDisk(location = "/vols/cms02/elaird1/14_skims/ZinvisibleJets-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/")',
           xs = 2.067155e-03 * 5.715000e+03)

#original photon-triggered data
photon.add("EG.Run2010A-Sep17ReReco_v2.RECO",             '%s/mjarvis//ICF/automated/2010_10_13_14_25_09/")'%srm, lumi = 99999.9 )
photon.add("Photon.Run2010B-PromptReco-v2.RECO.Alex",     '%s/as1604//ICF/automated/2010_10_26_15_38_03/")'%srm,  lumi = 99999.9 )
photon.add("Photon.Run2010B-PromptReco-v2.RECO.Martyn",   '%s/mjarvis//ICF/automated/2010_10_22_16_06_53/")'%srm, lumi = 99999.9 )
photon.add("Photon.Run2010B-PromptReco-v2.RECO.Robin",    '%s/rnandi//ICF/automated/2010_10_13_14_47_32/")'%srm,  lumi = 99999.9 )

#skims from photonSkim.py (1 even looser photon>80 GeV)
dir = "/vols/cms02/elaird1/11_skims/24_oneNoIsoReqPhotonGt80_jetDataset_skim"
photon.add("Run2010A_JMT_skim_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,lumi = 1.720000e-01)
photon.add("Run2010A_JM_skim_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir, lumi = 2.889000e+00)
photon.add("Run2010B_J_skim_noIsoReqSkim",   'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,  lumi = 3.897000e+00)
photon.add("Run2010B_J_skim2_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir, lumi = 5.107000e-01)
photon.add("Run2010B_MJ_skim_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir, lumi = 3.467000e+00)
photon.add("Run2010B_MJ_skim2_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim2_*_skim.root", isDirectory = False)'%dir,lumi = 4.150800e+00)
photon.add("Run2010B_MJ_skim3_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim3_*_skim.root", isDirectory = False)'%dir,lumi = 6.807000e+00)
photon.add("Run2010B_MJ_skim4_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim4_*_skim.root", isDirectory = False)'%dir,lumi = 1.283200e+01)
photon.add("Run2010B_MJ_skim5_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim5_*_skim.root", isDirectory = False)'%dir,lumi = 6.510000e-01)

dir = "/vols/cms02/elaird1/11_skims/27_oneNoIsoReqPhotonGt80/"
photon.add("Nov4_MJ_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/MultiJet.Run2010B-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,
           lumi = 2.790700e+01)
photon.add("Nov4_J_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/Jet.Run2010B-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,
           lumi = 2.853000e+00)
photon.add("Nov4_J2_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/Jet.Run2010B-Nov4ReReco_v1.RECO.Henning_*_skim.root", isDirectory = False)'%dir,
           lumi = 2.181000e+00)
photon.add("Nov4_JM_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/JetMET.Run2010A-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,
           lumi = 2.895000e+00)
photon.add("Nov4_JMT_noIsoReqSkim",'utils.fileListFromDisk(location = "%s/JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt_*_skim.root", isDirectory = False)'%dir,
           lumi = 1.670000e-01)
photon.add("Nov4_JMT2_noIsoReqSkim",'utils.fileListFromDisk(location = "%s/JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Henning_*_skim.root", isDirectory = False)'%dir,
           lumi = 1.170000e-01)

photon.add("v12_g_jets_mg_pt40_100_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir,
           xs = 4.537900e-03 * 2.999740e+04)
photon.add("v12_g_jets_mg_pt100_200_noIsoReqSkim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,
           xs = 8.116814e-02 * 4.414520e+03)
photon.add("v12_g_jets_mg_pt200_noIsoReqSkim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,
           xs = 1.545809e-01 * 6.159500e+02)

#photon.add("v12_qcd_mg_ht_50_100_noIsoReqSkim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,
#           xs = 0.000000e+00 * 3.810000e+07)
photon.add("v12_qcd_mg_ht_100_250_noIsoReqSkim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,
           xs = 1.207488e-04 * 8.890000e+06)
photon.add("v12_qcd_mg_ht_250_500_noIsoReqSkim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,
           xs = 4.684685e-03 * 2.171700e+05)
photon.add("v12_qcd_mg_ht_500_1000_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir,
           xs = 6.404507e-03 * 6.604000e+03)
photon.add("v12_qcd_mg_ht_1000_inf_noIsoReqSkim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir,
           xs = 4.865820e-03 * 1.054100e+02)

#skims from photonSkim.py (1 very loose photon>80 GeV)
photon.add("Ph.Data_markusSkim", 'utils.fileListFromDisk(location=  "/vols/cms02/elaird1/11_skims/18_photon_dataset/")', lumi = 13.48) #/pb

dir = "/vols/cms02/elaird1/11_skims/21_onePhotonGt80_jetDataset_skim"
photon.add("Run2010A_JMT_skim_markusSkim", 'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,lumi = 1.720000e-01)
photon.add("Run2010A_JM_skim_markusSkim",  'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir, lumi = 2.889000e+00)
photon.add("Run2010B_J_skim_markusSkim",   'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,  lumi = 3.897000e+00)
photon.add("Run2010B_J_skim2_markusSkim",  'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir, lumi = 5.107000e-01)
photon.add("Run2010B_MJ_skim_markusSkim",  'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir, lumi = 3.467000e+00)
photon.add("Run2010B_MJ_skim2_markusSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim2_*_skim.root", isDirectory = False)'%dir,lumi = 4.150800e+00)
photon.add("Run2010B_MJ_skim3_markusSkim", 'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim3_*_skim.root", isDirectory = False)'%dir,lumi = 6.807000e+00)
photon.add("Run2010B_MJ_4_markusSkim",     'utils.fileListFromDisk(location = "%s/MultiJet.Run2010B-PromptReco-v2.RECO.RAW.Robin_*_skim.root", isDirectory = False)'%dir,lumi = 12.832)

dir = "/vols/cms02/elaird1/11_skims/19_onePhotonGt80_skim/"
photon.add("v12_g_jets_mg_pt100_200_markusSkim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,
           xs = 8.003540e-02 * 4.414520e+03)
photon.add("v12_g_jets_mg_pt200_markusSkim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,
           xs = 1.375949e-01 * 6.159500e+02)
photon.add("v12_g_jets_mg_pt40_100_markusSkim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir,
           xs = 4.532579e-03 * 2.999740e+04)
photon.add("v12_qcd_mg_ht_1000_inf_markusSkim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir,
           xs = 1.232644e-03 * 1.054100e+02)
photon.add("v12_qcd_mg_ht_100_250_markusSkim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,
           xs = 8.336211e-05 * 8.890000e+06)
photon.add("v12_qcd_mg_ht_250_500_markusSkim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,
           xs = 1.871940e-03 * 2.171700e+05)
photon.add("v12_qcd_mg_ht_500_1000_markusSkim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir,
           xs = 1.747501e-03 * 6.604000e+03)
#photon.add("v12_qcd_mg_ht_50_100_markusSkim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,xs = 0.000000e+00 * 3.810000e+07)

##example from photonSkim.py
##-----------------------------------------------------------------------------------------------
##v12_qcd_mg_ht_500_1000
##-----------------------------------------------------------------------------------------------
##Calculables' configuration:
##photonIndicesPat                pT>=80.0 GeV; photonIDIsoRelaxedPat
##photonIDIsoRelaxedPat           relaxed trkIso [ ,10]; hcalIso[ ,6]; ecalIso[ ,8]
##photonIndicesOtherPat           pass ptMin; fail id/iso
##-----------------------------------------------------------------------------------------------
##Steps:                                                                       nPass      (nFail)
##progressPrinter               factor=2, offset=300
##multiplicityFilter            1 <= photonIndicesPat                           4080    (2330682)
##skimmer                       (see below)                                     4080          (0)
##-----------------------------------------------------------------------------------------------
##The output file: /vols/cms02/elaird1/tmp//photonSkim//config/v12_qcd_mg_ht_500_1000_plots.root has been written.
##-----------------------------------------------------------------------------------------------


#V5 skims
dir = "/vols/cms02/elaird1/11_skims/16_photons_skim/"
photon.add("Run2010A_JMT_skim_phskim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,      lumi = 1.720000e-01)
photon.add("Run2010A_JM_skim_phskim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 2.889000e+00)
photon.add("Run2010B_J_skim_phskim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,        lumi = 3.897000e+00)
photon.add("Run2010B_J_skim2_phskim",        'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir,       lumi = 5.107000e-01)
photon.add("Run2010B_MJ_skim_phskim",        'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 3.467000e+00)
photon.add("Run2010B_MJ_skim2_phskim",       'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim2_*_skim.root", isDirectory = False)'%dir,      lumi = 4.150800e+00)
photon.add("tt_tauola_mg_v12_phskim",        'utils.fileListFromDisk(location = "%s/tt_tauola_mg_v12_*_skim.root", isDirectory = False)'%dir,       xs = 5.766667e-04 * 1.575000e+02)
photon.add("v12_g_jets_mg_pt100_200_phskim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,xs = 1.331431e-05 * 4.414520e+03)
photon.add("v12_g_jets_mg_pt200_phskim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,    xs = 4.024784e-02 * 6.159500e+02)
#photon.add("v12_g_jets_mg_pt40_100_phskim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 2.999740e+04)
photon.add("v12_g_jets_py6_pt170_phskim",    'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 1.247300e-01 * 2.437000e+01)
photon.add("v12_g_jets_py6_pt30_phskim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir,    xs = 3.000000e-06 * 1.951350e+04)
photon.add("v12_g_jets_py6_pt80_phskim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 9.640000e-03 * 5.321300e+02)
photon.add("v12_qcd_mg_ht_1000_inf_phskim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir, xs = 1.144763e-03 * 1.054100e+02)
#photon.add("v12_qcd_mg_ht_100_250_phskim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,  xs = 0.000000e+00 * 8.890000e+06)
photon.add("v12_qcd_mg_ht_250_500_phskim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,  xs = 5.947784e-05 * 2.171700e+05)
photon.add("v12_qcd_mg_ht_500_1000_phskim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir, xs = 1.334183e-03 * 6.604000e+03)
#photon.add("v12_qcd_mg_ht_50_100_phskim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,   xs = 0.000000e+00 * 3.810000e+07)
photon.add("v12_qcd_py6_pt170_phskim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,      xs = 1.035641e-03 * 2.421400e+04)
photon.add("v12_qcd_py6_pt300_phskim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,      xs = 2.712465e-03 * 1.256000e+03)
photon.add("v12_qcd_py6_pt80_phskim",        'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,       xs = 5.276427e-05 * 8.983300e+05)
photon.add("w_jets_mg_v12_phskim",           'utils.fileListFromDisk(location = "%s/w_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 2.989590e-06 * 3.131400e+04)
photon.add("z_jets_mg_v12_phskim",           'utils.fileListFromDisk(location = "%s/z_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 1.106071e-05 * 3.048000e+03)

#V5 example
#----------------------------------------------------------------------------------------------
#Calculables' configuration:
#muonIndicesOtherPat             pass ptMin; fail id
#muonNumberOfMatchesPat          WARNING: dummy value always = 2
#xcak5JetIndicesOtherPat         pass ptMin; fail jetID or etaMax
#electronIndicesOtherPat         pass ptMin; fail id/iso
#muonIndicesNonIsoPat            pass ptMin & id; fail iso
#xcak5JetIndicesKilledPat                removed from consideration; gamma,e match or jetkill study
#photonIDIsoRelaxedPat           relaxed trkIso [ ,10]; hcalIso[ ,6]; ecalIso[ ,8]
#muonNumberOfValidPixelHitsPat           WARNING: dummy value always = 1
#xcak5JetCorrectedP4Pat          muonPatDR<0.50; electronPatDR<0.50; photonPatDR<0.50
#photonIndicesPat                pT>=25.0 GeV; photonIDIsoRelaxedPat
#photonIndicesOtherPat           pass ptMin; fail id/iso
#electronIndicesPat              pt>20.0; simple95; cIso; no conversion cut
#xcak5JetIndicesPat              pT>=36.0 GeV; |eta|<3.0; JetIDloose
#muonCombinedRelativeIsoPat              (trackIso + ecalIso + hcalIso) / pt_mu
#muonIndicesPat          tight; pt>10.0 GeV; cmbRelIso<0.15
#muonIDtightPat          implemented by hand, CMS AN-2010/211
#-----------------------------------------------------------------------------------------------
#Steps:                                                                       nPass      (nFail)
#progressPrinter               factor=2, offset=300
#histogrammer                  (genpthat)
#jetPtSelector                 xcak5JetPat; pT[index[0]]>=72.0 GeV          3130304         (59)
#jetPtSelector                 xcak5JetPat; pT[index[1]]>=72.0 GeV          3119485      (10819)
#jetEtaSelector                xcak5JetPat; |eta[index[0]]|<=2.5            3112101       (7384)
#lowestUnPrescaledTrigger      lowest unprescaled of                              -          (-)
#vertexRequirementFilter       any v: !fake; ndf>=5.0; |z|<=24.0 cm; d0<=2.0 cm     3110814       (1287)
#techBitFilter                 any tech. bit in [0]                               -          (-)
#physicsDeclared                                                                  -          (-)
#monsterEventFilter            <=10 tracks or >0.25 good fraction           3110763         (51)
#hbheNoiseFilter                                                                  -          (-)
#histogrammer                  (xcak5JetSumEtPat)
#variableGreaterFilter         xcak5JetSumEtPat>=250.000 GeV                3110525        (238)
#photonPtSelector              photonPat; pT[index[0]]>=80.0 GeV               8491    (3102034)
#skimmer                       (see below)                                     8491          (0)
#-----------------------------------------------------------------------------------------------
#
