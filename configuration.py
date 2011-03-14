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
    return ["Gen", "Jet", "Muon", "Electron", "Photon", "Other", "Vertex", "XClean", "Top", "Compatibility"]

def samplesFiles() :
    return ["MC", "JetMET", "Muon", "Electron", "Photon", "SignalSkim", "WPol"]

def stepsFiles() :
    return ["Other", "Filter", "Histos", "Jet", "Trigger", "Photon", "Top", "Print", "Gen", "Xclean", "Displayer", "Master"]

def stepsToDisableForData() :
    return ["genMotherHistogrammer", "photonPurityPlots", "photonEfficiencyPlots"]

def stepsToDisableForMc() :
    return ["hltFilter", "hltFilterList", "lowestUnPrescaledTrigger", "lowestUnPrescaledTriggerHistogrammer", "hbheNoiseFilter", "bxFilter", "physicsDeclared", "techBitFilter", "hbheNoise"]

def histogramsToDisableForData() :
    return ["genpthat"]

def histogramsToDisableForMc() :
    return []

def sourceFiles() :
    return ["pragmas.h"]

def sitePrefix() :
    d = {"hep.ph.ic.ac.uk":"ic",
         "sesame1":"pu",
         "cern.ch":"cern",
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
                "queueHeaders"   : ["job-ID", "prior", "name", "user", "state", "submit1", "submit2", "queue", "slots", "ja-task-ID"],
                "queueVars"      : {"queue":"queue", "user":"user", "state":"state", "run":"r", "summary":"qstat -u '*'", "sample":"qstat | head"},
                },
        "pu"  :{"localOutputDir" : "/tmp/%s"%user,
                "globalOutputDir": "/tigress-hsm/%s/tmp/"%user,
                "dCachePrefix"   : "",
                "srmPrefix"      : "",
                "queueHeaders"   : ["Job id","Name","User","Time Use","S","Queue"],
                "queueVars"      : {"queueName":"hep", "queue": "Queue", "user":"User", "state":"S", "run":"R", "summary":"qstat", "sample": "qstat -u %s | head"%user}
                },
        "cern":{"localOutputDir" : "/tmp/%s"%user,
                "globalOutputDir": "/tmp/%s"%user,
                "dCachePrefix"   : "",
                "srmPrefix"      : "",
                "queueHeaders"   : ["JOBID", "USER", "STAT", "QUEUE", "FROM_HOST", "EXEC_HOST", "JOB_NAME", "SUBMIT_TIME"],
                "queueVars"      : {"queueName":"8nm", "queue":"QUEUE", "user":"USER", "state":"STAT", "run":"RUN", "summary":"bjobs -u all", "sample": "bjobs | head"}
                },
        "fnal":{"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/tmp/%s"%user,
                "globalOutputDir": "%s/supyOutput/"%os.environ["HOME"],
                #"globalOutputDir":"/pnfs/cms/WAX/resilient/%s/tmp/"%user,
                "dCachePrefix"   : "dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
                "srmPrefix"      : "srm://cmssrm.fnal.gov:8443/",
                "queueHeaders"   : ["ID", "OWNER", "SUBMITTED1", "SUBMITTED2", "RUN_TIME", "ST", "PRI", "SIZE", "CMD"],
                "queueVars"      : {"user":"OWNER", "state":"ST", "run":"R", "summary":"condor_q -global", "sample": "condor_q -global -submitter %s | head"%user}
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
         "cern":"mv %s %s"%(src, dest),
         "fnal":"mv %s %s"%(src, dest),
         #"fnal":"srmcp file:///%s %s/%s"%(src, srmPrefix("fnal"), dest.replace("/pnfs/cms/WAX/","/")),
        }
    assert site in d, "site %s does not have a mvCommand defined"%site
    return d[site]

srm = 'utils.fileListFromSrmLs(dCachePrefix = "%s", location="%s'%(siteInfo(key = "dCachePrefix"), siteInfo(key = "srmPrefix"))
