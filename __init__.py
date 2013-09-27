from __wrappedChain__ import keyTracer
import defaults
import options
import sites

def whereami() :
    return max('/'.join(__file__.split('/')[:-1]), '.')

def batchScripts() :
    p = "%s/sites/%s" % (whereami(), sites.prefix())
    return {"submission": "%sSub.sh" % p,
            "jobTemplate": "%sJob.sh" % p,
            "condorTemplate": "%sTemplate.condor" % p,
            }

for item in [
    'autoBook',
    'wrappedChain',
    'organizer',
    'plotter',
    'analysisStep',
    'analysisLooper',
    'analysis',
    ] : exec("from __%s__ import %s"%(item,item))
