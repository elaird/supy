import samples
from core.configuration import srm
ht = samples.SampleHolder()

a = ", alwaysUseLastAttempt = True"
#L1FJL2L3Residual
ht.add("HT.Run2011A-May10ReReco-v1.AOD.job536", '%s/dburton/ICF/automated/2011_10_04_23_05_48/HT.Run2011A-May10ReReco-v1.AOD"%s)'%(srm,a), lumi = 1.0) #job 536, 1769/1769 comp.
ht.add("HT.Run2011A-05Aug2011-v1.AOD.job528",   '%s/bm409/ICF/automated/2011_09_29_15_37_16/HT.Run2011A-05Aug2011-v1.AOD")'%srm,           lumi = 1.0) #job 528,  550/552  comp.
ht.add("HT.Run2011A-PromptReco-v4.AOD.job535",  '%s/bm409/ICF/automated/2011_10_04_17_23_30/HT.Run2011A-PromptReco-v4.AOD"%s)'%(srm,a),    lumi = 1.0) #job 535, 1735/2167 comp.
ht.add("HT.Run2011A-PromptReco-v6.AOD.job527",  '%s/bm409/ICF/automated/2011_09_29_13_50_58/HT.Run2011A-PromptReco-v6.AOD"%s)'%(srm,a),    lumi = 1.0) #job 527,  838/839  comp.
ht.add("HT.Run2011B-PromptReco-v1.AOD.job515",  '%s/bm409/ICF/automated/2011_09_19_19_13_32/HT.Run2011B-PromptReco-v1.AOD")'%srm,          lumi = 1.0) #job 515,  336/381  comp.
ht.add("HT.Run2011B-PromptReco-v1.AOD.job519",  '%s/bm409/ICF/automated/2011_09_26_16_02_44/HT.Run2011B-PromptReco-v1.AOD")'%srm,          lumi = 1.0) #job 519,  361/400  comp.
ht.add("HT.Run2011B-PromptReco-v1.AOD.job531",  '%s/bm409/ICF/automated/2011_10_03_12_23_10/HT.Run2011B-PromptReco-v1.AOD"%s)'%(srm,a),    lumi = 1.0) #job 531,  337/538  comp.

ht.add("HT.Run2011B-PromptReco-v1.AOD.job533",  '%s/bm409//ICF/automated/2011_10_03_16_39_43/")'%srm, lumi = 1.0) #job 533,   108/125 comp.
ht.add("HT.Run2011B-PromptReco-v1.AOD.job564",  '%s/bm409//ICF/automated/2011_10_13_16_03_09/")'%srm, lumi = 1.0) #job 564,   435/438 comp.
ht.add("HT.Run2011B-PromptReco-v1.AOD.job592",  '%s/bm409//ICF/automated/2011_10_23_12_26_43/")'%srm, lumi = 1.0) #job 592,   203/204 comp.

#ht.add("HT.Run2011B-PromptReco-v1.AOD.job570",  '%s/bm409//ICF/automated/2011_10_17_12_55_58/HT.Run2011B-PromptReco-v1.AOD")'%srm,         lumi = 1.0) #job 570,   82/432  comp.
