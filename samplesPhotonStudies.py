import samples

ph = samples.SampleHolder()

#V4 skims
dir = /vols/cms02/elaird1/11_skims/14_photons_skim
ph.add("Run2010A_JMT_skim_skim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,      lumi = 1.720000e-01)
ph.add("Run2010A_JM_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 2.889000e+00)
ph.add("Run2010B_J_skim_skim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,        lumi = 3.897000e+00)
ph.add("Run2010B_J_skim2_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir,       lumi = 5.107000e-01)
ph.add("Run2010B_MJ_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 3.467000e+00)
ph.add("Run2010B_MJ_skim2_skim",       'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim2_*_skim.root", isDirectory = False)'%dir,      lumi = 4.150800e+00)
ph.add("tt_tauola_mg_v12_skim",        'utils.fileListFromDisk(location = "%s/tt_tauola_mg_v12_*_skim.root", isDirectory = False)'%dir,       xs = 2.966667e-04 * 1.575000e+02)
ph.add("v12_g_jets_mg_pt100_200_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,xs = 1.024178e-06 * 4.414520e+03)
ph.add("v12_g_jets_mg_pt200_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,    xs = 2.460793e-02 * 6.159500e+02)
ph.add("v12_g_jets_mg_pt40_100_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 2.999740e+04)
ph.add("v12_g_jets_py6_pt170_skim",    'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 7.161000e-02 * 2.437000e+01)
ph.add("v12_g_jets_py6_pt30_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir,    xs = 1.000000e-06 * 1.951350e+04)
ph.add("v12_g_jets_py6_pt80_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 4.560000e-03 * 5.321300e+02)
ph.add("v12_qcd_mg_ht_1000_inf_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir, xs = 1.096197e-03 * 1.054100e+02)
ph.add("v12_qcd_mg_ht_100_250_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,  xs = 0.000000e+00 * 8.890000e+06)
ph.add("v12_qcd_mg_ht_250_500_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,  xs = 2.519751e-05 * 2.171700e+05)
ph.add("v12_qcd_mg_ht_500_1000_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir, xs = 1.009503e-03 * 6.604000e+03)
ph.add("v12_qcd_mg_ht_50_100_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,   xs = 0.000000e+00 * 3.810000e+07)
ph.add("v12_qcd_py6_pt170_skim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,      xs = 7.339334e-04 * 2.421400e+04)
ph.add("v12_qcd_py6_pt300_skim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,      xs = 2.502585e-03 * 1.256000e+03)
ph.add("v12_qcd_py6_pt80_skim",        'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,       xs = 2.710825e-05 * 8.983300e+05)
ph.add("w_jets_mg_v12_skim",           'utils.fileListFromDisk(location = "%s/w_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 9.965299e-07 * 3.131400e+04)
ph.add("z_jets_mg_v12_skim",           'utils.fileListFromDisk(location = "%s/z_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 5.530357e-06 * 3.048000e+03)


#V4 example
##-----------------------------------------------------------------------------------------------
##Calculables' configuration:
##muonIndicesOtherPat             pass ptMin; fail id
##muonNumberOfMatchesPat          WARNING: dummy value always = 2
##xcak5JetIndicesOtherPat         pass ptMin; fail jetID or etaMax
##electronIndicesOtherPat         pass ptMin; fail id/iso
##muonIndicesNonIsoPat            pass ptMin & id; fail iso
##xcak5JetIndicesKilledPat                removed from consideration; gamma,e match or jetkill study
##photonIDIsoRelaxedPat           relaxed trkIso [ ,10]; hcalIso[ ,6]; ecalIso[ ,8]
##muonNumberOfValidPixelHitsPat           WARNING: dummy value always = 1
##xcak5JetIndicesPat              pT>=50.0 GeV; |eta|<3.0; JetIDloose
##xcak5JetCorrectedP4Pat          muonPatDR<0.50; electronPatDR<0.50; photonPatDR<0.50
##photonIndicesPat                pT>=25.0 GeV; photonIDIsoRelaxedPat
##photonIndicesOtherPat           pass ptMin; fail id/iso
##electronIndicesPat              pt>20.0; simple95; cIso; no conversion cut
##muonCombinedRelativeIsoPat              (trackIso + ecalIso + hcalIso) / pt_mu
##muonIndicesPat          tight; pt>10.0 GeV; cmbRelIso<0.15
##muonIDtightPat          implemented by hand, CMS AN-2010/211
##-----------------------------------------------------------------------------------------------
##Steps:                                                                       nPass      (nFail)
##progressPrinter               factor=2, offset=300
##histogrammer                  (genpthat)
##jetPtSelector                 xcak5JetPat; pT[index[0]]>=100.0 GeV         3129937        (426)
##jetPtSelector                 xcak5JetPat; pT[index[1]]>=100.0 GeV         3110787      (19150)
##jetEtaSelector                xcak5JetPat; |eta[index[0]]|<=2.5            3103448       (7339)
##lowestUnPrescaledTrigger      lowest unprescaled of ['HT100U', 'HT120U', 'HT140U']           -          (-)
##vertexRequirementFilter       any v: !fake; ndf>=5.0; |z|<=24.0 cm; d0<=2.0 cm     3102166       (1282)
##techBitFilter                 any tech. bit in [0]                               -          (-)
##physicsDeclared                                                                  -          (-)
##monsterEventFilter            <=10 tracks or >0.25 good fraction           3102115         (51)
##hbheNoiseFilter                                                                  -          (-)
##histogrammer                  (xcak5JetSumEtPat)
##variableGreaterFilter         xcak5JetSumEtPat>=250.000 GeV                3102002        (113)
##photonPtSelector              photonPat; pT[index[0]]>=80.0 GeV               7834    (3094168)
##skimmer                       (see below)                                     7834          (0)
##-----------------------------------------------------------------------------------------------

##V3 skims
#dir = "/vols/cms02/elaird1/11_skims/12_photons_skim/"
#ph.add("Run2010A_JMT_skim_skim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,      lumi = 1.720000e-01)
#ph.add("Run2010A_JM_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 2.889000e+00)
#ph.add("Run2010B_J_skim_skim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,        lumi = 3.897000e+00)
#ph.add("Run2010B_J_skim2_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir,       lumi = 5.107000e-01)
#ph.add("Run2010B_MJ_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 3.467000e+00)
#ph.add("tt_tauola_mg_v12_skim",        'utils.fileListFromDisk(location = "%s/tt_tauola_mg_v12_*_skim.root", isDirectory = False)'%dir,       xs = 4.713333e-03 * 1.575000e+02)
#ph.add("v12_g_jets_mg_pt100_200_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,xs = 1.024178e-06 * 4.414520e+03)
#ph.add("v12_g_jets_mg_pt200_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,    xs = 2.519318e-02 * 6.159500e+02)
##ph.add("v12_g_jets_mg_pt40_100_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 2.999740e+04)
#ph.add("v12_g_jets_py6_pt170_skim",    'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 7.470000e-02 * 2.437000e+01)
#ph.add("v12_g_jets_py6_pt30_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir,    xs = 2.000000e-06 * 1.951350e+04)
#ph.add("v12_g_jets_py6_pt80_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 4.880000e-03 * 5.321300e+02)
#ph.add("v12_qcd_mg_ht_1000_inf_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir, xs = 1.100822e-03 * 1.054100e+02)
##ph.add("v12_qcd_mg_ht_100_250_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,  xs = 0.000000e+00 * 8.890000e+06)
#ph.add("v12_qcd_mg_ht_250_500_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,  xs = 3.017841e-05 * 2.171700e+05)
#ph.add("v12_qcd_mg_ht_500_1000_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir, xs = 1.065633e-03 * 6.604000e+03)
##ph.add("v12_qcd_mg_ht_50_100_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,   xs = 0.000000e+00 * 3.810000e+07)
#ph.add("v12_qcd_py6_pt170_skim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,      xs = 7.960403e-04 * 2.421400e+04)
#ph.add("v12_qcd_py6_pt300_skim",       'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,      xs = 2.539961e-03 * 1.256000e+03)
#ph.add("v12_qcd_py6_pt80_skim",        'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,       xs = 2.517194e-05 * 8.983300e+05)
#ph.add("w_jets_mg_v12_skim",           'utils.fileListFromDisk(location = "%s/w_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 4.653795e-05 * 3.131400e+04)
#ph.add("z_jets_mg_v12_skim",           'utils.fileListFromDisk(location = "%s/z_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,          xs = 1.493196e-04 * 3.048000e+03)
#
##V3 example
##ALSO: PIXEL SEED CUT WAS PURPOSEFULLY COMMENTED DURING THE SKIMMING
##-----------------------------------------------------------------------------------------------
##Calculables' configuration:
##muonIndicesOtherPat             pass ptMin; fail id
##muonNumberOfMatchesPat          WARNING: dummy value always = 2
##xcak5JetIndicesOtherPat         pass ptMin; fail jetID or etaMax
##photonIndicesPat                pT>=25.0 GeV; photonIDTrkIsoRelaxedPat
##electronIndicesOtherPat         pass ptMin; fail id/iso
##muonIndicesNonIsoPat            pass ptMin & id; fail iso
##xcak5JetIndicesKilledPat                removed from consideration; gamma,e match or jetkill study
##muonNumberOfValidPixelHitsPat           WARNING: dummy value always = 1
##xcak5JetIndicesPat              pT>=50.0 GeV; |eta|<3.0; JetIDloose
##photonIDTrkIsoRelaxedPat                relaxed trkIso
##xcak5JetCorrectedP4Pat          muonPatDR<0.50; electronPatDR<0.50; photonPatDR<0.50
##photonIndicesOtherPat           pass ptMin; fail id/iso
##electronIndicesPat              pt>20.0; simple95; cIso; no conversion cut
##muonCombinedRelativeIsoPat              (trackIso + ecalIso + hcalIso) / pt_mu
##muonIndicesPat          tight; pt>10.0 GeV; cmbRelIso<0.15
##muonIDtightPat          implemented by hand, CMS AN-2010/211
##-----------------------------------------------------------------------------------------------
##Steps:                                                                       nPass      (nFail)
##progressPrinter               factor=2, offset=300
##histogrammer                  (genpthat)
##jetPtSelector                 xcak5JetPat; pT[index[0]]>=100.0 GeV              11     (220704)
##jetPtSelector                 xcak5JetPat; pT[index[1]]>=100.0 GeV               4          (7)
##jetEtaSelector                xcak5JetPat; |eta[index[0]]|<=2.5                  4          (0)
##lowestUnPrescaledTrigger      lowest unprescaled of ['HT100U', 'HT120U', 'HT140U']           -          (-)
##vertexRequirementFilter       any v: !fake; ndf>=5.0; |z|<=24.0 cm; d0<=2.0 cm           4          (0)
##techBitFilter                 any tech. bit in [0]                               -          (-)
##physicsDeclared                                                                  -          (-)
##monsterEventFilter            <=10 tracks or >0.25 good fraction                 4          (0)
##hbheNoiseFilter                                                                  -          (-)
##histogrammer                  (xcak5JetSumEtPat)
##variableGreaterFilter         xcak5JetSumEtPat>=250.000 GeV                      2          (2)
##photonPtSelector              photonPat; pT[index[0]]>=80.0 GeV                  0          (2)
##skimmer                       (see below)                                        0          (0)
##-----------------------------------------------------------------------------------------------

###V2 skims
##dir = "/vols/cms02/elaird1/11_skims/11_photons_skim/"
##ph.add("Run2010A_JMT_skim_skim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'%dir,      lumi = 1.720000e-01)
##ph.add("Run2010A_JM_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 2.889000e+00)
##ph.add("Run2010B_J_skim_skim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'%dir,        lumi = 3.897000e+00)
##ph.add("Run2010B_J_skim2_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'%dir,       lumi = 5.107000e-01)
##ph.add("Run2010B_MJ_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'%dir,       lumi = 3.467000e+00)
##ph.add("v12_g_jets_mg_pt100_200_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)'%dir,xs = 1.024178e-06 * 4.414520e+03)
##ph.add("v12_g_jets_mg_pt200_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'%dir,    xs = 2.252736e-02 * 6.159500e+02)
###ph.add("v12_g_jets_mg_pt40_100_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 2.999740e+04)
##ph.add("v12_qcd_mg_ht_1000_inf_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir, xs = 4.602178e-04 * 1.054100e+02)
###ph.add("v12_qcd_mg_ht_100_250_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)'%dir,  xs = 0.000000e+00 * 8.890000e+06)
##ph.add("v12_qcd_mg_ht_250_500_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)'%dir,  xs = 9.668811e-06 * 2.171700e+05)
##ph.add("v12_qcd_mg_ht_500_1000_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir, xs = 3.978992e-04 * 6.604000e+03)
###ph.add("v12_qcd_mg_ht_50_100_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)'%dir,   xs = 0.000000e+00 * 3.810000e+07)
##
##ph.add("tt_tauola_mg_v12_skim",     'utils.fileListFromDisk(location = "%s/tt_tauola_mg_v12_*_skim.root", isDirectory = False)'%dir,    xs = 1.633333e-04 * 1.575000e+02)
##ph.add("v12_g_jets_py6_pt170_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,xs = 6.832000e-02 * 2.437000e+01)
##ph.add("v12_g_jets_py6_pt30_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir, xs = 1.000000e-06 * 1.951350e+04)
##ph.add("v12_g_jets_py6_pt80_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir, xs = 4.390000e-03 * 5.321300e+02)
##ph.add("v12_qcd_py6_pt170_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 5.296426e-04 * 2.421400e+04)
##ph.add("v12_qcd_py6_pt300_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,   xs = 1.912238e-03 * 1.256000e+03)
##ph.add("v12_qcd_py6_pt80_skim",     'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 1.887896e-05 * 8.983300e+05)
##ph.add("w_jets_mg_v12_skim",        'utils.fileListFromDisk(location = "%s/w_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,       xs = 7.972239e-07 * 3.131400e+04)
##ph.add("z_jets_mg_v12_skim",        'utils.fileListFromDisk(location = "%s/z_jets_mg_v12_*_skim.root", isDirectory = False)'%dir,       xs = 4.608630e-06 * 3.048000e+03)
##
##V2 example
##-----------------------------------------------------------------------------------------------
##Run2010B_MJ_skim
##-----------------------------------------------------------------------------------------------
##Calculables' configuration:
##muonIndicesOtherPat             pass ptMin; fail id
##photonIndicesPat                pT>=25.0 GeV; photonIDLooseFromTwikiPat
##muonNumberOfMatchesPat          WARNING: dummy value always = 2
##xcak5JetIndicesOtherPat         pass ptMin; fail jetID or etaMax
##electronIndicesOtherPat         pass ptMin; fail id/iso
##muonIndicesNonIsoPat            pass ptMin & id; fail iso
##xcak5JetIndicesKilledPat                removed from consideration; gamma,e match or jetkill study
##muonNumberOfValidPixelHitsPat           WARNING: dummy value always = 1
##xcak5JetIndicesPat              pT>=50.0 GeV; |eta|<3.0; JetIDloose
##photonIDLooseFromTwikiPat               twiki.cern.ch/twiki/bin/viewauth/CMS/PhotonID, 2010-10-14
##xcak5JetCorrectedP4Pat          muonPatDR<0.50; electronPatDR<0.50; photonPatDR<0.50
##photonIndicesOtherPat           pass ptMin; fail id/iso
##electronIndicesPat              pt>20.0; simple95; cIso; no conversion cut
##muonCombinedRelativeIsoPat              (trackIso + ecalIso + hcalIso) / pt_mu
##muonIndicesPat          tight; pt>10.0 GeV; cmbRelIso<0.15
##muonIDtightPat          implemented by hand, CMS AN-2010/211
##-----------------------------------------------------------------------------------------------
##Steps:                                                                       nPass      (nFail)
##progressPrinter               factor=2, offset=300
##histogrammer                  (genpthat)
##jetPtSelector                 xcak5JetPat; pT[index[0]]>=100.0 GeV          731481     (104583)
##jetPtSelector                 xcak5JetPat; pT[index[1]]>=100.0 GeV          412764     (318717)
##jetEtaSelector                xcak5JetPat; |eta[index[0]]|<=2.5             388828      (23936)
##lowestUnPrescaledTrigger      lowest unprescaled of ['HT100U', 'HT120U', 'HT140U']      388828          (0)
##vertexRequirementFilter       any v: !fake; ndf>=5.0; |z|<=24.0 cm; d0<=2.0 cm      388828          (0)
##techBitFilter                 any tech. bit in [0]                          388828          (0)
##physicsDeclared                                                             388828          (0)
##monsterEventFilter            <=10 tracks or >0.25 good fraction            388828          (0)
##hbheNoiseFilter                                                             383280       (5548)
##histogrammer                  (xcak5JetSumEtPat)
##variableGreaterFilter         xcak5JetSumEtPat>=250.000 GeV                 320344      (62936)
##photonPtSelector              photonPat; pT[index[0]]>=80.0 GeV                 97     (320247)
##skimmer                       (see below)                                       97          (0)
##-----------------------------------------------------------------------------------------------
##The output file: /vols/cms02/elaird1/tmp//photonLook/madgraph_ge2_caloAK5_photonLoose_fullSample/config00/Run2010B_MJ_skim_plots.root has been written.
##-----------------------------------------------------------------------------------------------
##The 10 skim files have been written.
##( e.g. /vols/cms02/elaird1/tmp//photonLook/madgraph_ge2_caloAK5_photonLoose_fullSample/config00/Run2010B_MJ_skim_0_skim.root )
##-----------------------------------------------------------------------------------------------





###V1 skims
##dir = "/vols/cms02/elaird1/11_skims/09_photons_skim/"
###data
##ph.add("Run2010A_JMT_skim_skim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'  %dir,  lumi = 1.720000e-01)
##ph.add("Run2010A_JM_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'   %dir,  lumi = 2.889000e+00)
##ph.add("Run2010B_J_skim_skim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'    %dir,  lumi = 3.897000e+00)
##ph.add("Run2010B_J_skim2_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_J_skim2_*_skim.root", isDirectory = False)'   %dir,  lumi = 5.107000e-01)
##ph.add("Run2010B_MJ_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010B_MJ_skim_*_skim.root", isDirectory = False)'   %dir,  lumi = 3.467000e+00)
##
##
###MG
##ph.add("v12_g_jets_mg_pt200_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'   %dir,  xs = 1.189819e-02 * 6.159500e+02)
##ph.add("v12_qcd_mg_ht_1000_inf_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir,  xs = 2.081387e-04 * 1.054100e+02)
##ph.add("v12_qcd_mg_ht_250_500_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)' %dir,  xs = 2.343954e-06 * 2.171700e+05)
##ph.add("v12_qcd_mg_ht_500_1000_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir,  xs = 1.648990e-04 * 6.604000e+03)
###ph.add("v12_g_jets_mg_pt100_200_skim", 'utils.fileListFromDisk(location = dir+"/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)', xs = 0.000000e+00 * 4.414520e+03)
###ph.add("v12_g_jets_mg_pt40_100_skim",  'utils.fileListFromDisk(location = dir+"/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)',  xs = 0.000000e+00 * 2.999740e+04)
###ph.add("v12_qcd_mg_ht_100_250_skim",   'utils.fileListFromDisk(location = dir+"/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)',   xs = 0.000000e+00 * 8.890000e+06)
###ph.add("v12_qcd_mg_ht_50_100_skim",    'utils.fileListFromDisk(location = dir+"/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)',    xs = 0.000000e+00 * 3.810000e+07)
##
###PYTHIA
##ph.add("v12_g_jets_py6_pt170_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,xs = 5.790000e-02 * 2.437000e+01)
##ph.add("v12_g_jets_py6_pt80_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir, xs = 2.430000e-03 * 5.321300e+02)
##ph.add("v12_qcd_py6_pt170_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 1.456517e-04 * 2.421400e+04)
##ph.add("v12_qcd_py6_pt300_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,   xs = 8.832841e-04 * 1.256000e+03)
##ph.add("v12_qcd_py6_pt80_skim",     'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 9.681517e-07 * 8.983300e+05)
###ph.add("v12_g_jets_py6_pt30_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 1.951350e+04)

