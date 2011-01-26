import os

def useCachedFileLists() :
    return True

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

def siteSpecs() :
    user = os.environ["USER"]
    return {
        "ic"  :{"localOutputDir" : "/vols/cms02/%s/tmp/"%user,
                "globalOutputDir": "/vols/cms02/%s/tmp/"%user,
                "dCachePrefix"   : "dcap://gfe02.grid.hep.ph.ic.ac.uk:22128",
                "srmPrefix"      : "srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/cms/store/user",
                },                 
        "pu"  :{"localOutputDir" : "/tmp/%s"%user,
                "globalOutputDir": "/tigress-hsm/%s/tmp/"%user,
                },
        "fnal":{"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/tmp/%s"%user,
                "globalOutputDir": "%s/supyOutput/"%os.environ["HOME"],
                #"globalOutputDir":"/pnfs/cms/WAX/resilient/%s/tmp/"%user,
                "dCachePrefix"   : "dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
                "srmPrefix"      : "srm://cmssrm.fnal.gov:8443/",
                },
        }

def siteInfo(site = None, key = None) :
    if site==None : site = sitePrefix()
    ss = siteSpecs()
    assert site in ss, "site %s does not appear in siteSpecs()"%site
    assert key in ss[site], "site %s does not have key %s"%(site, key)
    return ss[site][key]

def batchScripts() :
    p = sitePrefix()
    return ("%sSub.sh"%p, "%sJob.sh"%p, "%sTemplate.condor"%p)

def qlook() :
    return "%sQlook"%sitePrefix()
    
def mvCommand(site = None, src = None, dest = None) :
    d = {"ic":"mv %s %s"%(src, dest),
         "pu":"mv %s %s"%(src, dest),
         "fnal":"mv %s %s"%(src, dest),
         #"fnal":"srmcp file:///%s %s/%s"%(src, srmPrefix("fnal"), dest.replace("/pnfs/cms/WAX/","/")),
        }
    assert site in d, "site %s does not have a mvCommand defined"%site
    return d[site]

srm = 'utils.fileListFromSrmLs(dCachePrefix = "%s", location="%s'%(siteInfo(key = "dCachePrefix"), siteInfo(key = "srmPrefix"))
