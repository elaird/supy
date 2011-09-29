import samples

signalSkim = samples.SampleHolder()

#<             steps.Trigger.lowestUnPrescaledTriggerFilter(),
#<             steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
#<
#<             steps.Trigger.physicsDeclaredFilter(),
#<             steps.Other.monsterEventFilter(),
#<             steps.Other.hbheNoiseFilter(),
#---
#>             #steps.Trigger.lowestUnPrescaledTriggerFilter(),
#>             #steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
#>             #
#>             #steps.Trigger.physicsDeclaredFilter(),
#>             #steps.Other.monsterEventFilter(),
#>             #steps.Other.hbheNoiseFilter(),
#181c182
#<             steps.Other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met)),
#---
#>             #steps.Other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met)),
#234c235
#<             steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
#---
#>             #steps.Other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
#237c238
#<             steps.Jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),
#---
#>             #steps.Jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),
#241c242
#<             steps.Other.variableGreaterFilter(0.55,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
#---
#>             steps.Other.variableGreaterFilter(0.53,"%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1])),
#251c252
#<             #steps.Other.skimmer(),
#---
#>             steps.Other.skimmer(),

##HT275-325
#dir = "/vols/cms02/elaird1/29_skims/06_had/275/"
#signalSkim.add("HT_skim", 'utils.fileListFromDisk(location = "%s/HT*_skim.root", isDirectory = False)'%dir, lumi = 183.0)
#
#signalSkim.add("tt_tauola_mg_skim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_*_skim.root", isDirectory = False)'%dir,xs = 2.033755e-03 * 1.575000e+02)
#signalSkim.add("zinv_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/zinv_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 5.542720e-05 * 5.715000e+03)
#signalSkim.add("w_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/w_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 1.442660e-05 * 3.192400e+04)
#
##HT325-375
#dir = "/vols/cms02/elaird1/29_skims/06_had/325/"
#signalSkim.add("HT_skim", 'utils.fileListFromDisk(location = "%s/HT*_skim.root", isDirectory = False)'%dir, lumi = 183.0)
#
#signalSkim.add("tt_tauola_mg_skim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_*_skim.root", isDirectory = False)'%dir,xs = 1.056029e-03 * 1.575000e+02)
#signalSkim.add("zinv_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/zinv_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 2.124709e-05 * 5.715000e+03)
#signalSkim.add("w_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/w_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 5.955936e-06 * 3.192400e+04)

#HT375
dir = "/vols/cms02/elaird1/29_skims/06_had/375/"
signalSkim.add("HT_skim", 'utils.fileListFromDisk(location = "%s/HT*_skim.root", isDirectory = False)'%dir, lumi = 940.8)

signalSkim.add("tt_tauola_mg_skim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_*_skim.root", isDirectory = False)'%dir,xs = 1.223216e-03 * 1.575000e+02)
signalSkim.add("zinv_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/zinv_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 3.279443e-05 * 5.715000e+03)
signalSkim.add("w_jets_mg_skim", 'utils.fileListFromDisk(location = "%s/w_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 7.014770e-06 * 3.192400e+04)

