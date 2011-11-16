import samples
from core.configuration import srm
mumu = samples.SampleHolder()

#L1FJL2L3Residual
a = ", alwaysUseLastAttempt = True"
mumu.add("DoubleMu.Run2011A-05Aug2011-v1.AOD.job663", '%s/elaird/ICF/automated/2011_11_11_15_48_22/DoubleMu.Run2011A-05Aug2011-v1.AOD"%s)'%(srm,a),lumi = 356.7)
mumu.add("DoubleMu.Run2011A-May10ReReco-v1.AOD.job662", '%s/henning/ICF/automated/2011_11_11_14_03_49/DoubleMu.Run2011A-May10ReReco-v1.AOD")'%srm, lumi = 202.3)
mumu.add("DoubleMu.Run2011A-PromptReco-v4.AOD.job664", '%s/dburton/ICF/automated/2011_11_11_14_54_49/DoubleMu.Run2011A-PromptReco-v4.AOD")'%srm,   lumi = 851.5)
mumu.add("DoubleMu.Run2011A-PromptReco-v6.AOD.job665", '%s/bainbrid/ICF/automated/2011_11_12_15_35_18/DoubleMu.Run2011A-PromptReco-v6.AOD")'%srm,  lumi = 617.3)
mumu.add("DoubleMu.Run2011B-PromptReco-v1.AOD.job666", '%s/bm409/ICF/automated/2011_11_11_13_34_14/DoubleMu.Run2011B-PromptReco-v1.AOD")'%srm,     lumi = 2545.2)
