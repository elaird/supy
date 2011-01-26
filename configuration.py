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
    
def outputDir(site, isLocal) :
    user = os.environ["USER"]

    #sitePrefix: (localOutputDir, globalOutputDir)
    d = {"ic":tuple(["/vols/cms02/%s/tmp/"%user]*2),
         #"ic":("/vols/cms02/elaird1/tmpLocal/", "/vols/cms02/elaird1/tmpGlobal/"),
         "pu":("/tmp/%s"%user, "/tigress-hsm/%s/tmp/"%user),
         #"fnal":("/tmp/%s"%user, "/pnfs/cms/WAX/resilient/%s/tmp/"%user)
         "fnal":("/tmp/%s"%user, "%s/supyOutput/"%os.environ["HOME"])
         }
         
    assert site in d, "site %s needs to have output directories defined"%site
    return d[site][int(not isLocal)]

def dCachePrefix() :
    d = {"ic":"dcap://gfe02.grid.hep.ph.ic.ac.uk:22128",
         "fnal":"dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
        }
    site = sitePrefix()
    assert site in d, "site %s needs to have a dCache prefix defined"%site
    return d[site]

def srmPrefix(site = None) :
    d = {"ic":"srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/cms/store/user",
         "fnal":"srm://cmssrm.fnal.gov:8443/",
        }
    if site==None : site = sitePrefix() 
    assert site in d, "site %s needs to have a srm prefix defined"%site
    return d[site]

def mvCommand(site = None, src = None, dest = None) :
    d = {"ic":"mv %s %s"%(src, dest),
         "pu":"mv %s %s"%(src, dest),
         "fnal":"mv %s %s"%(src, dest),
         #"fnal":"srmcp file:///%s %s/%s"%(src, srmPrefix("fnal"), dest.replace("/pnfs/cms/WAX/","/")),
        }
    assert site in d, "site %s needs to have a mvCommand defined"%site
    return d[site]
