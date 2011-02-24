import samples
from configuration import srm
wpol = samples.SampleHolder()

wpol.add("wpol_38", 'utils.fileListFromTextFile(fileName = "/home/hep/elaird1/58_wpol_events/EG_Nov4th_v1.txt")', lumi = 35.38)
wpol.add("wpol_39", 'utils.fileListFromTextFile(fileName = "/home/hep/elaird1/58_wpol_events/EG_39.txt")', lumi = 35.38)
