import os

def maxArrayLength() :
    return 256

def computeEntriesForReport() :
    return False

def printNodesUsed() :
    return False

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

def sitePrefix() :
    d = {"hep.ph.ic.ac.uk":"ic",
         "sesame1":"pu",
         "fnal.gov":"fnal",
         }

    hostName = os.environ["HOSTNAME"]
    for match,prefix in d.iteritems() :
        if match in hostName :
            return prefix
    assert False,"hostname %s does not match anything in %s"%(hostName, str(d))

def batchScripts() :
    p = sitePrefix()
    return ("%sSub.sh"%p, "%sJob.sh"%p)

def qlook() :
    return "%sQlook"%sitePrefix()
    
def outputDir(sitePrefix, isLocal) :
    user = os.environ["USER"]

    #sitePrefix: (localOutputDir, globalOutputDir)
    d = {"ic":tuple(["/vols/cms02/%s/tmp/"%user]*2),
         #"ic":("/vols/cms02/elaird1/tmpLocal/", "/vols/cms02/elaird1/tmpGlobal/"),
         "pu":("/tmp/%s"%user, "/tigress-hsm/%s/tmp/"%user),
         "fnal":("/tmp/%s"%user, "/pnfs/cms/WAX/resilient/%s/tmp/"%user)
         }
         
    assert sitePrefix in d, "sitePrefix %s needs to have output directories defined"%sitePrefix
    return d[sitePrefix][int(not isLocal)]

def dCachePrefix() :
    d = {"ic":"dcap://gfe02.grid.hep.ph.ic.ac.uk:22128",
         "fnal":"dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
        }
    sp = sitePrefix()
    assert sp in d, "sitePrefix %s needs to have a dCache prefix defined"%sp
    return d[sp]

def srmPrefix() :
    d = {"ic":"srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/cms/store/user",
         "fnal":"srm://cmssrm.fnal.gov:8443/",
        }
    sp = sitePrefix()
    assert sp in d, "sitePrefix %s needs to have a srm prefix defined"%sp
    return d[sp]
