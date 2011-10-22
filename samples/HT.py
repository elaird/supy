import samples
from core.configuration import srm
ht = samples.SampleHolder()

#L1FJL2L3Residual
ht.add("HT.Run2011A-May10ReReco-v1.AOD.job536", '%s/dburton/ICF/automated/2011_10_04_23_05_48/HT.Run2011A-May10ReReco-v1.AOD", alwaysUseLastAttempt = True)'%srm, lumi = 1.0) #job 536, 1769/1769 completed
ht.add("HT.Run2011A-05Aug2011-v1.AOD.job528",     '%s/bm409/ICF/automated/2011_09_29_15_37_16/HT.Run2011A-05Aug2011-v1.AOD")'%srm, lumi = 1.0) #job 528,  550/552 completed
ht.add("HT.Run2011A-PromptReco-v4.AOD.job535",    '%s/bm409/ICF/automated/2011_10_04_17_23_30/HT.Run2011A-PromptReco-v4.AOD", alwaysUseLastAttempt = True)'%srm, lumi = 1.0) #job 535,  1735/2167 completed
ht.add("HT.Run2011A-PromptReco-v6.AOD.job527",    '%s/bm409/ICF/automated/2011_09_29_13_50_58/HT.Run2011A-PromptReco-v6.AOD", alwaysUseLastAttempt = True)'%srm, lumi = 1.0) #job 527,  838/839 completed
ht.add("HT.Run2011B-PromptReco-v1.AOD.job515",    '%s/bm409/ICF/automated/2011_09_19_19_13_32/HT.Run2011B-PromptReco-v1.AOD")'%srm, lumi = 1.0) #job 515,  336/381 completed
ht.add("HT.Run2011B-PromptReco-v1.AOD.job519",    '%s/bm409/ICF/automated/2011_09_26_16_02_44/HT.Run2011B-PromptReco-v1.AOD")'%srm, lumi = 1.0) #job 519,  361/400 completed
ht.add("HT.Run2011B-PromptReco-v1.AOD.job531",    '%s/bm409/ICF/automated/2011_10_03_12_23_10/HT.Run2011B-PromptReco-v1.AOD", alwaysUseLastAttempt = True)'%srm, lumi = 1.0) #job 531,  337/538 completed
#ht.add("HT.Run2011B-PromptReco-v1.AOD.job570",    '%s/bm409//ICF/automated/2011_10_17_12_55_58/HT.Run2011B-PromptReco-v1.AOD")'%srm, lumi = 1.0) #job 570,   82/ 432 completed
#jobs 533,564 ?? (e.g., compared with 531)
