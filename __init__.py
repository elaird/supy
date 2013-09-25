from __wrappedChain__ import keyTracer
import defaults
import options
import batch


def whereami() :
    return max('/'.join(__file__.split('/')[:-1]), '.')

for item in [
    'autoBook',
    'wrappedChain',
    'organizer',
    'plotter',
    'analysisStep',
    'analysisLooper',
    'analysis',
    ] : exec("from __%s__ import %s"%(item,item))
