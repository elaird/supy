def maxArrayLength() :
    return 256

def fakeString() :
    return ";FAKE"

def calculablesFiles() :
    return ["Gen", "Jet", "Muon", "Electron", "Photon", "Other", "Vertex", "XClean", "Compatibility"]

def samplesFiles() :
    return ["MC", "JetMET", "Muon", "Photon", "SignalSkim"]

def stepsFiles() :
    return ["Other", "Jet", "Trigger", "Photon", "Print", "Gen", "Xclean", "Displayer", "Master"]

def stepsToDisableForData() :
    return ["genMotherHistogrammer", "photonPurityPlots", "photonEfficiencyPlots"]

def stepsToDisableForMc() :
    return ["hltFilter", "hltFilterList", "lowestUnPrescaledTrigger", "lowestUnPrescaledTriggerHistogrammer", "hbheNoiseFilter", "bxFilter", "physicsDeclared", "techBitFilter"]

def histogramsToDisableForData() :
    return ["genpthat"]

def histogramsToDisableForMc() :
    return []

def sourceFiles() :
    return ["pragmas.h"]

def batchScripts(hostName) :
    d = {"lx05.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
         "lx06.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
         }
    assert hostName in d,"hostname %s not recognized"%hostName
    return d[hostName]
